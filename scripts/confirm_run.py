"""Entry point of the confirmatory pipeline (plan draft 3): one sub-command per step, --mode dry-run or confirmatory.

Sub-commands (every step after 'frame' reads a part specification, a JSON file):
  frame          snapshot frames of a list of families and windows (files checked against the SHA-256 manifest)
  phase1         phase-1 sample of the part (seed 20261121; state of the generator saved for the later steps)
  covariates     observed_on, observer-activity stratum and queue load of the phase-1 rows from the snapshot (files
                 checked against the SHA-256 manifest; src/confirm/covariates.py)
  histories      identification histories from the public API, history fields and strata
  report-strata  stratum counts and the projected photographs, gigabytes and hours (the report between the phases)
  phase2         phase-2 selection with the registered fractions and the cap rule; weights
  download       first photographs of the phase-2 observations, with a manifest; failures per stratum
  predict        top-1 species of the four models; exact and perceptual duplicates
  analyse        every estimate of sections 7 and 10 that applies to the part, with the bootstrap
  h6             H6 over parts (Spearman correlation of Delta and the fast share across families, one-sided
                 permutation test, and a bootstrap interval of rho over families) with the not-estimable rule; --spec
                 names a JSON file with keys parts (list of part output folders), model, n_perm, n_boot and out
  analyse-joint  heterogeneity over several parts analysed together (groups of plan section 10 across the eight and
                 the six new families, per-family Delta and ER, and the Spearman relation over their families);
                 --spec names a JSON file with keys parts (list of part specifications), models, replicates, n_perm, out
  decide         Holm over H1 to H6 and the grading of section 9 (src/confirm/decide.py); --spec names a JSON file
                 with keys parts ({eight_W, new_W, eight_W2: analysis folders}), h6 (h6.json), secondary_models, out
The guard (src/confirm/guard.py) is called before any history, photograph or prediction is read; in dry-run mode it
refuses locked observers and the six new and 30 replication families.

Part specification keys: name, out, families, window, frame, n1, f_A0, f_B1, research_only, exclude (list of
'path:column'), dates, s_star, models, planned_fraction ({family: expected phase-2 share of phase 1}), replicates,
q_window (true for window W of the eight families), eligible (species table), snapshot, manifest, hf_cache,
analysis_out (optional subfolder of out for the outputs of 'analyse'), replicates_hypotheses (5,000 replicates for
the estimates that carry a hypothesis: Delta and ER of the primary model, and with hypothesis_c2 also O, R and G_sup
at S*), ident_sources (stored development histories of the same window: list of {api_raw, table}) and
ident_population_extra ({family: development-half frame size} added to the part's frame size for the scale of
identifier availability).
"""
import os
THREADS = 20
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = str(THREADS)
import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src import d6_lib as L  # noqa: E402
from src import moderation as MD  # noqa: E402
from src.confirm import acquisition as A  # noqa: E402
from src.confirm import analysis as AN  # noqa: E402
from src.confirm import covariates as CV  # noqa: E402
from src.confirm import decide as DC  # noqa: E402
from src.confirm import estimators as E  # noqa: E402
from src.confirm import guard as G  # noqa: E402
from src.confirm.config import load_config  # noqa: E402

PHOTO_B, PHOTO_S = 3_020_246_545 / 23_747, 0.110


def spec_of(path):
    s = json.loads(Path(path).read_text(encoding="utf-8"))
    s["out"] = ROOT / s["out"]
    s["out"].mkdir(parents=True, exist_ok=True)
    return s


def save_json(p, obj):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=1, default=str)


def guard(a, s, step, families, observers):
    G.check(a.mode, f"{s['name']}: {step}", families, observers, s["out"].parent / "guard_log.jsonl")


def timing_update(s, **kw):
    p = s["out"] / "timing.json"
    t = json.loads(p.read_text()) if p.exists() else {}
    t.update(kw)
    save_json(p, t)


