"""D14 (post hoc, docs/PLAN.md): sensitivity of the confirmatory results to the two failure deviations of N18.

(a) rho of H6 (BioCLIP 2.5 Huge) without Ardeidae, without Coccinellidae, without both, and the minimum and maximum
    of rho over leave-one-family-out; each with a one-sided permutation p from 10,000 permutations (a generator with
    seed 20261121 for every computation). Inputs: outputs/confirm/h6.json (family Delta and fast share of N18).
(b) Ardeidae: the replication phase-1 sample (outputs/confirm/replication_W/phase1.parquet) was sent to the API in its
    row order in batches of 200; batches 0 and 2 failed in N18. One re-request of these two batches under the
    registered API rules (one request per second at most, 3 retries with the registered pauses, identifications after
    2026-10-27 23:59:59 UTC ignored); raw responses in outputs/D14/api_raw/ (git-ignored). If obtained: stratum counts
    of the newly obtained observations against those already obtained (chi-square test); phase-2 selection among the
    newly obtained observations only (all of A1 to A3, A0 with fraction 0.5; generator with seed 20261123); first
    photographs (frame filters of N18, medium size) and predictions of the four models; Ardeidae Delta and ER with the
    weights of the full phase-1 sample (frame size / 1,500 divided by the realized phase-2 fraction of the stratum in
    the original or the new part; 2,000 observer-bootstrap replicates, the generator of seed 20261123 continued); H6
    recomputed with the new Ardeidae Delta and fast share (10,000 permutations, seed 20261121; 5,000 bootstrap
    replicates over families).
(c) No retry of the failed Coccinellidae photograph.
The N18 outputs are only read. The guard (confirmatory mode, registration lock) is called before any request.
Outputs: outputs/D14/ (a.json, b.json, tables). Usage: python scripts/d14_run.py --snapshot <folder> --hf-cache <folder>
"""
import os
THREADS = 20
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = str(THREADS)
import argparse  # noqa: E402
import gzip  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import chi2_contingency  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src import d6_lib as L  # noqa: E402
from src.confirm import acquisition as A  # noqa: E402
from src.confirm import estimators as E  # noqa: E402
from src.confirm import guard as G  # noqa: E402

C = ROOT / "outputs/confirm"
OUT = ROOT / "outputs/D14"
FAM = "Ardeidae"
FAILED = [0, 2]
MODELS = ["Z25", "Z2", "Z1", "BT-CLIP-O"]


def save(p, obj):
    p.write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8", newline="\n")


def part_a(h6):
    d, fs = h6["delta"], h6["fast_share"]

    def rho_p(drop):
        dd = {k: v for k, v in d.items() if k not in drop}
        r = E.h6(dd, fs, 10000, np.random.default_rng(L.SEED))
        return {"families": r["families_used"], "rho": r["rho"], "p": r["p"]}

    out = {"registered": {"families": h6["families_used"], "rho": h6["rho"], "p": h6["p"]},
           "without Ardeidae": rho_p({"Ardeidae"}), "without Coccinellidae": rho_p({"Coccinellidae"}),
           "without both": rho_p({"Ardeidae", "Coccinellidae"})}
    loo = {f: rho_p({f}) for f in sorted(d)}
    lo = min(loo, key=lambda k: loo[k]["rho"])
    hi = max(loo, key=lambda k: loo[k]["rho"])
    out["leave-one-out minimum"] = dict(loo[lo], family_left_out=lo)
    out["leave-one-out maximum"] = dict(loo[hi], family_left_out=hi)
    out["leave-one-out all"] = loo
    return out


