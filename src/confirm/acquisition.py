"""Acquisition code of the confirmatory pipeline (plan draft 3, sections 4 and 5).

- build_frames: one pass over the snapshot observations and one over the photos (files checked against the SHA-256
  manifest) for a list of families and windows; frame rules of section 4.1 (first photograph passing the licence and
  size filter, every photo id above max_M1, research grade with the species in the label space or needs_id with an
  eligible genus; research_only for the replication design); half filter (development, locked or both).
- phase1: per family a simple random sample of n1 frame rows (whole frame if smaller), candidates sorted by uuid,
  excluding given uuids; one generator.
- fetch_histories: public API v1, up to 200 uuids per request, at least one second between requests, at most 3 retries
  with back-off; stops if requests keep failing for more than 30 minutes; raw responses gzipped in a git-ignored folder.
- parse_histories / strata: owner, created_at, location, identifications (current, disagreement, vision, hidden
  excluded, created up to 2026-10-27 23:59:59 UTC); T (src/d6_lib.t_days), research grade at dates S, label support,
  disagreement before research grade, vision assistance, number of agreeing species-level identifications.
- stratum_counts and phase2: counts per family and stratum; phase-2 selection with the registered fractions and the cap
  rule; weight = (frame size / phase-1 size) / realized phase-2 fraction of the stratum.
- download_photos: first photographs (medium) with 8 connections, manifest (photo id, bytes, SHA-256, status).
- duplicates: exact SHA-256 groups and 64-bit perceptual hashes (imagehash.phash).
"""
import csv
import gzip
import hashlib
import json
import shutil
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pcsv

from src import d6_lib as L
from src.halves import is_locked
from src.confirm.config import ROOT

API = "https://api.inaturalist.org/v1/observations?uuid={uuids}&per_page=200&order_by=id&order=asc"
PHOTO_URL = "https://inaturalist-open-data.s3.amazonaws.com/photos/{photo_id}/medium.{extension}"
UA = {"User-Agent": "research-script/1.0"}
PAUSES = [5, 30, 60]
BIG = np.iinfo(np.int64).max
POS_EMPTY = np.iinfo(np.int32).max


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def _batches(path, types):
    return pcsv.open_csv(path, read_options=pcsv.ReadOptions(block_size=64 << 20),
                         parse_options=pcsv.ParseOptions(delimiter="\t", quote_char=False),
                         convert_options=pcsv.ConvertOptions(include_columns=list(types), column_types=types))


def _int(col, fill):
    return col.fill_null(fill).to_numpy(zero_copy_only=False).astype(np.int64)


# ---------------------------------------------------------------- taxonomy and label spaces
def taxonomy(snapshot):
    tx = pd.read_csv(gzip.open(Path(snapshot) / "taxa.csv.gz", "rt", encoding="utf-8"), sep="\t",
                     quoting=csv.QUOTE_NONE, usecols=["taxon_id", "ancestry", "rank_level", "rank", "name"], dtype=str,
                     keep_default_na=False)
    tid = tx["taxon_id"].astype(np.int64).to_numpy()
    return {"tid": tid, "rank": dict(zip(tid, tx["rank"])), "name": dict(zip(tid, tx["name"])),
            "rlev": dict(zip(tid, pd.to_numeric(tx["rank_level"], errors="coerce"))),
            "anc": dict(zip(tid, tx["ancestry"]))}


def species_genus_maps(tax, fam_ids):
    """family, species (taxon or nearest species ancestor below species) and genus (genus taxon or genus ancestor of a
    species taxon) of every taxon of the given families (as in scripts/d04_sample.py)."""
    rank, rlev, anc = tax["rank"], tax["rlev"], tax["anc"]
    fam_of, species_of, genus_of = {}, {}, {}
    for t in tax["tid"]:
        a_ = [int(x) for x in anc[t].split("/") if x]
        f = fam_ids.get(t) or next((fam_ids[x] for x in a_ if x in fam_ids), None)
        if not f:
            continue
        fam_of[t] = f
        if rank[t] == "species":
            species_of[t] = t
        elif rlev[t] == rlev[t] and rlev[t] < 10:
            species_of[t] = next((x for x in reversed(a_) if rank.get(x) == "species"), None)
        if rank[t] == "genus":
            genus_of[t] = t
        elif rank[t] == "species":
            genus_of[t] = next((x for x in reversed(a_) if rank.get(x) == "genus"), None)
    return fam_of, species_of, genus_of