# ---------------------------------------------------------------- steps
def cmd_frame(a):
    cfg = load_config()
    e1 = pd.read_csv(a.eligible)
    fams = a.families
    G.check(a.mode, "frame", fams, [], ROOT / a.out_dir / "guard_log.jsonl")
    ids = e1[e1["family"].isin(fams)].drop_duplicates("family_taxon_id")
    fam_ids = dict(zip(ids["family_taxon_id"].astype(int), ids["family"]))
    lab = {f: set(e1[(e1["family"] == f) & (e1["eligible_primary"] == "yes")]["species_taxon_id"].astype(int))
           for f in fams}
    wins = {w: (cfg["windows"][w]["start"], cfg["windows"][w]["end"]) for w in a.windows}
    info = {"families": fams, "windows": a.windows, "half": a.half}
    t0 = time.time()
    fr, _ = A.build_frames(a.snapshot, a.manifest, fam_ids, lab, wins, cfg["windows"]["W"]["max_M1"],
                           cfg["frame"]["licences"], cfg["frame"]["min_shorter_side_px"], a.half, info)
    info["minutes"] = round((time.time() - t0) / 60, 1)
    info["frame_rows"] = fr.groupby(["window", "family", "grade"]).size().reset_index(name="n").to_dict("records")
    out = ROOT / a.out_dir
    out.mkdir(parents=True, exist_ok=True)
    fr.to_parquet(out / a.name, index=False)
    save_json(out / (a.name + ".json"), info)
    print(json.dumps({k: v for k, v in info.items() if k != "frame_rows"}, indent=1))


def cmd_phase1(a):
    s = spec_of(a.spec)
    fr = pd.read_parquet(ROOT / s["frame"])
    fr = fr[(fr["window"] == s["window"]) & fr["family"].isin(s["families"])]
    excl = set()
    for e in s.get("exclude", []):
        p, c = e.rsplit(":", 1)
        t = pd.read_parquet(ROOT / p) if p.endswith(".parquet") else pd.read_csv(ROOT / p)
        excl |= set(t[c])
    rng = L.rng_new()
    p1, sizes = A.phase1(fr, s["n1"], rng, excl, s.get("research_only", False))
    L.rng_save(rng, s["out"] / "rng_after_phase1.json")
    p1.to_parquet(s["out"] / "phase1.parquet", index=False)
    save_json(s["out"] / "phase1.json", {"frame_and_sample_sizes": sizes, "excluded_uuids": len(excl)})
    print(sizes)


def cmd_covariates(a):
    s = spec_of(a.spec)
    p1 = pd.read_parquet(s["out"] / "phase1.parquet")
    guard(a, s, "covariates", p1["family"].unique(), p1["observer_id"].unique())
    e1 = pd.read_csv(ROOT / s["eligible"])
    ids = e1[e1["family"].isin(s["families"])].drop_duplicates("family_taxon_id")
    fam_ids = dict(zip(ids["family_taxon_id"].astype(int), ids["family"]))
    if sorted(fam_ids.values()) != sorted(s["families"]):
        raise RuntimeError("family taxon ids not found once for each family")
    info = {"families": s["families"]}
    t0 = time.time()
    cov = CV.snapshot_covariates(s["snapshot"], s["manifest"], fam_ids, p1, info)
    info["minutes"] = round((time.time() - t0) / 60, 2)
    cov.to_parquet(s["out"] / "covariates.parquet", index=False)
    save_json(s["out"] / "covariates.json", info)
    print(json.dumps(info, indent=1, default=str))


def cmd_histories(a):
    s = spec_of(a.spec)
    p1 = pd.read_parquet(s["out"] / "phase1.parquet")
    guard(a, s, "histories", p1["family"].unique(), p1["observer_id"].unique())
    tm = {}
    st = A.fetch_histories(p1["observation_uuid"].tolist(), s["out"] / "api_raw", tm)
    if st["stopped"]:  # API failing for more than 30 minutes or free space: the step stops (resumable)
        save_json(s["out"] / "histories_stopped.json", st)
        raise RuntimeError(f"histories stopped: {st['stopped']}")
    rec, hidden = A.parse_histories(s["out"] / "api_raw")
    guard(a, s, "history owners", p1["family"].unique(), [r["owner"] for r in rec.values()])
    rows = []
    for r in p1.itertuples(index=False):
        h = rec.get(r.observation_uuid)
        if h is None:
            rows.append({"history": False})
            continue
        f = A.history_fields(h, r.grade, r.species, r.genus_label, s["dates"])
        f["history"] = True
        rows.append(f)
    hf = pd.DataFrame(rows, index=p1.index)
    d = pd.concat([p1, hf], axis=1)
    for col in ("T", "support"):  # D12 correction: a design without one grade has no column for it
        if col not in d:
            d[col] = np.nan
    d["stratum"] = [A.stratum(g, t if t == t else np.nan, sp if sp == sp else 0) if h else "failed"
                    for g, t, sp, h in zip(d["grade"], d["T"], d["support"], d["history"])]
    d.loc[d["stratum"] == "", "stratum"] = "excluded_T_undefined"
    d["proposed"] = d["proposed"].apply(lambda x: sorted(x) if isinstance(x, (set, frozenset)) else [])
    d.to_parquet(s["out"] / "strata.parquet", index=False)
    rgshare = float(d.loc[(d["grade"] == "research") & d["history"], "rg_today"].mean())
    save_json(s["out"] / "histories.json", dict(st, hidden=hidden, returned=int(d["history"].sum()),
                                                requested=int(len(d)), research_rg_today_share=rgshare))
    timing_update(s, api_seconds=tm.get("api_seconds", 0), api_requests=tm.get("api_requests", 0),
                  api_observations=int(len(d)))
    print(st, "research reconstructed today", round(rgshare, 4))


