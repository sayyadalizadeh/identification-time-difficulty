"""D16 (post hoc, docs/PLAN.md, registered in commit 0a5843e): completion of the run stopped in task N21 at its
download limit, with the design unchanged. The files written in task N21 (outputs/D16/frame.parquet, sample.parquet,
api_raw/, photos/ with its manifest, run.json, guard_log.jsonl) are read and never changed:
- no new API request: the 60 history batches of N21 must all be present;
- T and the rows with T < 1 day are recomputed exactly as in scripts/d16_run.py;
- the first photographs still missing are downloaded to outputs/D16/photos_n22/ (own manifest); the photographs that
  failed after 3 retries in N21 are not retried; before each batch of up to 100 photographs the ledger
  is checked against the batch size bounded by the largest photograph of the N21 manifest; the photographs have their
  own ledger (outputs/N22/ledger_d16.json) whose limit is 11.0 GB minus the whole size of the provenance file of D17
  (that file has the ledger outputs/N22/ledger.json and is downloaded at the same time);
- predictions of Z25, Z2 and Z1 with the registered zero-shot code; estimates with scripts/d16_run.estimate;
- outputs: outputs/D16/predictions.parquet, accuracy_by_set.csv, results.json, guard_log_n22.jsonl.
Usage: python scripts/d16_complete.py --snapshot <folder> --hf-cache <folder>
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
sys.path.insert(0, str(ROOT / "scripts"))
import d16_run as R  # noqa: E402  (constants, label spaces and the estimator of D16)
from src.budget_ledger import Ledger  # noqa: E402
from src.confirm import acquisition as A  # noqa: E402
from src.confirm import guard as G  # noqa: E402
from src.confirm.config import load_config  # noqa: E402

OUT = ROOT / "outputs/D16"
PROV_SIZE = 10_286_368_327  # provenance file of D17 (reserved in the ledger while it is being downloaded)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--hf-cache", required=True)
    a = ap.parse_args()
    t0 = time.time()
    info = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "controls": {}}
    cfg = load_config()
    fams = cfg["sets"]["eight"]["families"]
    e1 = pd.read_csv(R.E1)
    lab = {f: set(e1[(e1["family"] == f) & (e1["eligible_primary"] == "yes")]["species_taxon_id"].astype(int)) for f in fams}

    s = pd.read_parquet(OUT / "sample.parquet")
    G.check("dry-run", "D16 set B completion", s["family"].unique(), s["observer_id"].unique(), OUT / "guard_log_n22.jsonl")
    nb = int(np.ceil(len(s) / 200))
    have = sorted((OUT / "api_raw").glob("batch_*.json.gz"))
    info["controls"]["all_history_batches_present"] = len(have) == nb
    if len(have) != nb:
        raise SystemExit(f"{len(have)} of {nb} history batches present; no API request is made in this task")
    rec, hidden = A.parse_histories(OUT / "api_raw")
    T = [A.history_fields(rec[r.observation_uuid], "research", r.species, r.genus_label, [])["T"]
         if r.observation_uuid in rec else np.nan for r in s.itertuples(index=False)]
    s = s.assign(T=T)
    fast = s[s["T"] < 1].reset_index(drop=True)
    old = json.loads((OUT / "run.json").read_text(encoding="utf-8"))
    info["controls"]["fast_rows_equal_N21"] = len(fast) == old["histories"]["fast"]
    info["controls"]["T_defined_equal_N21"] = int(np.isfinite(s["T"]).sum()) == old["histories"]["T_defined"]
    if not all(info["controls"].values()):
        raise SystemExit(f"recomputed rows differ from N21: {info['controls']}")
    info["histories"] = {"returned": len(rec), "hidden": hidden, "fast": len(fast)}

    # photographs: N21 manifest (read only) and the new folder of this task
    m21 = pd.read_csv(OUT / "photos/manifest.csv")
    ok21 = set(m21.loc[m21["status"] == "ok", "photo_id"].astype(np.int64))
    failed21 = set(m21.loc[m21["status"] == "failed", "photo_id"].astype(np.int64))
    bound = int(m21.loc[m21["status"] == "ok", "bytes"].max())
    rest = fast[~fast["first_photo_id"].astype(np.int64).isin(ok21 | failed21)].reset_index(drop=True)
    info["photographs"] = {"ok_N21": int(fast["first_photo_id"].astype(np.int64).isin(ok21).sum()),
                           "failed_N21_not_retried": int(fast["first_photo_id"].astype(np.int64).isin(failed21).sum()),
                           "to_download": int(len(rest)), "batch_bound_bytes_per_photo": bound,
                           "to_download_by_family": rest["family"].value_counts().to_dict()}
    print(json.dumps(info, indent=1, default=str), flush=True)
    led = Ledger(ROOT / "outputs/N22/ledger_d16.json", 11_000_000_000 - PROV_SIZE)
    P2 = OUT / "photos_n22"
    for k in range(0, len(rest), 100):
        chunk = rest.iloc[k:k + 100]
        led.check(len(chunk) * bound, f"photographs {k}-{k + len(chunk) - 1}")
        budget = {"limit_bytes": 10**15, "used_bytes": 0}
        man2, tmd = A.download_photos(chunk, P2, budget)
        led.add("D16 photographs (medium)", budget["used_bytes"], requests=len(chunk) if budget["used_bytes"] else 0)
        print(time.strftime("%H:%M:%S"), f"batch {k}: {budget['used_bytes']:,} bytes", flush=True)
    m22 = pd.read_csv(P2 / "manifest.csv") if (P2 / "manifest.csv").exists() else \
        pd.DataFrame(columns=["photo_id", "bytes", "sha256", "status"])
    ok22 = set(m22.loc[m22["status"] == "ok", "photo_id"].astype(np.int64))
    info["photographs"].update({"ok_N22": len(ok22 & set(rest["first_photo_id"].astype(np.int64))),
                                "failed_N22": int((m22["status"] == "failed").sum()),
                                "bytes_N22": int(m22.loc[m22["status"] == "ok", "bytes"].sum())})

    pp = OUT / "predictions.parquet"
    if not pp.exists():
        from src import zeroshot as Z
        from src.confirm import infer as I
        where = {int(p): (OUT / "photos", sh) for p, sh in zip(m21.loc[m21["status"] == "ok", "photo_id"],
                                                               m21.loc[m21["status"] == "ok", "sha256"])}
        where.update({int(p): (P2, sh) for p, sh in zip(m22.loc[m22["status"] == "ok", "photo_id"],
                                                        m22.loc[m22["status"] == "ok", "sha256"])})
        d = fast[fast["first_photo_id"].astype(np.int64).isin(set(where))].reset_index(drop=True)
        tax = A.taxonomy(a.snapshot)
        spaces = {f: np.sort(np.array(sorted(lab[f]), np.int64)) for f in d["family"].unique()}
        texts = {f: [A.species_text(tax, int(x)) for x in sp2] for f, sp2 in spaces.items()}
        blobs = {f: [A.read_checked(where[int(p)][0], int(p), e, where[int(p)][1])
                     for p, e in zip(d.loc[d["family"] == f, "first_photo_id"], d.loc[d["family"] == f, "extension"])]
                 for f in spaces}
        info["controls"]["photographs_sha256_checked"] = int(sum(len(v) for v in blobs.values())) == len(d)
        for key in R.MODELS:
            t1 = time.time()
            m = I.load(key, a.hf_cache)
            info.setdefault("model_checks", {})[key] = m.get("checks")
            pred = np.zeros(len(d), np.int64)
            for f in spaces:
                k = np.flatnonzero((d["family"] == f).to_numpy())
                pred[k] = I.predict_family(m, blobs[f], texts[f], spaces[f])
            Z.free_model(m)
            d[f"c_{key}"] = (pred == d["species"].astype(np.int64).to_numpy()).astype(float)
            print(time.strftime("%H:%M:%S"), f"{key}: {time.time() - t1:.0f} s", flush=True)
        d[["observation_uuid", "observer_id", "family", "species", "T"] + [f"c_{m}" for m in R.MODELS]].to_parquet(pp, index=False)
    b = pd.read_parquet(pp)

    rows = pd.read_parquet(ROOT / "outputs/D6/rows.parquet")
    av = rows[(rows["sample_grade"] == "research") & (rows["T"] < 1)].copy()
    G.check("dry-run", "D16 set A", av["family"].unique(), av["observer_id"].unique(), OUT / "guard_log_n22.jsonl")
    av["species"] = av["species"].astype(np.int64)
    b["species"] = b["species"].astype(np.int64)
    acc = []
    for setname, d in (("A", av), ("B", b)):
        for f, g in d.groupby("family"):
            acc.append(dict({"set": setname, "family": f, "rows": len(g), "observers": int(g["observer_id"].nunique()),
                             "species": int(g["species"].nunique())}, **{f"acc_{m}": float(g[f"c_{m}"].mean()) for m in R.MODELS}))
    pd.DataFrame(acc).to_csv(OUT / "accuracy_by_set.csv", index=False, lineterminator="\n")
    res = {ref: R.estimate(av, b, ref) for ref in ("Z2", "Z1")}
    r2 = res["Z2"]
    reading = ("no material sign of exposure" if r2["hi95"] < 1.0 else
               "a sign of exposure" if r2["lo95"] > 1.0 else "inconclusive")
    info.update({"estimates": res, "reading_Z2": reading, "set_A_rows": int(len(av)), "set_B_rows": int(len(b)),
                 "minutes": round((time.time() - t0) / 60, 1)})
    (OUT / "results.json").write_text(json.dumps(info, indent=1, default=str), encoding="utf-8", newline="\n")
    print(json.dumps({k: v for k, v in info.items() if k != "estimates"}, indent=1, default=str))
    print(json.dumps(res, indent=1)[:4000])


if __name__ == "__main__":
    main()