def request_batches(uuids_by_batch, raw):
    """One re-request of each batch: up to 4 attempts (3 retries) with the registered pauses; at least one second
    between requests. Returns {batch: status text}."""
    raw.mkdir(parents=True, exist_ok=True)
    status, last = {}, 0.0
    for b, bu in uuids_by_batch.items():
        f = raw / f"batch_{b:05d}.json.gz"
        if f.exists():
            status[b] = "ok (file present)"
            continue
        errs = []
        for attempt in range(4):
            wait = 1.0 - (time.time() - last)
            if wait > 0:
                time.sleep(wait)
            last = time.time()
            try:
                body = A._fetch(A.API.format(uuids=",".join(bu)))
                got = [o["uuid"] for o in json.loads(body).get("results", [])]
                if not set(got) <= set(bu):
                    raise RuntimeError("unrequested uuid returned")
                with gzip.open(f, "wb") as g:
                    g.write(body)
                status[b] = f"ok after {attempt + 1} attempt(s); {len(got)} observations returned"
                break
            except Exception as ex:  # noqa: BLE001
                code = getattr(ex, "code", None)
                errs.append(f"{type(ex).__name__}" + (f" HTTP {code}" if code else "") + f": {str(ex)[:120]}")
                if attempt < 3:
                    time.sleep(A.PAUSES[attempt])
        else:
            status[b] = "failed: " + " | ".join(errs)
    return status


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--hf-cache", required=True)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    h6 = json.loads((C / "h6.json").read_text(encoding="utf-8"))
    ra = part_a(h6)
    save(OUT / "a.json", ra)
    print("(a)", {k: v for k, v in ra.items() if k != "leave-one-out all"})

    # (b) batches of the replication phase-1 sample
    p1 = pd.read_parquet(C / "replication_W/phase1.parquet")
    batches = {b: p1["observation_uuid"].iloc[b * 200:(b + 1) * 200].tolist() for b in range(int(np.ceil(len(p1) / 200)))}
    fam_rows = np.flatnonzero((p1["family"] == FAM).to_numpy())
    rb = {"phase1_rows": int(len(p1)), "batches": len(batches), "ardeidae_rows": [int(fam_rows.min()), int(fam_rows.max())],
          "ardeidae_batches": sorted({int(i // 200) for i in fam_rows}),
          "failed_batches": FAILED, "failed_batch_families": {b: sorted(p1["family"].iloc[b * 200:(b + 1) * 200].unique())
                                                              for b in FAILED}}
    st = pd.read_parquet(C / "replication_W/strata.parquet")
    G.check("confirmatory", "D14 (b) re-request", [FAM], st.loc[st["family"] == FAM, "observer_id"].unique(),
            OUT / "guard_log.jsonl")
    status = request_batches({b: batches[b] for b in FAILED}, OUT / "api_raw")
    rb["request_status"] = status
    save(OUT / "b.json", rb)
    print("(b) requests:", status)
    if not all(v.startswith("ok") for v in status.values()):
        rb["stopped"] = "a failed batch was not obtained again; part (b) stops here"
        rb["minutes"] = round((time.time() - t0) / 60, 2)
        save(OUT / "b.json", rb)
        print(rb["stopped"])
        return
    rec, hidden = A.parse_histories(OUT / "api_raw")
    newu = [u for b in FAILED for u in batches[b]]
    new = p1[p1["observation_uuid"].isin(newu)].copy()
    rows = []
    for r in new.itertuples(index=False):
        h = rec.get(r.observation_uuid)
        if h is None:
            rows.append({"history": False})
            continue
        f = A.history_fields(h, r.grade, r.species, r.genus_label, [])
        f["history"] = True
        rows.append(f)
    hf = pd.DataFrame(rows, index=new.index)
    new = pd.concat([new, hf], axis=1)
    new["stratum"] = [A.stratum(g, t if t == t else np.nan, 0) if hh else "failed"
                      for g, t, hh in zip(new["grade"], new["T"], new["history"])]
    new.loc[new["stratum"] == "", "stratum"] = "excluded_T_undefined"
    old = st[(st["family"] == FAM) & (st["stratum"] != "failed")]
    cats = ["A0", "A1", "A2", "A3", "excluded_T_undefined", "failed"]
    cnt = pd.DataFrame({"already obtained": old["stratum"].value_counts().reindex(cats, fill_value=0),
                        "newly obtained": new["stratum"].value_counts().reindex(cats, fill_value=0)})
    cnt.to_csv(OUT / "b_stratum_counts.csv", lineterminator="\n")
    tab = cnt.loc[["A0", "A1", "A2", "A3"]]
    tab = tab[(tab.sum(axis=1) > 0)]
    chi2, pchi, dof, _ = chi2_contingency(tab.T.to_numpy())
    rb.update({"hidden_identifications": hidden, "new_rows": int(len(new)), "new_with_history": int(new["history"].sum()),
               "stratum_counts": cnt.to_dict(), "chi_square": {"statistic": float(chi2), "dof": int(dof),
                                                               "p": float(pchi), "strata": list(tab.index)}})
    # phase 2 among the new rows
    rng = np.random.default_rng(20261123)
    base = float(old["frame_size"].iloc[0]) / float(old["n1"].iloc[0])
    new["selected"], new["w"] = False, 0.0
    real = {}
    for s_, fr in (("A0", 0.5), ("A1", 1.0), ("A2", 1.0), ("A3", 1.0)):
        j = np.flatnonzero((new["stratum"] == s_).to_numpy())
        m = int(round(fr * len(j)))
        real[s_] = (len(j), m)
        if m > 0:
            pick = j[rng.choice(len(j), m, replace=False)]
            new.iloc[pick, new.columns.get_loc("selected")] = True
            new.iloc[pick, new.columns.get_loc("w")] = base / (m / len(j))
    rb["phase2_new"] = {k: {"rows": v[0], "selected": v[1]} for k, v in real.items()}
    sel = new[new["selected"]]
    budget = {"limit_bytes": 500_000_000, "used_bytes": 0}
    man, tm = A.download_photos(sel, OUT / "photos", budget)
    ok = set(man.loc[man["status"] == "ok", "photo_id"].astype(np.int64))
    sel = sel[sel["first_photo_id"].astype(np.int64).isin(ok)].reset_index(drop=True)
    rb["photographs"] = {"selected": int(new["selected"].sum()), "ok": int(len(sel)), "bytes": int(budget["used_bytes"]),
                         "stopped": tm["stopped"]}
    # predictions of the four models (label space and template of N18)
    from src import zeroshot as Z
    from src.confirm import infer as I
    tax = A.taxonomy(a.snapshot)
    e1 = pd.read_csv(ROOT / "inputs/earlier_gates/outputs/G-IG8.0/e1_species_primary.csv")
    space = np.sort(e1[(e1["family"] == FAM) & (e1["eligible_primary"] == "yes")]["species_taxon_id"].astype(np.int64).to_numpy())
    texts = [A.species_text(tax, int(x)) for x in space]
    mp = man.set_index("photo_id")
    blobs = [A.read_checked(OUT / "photos", int(p), e, mp.loc[int(p), "sha256"])
             for p, e in zip(sel["first_photo_id"], sel["extension"])]
    for key in MODELS:
        m_ = I.load(key, a.hf_cache)
        pred = I.predict_family(m_, blobs, texts, space)
        Z.free_model(m_)
        sel[f"c_{key}"] = (pred == sel["species"].astype(np.int64).to_numpy()).astype(float)
    # Ardeidae Delta and ER with the weights of the full phase-1 sample
    import scripts.confirm_run as CR
    p2 = pd.read_parquet(C / "replication_W/phase2.parquet")
    pr = pd.read_parquet(C / "replication_W/predictions.parquet")
    d = p2.merge(pr.drop(columns=["family", "grade", "species", "genus_label"]), on="observation_uuid", how="inner")
    man0 = pd.read_csv(C / "replication_W/photos/manifest.csv").set_index("photo_id")
    rec0, _ = A.parse_histories(C / "replication_W/api_raw")
    d = d[~CR.exact_duplicates(d, man0, rec0)]
    d = d[d["family"] == FAM]
    cols = ["observation_uuid", "observer_id", "species", "T", "w"] + [f"c_{m}" for m in MODELS]
    allr = pd.concat([d[cols].assign(part="original"), sel[cols].assign(part="new")], ignore_index=True)
    allr = allr[allr["T"].notna()].reset_index(drop=True)
    W = E.boot_matrix(allr["observer_id"].to_numpy(), allr["w"].to_numpy(float), 2000, rng)
    spi, _ = pd.factorize(allr["species"].astype(np.int64))
    tt = allr["T"].to_numpy(float)
    res = {}
    for m in MODELS:
        for lab, part in (("original rows only (N18)", allr["part"] == "original"), ("full phase-1 sample", None)):
            k = np.ones(len(allr), bool) if part is None else part.to_numpy()
            r = E.c1(W, spi, np.zeros(spi.max() + 1, int), 1 - allr[f"c_{m}"].to_numpy(float), k & (tt >= 1), k & (tt < 1), 1)
            res[f"{m} | {lab}"] = {"Delta": float(r["Delta"][0]), "Delta_lo95": E.interval(r["Delta"])[0],
                                   "Delta_hi95": E.interval(r["Delta"])[1], "ER": float(r["ER"][0]),
                                   "ER_lo95": E.interval(r["ER"])[0], "ER_hi95": E.interval(r["ER"])[1]}
    rb["ardeidae_estimates"] = res
    rb["ardeidae_rows"] = {"original": int((allr["part"] == "original").sum()), "new": int((allr["part"] == "new").sum())}
    # H6 recomputed
    allp1 = pd.concat([old[["observation_uuid", "grade", "T"]], new[["observation_uuid", "grade", "T"]]])
    rr = allp1[(allp1["grade"] == "research") & allp1["T"].notna()]
    fs = dict(h6["fast_share"])
    fs[FAM] = float((rr["T"] < 1).mean())
    dl = dict(h6["delta"])
    dl[FAM] = res["Z25 | full phase-1 sample"]["Delta"]
    r6 = E.h6(dl, fs, 10000, np.random.default_rng(L.SEED), n_boot=5000)
    rb["h6_recomputed"] = {k: r6[k] for k in ("rho", "p", "rho_lo95", "rho_hi95", "families_used")}
    rb["ardeidae_fast_share"] = {"N18": h6["fast_share"][FAM], "full phase-1 sample": fs[FAM]}
    rb["ardeidae_delta_N18"] = h6["delta"][FAM]
    rb["minutes"] = round((time.time() - t0) / 60, 2)
    save(OUT / "b.json", rb)
    print("(b)", json.dumps({k: v for k, v in rb.items() if k not in ("stratum_counts",)}, indent=1, default=str)[:3000])


if __name__ == "__main__":
    main()