def planned_photos(s, p1):
    return {f: s["planned_fraction"][f] * int((p1["family"] == f).sum()) for f in p1["family"].unique()}


def cmd_report_strata(a):
    s = spec_of(a.spec)
    d = pd.read_parquet(s["out"] / "strata.parquet")
    guard(a, s, "stratum counts", d["family"].unique(), d["observer_id"].unique())
    t = A.stratum_counts(d[d["stratum"] != "failed"])
    t["failed_history"] = d[d["stratum"] == "failed"].groupby("family").size().reindex(t.index).fillna(0).astype(int)
    fa, fb = s["f_A0"], s.get("f_B1") or 0.0
    t["expected_phase2"] = t["A1"] + t["A2"] + t["A3"] + t["B2"] + fa * t["A0"] + fb * t["B1"]
    plan = planned_photos(s, d)
    t["planned"] = [plan[f] for f in t.index]
    t["cap"] = 1.5 * t["planned"]
    # after the registered cap rule (stratum counts only; same function and rounding as phase 2; N18a)
    after, rules = [], []
    for f in t.index:
        n = {k: int(t.loc[f, k]) for k in ("A0", "A1", "A2", "A3", "B1", "B2")}
        frac, rule, _ = A.cap_fractions(n, s["f_A0"], s.get("f_B1"), plan[f])
        after.append(A.expected_phase2(n, frac))
        rules.append(rule)
    t["phase2_after_cap"] = after
    t["cap_rule"] = rules
    t["expected_GB"] = t["expected_phase2"] * PHOTO_B / 1e9
    t["projected_bytes_after_cap"] = (t["phase2_after_cap"] * PHOTO_B).round().astype(np.int64)
    t["expected_download_hours"] = t["phase2_after_cap"] * PHOTO_S / 3600
    t.reset_index().to_csv(s["out"] / "stratum_report.csv", index=False, lineterminator="\n")
    print(t.to_string())


def cmd_phase2(a):
    s = spec_of(a.spec)
    d = pd.read_parquet(s["out"] / "strata.parquet")
    guard(a, s, "phase 2", d["family"].unique(), d["observer_id"].unique())
    rng = L.rng_load(s["out"] / "rng_after_phase1.json")
    plan = planned_photos(s, d)
    p2, real = A.phase2(d, s["f_A0"], s.get("f_B1"), plan, rng)
    L.rng_save(rng, s["out"] / "rng_after_phase2.json")
    p2.to_parquet(s["out"] / "phase2.parquet", index=False)
    real.to_csv(s["out"] / "phase2_fractions.csv", index=False, lineterminator="\n")
    print(real.to_string())


