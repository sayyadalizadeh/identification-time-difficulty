"""D14 report (post hoc): docs/reports/D14_report.md from outputs/D14/a.json, b.json and b_stratum_counts.csv.
Usage: python scripts/d14_report.py --plan-commit <commit of the D14 entry>
"""
import argparse
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "outputs/D14"
NAMES = {"Z25": "BioCLIP 2.5 Huge", "Z2": "BioCLIP 2", "Z1": "first BioCLIP", "BT-CLIP-O": "BT-CLIP-O"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-commit", required=True)
    a_ = ap.parse_args()
    a = json.loads((D / "a.json").read_text(encoding="utf-8"))
    b = json.loads((D / "b.json").read_text(encoding="utf-8"))
    cnt = pd.read_csv(D / "b_stratum_counts.csv")
    p1 = pd.read_parquet(ROOT / "outputs/confirm/replication_W/phase1.parquet", columns=["family"])
    fr = [int(i) for i in p1.index[p1["family"] == "Ardeidae"]]
    L = ["# D14 - Sensitivity of the confirmatory results to the two failure deviations (post hoc)", "",
         f"Decision D14 in docs/PLAN.md (post hoc, written after the confirmatory results were seen; commit "
         f"{a_.plan_commit}, before any part of D14 was run). The registered results (docs/reports/confirmatory_results.md) "
         "stay primary; everything below is post hoc. Script: scripts/d14_run.py; outputs in outputs/D14/. No decision "
         "rule; the results are described.", "",
         "## (a) rho of H6 without the families with a failure deviation (BioCLIP 2.5 Huge)", "",
         "One-sided permutation p from 10,000 permutations (a generator with seed 20261121 for every row); family values "
         "of N18 (outputs/confirm/h6.json).", "", "| families | n | rho | p |", "|---|---|---|---|"]
    for k in ("registered", "without Ardeidae", "without Coccinellidae", "without both", "leave-one-out minimum",
              "leave-one-out maximum"):
        r = a[k]
        lab = k + (f" (left out: {r['family_left_out']})" if "family_left_out" in r else "")
        L.append(f"| {lab} | {r['families']} | {r['rho']:.3f} | {r['p']:.5f} |")
    loo = pd.DataFrame(a["leave-one-out all"]).T
    L += ["", f"Leave-one-family-out over the 36 families: rho from {loo['rho'].min():.3f} to {loo['rho'].max():.3f}; "
          f"p from {loo['p'].min():.5f} to {loo['p'].max():.5f}.", "",
          "## (b) Ardeidae: the two failed history batches", "",
          f"Batching in N18: the replication phase-1 sample ({b['phase1_rows']:,} rows, families in the order of the frame) "
          f"was sent to the API in its row order in {b['batches']} batches of 200 observations. Ardeidae, the first "
          f"family, holds rows {fr[0]} to {fr[-1]:,}, that is batches {b['ardeidae_batches'][0]} to "
          f"{b['ardeidae_batches'][-2]} and the first 100 rows of batch {b['ardeidae_batches'][-1]}. Batches 0 and 2 (rows 0-199 and 400-599, Ardeidae only) were not obtained after 3 "
          "retries in N18; batch 1 between them was.", "",
          "Re-request (one per batch, registered API rules, raw responses in outputs/D14/api_raw/, not tracked): "
          + "; ".join(f"batch {k}: {v}" for k, v in b["request_status"].items()) + f". Hidden identifications: "
          f"{b['hidden_identifications']}. Newly obtained observations with a history: {b['new_with_history']} of "
          f"{b['new_rows']}.", "",
          "Stratum counts of the newly obtained observations against those already obtained in N18:", "",
          "| stratum | already obtained | newly obtained |", "|---|---|---|"]
    for r in cnt.itertuples():
        L.append(f"| {r.stratum} | {r._2:,} | {r._3:,} |")
    cs = b["chi_square"]
    L += ["", f"Chi-square test over {', '.join(cs['strata'])}: statistic {cs['statistic']:.3f}, {cs['dof']} degrees of "
          f"freedom, p = {cs['p']:.4f}.", "",
          "Phase 2 among the newly obtained observations (all of A1 to A3, A0 with fraction 0.5; seed 20261123): "
          + "; ".join(f"{k} {v['selected']} of {v['rows']}" for k, v in b["phase2_new"].items())
          + f". Photographs: {b['photographs']['ok']} of {b['photographs']['selected']} downloaded "
          f"({b['photographs']['bytes']:,} bytes); predictions of the four models.", "",
          f"Ardeidae Delta and ER (weights of the full phase-1 sample of 1,500: frame size / 1,500 divided by the realized "
          f"phase-2 fraction of the stratum in the original or the new part; 2,000 observer-bootstrap replicates). Rows: "
          f"original {b['ardeidae_rows']['original']}, new {b['ardeidae_rows']['new']} (research grade with T).", "",
          "| model | rows | Delta [95%] | ER [95%] |", "|---|---|---|---|"]
    for k, v in b["ardeidae_estimates"].items():
        m, lab = k.split(" | ")
        L.append(f"| {NAMES[m]} | {lab} | {v['Delta']:.3f} [{v['Delta_lo95']:.3f}, {v['Delta_hi95']:.3f}] | "
                 f"{v['ER']:.3f} [{v['ER_lo95']:.3f}, {v['ER_hi95']:.3f}] |")
    h = b["h6_recomputed"]
    L += ["", f"The point values on the original rows reproduce the N18 Ardeidae Delta ({b['ardeidae_delta_N18']:.3f}); "
          "the intervals differ from N18 because this bootstrap resamples the Ardeidae observers only, with another "
          "generator.", "",
          f"Ardeidae share of fast observations: N18 {b['ardeidae_fast_share']['N18']:.4f}; full phase-1 sample "
          f"{b['ardeidae_fast_share']['full phase-1 sample']:.4f}.", "",
          f"H6 recomputed with the full-sample Ardeidae Delta and fast share: rho = {h['rho']:.3f} [{h['rho_lo95']:.3f}, "
          f"{h['rho_hi95']:.3f}] (5,000 bootstrap replicates over families), one-sided permutation p = {h['p']:.5f} "
          f"(10,000 permutations, seed 20261121), {h['families_used']} families. Registered: rho = "
          f"{a['registered']['rho']:.3f}, p = {a['registered']['p']:.5f}.", "",
          "## (c) Coccinellidae", "", "The failed photograph (1 of 21 in stratum A3) was not requested again, as registered.",
          "", f"Run time of (a) and (b): {b['minutes']:.1f} minutes.", ""]
    (ROOT / "docs/reports/D14_report.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
