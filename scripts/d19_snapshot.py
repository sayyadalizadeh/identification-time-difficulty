"""D19 (post hoc): one pass over the metadata snapshot for items A10, B9 and C3 and the family taxonomy of B7.

Reads the snapshot tables in place (observations, photos, taxa), each checked against its SHA-256 manifest in this
run. Writes only to outputs/D19/snapshot/.

- A10: flow counts for window W (2024-07-01 to 2024-09-30) per family of the eight, six new and 30 replication
  families, both halves and each half: all observations in W (valid observer and date); with a photograph; every
  photo id above max_M1; first photograph passing the licence and size filter (the frame filter of
  src/confirm/acquisition.build_frames); then by grade: research grade with an eligible species, research grade other,
  needs ID at genus or species rank with an eligible genus, needs ID other, casual, other. Check: the frame rows of
  window W equal the stored frame tables (eight families: locked half; new and replication families: both halves).
- B9: the (observer, species) pairs with at least one research-grade observation observed before 2024-05-01, for the
  observers of the phase-2 rows of eight_W, eight_W2 and new_W and the species of the eight and six new families.
- C3: snapshot fields of the observations of the earlier-gate photo manifests (training candidates): observer, half,
  grade, observed_on, species, family, first photograph.
- Family taxonomy: kingdom and class of the 44 families; species ancestry and texts (full registered text and the
  species name only) of every eligible species.
"""
import argparse
import csv
import gzip
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc

import d19_common as C
from src.confirm import acquisition as A
from src.confirm.config import load_config
from src.halves import is_locked

EXPOSURE_BEFORE = "2024-05-01"