def cmd_download(a):
    s = spec_of(a.spec)
    p2 = pd.read_parquet(s["out"] / "phase2.parquet")
    sel = p2[p2["selected"]]
    guard(a, s, "download", sel["family"].unique(), sel["observer_id"].unique())
    # download budget (N18a): limit and counter of the mode from configs/confirmatory.yaml; the confirmatory counter
    # starts from 0 and the dry-run counter is never used by the confirmatory run
    rs = load_config()["run_settings"]
    mode = "confirmatory" if a.mode == "confirmatory" else "dry_run"
    bp = ROOT / rs["download_counter"][mode]
    bp.parent.mkdir(parents=True, exist_ok=True)
    budget = {"limit_bytes": int(rs["download_limit_bytes"][mode]),
              "used_bytes": json.loads(bp.read_text())["used_bytes"] if bp.exists() else 0}
    man, tm = A.download_photos(sel, s["out"] / "photos", budget)
    bp.write_text(json.dumps({"used_bytes": budget["used_bytes"]}), encoding="utf-8")
    if tm["stopped"]:  # free space or download budget reached: the step stops (resumable)
        raise RuntimeError(f"download stopped: {tm['stopped']}")
    ok = set(man.loc[man["status"] == "ok", "photo_id"].astype(np.int64))
    sel = sel.assign(photo_ok=sel["first_photo_id"].astype(np.int64).isin(ok))
    fail = sel.groupby(["family", "stratum"]).agg(selected=("photo_ok", "size"), ok=("photo_ok", "sum")).reset_index()
    fail["failed"] = fail["selected"] - fail["ok"]
    fail["failed_share"] = fail["failed"] / fail["selected"]
    fail.to_csv(s["out"] / "photo_failures.csv", index=False, lineterminator="\n")
    mm = man[man["photo_id"].isin(sel["first_photo_id"])]
    timing_update(s, download_seconds=tm["seconds"], downloaded=tm["downloaded"],
                  bytes=int(mm.loc[mm["status"] == "ok", "bytes"].sum()), photographs_ok=int(sel["photo_ok"].sum()),
                  download_stopped=tm["stopped"])
    print(tm, "failed share max", round(float(fail["failed_share"].max()), 4))


def cmd_predict(a):
    from src import zeroshot as Z
    from src.confirm import infer as I
    s = spec_of(a.spec)
    p2 = pd.read_parquet(s["out"] / "phase2.parquet")
    man = pd.read_csv(s["out"] / "photos/manifest.csv").set_index("photo_id")
    ok = man.index[man["status"] == "ok"]
    d = p2[p2["selected"] & p2["first_photo_id"].isin(ok)].reset_index(drop=True)
    guard(a, s, "predict", d["family"].unique(), d["observer_id"].unique())
    tax = A.taxonomy(s["snapshot"])
    e1 = pd.read_csv(ROOT / s["eligible"])
    spaces = {f: np.sort(e1[(e1["family"] == f) & (e1["eligible_primary"] == "yes")]["species_taxon_id"].astype(np.int64).to_numpy())
              for f in d["family"].unique()}
    fam_ids = dict(zip(e1.drop_duplicates("family_taxon_id")["family_taxon_id"].astype(int), e1.drop_duplicates("family_taxon_id")["family"]))
    fam_ids = {k: v for k, v in fam_ids.items() if v in spaces}
    _, _, genus_of = A.species_genus_maps(tax, fam_ids)
    texts = {f: [A.species_text(tax, int(x)) for x in sp] for f, sp in spaces.items()}
    blobs = {}
    for f in spaces:
        sub = d[d["family"] == f]
        blobs[f] = [A.read_checked(s["out"] / "photos", int(p), e, man.loc[int(p), "sha256"])
                    for p, e in zip(sub["first_photo_id"], sub["extension"])]
    out, tinf = d[["observation_uuid", "family", "grade", "species", "genus_label"]].copy(), {}
    for key in s["models"]:
        m = I.load(key, s["hf_cache"])
        t0, n = time.time(), 0
        pred = np.zeros(len(d), np.int64)
        for f in spaces:
            k = np.flatnonzero((d["family"] == f).to_numpy())
            if len(k):
                pred[k] = I.predict_family(m, blobs[f], texts[f], spaces[f])
                n += len(k)
        tinf[key] = (time.time() - t0) / max(n, 1)
        Z.free_model(m)
        out[f"p_{key}"] = pred
        out[f"c_{key}"] = ((out["grade"] == "research") & (pred == out["species"].fillna(-1).astype(np.int64))).astype(float)
        pg = np.array([genus_of.get(int(x)) or -1 for x in pred])
        out[f"g_{key}"] = (pg == out["genus_label"].fillna(-2).astype(np.int64).to_numpy()).astype(float)
    # duplicates: exact SHA-256 and 64-bit perceptual hash; threshold h from the configuration (D13 addendum 1)
    h_dup = int(load_config()["sensitivity"]["duplicates_h"])
    sha = man.loc[d["first_photo_id"].astype(np.int64), "sha256"].to_numpy()
    out["exact_dup_drop"] = pd.Series(sha).duplicated(keep="first").to_numpy()
    paths = [s["out"] / "photos" / f"{int(p)}.{e}" for p, e in zip(d["first_photo_id"], d["extension"])]
    hv, hok = A.phash_values(paths)
    idx = np.flatnonzero(hok)
    pairs = [(int(idx[i]), int(idx[j]), dd) for i, j, dd in A.hamming_pairs(hv[idx], 12)] if len(idx) > 1 else []
    pr = pd.DataFrame(pairs, columns=["i", "j", "distance"])
    pr.to_csv(s["out"] / "phash_pairs.csv", index=False, lineterminator="\n")
    grp = np.full(len(d), -1)
    for i, j, dist in pairs:
        if dist <= h_dup:
            gi = grp[i] if grp[i] >= 0 else (grp[j] if grp[j] >= 0 else i)
            grp[i] = grp[j] = gi
    out["dup_group"] = grp
    out.to_parquet(s["out"] / "predictions.parquet", index=False)
    timing_update(s, inference_seconds_per_photo=tinf, photographs_predicted=int(len(d)))
    acc = out[out["grade"] == "research"].groupby("family")[[f"c_{k}" for k in s["models"]]].mean()
    acc.reset_index().to_csv(s["out"] / "accuracy.csv", index=False, lineterminator="\n")
    flags = []
    for key in s["models"]:
        for f in spaces:
            r = out[(out["family"] == f) & (out["grade"] == "research")]
            fl = E.regime_check(r[f"p_{key}"].to_numpy(), r["species"].astype(np.int64).to_numpy())
            flags.append({"model": key, "family": f, "flagged_species": " ".join(map(str, fl)), "flagged": bool(fl)})
    pd.DataFrame(flags).to_csv(s["out"] / "regime_check.csv", index=False, lineterminator="\n")
    print(acc.round(3).to_string())
    print({k: round(v * 1000, 2) for k, v in tinf.items()}, "seconds per 1,000 photographs")


