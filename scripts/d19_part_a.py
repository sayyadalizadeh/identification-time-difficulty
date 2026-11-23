"""D19 Part A (post hoc): numbers from the stored outputs of the confirmatory run.

Items A1 to A7, A9, A11 and A12 (A8 is written by d19_part_c.py from the loaded model configurations; A10 by
d19_snapshot.py). Point values that the stored tables do not hold are recomputed from the stored analysis rows with
the frozen estimators (no bootstrap); the recomputation first reproduces every stored pooled and per-family Delta and
ER of the four models and four sets (check, tolerance 1e-9). Outputs: outputs/D19/A/.
"""
import hashlib
import json
import re
import time

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

import d19_common as C
from d19_common import E

OUT = C.OUT / "A"


def est_table(s):
    return pd.read_csv(C.CONF / s / "estimates.csv")


def get(est, model, q, unit="pooled"):
    r = est[(est["model"] == model) & (est["quantity"] == q) & (est["unit"] == unit)]
    if len(r) != 1:
        raise RuntimeError(f"{model} {q} {unit}: {len(r)} rows")
    return r.iloc[0]


def code_lines(path, a, b):
    lines = (C.ROOT / path).read_text(encoding="utf-8").splitlines()
    return [f"{path}:{i}: {lines[i - 1]}" for i in range(a, b + 1)]