def species_text(tax, s):
    """'a photo of ' + kingdom, phylum, class, order and family names + species name + '.' (section 6)."""
    names = {}
    for x in [int(v) for v in tax["anc"][s].split("/") if v]:
        r = tax["rank"].get(x)
        if r in ("kingdom", "phylum", "class", "order", "family"):
            names[r] = tax["name"][x]
    parts = [names.get(r) for r in ("kingdom", "phylum", "class", "order", "family") if names.get(r)]
    return "a photo of " + " ".join(parts + [tax["name"][s]]) + "."


# ---------------------------------------------------------------- frames
def build_frames(snapshot, manifest, family_ids, label_space, windows, max_m1, licences, min_side, half, info):
    """family_ids: {family taxon id: name}; label_space: {name: set of species ids}; windows: {name: (start, end)}.
    Returns one DataFrame with every frame row (both grades) of every family and window, development or locked half
    as asked ('development', 'locked', 'both'); locked rows are dropped before any field other than the observer id is
    used when half = 'development'."""
    snap = Path(snapshot)
    man = {Path(r["path"]).name: r for r in csv.DictReader(open(manifest, encoding="utf-8"))}
    for fn in ("observations.csv.gz", "photos.csv.gz", "taxa.csv.gz"):
        ok = (snap / fn).stat().st_size == int(man[fn]["size"]) and sha256_file(snap / fn) == man[fn]["sha256"]
        info[f"manifest_{fn}"] = ok
        if not ok:
            raise RuntimeError(f"{fn} differs from its manifest")
    tax = taxonomy(snap)
    fam_of, species_of, genus_of = species_genus_maps(tax, family_ids)
    names = list(dict.fromkeys(family_ids.values()))
    code = {n: i for i, n in enumerate(names)}
    tax_fam = np.full(tax["tid"].max() + 1, -1, np.int16)
    for t, f in fam_of.items():
        tax_fam[t] = code[f]
    lab_genera = {f: {genus_of.get(s) for s in label_space.get(f, ())} - {None} for f in names}
    U, O, Tx, F, G, Wn, LA, LO = [], [], [], [], [], [], [], []
    t1 = time.time()
    types = {"observation_uuid": pa.string(), "observer_id": pa.int64(), "taxon_id": pa.int64(),
             "quality_grade": pa.string(), "observed_on": pa.string(), "latitude": pa.float64(), "longitude": pa.float64()}
    for b in _batches(snap / "observations.csv.gz", types):
        t_ = _int(b.column("taxon_id"), 0)
        t_ = np.where((t_ > 0) & (t_ < len(tax_fam)), t_, 0)
        f = tax_fam[t_]
        d = b.column("observed_on")
        win = np.full(b.num_rows, -1, np.int8)
        for wi, (s0, s1) in enumerate(windows.values()):
            m = pc.and_(pc.greater_equal(d, s0), pc.less_equal(d, s1)).fill_null(False).to_numpy(zero_copy_only=False)
            win[m] = wi
        keep = (win >= 0) & (f >= 0) & pc.is_valid(b.column("observer_id")).to_numpy(zero_copy_only=False)
        if keep.any():
            k = pa.array(np.flatnonzero(keep))
            ok = pc.is_valid(pc.strptime(pc.take(d, k), format="%Y-%m-%d", unit="s", error_is_null=True))
            k = pc.filter(k, ok)
            kn = k.to_numpy()
            U.append(pc.take(b.column("observation_uuid"), k))
            O.append(_int(pc.take(b.column("observer_id"), k), -1))
            Tx.append(t_[kn])
            F.append(f[kn])
            Wn.append(win[kn])
            G.append(pc.take(b.column("quality_grade"), k))
            LA.append(pc.take(b.column("latitude"), k).to_numpy(zero_copy_only=False))
            LO.append(pc.take(b.column("longitude"), k).to_numpy(zero_copy_only=False))
    info["pass1_minutes"] = round((time.time() - t1) / 60, 1)
    w = pd.DataFrame({"observation_uuid": pa.chunked_array(U).to_numpy(), "observer_id": np.concatenate(O),
                      "taxon": np.concatenate(Tx), "fam_code": np.concatenate(F), "win_code": np.concatenate(Wn),
                      "latitude": np.concatenate(LA), "longitude": np.concatenate(LO)})
    grade = pa.chunked_array(G).to_numpy()
    lk = {o: is_locked(int(o)) for o in np.unique(w["observer_id"])}
    locked = w["observer_id"].map(lk).to_numpy()
    sel = ~locked if half == "development" else (locked if half == "locked" else np.ones(len(w), bool))
    info["rows_in_windows"] = int(len(w))
    w = w[sel].reset_index(drop=True)
    w["quality_grade"] = grade[sel]
    info["rows_in_windows_half"] = int(len(w))
    index = pd.Index(w["observation_uuid"])
    if not index.is_unique:
        raise RuntimeError("observation_uuid not unique")
    m = len(index)
    min_pid = np.full(m, BIG, np.int64)
    fpos = np.full(m, BIG, np.int64)
    fpid = np.full(m, -1, np.int64)
    flic = np.full(m, -1, np.int8)
    fw, fh, nph = np.zeros(m, np.int64), np.zeros(m, np.int64), np.zeros(m, np.int64)
    fext = np.empty(m, object)
    licmap = {v: i for i, v in enumerate(licences)}
    t2 = time.time()
    types = {"photo_id": pa.int64(), "observation_uuid": pa.string(), "extension": pa.string(), "license": pa.string(),
             "width": pa.int64(), "height": pa.int64(), "position": pa.int64()}
    for b in _batches(snap / "photos.csv.gz", types):
        ix = index.get_indexer(b.column("observation_uuid").to_numpy(zero_copy_only=False))
        k = np.flatnonzero(ix >= 0)
        if not len(k):
            continue
        ka = pa.array(k)
        ix = ix[k]
        pid = _int(pc.take(b.column("photo_id"), ka), -1)
        pos = _int(pc.take(b.column("position"), ka), -1)
        pos = np.where(pos >= 0, pos, POS_EMPTY)
        wd, ht = _int(pc.take(b.column("width"), ka), 0), _int(pc.take(b.column("height"), ka), 0)
        lic = pd.Series(pc.take(b.column("license"), ka).to_numpy(zero_copy_only=False)).map(licmap).fillna(len(licences))
        lic = lic.to_numpy().astype(np.int8)
        ext = pc.take(b.column("extension"), ka).to_numpy(zero_copy_only=False)
        g = pid >= 0
        ix, pid, pos, wd, ht, lic, ext = ix[g], pid[g], pos[g], wd[g], ht[g], lic[g], ext[g]
        np.minimum.at(min_pid, ix, pid)
        np.add.at(nph, ix, 1)
        o = np.lexsort((np.arange(len(ix)), pos, ix))
        ixs = ix[o]
        head = o[np.r_[True, ixs[1:] != ixs[:-1]]]
        hi = ix[head]
        better = (pos[head] < fpos[hi]) | (fpid[hi] < 0)
        hb = head[better]
        ib = ix[hb]
        fpos[ib], fpid[ib], flic[ib], fw[ib], fh[ib], fext[ib] = pos[hb], pid[hb], lic[hb], wd[hb], ht[hb], ext[hb]
    info["pass2_minutes"] = round((time.time() - t2) / 60, 1)
    has = fpid >= 0
    w["in_window"] = has & (min_pid > max_m1) & (flic >= 0) & (flic < len(licences)) & (fw > 0) & (fh > 0) & \
        (np.minimum(fw, fh) >= min_side)
    w["first_photo_id"], w["extension"], w["license_code"] = fpid, fext, flic
    w["width"], w["height"], w["n_photos"] = fw, fh, nph
    w["family"] = np.array(names)[w["fam_code"].to_numpy()]
    w["window"] = np.array(list(windows))[w["win_code"].to_numpy()]
    w["species"] = w["taxon"].map(species_of)
    w["genus_label"] = w["taxon"].map(genus_of)
    rk = w["taxon"].map(tax["rank"])
    w["research_eligible"] = (w["quality_grade"] == "research").to_numpy() & np.array(
        [s == s and s is not None and int(s) in label_space.get(f, ()) for s, f in zip(w["species"], w["family"])])
    w["needs_eligible"] = (w["quality_grade"] == "needs_id").to_numpy() & rk.isin(["species", "genus"]).to_numpy() & \
        np.array([g == g and g is not None and int(g) in lab_genera[f] for g, f in zip(w["genus_label"], w["family"])])
    fr = w[w["in_window"] & (w["research_eligible"] | w["needs_eligible"])].copy()
    fr["grade"] = np.where(fr["research_eligible"], "research", "needs_id")
    # research: the genus label is the genus of the species
    fr.loc[fr["grade"] == "research", "genus_label"] = fr.loc[fr["grade"] == "research", "species"].map(genus_of)
    return fr.drop(columns=["fam_code", "win_code", "research_eligible", "needs_eligible", "in_window"]), tax