def exact_duplicates(d, man, rec):
    """Plan section 5 (I7): among the first photographs of different sampled observations, exact SHA-256 duplicates
    keep only the observation with the lowest id (numeric observation id of the API record). Returns a boolean array
    (True = dropped)."""
    sha = man.loc[d["first_photo_id"].astype(np.int64), "sha256"].to_numpy()
    oid = np.array([(rec.get(u) or {}).get("obs_id") for u in d["observation_uuid"]], dtype=float)
    if np.isnan(oid).any():
        raise RuntimeError(f"{int(np.isnan(oid).sum())} rows without an observation id in the histories")
    t = pd.DataFrame({"sha": sha, "oid": oid, "i": np.arange(len(d))}).sort_values(["sha", "oid"], kind="stable")
    drop = np.zeros(len(d), bool)
    drop[t.loc[t["sha"].duplicated(keep="first"), "i"].to_numpy()] = True
    return drop


def prepare_rows(a, s, info, covariates=True):
    """Analysis rows of one part: phase-2 rows with a prediction, exact duplicates dropped (lowest id kept), history
    fields, cell, snapshot covariates, identifier availability and experience, Q (window W of the eight families)."""
    p2 = pd.read_parquet(s["out"] / "phase2.parquet")
    pr = pd.read_parquet(s["out"] / "predictions.parquet")
    guard(a, s, "analyse", p2["family"].unique(), p2["observer_id"].unique())
    rec, _ = A.parse_histories(s["out"] / "api_raw")
    d = p2.merge(pr.drop(columns=["family", "grade", "species", "genus_label"]), on="observation_uuid", how="inner")
    man = pd.read_csv(s["out"] / "photos/manifest.csv").set_index("photo_id")
    drop = exact_duplicates(d, man, rec)
    info["exact_duplicates_dropped"] = int(drop.sum())
    info["exact_duplicates_dropped_by_predict_step"] = int(d["exact_dup_drop"].sum())
    d = d[~drop].reset_index(drop=True)
    for col in ("support", "support_other", "agreeing", "disagreeing_now", "T_within_horizon", "disagreement", "vision"):
        if col not in d:  # D12 correction: columns of a grade absent from the design
            d[col] = np.nan
    d["genus"] = d["genus_label"]
    d["cell"] = [A.cell_of(x) for x in d["location"]]
    if covariates:
        # snapshot covariates (D13 addendum 1): observed_on, activity stratum, queue load; week of observed_on
        cov = pd.read_parquet(s["out"] / "covariates.parquet")
        d = d.merge(cov, on="observation_uuid", how="left", validate="one_to_one")
        if d["observed_on"].isna().any():
            raise RuntimeError(f"{int(d['observed_on'].isna().sum())} rows without observed_on in covariates.parquet")
        d["week"] = pd.to_datetime(d["observed_on"]).dt.isocalendar().week.astype(float).to_numpy()
    d["proposed"] = d["proposed"].apply(lambda x: set(x) if x is not None else set())
    p1 = pd.read_parquet(s["out"] / "strata.parquet")
    p1["cell"] = [A.cell_of(x) if isinstance(x, str) else None for x in p1["location"]]
    # identifier availability and experience (section 7.3, item 5; N18a): all stored histories of the same families
    # and window, i.e. the part's phase-1 histories plus the development histories named in ident_sources; scale =
    # population (part frame + ident_population_extra) / sampled observations with a history
    hist = [p1.loc[p1["history"].fillna(False).astype(bool), ["observation_uuid", "family", "cell"]]]
    rec_all = dict(rec)
    fams = set(p1["family"])
    for src in s.get("ident_sources", []):
        r2, _ = A.parse_histories(ROOT / src["api_raw"])
        tp = ROOT / src["table"]
        tb = pd.read_parquet(tp) if str(tp).endswith(".parquet") else pd.read_csv(tp)
        tb = tb[tb["family"].isin(fams) & tb["observation_uuid"].isin(set(r2))][["observation_uuid", "family"]]
        tb = tb.drop_duplicates("observation_uuid")
        tb["cell"] = [A.cell_of(r2[u]["location"]) if r2[u]["location"] else None for u in tb["observation_uuid"]]
        hist.append(tb)
        for u in tb["observation_uuid"]:
            rec_all.setdefault(u, r2[u])
    hist = pd.concat(hist, ignore_index=True).drop_duplicates("observation_uuid")
    extra = s.get("ident_population_extra", {})
    scale, ninfo = {}, {}
    for f in fams:
        pop = float(p1.loc[p1["family"] == f, "frame_size"].iloc[0]) + float(extra.get(f, 0))
        n_s = int((hist["family"] == f).sum())
        scale[f] = pop / n_s if n_s else 1.0
        ninfo[f] = {"population": pop, "sampled_with_history": n_s, "scale": scale[f]}
    info["identifier_availability"] = {"sources": [x["api_raw"] for x in s.get("ident_sources", [])], "families": ninfo}
    d["ident_avail"], d["ident_experience"] = A.identifier_measures(d, hist, rec_all, scale)
    if s.get("q_window"):
        q1 = p1[(p1["grade"] == "research") & p1["T"].notna() & p1["cell"].notna()]
        q = MD.local_q(q1["family"].to_numpy(), q1["cell"].to_numpy(), q1["observer_id"].to_numpy(),
                       (q1["T"] < 1).astype(float).to_numpy(), np.ones(len(q1)), 20)
        d["Q"] = d["observation_uuid"].map(pd.Series(q, index=q1["observation_uuid"]))
    rf = pd.read_csv(s["out"] / "regime_check.csv")
    flags = {(r.model, r.family) for r in rf.itertuples() if r.flagged}
    return d, p1, flags


