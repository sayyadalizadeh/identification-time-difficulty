"""D16 report (post hoc): docs/reports/D16_report.md from outputs/D16/run.json and accuracy_by_set.csv.
Usage: python scripts/d16_report.py --plan-commit <commit of the D16 entry>
"""
import argparse
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "outputs/D16"
NAMES = {"Z25": "BioCLIP 2.5 Huge", "Z2": "BioCLIP 2", "Z1": "first BioCLIP"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-commit", required=True)
    a = ap.parse_args()
    r = json.loads((D / "run.json").read_text(encoding="utf-8"))
    acc = pd.read_csv(D / "accuracy_by_set.csv")
    h, ph, fr = r["histories"], r["photographs"], r.get("frame", {})
    L = ["# D16 - Exposure test of BioCLIP 2.5 Huge (post hoc)", "",
         f"Decision D16 in docs/PLAN.md (post hoc, written after the confirmatory results were seen; commit "
         f"{a.plan_commit}, before any part of D16 was run). Development half only. Script: scripts/d16_run.py; outputs "
         "in outputs/D16/ (row tables, raw responses and photographs not tracked). The results are described; the "
         "reading below is the one fixed in D16.", "",
         "## Data", "",
         f"Set A: research-grade observations of the D4 sample (window W 2024-07-01 to 2024-09-30, eight families, "
         f"development half) with T < 1 day and the stored first-photograph correctness of the three models: "
         f"{r['set_A_rows']:,} rows.", "",
         f"Set B: development-half observations of the eight families observed {r['window_B'][0]} to {r['window_B'][1]}, "
         f"first photograph passing the licence and size filters, research grade in the snapshot with a label-space "
         f"species. Frame rows (both grades, all eight families): {fr.get('rows_in_windows_half', 'n/a'):,} in the window "
         f"for the development half before the photograph and label filters; frame manifest checks: "
         + ", ".join(f"{k} {'PASS' if v else 'FAIL'}" for k, v in fr.items() if k.startswith("manifest_")) + ". "
         "Simple random sample of up to 1,500 research-grade frame rows per family (seed 20261124): "
         + "; ".join(f"{f} {v[1]:,} of {v[0]:,}" for f, v in r["sample_sizes"].items()) + ".", "",
         f"Histories: {h['requests_needed']} requests of up to 200 observations (at most one per second), "
         f"{h['returned']:,} returned, failed batches {len(h['failed'])}, hidden identifications {h['hidden']}; identification "
         f"time reconstructed for {h['T_defined']:,}; T < 1 day: {h['fast']:,}.", "",
         f"Photographs (medium size): {ph['ok']:,} of {ph['selected']:,} obtained; bytes downloaded in this run "
         f"{ph['bytes_this_run']:,}. Rows of set B with predictions: {r['set_B_rows']:,}.", "",
         "## Accuracy per set and family (species level, unweighted, rows with T < 1 day)", "",
         "| set | family | rows | observers | species | BioCLIP 2.5 Huge | BioCLIP 2 | first BioCLIP |", "|---|---|---|---|---|---|---|---|"]
    for x in acc.sort_values(["family", "set"]).itertuples():
        L.append(f"| {x.set} | {x.family} | {x.rows:,} | {x.observers:,} | {x.species:,} | {x.acc_Z25:.3f} | "
                 f"{x.acc_Z2:.3f} | {x.acc_Z1:.3f} |")
    for ref in ("Z2", "Z1"):
        e = r["estimates"][ref]
        L += ["", f"## D with reference {NAMES[ref]}" + (" (primary reading)" if ref == "Z2" else ""), "",
              "D_f = gain of BioCLIP 2.5 Huge over the reference in set A minus that in set B, over the species present in "
              "both sets, weighted by the set-A species shares; points. 2,000 observer-cluster bootstrap replicates "
              "within each set (seed 20261121).", "",
              "| family | species in both sets | rows A | rows B | D_f [95%] |", "|---|---|---|---|---|"]
        for f, v in e["families"].items():
            L.append(f"| {f} | {v['species_common']} | {v['rows_A']:,} | {v['rows_B']:,} | {v['D_f']:.3f} "
                     f"[{v['lo95']:.3f}, {v['hi95']:.3f}] |")
        L += ["", f"D (mean over the eight families, equal weights) = {e['D']:.3f} [{e['lo95']:.3f}, {e['hi95']:.3f}] points."]
    r2 = r["estimates"]["Z2"]
    L += ["", "## Reading fixed in D16 (reference BioCLIP 2)", "",
          f"Upper bound of the 95% interval {r2['hi95']:.3f}; lower bound {r2['lo95']:.3f}; threshold 1.0 point. "
          f"Reading: {r['reading_Z2']}.", "",
          "## Limitations stated in D16", "",
          "Two years of change in cameras and observers between the sets; a partly matched season (set A July to "
          "September 2024, set B late August to October 2026); possible exposure of BioCLIP 2 through images republished "
          "by EOL.", "", f"Run time: {r['minutes']:.1f} minutes.", ""]
    (ROOT / "docs/reports/D16_report.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
