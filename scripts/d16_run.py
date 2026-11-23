"""D16 (post hoc, docs/PLAN.md): exposure test of BioCLIP 2.5 Huge. Development half only.

Set A: D4 sample rows (outputs/D6/rows.parquet: window W, eight families) that are research grade with T < 1 day, with
the stored correctness of BioCLIP 2.5 Huge (Z25), BioCLIP 2 (Z2) and first BioCLIP (Z1) on the first photograph.
Set B: development-half observations of the eight families observed 2026-08-28 to 2026-10-20 (frame built with the
frozen frame code, src/confirm/acquisition.build_frames: licence and size filters, photo ids above max_M1, research
grade with a label-space species), research-grade frame only; simple random sample of up to 1,500 per family
(acquisition.phase1, seed 20261124); histories from the public API v1 (acquisition.fetch_histories: at most one request
per second, 200 observations per request, 3 retries; identifications after 2026-10-27 23:59:59 UTC ignored); T as in
the registered reconstruction; rows with T < 1 day kept; first photographs at medium size (acquisition.download_photos,
budget 1.5 GB); predictions of Z25, Z2 and Z1 with the registered zero-shot code (src/confirm/infer.py).
Estimand per family f, over the species present in both sets: gain_X = sum_s pi_s (acc_Z25,X,s - acc_ref,X,s) with
pi_s the share of species s among the set-A rows of these species; D_f = gain_A - gain_B; D = 100 x mean over families.
Bootstrap: 2,000 replicates, observers resampled within each set (one generator, seed 20261121: set A, then set B);
in a replicate, a species without rows in one of the sets is left out and the shares are renormalized.
Every stage is resumable (outputs in outputs/D16/; raw responses in outputs/D16/api_raw/, photographs in
outputs/D16/photos/, both git-ignored). Usage: python scripts/d16_run.py --snapshot <folder> --manifest <csv> --hf-cache <folder>
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
import scipy.sparse as sp  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.confirm import acquisition as A  # noqa: E402
from src.confirm import estimators as E  # noqa: E402
from src.confirm import guard as G  # noqa: E402
from src.confirm.config import load_config  # noqa: E402

OUT = ROOT / "outputs/D16"
E1 = ROOT / "inputs/earlier_gates/outputs/G-IG8.0/e1_species_primary.csv"
MODELS = ["Z25", "Z2", "Z1"]
WINDOW = ("2026-08-28", "2026-10-20")


def log(msg, info):
    print(time.strftime("%H:%M:%S"), msg, flush=True)
    info.setdefault("log", []).append(f"{time.strftime('%H:%M:%S')} {msg}")
    (OUT / "run.json").write_text(json.dumps(info, indent=1, default=str), encoding="utf-8", newline="\n")


def set_b(a, cfg, info):
    fams = cfg["sets"]["eight"]["families"]
    e1 = pd.read_csv(E1)
    ids = e1[e1["family"].isin(fams)].drop_duplicates("family_taxon_id")
    fam_ids = dict(zip(ids["family_taxon_id"].astype(int), ids["family"]))
    lab = {f: set(e1[(e1["family"] == f) & (e1["eligible_primary"] == "yes")]["species_taxon_id"].astype(int)) for f in fams}
    fp = OUT / "frame.parquet"
    if not fp.exists():
        t0 = time.time()
        finfo = {}
        fr, _ = A.build_frames(a.snapshot, a.manifest, fam_ids, lab, {"B": WINDOW}, cfg["windows"]["W"]["max_M1"],
                               cfg["frame"]["licences"], cfg["frame"]["min_shorter_side_px"], "development", finfo)
        fr.to_parquet(fp, index=False)
        info["frame"] = dict(finfo, minutes=round((time.time() - t0) / 60, 1))
        log(f"frame built: {len(fr):,} rows", info)
    fr = pd.read_parquet(fp)
    sp_ = OUT / "sample.parquet"
    if not sp_.exists():
        s, sizes = A.phase1(fr, 1500, np.random.default_rng(20261124), research_only=True)
        s.to_parquet(sp_, index=False)
        info["sample_sizes"] = {k: list(v) for k, v in sizes.items()}
        log(f"sample drawn: {len(s):,} rows", info)
    s = pd.read_parquet(sp_)
    G.check("dry-run", "D16 set B", s["family"].unique(), s["observer_id"].unique(), OUT / "guard_log.jsonl")
    tm = {}
    st = A.fetch_histories(s["observation_uuid"].tolist(), OUT / "api_raw", tm)
    info["histories"] = dict(st, api_seconds=tm.get("api_seconds"), requests_needed=int(np.ceil(len(s) / 200)))
    if st["stopped"]:
        log(f"histories stopped: {st['stopped']}", info)
        raise SystemExit("histories stopped")
    rec, hidden = A.parse_histories(OUT / "api_raw")
    T = []
    for r in s.itertuples(index=False):
        h = rec.get(r.observation_uuid)
        T.append(A.history_fields(h, "research", r.species, r.genus_label, [])["T"] if h is not None else np.nan)
    s = s.assign(T=T, history=[u in rec for u in s["observation_uuid"]])
    info["histories"].update({"returned": int(s["history"].sum()), "hidden": hidden,
                              "T_defined": int(np.isfinite(s["T"]).sum()), "fast": int((s["T"] < 1).sum())})
    log(f"histories: {int(s['history'].sum()):,} returned; fast {int((s['T'] < 1).sum()):,}", info)
    fast = s[s["T"] < 1].reset_index(drop=True)
    budget = {"limit_bytes": 1_500_000_000, "used_bytes": 0}
    man, tmd = A.download_photos(fast, OUT / "photos", budget)
    okb = man[man["status"] == "ok"]
    info["photographs"] = {"selected": int(len(fast)), "ok": int(okb["photo_id"].isin(fast["first_photo_id"]).sum()),
                           "bytes_total_in_manifest": int(okb["bytes"].sum()), "bytes_this_run": int(budget["used_bytes"]),
                           "stopped": tmd["stopped"]}
    log(f"photographs: {info['photographs']}", info)
    if tmd["stopped"]:
        raise SystemExit("download stopped")
    pp = OUT / "predictions.parquet"
    if not pp.exists():
        from src import zeroshot as Z
        from src.confirm import infer as I
        mp = man.set_index("photo_id")
        d = fast[fast["first_photo_id"].astype(np.int64).isin(set(okb["photo_id"].astype(np.int64)))].reset_index(drop=True)
        tax = A.taxonomy(a.snapshot)
        spaces = {f: np.sort(np.array(sorted(lab[f]), np.int64)) for f in d["family"].unique()}
        texts = {f: [A.species_text(tax, int(x)) for x in sp2] for f, sp2 in spaces.items()}
        blobs = {f: [A.read_checked(OUT / "photos", int(p), e, mp.loc[int(p), "sha256"])
                     for p, e in zip(d.loc[d["family"] == f, "first_photo_id"], d.loc[d["family"] == f, "extension"])]
                 for f in spaces}
        for key in MODELS:
            m = I.load(key, a.hf_cache)
            pred = np.zeros(len(d), np.int64)
            for f in spaces:
                k = np.flatnonzero((d["family"] == f).to_numpy())
                pred[k] = I.predict_family(m, blobs[f], texts[f], spaces[f])
            Z.free_model(m)
            d[f"c_{key}"] = (pred == d["species"].astype(np.int64).to_numpy()).astype(float)
        d[["observation_uuid", "observer_id", "family", "species", "T"] + [f"c_{m}" for m in MODELS]].to_parquet(pp, index=False)
        log("predictions done", info)
    return pd.read_parquet(pp)


def estimate(a_rows, b_rows, ref, R=2000):
    rng = np.random.default_rng(20261121)
    WA = E.boot_matrix(a_rows["observer_id"].to_numpy(), np.ones(len(a_rows)), R, rng).astype(float)
    WB = E.boot_matrix(b_rows["observer_id"].to_numpy(), np.ones(len(b_rows)), R, rng).astype(float)
    fams = sorted(set(a_rows["family"]) & set(b_rows["family"]))
    Df, per = [], {}
    for f in fams:
        sa = a_rows["family"].to_numpy() == f
        sb = b_rows["family"].to_numpy() == f
        common = sorted(set(a_rows.loc[sa, "species"]) & set(b_rows.loc[sb, "species"]))
        code = {s: i for i, s in enumerate(common)}

        def sums(rows, mask, W):
            idx = np.flatnonzero(mask & rows["species"].isin(code).to_numpy())
            g = rows["species"].to_numpy()[idx]
            M = sp.csr_matrix((np.ones(len(idx)), (idx, [code[x] for x in g])), shape=(len(rows), len(common)))
            dd = (rows[f"c_Z25"] - rows[f"c_{ref}"]).to_numpy(float)
            return W @ M, (W * dd[None, :]) @ M, len(idx)

        nA, sA, rA = sums(a_rows, sa, WA)
        nB, sB, rB = sums(b_rows, sb, WB)
        with np.errstate(invalid="ignore", divide="ignore"):
            ok = (nA > 0) & (nB > 0)
            pi = np.where(ok, nA, 0)
            pi = pi / pi.sum(axis=1, keepdims=True)
            g = np.where(ok, sA / np.where(nA > 0, nA, 1) - sB / np.where(nB > 0, nB, 1), 0)
            d = (pi * g).sum(axis=1)
        Df.append(d)
        lo, hi = E.interval(100 * d)
        per[f] = {"species_common": len(common), "rows_A": rA, "rows_B": rB, "D_f": 100 * float(d[0]), "lo95": lo, "hi95": hi}
    Dm = 100 * np.mean(np.vstack(Df), axis=0)
    lo, hi = E.interval(Dm)
    return {"D": float(Dm[0]), "lo95": lo, "hi95": hi, "families": per}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--hf-cache", required=True)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    info = {"window_B": WINDOW, "seed_sample": 20261124, "seed_bootstrap": 20261121}
    t0 = time.time()
    cfg = load_config()
    b = set_b(a, cfg, info)
    rows = pd.read_parquet(ROOT / "outputs/D6/rows.parquet")
    av = rows[(rows["sample_grade"] == "research") & (rows["T"] < 1)].copy()
    av["species"] = av["species"].astype(np.int64)
    b["species"] = b["species"].astype(np.int64)
    acc = []
    for setname, d in (("A", av), ("B", b)):
        for f, g in d.groupby("family"):
            acc.append(dict({"set": setname, "family": f, "rows": len(g), "observers": int(g["observer_id"].nunique()),
                             "species": int(g["species"].nunique())}, **{f"acc_{m}": float(g[f"c_{m}"].mean()) for m in MODELS}))
    accd = pd.DataFrame(acc)
    accd.to_csv(OUT / "accuracy_by_set.csv", index=False, lineterminator="\n")
    res = {ref: estimate(av, b, ref) for ref in ("Z2", "Z1")}
    r2 = res["Z2"]
    reading = ("no material sign of exposure" if r2["hi95"] < 1.0 else
               "a sign of exposure" if r2["lo95"] > 1.0 else "inconclusive")
    info.update({"estimates": res, "reading_Z2": reading, "minutes": round((time.time() - t0) / 60, 1),
                 "set_A_rows": int(len(av)), "set_B_rows": int(len(b))})
    (OUT / "run.json").write_text(json.dumps(info, indent=1, default=str), encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in info.items() if k != "log"}, indent=1, default=str)[:3000])


if __name__ == "__main__":
    main()