def cmd_analyse(a):
    s = spec_of(a.spec)
    ao = s["out"] / s["analysis_out"] if s.get("analysis_out") else s["out"]
    ao.mkdir(parents=True, exist_ok=True)
    pinfo = {}
    d, p1, flags = prepare_rows(a, s, pinfo)
    rng = L.rng_load(s["out"] / "rng_after_phase2.json")
    t0 = time.time()
    est, info = AN.analyse(d, s["models"], s["dates"], s["s_star"], s["replicates"], rng, regime_flags=flags,
                           q_window=bool(s.get("q_window")), sensitivities=True)
    if "external_without" in s:
        keep = ~d["family"].isin(s["external_without"])
        ext = s["models"][-1]
        e2, _ = AN.analyse(d[keep], [ext], s["dates"], s["s_star"], s["replicates"], rng, fe=False, sensitivities=False)
        e2["quantity"] = e2["quantity"] + " without " + "+".join(s["external_without"])
        est = pd.concat([est, e2], ignore_index=True)
    info.update(pinfo)
    info["ident_experience_rows_defined"] = int(np.isfinite(d["ident_experience"]).sum())
    if s.get("replicates_hypotheses"):
        # N18a: the estimates that carry a hypothesis with the registered 5,000 replicates (section 8): Delta and ER of
        # the primary model (H1, H2, H5), and with hypothesis_c2 O and R (H3) and G_sup (H4) at S*; one bootstrap
        # matrix drawn after all other estimates
        m0 = s["models"][0]
        fam_i, _ = AN._codes(d["family"])
        isr = (d["grade"] == "research").to_numpy()
        tt = d["T"].to_numpy(float)
        td = isr & np.isfinite(tt)
        key = pd.Series([f"{f}|{x}" for f, x in zip(fam_i, np.where(isr, d["species"].fillna(-1), -1).astype(np.int64))])
        spi, spu = AN._codes(key)
        spf = np.array([int(k.split("|")[0]) for k in spu])
        e0 = 1 - d[f"c_{m0}"].to_numpy(float)
        Rp = int(s["replicates_hypotheses"])
        Fn = len(np.unique(fam_i))
        t1 = time.time()
        Wt = E.boot_matrix(d["observer_id"].to_numpy(), d["w"].to_numpy(float), Rp, rng)
        r = E.c1(Wt, spi, spf, e0, td & (tt >= 1), td & (tt < 1), Fn)
        fams_h = list(AN._codes(d["family"])[1])
        o = AN.Out()
        o.add(m0, f"Delta ({Rp} replicates)", "pooled", r["Delta"], AN._left(fams_h, r["est"]))
        o.add(m0, f"ER ({Rp} replicates)", "pooled", r["ER"], AN._left(fams_h, r["est"]))
        if s.get("hypothesis_c2"):
            S = s["s_star"]
            isn = ~isr
            g0 = d[f"g_{m0}"].to_numpy(float)
            rgS = d[f"rg_{S}"].fillna(False).to_numpy(bool)
            cS = d[f"created_before_{S}"].fillna(False).to_numpy(bool)
            s2 = (d["support"].fillna(0).to_numpy() >= 2) & isn
            c2 = E.c2(Wt, fam_i, Fn, isr, 1 - e0, g0, rgS, cS, isn, s2)
            for k in ("O", "R", "G_sup", "G_all"):
                o.add(m0, f"{k} ({Rp} replicates)", "pooled", c2[k], AN._left(fams_h, c2[k + "_est"]))
        est = pd.concat([est, pd.DataFrame(o.rows)], ignore_index=True)
        info["hypothesis_replicates"] = Rp
        info["hypothesis_minutes"] = round((time.time() - t1) / 60, 2)
    # fast share among the phase-1 research rows with T, per family (H6 input)
    fs = p1[(p1["grade"] == "research") & p1["T"].notna()].groupby("family")["T"].apply(lambda t: float((t < 1).mean()))
    fs.rename("fast_share").reset_index().to_csv(ao / "fast_share.csv", index=False, lineterminator="\n")
    est.to_csv(ao / "estimates.csv", index=False, lineterminator="\n")
    if "q_tertile_figure" in info:
        pd.DataFrame(info.pop("q_tertile_figure")).to_csv(ao / "q_tertiles.csv", index=False, lineterminator="\n")
    info["analysis_minutes"] = round((time.time() - t0) / 60, 2)
    info["nonfinite"] = est[~np.isfinite(est["value"])][["model", "quantity", "unit"]].to_dict("records")
    info["not_estimable"] = est[est["status"] == "not estimable"][["model", "quantity", "unit"]].to_dict("records")
    info["pooled_with_families_left_out"] = est[est["families_left_out"].fillna("") != ""][
        ["model", "quantity", "unit", "families_left_out"]].to_dict("records")
    save_json(ao / "analysis.json", info)
    print(est[est["unit"] == "pooled"].head(30).to_string())


