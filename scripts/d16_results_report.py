"""D16 results (post hoc): docs/reports/D16_results.md from outputs/D16/run.json (task N21, read only),
outputs/D16/results.json and accuracy_by_set.csv (task N22). The stop report docs/reports/D16_report.md is not changed.
Usage: python scripts/d16_results_report.py --plan-commit <commit of the D16 entry>
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
    r21 = json.loads((D / "run.json").read_text(encoding="utf-8"))
    r = json.loads((D / "results.json").read_text(encoding="utf-8"))
    acc = pd.read_csv(D / "accuracy_by_set.csv")
    led = json.loads((ROOT / "outputs/N22/ledger_d16.json").read_text(encoding="utf-8"))
    h, ph, fr = r21["histories"], r["photographs"], r21.get("frame", {})
    L = ["# D16 - Exposure test of BioCLIP 2.5 Huge (post hoc): results", "",
         f"Decision D16 in docs/PLAN.md (post hoc, written after the confirmatory results were seen; commit "
         f"{a.plan_commit}, before any part of D16 was run). Development half only. Task N21 stopped D16 at its download "
         "limit (docs/reports/D16_report.md, unchanged); task N22 completed it with the design unchanged. Scripts: "
         "scripts/d16_run.py (N21) and scripts/d16_complete.py (N22); outputs in outputs/D16/ (row tables, raw responses "
         "and photographs not tracked).", "",
         "## Download limit of task N21", "",
         "Task N21 passed its download limit of 1.5 GB: the photographs of set B came to 1,505,970,832 bytes, 5,970,832 "
         "bytes above the limit (the budget was checked before each batch of 400 photographs), and the 31.5 MB of raw API "
         "responses of the histories were not counted against the limit.", "",
         "## Data", "",
         f"Set A: research-grade observations of the D4 sample (window W 2024-07-01 to 2024-09-30, eight families, "
         f"development half) with T < 1 day and the stored first-photograph correctness of the three models: "
         f"{r['set_A_rows']:,} rows.", "",
         f"Set B (N21): development-half observations of the eight families observed {r21['window_B'][0]} to "
         f"{r21['window_B'][1]}; frame manifest checks "
         + ", ".join(f"{k[9:]} {'PASS' if v else 'FAIL'}" for k, v in fr.items() if k.startswith("manifest_")) + "; "
         f"{fr.get('rows_in_windows_half', 0):,} development-half rows of the eight families in the window before the "
         "photograph and label filters; simple random sample of up to 1,500 research-grade frame rows per family (seed "
         "20261124): " + "; ".join(f"{f} {v[1]:,} of {v[0]:,}" for f, v in r21["sample_sizes"].items()) + ".", "",
         f"Histories (N21): {h['requests_needed']} requests, {h['returned']:,} returned, failed batches {len(h['failed'])}, "
         f"hidden identifications {h['hidden']}; T reconstructed for {h['T_defined']:,}; T < 1 day: {h['fast']:,}. "
         "N22 made no API request; it recomputed T from the saved responses (controls: all 60 batches present "
         f"{'PASS' if r['controls']['all_history_batches_present'] else 'FAIL'}; rows with T < 1 day equal to N21 "
         f"{'PASS' if r['controls']['fast_rows_equal_N21'] else 'FAIL'}; rows with T defined equal to N21 "
         f"{'PASS' if r['controls']['T_defined_equal_N21'] else 'FAIL'}).", "",
         f"Photographs (medium size) of the {h['fast']:,} rows with T < 1 day: {ph['ok_N21']:,} rows with a photograph "
         f"obtained in N21; {ph['failed_N21_not_retried']} rows whose photograph failed after 3 retries in N21 (not "
         f"retried); {ph['to_download']} rows downloaded in N22 ({', '.join(f'{k} {v}' for k, v in ph['to_download_by_family'].items())}), "
         f"{ph['ok_N22']} obtained and {ph['failed_N22']} failed, {ph['bytes_N22']:,} bytes "
         f"({sum(led['items'].values()):,} bytes counted in the N22 ledger). One Columbidae photograph (photo id "
         "730742096) is the first photograph of two sampled observations with different species; both rows are kept, as "
         "in the registered code. SHA-256 of every photograph checked against its manifest before prediction: "
         f"{'PASS' if r['controls'].get('photographs_sha256_checked') else 'FAIL'}. Rows of set B with predictions: "
         f"{r['set_B_rows']:,}.", "",
         "Model checks (pinned weight file, SHA-256): "
         + "; ".join(f"{NAMES[k]} " + ", ".join(f"{c} {'PASS' if v else 'FAIL'}" for c, v in (ck or {}).items())
                     for k, ck in r.get("model_checks", {}).items()) + ".", "",
         "## Accuracy per set and family (species level, unweighted, rows with T < 1 day)", "",
         "| set | family | rows | observers | species | BioCLIP 2.5 Huge | BioCLIP 2 | first BioCLIP |",
         "|---|---|---|---|---|---|---|---|"]
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
          "Rule: no material sign of exposure if the upper bound of the 95% interval is below 1.0 point; a sign of "
          "exposure if the lower bound is above 1.0 point; inconclusive otherwise.", "",
          f"Upper bound {r2['hi95']:.3f}: below 1.0 point - {'met' if r2['hi95'] < 1.0 else 'not met'}. Lower bound "
          f"{r2['lo95']:.3f}: above 1.0 point - {'met' if r2['lo95'] > 1.0 else 'not met'}. Reading: {r['reading_Z2']}.", "",
          "## Limitations stated in D16", "",
          "Two years of change in cameras and observers between the sets; a partly matched season (set A July to "
          "September 2024, set B late August to October 2026); possible exposure of BioCLIP 2 through images republished "
          "by EOL.", "", f"Run time of the completion in N22: {r['minutes']:.1f} minutes.", ""]
    (ROOT / "docs/reports/D16_results.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