def main():
    log = C.Log(OUT / "part_a_log.txt")
    log("D19 Part A (post hoc); started", time.strftime("%Y-%m-%d %H:%M:%S"))
    summary = {}
    a1, a2, a9 = [], [], []
    e1 = pd.read_csv(C.ROOT / "inputs/earlier_gates/outputs/G-IG8.0/e1_species_primary.csv")
    labsize = e1[e1["eligible_primary"] == "yes"].groupby("family").size()
    worst = 0.0
    obs_sets, multi = {}, {}
    for s in C.SETS:
        d, rec = C.load_rows(s)
        D = C.Design(d)
        est = est_table(s)
        W0 = D.w[None, :].astype(np.float32)
        obs_sets[s] = set(d["observer_id"])
        multi[s] = int((d.groupby("observer_id")["family"].nunique() > 1).sum())
        log(f"{s}: {len(d):,} analysis rows; research with T {int(D.tdef.sum()):,}; families {D.F}")
        for m in C.MODELS:
            e = 1 - d[f"c_{m}"].to_numpy(float)
            r = E.c1(W0, D.sp_idx, D.sp_fam, e, D.slow, D.fast, D.F)
            # reproduction of stored values
            dif = [abs(float(r["Delta"][0]) - get(est, m, "Delta")["value"]), abs(float(r["ER"][0]) - get(est, m, "ER")["value"])]
            for j, f in enumerate(D.fams):
                for q, x in (("Delta", r["Delta_f"][0, j]), ("ER", r["ER_f"][0, j])):
                    v = get(est, m, q, f)["value"]
                    dif.append(0.0 if (not np.isfinite(x) and not np.isfinite(v)) else abs(float(x) - v))
            worst = max(worst, max(dif))
            Es, Er = r["E_slow"][0], r["E_ref"][0]
            estf = r["est"]
            # A2: pooled E_slow and E_ref, raw error rates
            w, sl, fa = D.w, D.slow, D.fast
            raw_fast = float((w * e * fa).sum() / (w * fa).sum())
            raw_slow = float((w * e * sl).sum() / (w * sl).sum())
            fam_fast = np.array([(w * e * fa * (D.fam == j)).sum() / (w * fa * (D.fam == j)).sum() for j in range(D.F)])
            fam_slow = np.array([(w * e * sl * (D.fam == j)).sum() / (w * sl * (D.fam == j)).sum() for j in range(D.F)])
            a2.append({"set": s, "hypothesis": C.HYP.get(s, ""), "model": m, "E_slow_pooled": float(np.mean(Es[estf])),
                       "E_ref_pooled": float(np.mean(Er[estf])), "Delta": float(r["Delta"][0]), "ER": float(r["ER"][0]),
                       "raw_fast_error_weighted": raw_fast, "raw_slow_error_weighted": raw_slow,
                       "raw_difference_points": 100 * (raw_slow - raw_fast), "raw_ratio": raw_slow / raw_fast,
                       "raw_fast_error_equal_family": float(np.mean(fam_fast)),
                       "raw_slow_error_equal_family": float(np.mean(fam_slow)),
                       "raw_fast_error_unweighted": float(e[fa].mean()), "raw_slow_error_unweighted": float(e[sl].mean()),
                       "fast_rows": int(fa.sum()), "slow_rows": int(sl.sum())})
            # A1 and A9 per family
            for j, f in enumerate(D.fams):
                k = D.fam == j
                sp_f = np.flatnonzero(D.sp_fam == j)
                has_f = np.isin(sp_f, D.sp_idx[k & fa])
                has_s = np.isin(sp_f, D.sp_idx[k & sl])
                row = {"set": s, "model": m, "family": f, "label_space_species": int(labsize.get(f, 0)),
                       "species_with_research_rows": int(len(np.setdiff1d(np.unique(D.sp_idx[k & D.isR]), []))),
                       "species_with_fast": int(has_f.sum()), "species_with_slow": int(has_s.sum()),
                       "species_retained": int((has_f & has_s).sum()),
                       "fast_rows": int((k & fa).sum()), "slow_rows": int((k & sl).sum()),
                       "fast_error_all_fast_rows": float(fam_fast[j]), "slow_error_all_slow_rows": float(fam_slow[j]),
                       "E_slow": float(Es[j]), "E_ref": float(Er[j]), "Delta": float(r["Delta_f"][0, j]),
                       "Delta_lo95": get(est, m, "Delta", f)["lo95"], "Delta_hi95": get(est, m, "Delta", f)["hi95"],
                       "ER": float(r["ER_f"][0, j]), "ER_lo95": get(est, m, "ER", f)["lo95"],
                       "ER_hi95": get(est, m, "ER", f)["hi95"]}
                a9.append(row)
                if m == "Z25":
                    a1.append({"set": s, "hypothesis": C.HYP.get(s, ""), "family": f,
                               "dropped_share_of_slow_weight": float(r["dropped"][0, j]),
                               "slow_species": int(has_s.sum()), "slow_species_without_fast": int((has_s & ~has_f).sum()),
                               "fast_species_without_slow": int((has_f & ~has_s).sum()),
                               "slow_rows": int((k & sl).sum()),
                               "slow_rows_dropped": int((k & sl & np.isin(D.sp_idx, sp_f[has_s & ~has_f])).sum())})
            if m == "Z25":
                st = get(est, m, "dropped share of slow weight")
                a1.append({"set": s, "hypothesis": C.HYP.get(s, ""), "family": "pooled (mean over families)",
                           "dropped_share_of_slow_weight": float(np.nanmean(r["dropped"][0])),
                           "stored_value": st["value"], "stored_lo95": st["lo95"], "stored_hi95": st["hi95"]})
    log.check("A0 recomputed pooled and per-family Delta and ER equal the stored estimates (4 models x 4 sets)",
              worst < 1e-9, f"largest absolute difference {worst:.2e}")
    C.save_csv(pd.DataFrame(a1), OUT / "A1_dropped_slow_weight.csv")
    C.save_csv(pd.DataFrame(a2), OUT / "A2_pooled_errors.csv")
    C.save_csv(pd.DataFrame(a9), OUT / "A9_family_errors.csv")

    # A3: tipping points (analysis.json) and the 5,000-replicate lower bounds
    a3 = []
    for s in ("eight_W", "eight_W2", "new_W"):
        info = json.loads((C.CONF / s / "analysis.json").read_text(encoding="utf-8"))
        est = est_table(s)
        for m in C.MODELS:
            row = {"set": s, "hypothesis": C.HYP[s], "model": m, "tipping_point_to_0": info[f"{m}_tipping_point_to_0"],
                   "tipping_point_to_1": info[f"{m}_tipping_point_to_1"], "bootstrap_of_tipping_point": f"{info['replicates']} replicates",
                   "Delta_lower_bound_2000": get(est, m, "Delta")["lo_one_sided"]}
            if m == "Z25":
                b5 = get(est, m, "Delta (5000 replicates)")
                row.update({"Delta_lower_bound_5000 (Table of H1 to H6)": b5["lo_one_sided"],
                            "tipping_point_to_0_from_5000": b5["lo_one_sided"] / 100,
                            "tipping_point_to_1_from_5000": (b5["lo_one_sided"] - 1) / 100,
                            "ER_lower_bound_5000": get(est, m, "ER (5000 replicates)")["lo_one_sided"]})
            a3.append(row)
    C.save_csv(pd.DataFrame(a3), OUT / "A3_tipping_points.csv")
    summary["A3_code"] = code_lines("src/confirm/analysis.py", 141, 144) + code_lines("src/confirm/estimators.py", 47, 54)

    # A4: Spearman correlation over the 14 families (analyse-joint)
    j = json.loads((C.CONF / "joint_14/joint.json").read_text(encoding="utf-8"))
    rel = j["relation_across_families"]
    sj = json.loads((C.CONF / "spec_analyse-joint.json").read_text(encoding="utf-8"))
    ej = pd.read_csv(C.CONF / "joint_14/estimates_joint.csv")
    dl = ej[(ej["model"] == "Z25") & (ej["quantity"] == "Delta") & ej["unit"].isin(j["fast_share"])]
    x = dl.set_index("unit")["value"]
    y = pd.Series(j["fast_share"])
    fams = sorted(x.index)
    rho = E.spearman(x[fams].to_numpy(), y[fams].to_numpy())
    rng = np.random.default_rng(C.SEED)
    perm = np.array([E.spearman(x[fams].to_numpy(), rng.permutation(y[fams].to_numpy())) for _ in range(10000)])
    p_two = float((1 + (np.abs(perm) >= abs(rho) - 1e-12).sum()) / 10001)
    p_lower = float((1 + (perm <= rho + 1e-12).sum()) / 10001)
    a4 = {"rho_stored": rel["rho"], "p_stored": rel["p"], "families_used": rel["families_used"],
          "families_left_out": rel["families_left_out"], "n_perm": sj["n_perm"], "sidedness":
          "one-sided, alternative rho > 0: p = (1 + number of permuted rho >= observed) / (1 + n_perm)",
          "rho_recomputed": rho, "p_two_sided_D19": p_two, "p_one_sided_rho_below_D19": p_lower,
          "permutations_D19": 10000, "seed_D19": C.SEED, "families": fams,
          "code": code_lines("src/confirm/estimators.py", 274, 282) + code_lines("scripts/confirm_run.py", 503, 505)}
    log.check("A4 recomputed rho over the 14 families equals the stored rho", abs(rho - rel["rho"]) < 1e-12, f"{rho:.6f}")
    summary["A4"] = a4

    # A5: L, L_upload and L_ident at S*
    a5 = []
    for s in ("eight_W", "eight_W2"):
        est = est_table(s)
        for q in ("L", "L_upload", "L_ident"):
            r = get(est, "Z25", q)
            a5.append({"set": s, "quantity": f"{q}(S*)", "share": r["value"], "percent_3_decimals": round(100 * r["value"], 3),
                       "lo95": r["lo95"], "hi95": r["hi95"]})
    C.save_csv(pd.DataFrame(a5), OUT / "A5_L_shares.csv")

    # A6: bootstrap resampling unit (code and counts)
    summary["A6"] = {"code": code_lines("src/confirm/estimators.py", 27, 35) + code_lines("src/confirm/analysis.py", 75, 75)
                     + code_lines("scripts/confirm_run.py", 437, 437) + code_lines("scripts/confirm_run.py", 500, 503),
                     "observers_per_set": {s: len(v) for s, v in obs_sets.items()},
                     "observers_with_rows_in_more_than_one_family": multi,
                     "observers_in_both_eight_W_and_eight_W2": len(obs_sets["eight_W"] & obs_sets["eight_W2"]),
                     "observers_in_both_eight_W_and_new_W": len(obs_sets["eight_W"] & obs_sets["new_W"])}

    # A7: failure rates by family and stratum
    a7h, a7p = [], []
    for s in C.SETS:
        st = pd.read_parquet(C.CONF / s / "strata.parquet", columns=["family", "grade", "stratum"])
        g = st.groupby(["family", "grade"]).agg(phase1=("stratum", "size"),
                                                history_failed=("stratum", lambda v: int((v == "failed").sum())),
                                                T_undefined=("stratum", lambda v: int((v == "excluded_T_undefined").sum())))
        g = g.reset_index()
        g.insert(0, "set", s)
        g["history_failed_share"] = g["history_failed"] / g["phase1"]
        a7h.append(g)
        pf = pd.read_csv(C.CONF / s / "photo_failures.csv")
        pf.insert(0, "set", s)
        a7p.append(pf)
    a7h, a7p = pd.concat(a7h, ignore_index=True), pd.concat(a7p, ignore_index=True)
    C.save_csv(a7h, OUT / "A7_history_failures.csv")
    C.save_csv(a7p, OUT / "A7_photo_failures.csv")

    # A11: C3 coefficients
    a11 = []
    for s in ("eight_W", "eight_W2", "new_W"):
        est = est_table(s)
        for q in ("b0", "b3", "b_obs", "rho"):
            r = est[(est["model"] == "Z25") & (est["quantity"] == q) & (est["unit"] == "pooled")]
            if len(r):
                r = r.iloc[0]
                a11.append({"set": s, "quantity": q, "value": r["value"], "lo95": r["lo95"], "hi95": r["hi95"]})
    C.save_csv(pd.DataFrame(a11), OUT / "A11_c3_coefficients.csv")
    summary["A11_b3_covariates"] = {s: json.loads((C.CONF / s / "analysis.json").read_text())["b3_covariates"]
                                    for s in ("eight_W", "eight_W2")}

    # A12: provenance file of TreeOfLife-200M
    pth = C.ROOT / "outputs/retained/tol200m_97e2340/provenance.parquet"
    t0 = time.time()
    h = hashlib.sha256()
    with open(pth, "rb") as f:
        for b in iter(lambda: f.read(16 << 20), b""):
            h.update(b)
    sha_ok = h.hexdigest() == "7a4b02601f7352be68024d3b8012534949561430760875ff66b17efd0f3eb3a5"
    log.check("A12 provenance file SHA-256 equals the value recorded in D17", sha_ok, f"({time.time() - t0:.0f} s)")
    pf = pq.ParquetFile(pth)
    md = pf.metadata
    fields = [{"name": f.name, "type": str(f.type)} for f in pf.schema_arrow]
    kv = {k.decode(): (v.decode()[:200]) for k, v in (md.metadata or {}).items()}
    datelike = [f["name"] for f in fields if any(t in f["type"] for t in ("date", "timestamp", "time"))]
    rg0 = pf.read_row_group(0)
    pat = re.compile(r"(19|20)\d\d-\d\d-\d\d")
    scan = {}
    for f in fields:
        v = rg0.column(f["name"]).to_pandas()
        v = v.dropna().astype(str)
        scan[f["name"]] = {"non_null": int(len(v)), "values_with_a_YYYY-MM-DD_string": int(v.str.contains(pat).sum())}
    src = rg0.column("data_source").to_pandas().value_counts().to_dict()
    summary["A12"] = {"file": "outputs/retained/tol200m_97e2340/provenance.parquet", "sha256_equal_to_D17": sha_ok,
                      "rows": md.num_rows, "row_groups": md.num_row_groups, "fields": fields,
                      "key_value_metadata_keys": list(kv), "date_or_time_typed_fields": datelike,
                      "first_row_group_rows": rg0.num_rows, "first_row_group_date_pattern_scan": scan,
                      "first_row_group_sources": {str(k): int(v) for k, v in src.items()}}
    C.save_json(OUT / "A_summary.json", summary)
    log("finished", time.strftime("%Y-%m-%d %H:%M:%S"), f"({(time.time() - log.t0) / 60:.1f} min)")
    log("FAILED CHECKS:", log.fails if log.fails else "none")


if __name__ == "__main__":
    main()