def cmd_h6(a):
    s = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    delta, fshare = {}, {}
    for part in s["parts"]:
        est = pd.read_csv(ROOT / part / "estimates.csv")
        fams = pd.read_csv(ROOT / part / "fast_share.csv")
        guard(a, {"name": "H6", "out": ROOT / s["out"]}, "h6", fams["family"].tolist(), [])
        sel = est[(est["model"] == s["model"]) & (est["quantity"] == "Delta") & est["unit"].isin(fams["family"])]
        delta.update(dict(zip(sel["unit"], sel["value"])))
        fshare.update(dict(zip(fams["family"], fams["fast_share"])))
    r = E.h6(delta, fshare, s["n_perm"], L.rng_new(), n_boot=int(s.get("n_boot", 0)))
    (ROOT / s["out"]).mkdir(parents=True, exist_ok=True)
    save_json(ROOT / s["out"] / s.get("name", "h6.json"),
              dict(r, model=s["model"], n_perm=s["n_perm"], n_boot=s.get("n_boot", 0), delta=delta, fast_share=fshare))
    print(r)


def cmd_analyse_joint(a):
    """Several parts analysed together (C1 only, observer bootstrap over the union of their rows with their own
    weights): groups of plan section 10 across the eight and the six new families, per-family Delta and ER, and the
    Spearman relation over their families (secondary, one-sided permutation test)."""
    s = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    rows, fs = [], {}
    for sp_ in s["parts"]:
        ps = spec_of(ROOT / sp_)
        d, p1, _ = prepare_rows(a, ps, {}, covariates=False)
        rows.append(d)
        f_ = p1[(p1["grade"] == "research") & p1["T"].notna()].groupby("family")["T"].apply(lambda t: float((t < 1).mean()))
        fs.update(f_.to_dict())
    dj = pd.concat(rows, ignore_index=True)
    if dj["family"].nunique() != sum(r["family"].nunique() for r in rows):
        raise RuntimeError("a family occurs in more than one part")
    est, info = AN.analyse(dj, s["models"], [], None, int(s["replicates"]), L.rng_new(), fe=False, sensitivities=False)
    dl = est[(est["model"] == s["models"][0]) & (est["quantity"] == "Delta") & est["unit"].isin(fs)]
    rel = E.h6(dict(zip(dl["unit"], dl["value"])), fs, int(s["n_perm"]), L.rng_new())
    out = ROOT / s["out"]
    out.mkdir(parents=True, exist_ok=True)
    est.to_csv(out / "estimates_joint.csv", index=False, lineterminator="\n")
    save_json(out / "joint.json", dict(info, relation_across_families=rel, fast_share=fs))
    print(rel)