def manifest_check(snap, manifest, log):
    man = {Path(r["path"]).name: r for r in csv.DictReader(open(manifest, encoding="utf-8"))}
    for fn in ("observations.csv.gz", "photos.csv.gz", "taxa.csv.gz"):
        t0 = time.time()
        ok = (snap / fn).stat().st_size == int(man[fn]["size"]) and A.sha256_file(snap / fn) == man[fn]["sha256"]
        log.check(f"manifest {fn}", ok, f"({time.time() - t0:.0f} s)")
        if not ok:
            raise RuntimeError(f"{fn} differs from its manifest")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--manifest", required=True)
    a = ap.parse_args()
    out = C.OUT / "snapshot"
    out.mkdir(parents=True, exist_ok=True)
    log = C.Log(out / "snapshot_log.txt")
    log("D19 snapshot pass (post hoc); threads", C.THREADS, "; started", time.strftime("%Y-%m-%d %H:%M:%S"))
    snap = Path(a.snapshot)
    manifest_check(snap, a.manifest, log)
    cfg = load_config()
    e1 = pd.read_csv(C.ROOT / "inputs/earlier_gates/outputs/G-IG8.0/e1_species_primary.csv")
    sets = {"eight": cfg["sets"]["eight"]["families"], "new": cfg["sets"]["new"]["families"],
            "replication": cfg["sets"]["replication"]["families"]}
    fam_set = {f: k for k, v in sets.items() for f in v}
    fams = list(fam_set)
    ids = e1[e1["family"].isin(fams)].drop_duplicates("family_taxon_id")
    fam_ids = dict(zip(ids["family_taxon_id"].astype(int), ids["family"]))
    log.check("44 families found once in the eligible-species table", sorted(fam_ids.values()) == sorted(fams),
              f"{len(fam_ids)}")
    lab = {f: set(e1[(e1["family"] == f) & (e1["eligible_primary"] == "yes")]["species_taxon_id"].astype(int))
           for f in fams}
    tax = A.taxonomy(snap)
    fam_of, species_of, genus_of = A.species_genus_maps(tax, fam_ids)
    lab_genera = {f: {genus_of.get(s) for s in lab[f]} - {None} for f in fams}
    log("taxonomy read; taxa of the 44 families:", len(fam_of))

    # family taxonomy (kingdom, class) and species texts
    rows = []
    for t, f in fam_ids.items():
        anc = [int(x) for x in tax["anc"][t].split("/") if x]
        nm = {tax["rank"].get(x): tax["name"][x] for x in anc if tax["rank"].get(x) in ("kingdom", "phylum", "class", "order")}
        rows.append({"family": f, "family_taxon_id": t, "set": fam_set[f], "kingdom": nm.get("kingdom"),
                     "phylum": nm.get("phylum"), "class": nm.get("class"), "order": nm.get("order"),
                     "eligible_species": len(lab[f])})
    C.save_csv(pd.DataFrame(rows).sort_values(["set", "family"]), out / "families_taxonomy.csv")
    sp_rows = []
    for f in fams:
        for s in sorted(lab[f]):
            sp_rows.append({"family": f, "species_taxon_id": s, "name": tax["name"][s], "text_full": A.species_text(tax, s),
                            "ancestry": tax["anc"][s]})
    pd.DataFrame(sp_rows).to_parquet(out / "species_texts.parquet", index=False)
    log("eligible species written:", len(sp_rows))

    # code arrays over taxon ids
    names = fams
    code = {n: i for i, n in enumerate(names)}
    tax_fam = np.full(tax["tid"].max() + 1, -1, np.int16)
    for t, f in fam_of.items():
        tax_fam[t] = code[f]
    expo_fams = np.array([fam_set[f] in ("eight", "new") for f in names])

    # observers of the phase-2 rows of the three sets (B9) and training candidates (C3)
    obs_b9 = set()
    for s in ("eight_W", "eight_W2", "new_W"):
        p2 = pd.read_parquet(C.CONF / s / "phase2.parquet", columns=["observer_id", "selected"])
        obs_b9 |= set(p2.loc[p2["selected"], "observer_id"].astype(np.int64))
    obs_b9 = np.array(sorted(obs_b9), np.int64)
    log("observers of the phase-2 rows (B9):", len(obs_b9))
    mans = []
    for g in ("ig8", "ig9", "ig10"):
        m = pd.read_csv(C.ROOT / f"inputs/earlier_gates/code/docs/manifests/{g}_photos_manifest.csv")
        mans.append(m[["photo_id", "observation_uuid", "family"]].assign(source=g))
    cand = pd.concat(mans, ignore_index=True)
    cand_u = pd.Index(sorted(set(cand["observation_uuid"])))
    log("training-candidate photographs:", len(cand), "observations:", len(cand_u))

    w0, w1 = cfg["windows"]["W"]["start"], cfg["windows"]["W"]["end"]
    max_m1 = int(cfg["windows"]["W"]["max_M1"])
    licences = cfg["frame"]["licences"]
    min_side = int(cfg["frame"]["min_shorter_side_px"])

    # ---------------- pass 1: observations
    U, O, Tx, F, G = [], [], [], [], []
    expo = []
    CU, CO, CT, CG, CD = [], [], [], [], []
    t1 = time.time()
    types = {"observation_uuid": pa.string(), "observer_id": pa.int64(), "taxon_id": pa.int64(),
             "quality_grade": pa.string(), "observed_on": pa.string()}
    nrows = 0
    for b in A._batches(snap / "observations.csv.gz", types):
        nrows += b.num_rows
        t_ = A._int(b.column("taxon_id"), 0)
        t_ = np.where((t_ > 0) & (t_ < len(tax_fam)), t_, 0)
        f = tax_fam[t_]
        fk = np.flatnonzero(f >= 0)  # only rows of the 44 families are examined further
        if not len(fk):
            continue
        b = b.take(pa.array(fk))
        t_, f = t_[fk], f[fk]
        d = b.column("observed_on")
        okdate = pc.is_valid(pc.strptime(d, format="%Y-%m-%d", unit="s", error_is_null=True)).to_numpy(zero_copy_only=False)
        okobs = pc.is_valid(b.column("observer_id")).to_numpy(zero_copy_only=False)
        inw = pc.and_(pc.greater_equal(d, w0), pc.less_equal(d, w1)).fill_null(False).to_numpy(zero_copy_only=False)
        keep = inw & (f >= 0) & okobs & okdate
        if keep.any():
            k = pa.array(np.flatnonzero(keep))
            U.append(pc.take(b.column("observation_uuid"), k))
            O.append(A._int(pc.take(b.column("observer_id"), k), -1))
            Tx.append(t_[keep])
            F.append(f[keep])
            G.append(pc.take(b.column("quality_grade"), k))
        # B9: research grade, observed before 2024-05-01, eight or new families, observer of a phase-2 row
        before = pc.less(d, EXPOSURE_BEFORE).fill_null(False).to_numpy(zero_copy_only=False)
        rg = pc.equal(b.column("quality_grade"), "research").fill_null(False).to_numpy(zero_copy_only=False)
        ob = A._int(b.column("observer_id"), -1)
        kx = before & okdate & rg & (f >= 0) & np.isin(ob, obs_b9)
        if kx.any():
            fx = f[kx]
            kx2 = np.flatnonzero(kx)[expo_fams[fx]]
            if len(kx2):
                expo.append(pd.DataFrame({"observer_id": ob[kx2], "taxon": t_[kx2]}))
        # C3: training candidates (rows of the 44 families; the candidates belong to the eight families)
        ci =cand_u.get_indexer(b.column("observation_uuid").to_numpy(zero_copy_only=False))
        kc = np.flatnonzero(ci >= 0)
        if len(kc):
            ka = pa.array(kc)
            CU.append(pc.take(b.column("observation_uuid"), ka).to_numpy(zero_copy_only=False))
            CO.append(ob[kc])
            CT.append(A._int(pc.take(b.column("taxon_id"), ka), 0))
            CG.append(pc.take(b.column("quality_grade"), ka).to_numpy(zero_copy_only=False))
            CD.append(pc.take(d, ka).to_numpy(zero_copy_only=False))
    log(f"pass 1: {nrows:,} observation rows read in {(time.time() - t1) / 60:.1f} min")
    w = pd.DataFrame({"observation_uuid": pa.chunked_array(U).to_numpy(), "observer_id": np.concatenate(O),
                      "taxon": np.concatenate(Tx), "fam_code": np.concatenate(F)})
    w["quality_grade"] = pa.chunked_array(G).to_numpy()
    lk = {o: is_locked(int(o)) for o in np.unique(w["observer_id"])}
    w["locked"] = w["observer_id"].map(lk).to_numpy()
    log("window-W rows of the 44 families:", len(w), "locked:", int(w["locked"].sum()))

    ex = pd.concat(expo, ignore_index=True) if expo else pd.DataFrame(columns=["observer_id", "taxon"])
    ex["species"] = ex["taxon"].map(species_of)
    ex = ex.dropna(subset=["species"]).astype({"species": np.int64})
    ex = ex[["observer_id", "species"]].drop_duplicates()
    ex.to_parquet(out / "b9_exposure_pairs.parquet", index=False)
    log("B9 (observer, species) pairs with a research-grade observation before", EXPOSURE_BEFORE, ":", len(ex))

    cs = pd.DataFrame({"observation_uuid": np.concatenate(CU) if CU else [], "observer_id": np.concatenate(CO) if CO else [],
                       "taxon": np.concatenate(CT) if CT else [], "quality_grade": np.concatenate(CG) if CG else [],
                       "observed_on": np.concatenate(CD) if CD else []})
    log("training candidates found in the snapshot:", len(cs), "of", len(cand_u))

    # ---------------- pass 2: photos (first photograph by position; as build_frames)
    allu = pd.Index(np.concatenate([w["observation_uuid"].to_numpy(), cs["observation_uuid"].to_numpy()]))
    if not allu.is_unique:
        allu = pd.Index(pd.unique(allu))
    m = len(allu)
    min_pid = np.full(m, A.BIG, np.int64)
    fpos = np.full(m, A.BIG, np.int64)
    fpid = np.full(m, -1, np.int64)
    flic = np.full(m, -1, np.int8)
    fw, fh, nph = np.zeros(m, np.int64), np.zeros(m, np.int64), np.zeros(m, np.int64)
    licmap = {v: i for i, v in enumerate(licences)}
    t2 = time.time()
    types = {"photo_id": pa.int64(), "observation_uuid": pa.string(), "license": pa.string(),
             "width": pa.int64(), "height": pa.int64(), "position": pa.int64()}
    prow = 0
    for b in A._batches(snap / "photos.csv.gz", types):
        prow += b.num_rows
        ix = allu.get_indexer(b.column("observation_uuid").to_numpy(zero_copy_only=False))
        k = np.flatnonzero(ix >= 0)
        if not len(k):
            continue
        ka = pa.array(k)
        ix = ix[k]
        pid = A._int(pc.take(b.column("photo_id"), ka), -1)
        pos = A._int(pc.take(b.column("position"), ka), -1)
        pos = np.where(pos >= 0, pos, A.POS_EMPTY)
        wd, ht = A._int(pc.take(b.column("width"), ka), 0), A._int(pc.take(b.column("height"), ka), 0)
        lic = pd.Series(pc.take(b.column("license"), ka).to_numpy(zero_copy_only=False)).map(licmap).fillna(len(licences))
        lic = lic.to_numpy().astype(np.int8)
        g = pid >= 0
        ix, pid, pos, wd, ht, lic = ix[g], pid[g], pos[g], wd[g], ht[g], lic[g]
        np.minimum.at(min_pid, ix, pid)
        np.add.at(nph, ix, 1)
        o = np.lexsort((np.arange(len(ix)), pos, ix))
        ixs = ix[o]
        head = o[np.r_[True, ixs[1:] != ixs[:-1]]]
        hi = ix[head]
        better = (pos[head] < fpos[hi]) | (fpid[hi] < 0)
        hb = head[better]
        ib = ix[hb]
        fpos[ib], fpid[ib], flic[ib], fw[ib], fh[ib] = pos[hb], pid[hb], lic[hb], wd[hb], ht[hb]
    log(f"pass 2: {prow:,} photo rows read in {(time.time() - t2) / 60:.1f} min")

    # ---------------- A10 flow
    iw = allu.get_indexer(w["observation_uuid"])
    has = fpid[iw] >= 0
    above = has & (min_pid[iw] > max_m1)
    filt = above & (flic[iw] >= 0) & (flic[iw] < len(licences)) & (fw[iw] > 0) & (fh[iw] > 0) & \
        (np.minimum(fw[iw], fh[iw]) >= min_side)
    fam_names = np.array(names)[w["fam_code"].to_numpy()]
    sp = w["taxon"].map(species_of)
    gn = w["taxon"].map(genus_of)
    rk = w["taxon"].map(tax["rank"])
    qg = w["quality_grade"].to_numpy()
    res_el = (qg == "research") & np.array([s == s and s is not None and int(s) in lab[f] for s, f in zip(sp, fam_names)])
    need_el = (qg == "needs_id") & rk.isin(["species", "genus"]).to_numpy() & \
        np.array([g == g and g is not None and int(g) in lab_genera[f] for g, f in zip(gn, fam_names)])
    sp_el = np.array([s == s and s is not None and int(s) in lab[f] for s, f in zip(sp, fam_names)])
    flow = pd.DataFrame({"family": fam_names, "locked": w["locked"].to_numpy(), "all_in_W": True, "with_photo": has,
                         "all_photo_ids_above_max_M1": above, "licence_and_size_filter": filt,
                         "eligible_species_any_grade": filt & sp_el, "research_eligible": filt & res_el,
                         "research_other": filt & (qg == "research") & ~res_el, "needs_id_eligible": filt & need_el,
                         "needs_id_other": filt & (qg == "needs_id") & ~need_el, "casual": filt & (qg == "casual"),
                         "other_grade": filt & ~np.isin(qg, ["research", "needs_id", "casual"])})
    cols = [c for c in flow.columns if c not in ("family", "locked")]
    parts = []
    for half, sel in (("both", np.ones(len(flow), bool)), ("locked", flow["locked"].to_numpy()),
                      ("development", ~flow["locked"].to_numpy())):
        t = flow[sel].groupby("family")[cols].sum().reset_index()
        t.insert(1, "half", half)
        parts.append(t)
    fl = pd.concat(parts, ignore_index=True)
    fl.insert(1, "set", fl["family"].map(fam_set))
    C.save_csv(fl.sort_values(["set", "family", "half"]), out / "a10_flow.csv")
    # check against the stored frames (window W)
    fe = pd.read_parquet(C.CONF / "frames/frames_eight_locked.parquet", columns=["window", "family", "grade"])
    fn = pd.read_parquet(C.CONF / "frames/frames_new_replication_both.parquet", columns=["window", "family", "grade"])
    ref = pd.concat([fe[fe["window"] == "W"], fn[fn["window"] == "W"]]).groupby(["family", "grade"]).size()
    bad = 0
    for f in fams:
        half = "locked" if fam_set[f] == "eight" else "both"
        r = fl[(fl["family"] == f) & (fl["half"] == half)].iloc[0]
        for g, col in (("research", "research_eligible"), ("needs_id", "needs_id_eligible")):
            if int(ref.get((f, g), 0)) != int(r[col]):
                bad += 1
                log(f"  frame mismatch {f} {g}: stored {int(ref.get((f, g), 0))} recomputed {int(r[col])}")
    log.check("A10 frame rows of window W equal the stored frames (88 family x grade cells)", bad == 0,
              f"mismatches {bad}")

    # ---------------- C3 training candidates
    ic = allu.get_indexer(cs["observation_uuid"])
    cs["first_photo_id"] = fpid[ic]
    cs["n_photos"] = nph[ic]
    cs["family"] = cs["taxon"].map(fam_of)
    cs["species"] = cs["taxon"].map(species_of)
    cs["locked"] = [is_locked(int(o)) for o in cs["observer_id"]]
    cand2 = cand.merge(cs, on="observation_uuid", how="left", suffixes=("_manifest", ""))
    cand2.to_parquet(out / "c3_training_candidates.parquet", index=False)
    log("C3 candidate rows written:", len(cand2), "locked observers among them:", int(cand2["locked"].fillna(False).sum()))
    log("finished", time.strftime("%Y-%m-%d %H:%M:%S"), f"({(time.time() - log.t0) / 60:.1f} min)")
    log("FAILED CHECKS:", log.fails if log.fails else "none")
    if log.fails:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