# ---------------------------------------------------------------- phase 1
def phase1(frame, n1, rng, exclude=(), research_only=False):
    """Per family (in the order of first appearance), a simple random sample of n1 rows of the frame (whole frame if
    smaller); candidates sorted by uuid; uuids in exclude are removed first."""
    parts, sizes = [], {}
    fr = frame[~frame["observation_uuid"].isin(set(exclude))]
    if research_only:
        fr = fr[fr["grade"] == "research"]
    for f in dict.fromkeys(fr["family"]):
        c = fr[fr["family"] == f].sort_values("observation_uuid").reset_index(drop=True)
        k = min(n1, len(c))
        pick = rng.choice(len(c), size=k, replace=False)
        parts.append(c.iloc[np.sort(pick)].assign(frame_size=len(c), n1=k))
        sizes[f] = (len(c), k)
    return pd.concat(parts, ignore_index=True), sizes


# ---------------------------------------------------------------- API histories
def _fetch(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def fetch_histories(uuids, raw_dir, timing, max_fail_minutes=30.0, min_free_gb=5.0):
    """Batches of 200 uuids; existing batch files are kept (resumable). Returns a status dict."""
    raw = Path(raw_dir)
    raw.mkdir(parents=True, exist_ok=True)
    bl = [uuids[i:i + 200] for i in range(0, len(uuids), 200)]
    last, t0, failed, fail_since = 0.0, time.time(), [], None
    for b, bu in enumerate(bl):
        f = raw / f"batch_{b:05d}.json.gz"
        if f.exists():
            continue
        if shutil.disk_usage(ROOT).free / 1e9 < min_free_gb:
            return {"stopped": "free space", "failed": failed, "requests": b}
        ok = False
        for attempt in range(4):
            wait = 1.0 - (time.time() - last)
            if wait > 0:
                time.sleep(wait)
            last = time.time()
            try:
                body = _fetch(API.format(uuids=",".join(bu)))
                got = [o["uuid"] for o in json.loads(body).get("results", [])]
                if not set(got) <= set(bu) or len(got) != len(set(got)):
                    raise RuntimeError(f"batch {b}: unrequested or duplicated uuid returned")
                with gzip.open(f, "wb") as g:
                    g.write(body)
                ok = True
                fail_since = None
                break
            except RuntimeError:
                raise
            except Exception:  # noqa: BLE001
                fail_since = fail_since or time.time()
                if (time.time() - fail_since) / 60 > max_fail_minutes:
                    return {"stopped": "API failing for more than 30 minutes", "failed": failed, "requests": b}
                if attempt < 3:
                    time.sleep(PAUSES[attempt])
        if not ok:
            failed.append(b)
    timing["api_seconds"] = timing.get("api_seconds", 0) + time.time() - t0
    timing["api_requests"] = timing.get("api_requests", 0) + len(bl)
    return {"stopped": None, "failed": failed, "requests": len(bl)}


def parse_histories(raw_dir):
    """uuid -> record with owner, created_ns, location, identifications (ts, id, user, taxon, rank level, ancestors,
    current, disagreement, vision), hidden ones excluded and counted; numeric ids only."""
    rec, hidden = {}, 0
    for p in sorted(Path(raw_dir).glob("*.json.gz")):
        d = json.load(gzip.open(p, "rt", encoding="utf-8"))
        for o in d.get("results", []):
            ids = []
            for i in o.get("identifications") or []:
                if i.get("hidden"):
                    hidden += 1
                    continue
                tx = i.get("taxon") or {}
                rl = tx.get("rank_level")
                ids.append((pd.Timestamp(i["created_at"]).value, i.get("id"), (i.get("user") or {}).get("id"),
                            tx.get("id"), float(rl) if rl is not None else 99.0,
                            frozenset(int(x) for x in (tx.get("ancestor_ids") or [])), i.get("current") is True,
                            i.get("disagreement") is True, bool(i.get("vision"))))
            loc = o.get("location")
            rec[o["uuid"]] = {"owner": int(o["user"]["id"]), "created_ns": pd.Timestamp(o["created_at"]).value,
                              "location": loc, "ids": sorted(ids, key=lambda x: (x[0], x[1])),
                              "obs_id": int(o["id"]) if o.get("id") is not None else None}
    return rec, hidden


def rg_at(r, sp_id, end_ns):
    """Research grade with species sp_id using the identifications created before end_ns (N2 of D4)."""
    last = {}
    for x in r["ids"]:
        if x[0] >= end_ns:
            break
        last[x[2]] = x
    return L.n2([y for y in last.values() if y[4] <= 10], sp_id)


def history_fields(r, grade, species, genus_label, dates, horizon_days=540):
    """T, research grade at each date (identifications created on or before the UTC date), created before each date,
    support, disagreement before research grade, vision of the first identification, agreeing species-level
    identifications today, T within the common horizon."""
    out = {}
    cut = L.CUTOFF
    ids = [x for x in r["ids"] if x[0] < cut]
    rr = dict(r, ids=ids)
    if grade == "research":
        T = L.t_days(rr, int(species))
        out["T"] = T
        out["rg_today"] = rg_at(rr, int(species), cut)
        for d in dates:
            end = pd.Timestamp(d, tz="UTC").value + L.DAY_NS
            out[f"rg_{d}"] = rg_at(rr, int(species), end)
            out[f"created_before_{d}"] = r["created_ns"] < end
        t_rg = r["created_ns"] + (T * L.DAY_NS if np.isfinite(T) else 0)
        sp_ids = [x for x in ids if x[4] <= 10]
        out["disagreement"] = any(x[7] for x in sp_ids if not np.isfinite(T) or x[0] <= t_rg)
        last = {}
        for x in ids:
            last[x[2]] = x
        out["agreeing"] = sum(1 for x in last.values() if x[4] <= 10 and (x[3] == int(species) or int(species) in x[5]))
        out["disagreeing_now"] = sum(1 for x in last.values() if x[4] <= 10 and not (x[3] == int(species)
                                                                                      or int(species) in x[5]))
        out["T_within_horizon"] = bool(np.isfinite(T) and T <= horizon_days)
    else:
        out["support"] = L.support(rr, int(genus_label))
        users = {int(x[2]) for x in ids if x[6] and (x[3] == int(genus_label) or int(genus_label) in x[5])}
        out["support_other"] = len(users - {r["owner"]})
    out["proposed"] = frozenset(int(x[3]) for x in ids if x[4] == 10 and x[3] is not None)
    out["vision"] = bool(ids[0][8]) if ids else False
    out["owner"] = r["owner"]
    out["created_ns"] = r["created_ns"]
    out["location"] = r["location"]
    return out


def stratum(grade, T, support):
    if grade == "research":
        if not np.isfinite(T):
            return ""
        return "A0" if T < 1 else ("A1" if T < 30 else ("A2" if T < 365 else "A3"))
    return "B2" if support >= 2 else "B1"


# ---------------------------------------------------------------- between the phases
def stratum_counts(p1):
    t = p1.groupby(["family", "stratum"]).size().unstack(fill_value=0)
    for s in ("A0", "A1", "A2", "A3", "B1", "B2", ""):
        if s not in t.columns:
            t[s] = 0
    t = t.rename(columns={"": "excluded_T_undefined"})
    return t[["A0", "A1", "A2", "A3", "B1", "B2", "excluded_T_undefined"]]


def cap_fractions(n, f_A0, f_B1, planned_f, cap_factor=1.5):
    """Cap rule of section 4.3 for one family. n: {stratum: phase-1 count}; planned_f: planned photographs. Returns
    ({stratum: phase-2 fraction}, rule text, cap). Uses stratum counts only."""
    fa, fb, f1 = f_A0, (f_B1 or 0.0), 1.0
    fixed = n["A1"] + n["A2"] + n["A3"] + n["B2"]
    cap = cap_factor * planned_f
    need = fixed + fa * n["A0"] + fb * n["B1"]
    rule = "registered fractions"
    if need > cap:
        g = max(0.0, (cap - fixed) / (fa * n["A0"] + fb * n["B1"])) if (fa * n["A0"] + fb * n["B1"]) > 0 else 0.0
        g = min(g, 1.0)
        fa, fb = fa * g, fb * g
        rule = "fractions reduced by the cap rule"
        if fixed > cap and n["A1"] > 0:
            f1 = max(0.0, (cap - n["A2"] - n["A3"] - n["B2"]) / n["A1"])
            rule = "fractions reduced to 0 and A1 subsampled by the cap rule"
    return {"A0": fa, "A1": f1, "A2": 1.0, "A3": 1.0, "B1": fb, "B2": 1.0}, rule, cap


def expected_phase2(n, frac):
    """Phase-2 photographs implied by the fractions (same rounding as phase2)."""
    return sum(int(round(frac[s] * n[s])) for s in frac)


def phase2(p1, f_A0, f_B1, planned, rng, cap_factor=1.5):
    """Phase-2 selection per family with the cap rule (section 4.3). planned: {family: planned photographs}.
    Returns the phase-1 table with columns selected and w, and a table of realized fractions per family."""
    p1 = p1.copy()
    p1["selected"] = False
    p1["w"] = 0.0
    real = []
    for f in dict.fromkeys(p1["family"]):
        k = (p1["family"] == f).to_numpy()
        st = p1.loc[k, "stratum"].to_numpy()
        n = {s: int((st == s).sum()) for s in ("A0", "A1", "A2", "A3", "B1", "B2")}
        frac, rule, cap = cap_fractions(n, f_A0, f_B1, planned[f], cap_factor)
        idx = np.flatnonzero(k)
        base = p1.loc[k, "frame_size"].iloc[0] / p1.loc[k, "n1"].iloc[0]
        rf = {"family": f, "rule": rule, "planned": planned[f], "cap": cap}
        for s, fr_ in frac.items():
            j = idx[st == s]
            m = int(round(fr_ * len(j)))
            if m > 0:  # D12 correction: strata with no row kept are skipped (division by zero before)
                pick = j[rng.choice(len(j), m, replace=False)]
                p1.loc[p1.index[pick], "selected"] = True
                p1.loc[p1.index[pick], "w"] = base / (m / len(j))
            rf[f"n_{s}"], rf[f"kept_{s}"] = len(j), m
        real.append(rf)
    return p1, pd.DataFrame(real)


# ---------------------------------------------------------------- photographs
def download_photos(rows, photo_dir, budget, threads=8, min_free_gb=5.0):
    """rows: DataFrame with first_photo_id and extension. Existing files with a manifest line are kept. budget: dict
    with 'limit_bytes' and 'used_bytes' (shared across the whole run); the batch stops when the limit is reached.
    Returns the manifest DataFrame and timing."""
    pdir = Path(photo_dir)
    pdir.mkdir(parents=True, exist_ok=True)
    mp = pdir / "manifest.csv"
    done = pd.read_csv(mp) if mp.exists() else pd.DataFrame(columns=["photo_id", "bytes", "sha256", "status"])
    have = set(done.loc[done["status"] == "ok", "photo_id"].astype(np.int64))
    todo = [(int(p), e) for p, e in zip(rows["first_photo_id"], rows["extension"]) if int(p) not in have]
    out, t0 = [], time.time()

    def get(item):
        pid, ext = item
        for attempt in range(4):
            try:
                b = _fetch(PHOTO_URL.format(photo_id=pid, extension=ext), timeout=60)
                (pdir / f"{pid}.{ext}").write_bytes(b)
                return {"photo_id": pid, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest(), "status": "ok"}
            except Exception:  # noqa: BLE001
                if attempt < 3:
                    time.sleep(PAUSES[attempt] / 5)
        return {"photo_id": pid, "bytes": 0, "sha256": "", "status": "failed"}

    stopped = None
    for s in range(0, len(todo), 400):
        if shutil.disk_usage(ROOT).free / 1e9 < min_free_gb:
            stopped = "free space"
            break
        if budget["used_bytes"] >= budget["limit_bytes"]:
            stopped = "download budget"
            break
        with ThreadPoolExecutor(threads) as ex:
            res = list(ex.map(get, todo[s:s + 400]))
        out += res
        budget["used_bytes"] += sum(r["bytes"] for r in res)
    man = pd.concat([done, pd.DataFrame(out)], ignore_index=True).drop_duplicates("photo_id", keep="last")
    man.to_csv(mp, index=False, lineterminator="\n")
    return man, {"seconds": time.time() - t0, "downloaded": len(out), "stopped": stopped}


def read_checked(photo_dir, pid, ext, sha):
    b = (Path(photo_dir) / f"{pid}.{ext}").read_bytes()
    if hashlib.sha256(b).hexdigest() != sha:
        raise RuntimeError(f"photograph {pid} differs from its manifest")
    return b


def phash_values(paths):
    """64-bit perceptual hash (imagehash.phash, 8 x 8) of each image path: (unsigned 64-bit values, readable flags).
    D12 correction: values are unsigned (a 64-bit hash does not fit a signed integer)."""
    import imagehash
    from PIL import Image, ImageOps
    out, ok = [], []
    for p in paths:
        try:
            with Image.open(p) as im:
                h = imagehash.phash(ImageOps.exif_transpose(im).convert("RGB"))
            out.append(int(str(h), 16))
            ok.append(True)
        except Exception:  # noqa: BLE001
            out.append(0)
            ok.append(False)
    return np.array(out, dtype=np.uint64), np.array(ok, bool)


def hamming_pairs(hashes, max_d=12):
    """All pairs (i, j, distance) with Hamming distance <= max_d (numpy popcount over blocks)."""
    h = np.asarray(hashes).astype(np.uint64)
    n = len(h)
    res = []
    table = np.array([bin(v).count("1") for v in range(256)], np.int64)
    for i in range(n - 1):
        x = np.bitwise_xor(h[i], h[i + 1:])
        d = np.zeros(len(x), np.int64)
        for sh in range(0, 64, 8):
            d += table[((x >> np.uint64(sh)) & np.uint64(255)).astype(np.int64)]
        j = np.flatnonzero(d <= max_d)
        res += [(i, i + 1 + int(k), int(d[k])) for k in j]
    return res


def cell_of(location, deg=10):
    """10-degree cell 'lat|lon' of an API location string 'lat,lon' (public coordinates), or None."""
    if not location:
        return None
    la, lo = (float(x) for x in str(location).split(","))
    return f"{int(np.floor(la / deg))}|{int(np.floor(lo / deg))}"


def identifier_availability(rows, rec, scale, days=90):
    """Section 7.3, item 5: for each row (family, cell, created_ns), the number of distinct non-owner users who
    identified sampled observations of the same family and cell during the days before its creation, times scale
    (the inverse phase-1 sampling fraction of the family). rows: DataFrame with observation_uuid, family, cell,
    created_ns; rec: parsed histories of the sampled observations; scale: {family: factor}."""
    ev = []
    fam_of = dict(zip(rows["observation_uuid"], rows["family"]))
    cell_of_row = dict(zip(rows["observation_uuid"], rows["cell"]))
    for u, r in rec.items():
        if u not in fam_of or cell_of_row.get(u) is None:
            continue
        for x in r["ids"]:
            if x[0] < L.CUTOFF and x[2] is not None and int(x[2]) != r["owner"]:
                ev.append((fam_of[u], cell_of_row[u], x[0], int(x[2])))
    ev = pd.DataFrame(ev, columns=["family", "cell", "ts", "user"])
    out = np.zeros(len(rows))
    grp = {k: g.sort_values("ts") for k, g in ev.groupby(["family", "cell"])} if len(ev) else {}
    win = days * L.DAY_NS
    for i, (f, c, t) in enumerate(zip(rows["family"], rows["cell"], rows["created_ns"])):
        g = grp.get((f, c))
        if g is None or not np.isfinite(t):
            continue
        ts = g["ts"].to_numpy()
        a, b = np.searchsorted(ts, t - win), np.searchsorted(ts, t)
        out[i] = len(set(g["user"].to_numpy()[a:b])) * scale.get(f, 1.0)
    return out


def identifier_measures(targets, hist_rows, rec, scale, days=90):
    """Section 7.3, item 5 (N18a): for each target row (family, cell, created_ns), identifier availability = the number
    of distinct non-owner users who identified sampled observations of the same family and cell during the days
    before its creation, times scale[family] (population / number of sampled observations with a history), and
    experience = the median number of earlier identifications (before the target's creation) of these users in the
    family within the same histories (NaN without such users). hist_rows: DataFrame (observation_uuid, family, cell)
    of every sampled observation with a history (the set's phase-1 histories plus the stored development histories of
    the same window); rec: parsed histories covering hist_rows. Identifications created after the cutoff are ignored."""
    ev = []
    for u, f, c in zip(hist_rows["observation_uuid"], hist_rows["family"], hist_rows["cell"]):
        r = rec.get(u)
        if r is None:
            continue
        for x in r["ids"]:
            if x[0] < L.CUTOFF and x[2] is not None and int(x[2]) != r["owner"]:
                ev.append((f, c, x[0], int(x[2])))
    ev = pd.DataFrame(ev, columns=["family", "cell", "ts", "user"])
    avail = np.zeros(len(targets))
    exper = np.full(len(targets), np.nan)
    if not len(ev):
        return avail, exper
    grp = {k: g.sort_values("ts") for k, g in ev[ev["cell"].notna()].groupby(["family", "cell"])}
    by_user = {k: np.sort(g["ts"].to_numpy()) for k, g in ev.groupby(["family", "user"])}
    win = days * L.DAY_NS
    for i, (f, c, t) in enumerate(zip(targets["family"], targets["cell"], targets["created_ns"])):
        g = grp.get((f, c)) if c is not None else None
        if g is None or not np.isfinite(t):
            continue
        ts = g["ts"].to_numpy()
        a, b = np.searchsorted(ts, t - win), np.searchsorted(ts, t)
        users = set(g["user"].to_numpy()[a:b])
        avail[i] = len(users) * scale.get(f, 1.0)
        if users:
            exper[i] = float(np.median([np.searchsorted(by_user[(f, u)], t) for u in users]))
    return avail, exper