def cmd_decide(a):
    s = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    est = {k: pd.read_csv(ROOT / v / "estimates.csv") for k, v in s["parts"].items()}
    h6 = json.loads((ROOT / s["h6"]).read_text(encoding="utf-8"))
    tab = DC.decide(DC.primary_rows(est, h6, s.get("model", "Z25"), f"{int(s.get('replicates', 5000))} replicates"))
    sec = DC.secondary(est, s.get("secondary_models", []))
    out = ROOT / s["out"]
    out.mkdir(parents=True, exist_ok=True)
    tab.to_csv(out / "decisions.csv", index=False, lineterminator="\n")
    sec.to_csv(out / "decisions_secondary.csv", index=False, lineterminator="\n")
    print(tab[["hypothesis", "estimate", "lo95", "hi95", "p", "holm_threshold", "rejected", "grade"]].to_string())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["frame", "phase1", "covariates", "histories", "report-strata", "phase2",
                                        "download", "predict", "analyse", "h6", "analyse-joint", "decide"])
    ap.add_argument("--mode", required=True, choices=["dry-run", "confirmatory"])
    ap.add_argument("--spec")
    ap.add_argument("--families", nargs="+")
    ap.add_argument("--windows", nargs="+")
    ap.add_argument("--half")
    ap.add_argument("--snapshot")
    ap.add_argument("--manifest")
    ap.add_argument("--eligible")
    ap.add_argument("--out-dir")
    ap.add_argument("--name")
    a = ap.parse_args()
    {"frame": cmd_frame, "phase1": cmd_phase1, "covariates": cmd_covariates, "histories": cmd_histories,
     "report-strata": cmd_report_strata, "phase2": cmd_phase2, "download": cmd_download, "predict": cmd_predict,
     "analyse": cmd_analyse, "h6": cmd_h6, "analyse-joint": cmd_analyse_joint, "decide": cmd_decide}[a.command](a)


if __name__ == "__main__":
    main()
