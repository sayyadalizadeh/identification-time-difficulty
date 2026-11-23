"""N18, Step 4: report of the confirmatory run (docs/reports/confirmatory_results.md) from the outputs of
scripts/confirm_driver.py in outputs/confirm/ (no computation of new estimates; tables are read and formatted).

Usage: python scripts/n18_report.py --lock-commit <commit of the registration lock>
"""
import argparse
import json
import re
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs/confirm"
SETS = {"eight_W": "eight families, locked half, window W", "eight_W2": "eight families, locked half, window W2",
        "new_W": "six new families, both halves, window W",
        "replication_W": "30 replication families, both halves, window W (research-grade frame)"}
MODELS = ["Z25", "Z2", "Z1", "BT-CLIP-O"]
NAMES = {"Z25": "BioCLIP 2.5 Huge", "Z2": "BioCLIP 2", "Z1": "first BioCLIP", "BT-CLIP-O": "BT-CLIP-O"}


def f3(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return str(x)
    return "n/a" if not np.isfinite(x) else f"{x:.3f}"


def fp(x):
    x = float(x)
    return "n/a" if not np.isfinite(x) else (f"{x:.4f}" if x >= 0.0001 else "< 0.0001" if x > 0 else "0 (no replicate at or below 0)")


def ci(r):
    return f"{f3(r['value'])} [{f3(r['lo95'])}, {f3(r['hi95'])}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lock-commit", required=True)
    a = ap.parse_args()
    lock = json.loads((ROOT / "configs/registration_lock.json").read_text(encoding="utf-8"))
    prog = (OUT / "progress.md").read_text(encoding="utf-8").splitlines()
    start = next(x for x in prog if "| start |" in x)
    hw = start.split("| start |", 1)[1].strip()
    t0 = re.search(r"- (\S+ \S+) \| start", start).group(1)
    t1 = re.search(r"- (\S+ \S+) \| run complete", next(x for x in prog if "run complete" in x)).group(1)
    hours = (pd.Timestamp(t1) - pd.Timestamp(t0)).total_seconds() / 3600
    secs = {}
    for x in prog:
        m = re.search(r"\| (.+?) \| (?:done|stopped) in (\d+) s", x)
        if m and "| start |" not in x:
            secs[m.group(1)] = secs.get(m.group(1), 0) + int(m.group(2))
    used = json.loads((OUT / "download_bytes.json").read_text())["used_bytes"]
    est = {s: pd.read_csv(OUT / s / "estimates.csv") for s in SETS}
    info = {s: json.loads((OUT / s / "analysis.json").read_text(encoding="utf-8")) for s in SETS}
    dec = pd.read_csv(OUT / "decisions.csv")
    sec = pd.read_csv(OUT / "decisions_secondary.csv")
    h6 = json.loads((OUT / "h6.json").read_text(encoding="utf-8"))
    jt = json.loads((OUT / "joint_14/joint.json").read_text(encoding="utf-8"))
    ej = pd.read_csv(OUT / "joint_14/estimates_joint.csv")

    L = ["# Confirmatory results", "",
         f"Registration: {lock['registration_id']} (with its update note on the corrected freeze). Original code freeze: "
         "f3d452832935f5e9d8f829dc6f588e58cb4c2a5b; corrected freeze: 966fa55500ba48d892c9c2ed403b5ad8dea9d1aa "
         "(docs/reports/code_freeze_v2.md); registration lock: commit " + a.lock_commit + ". Driver: "
         "scripts/confirm_driver.py, confirmatory mode, every step through scripts/confirm_run.py; single run.", "",
         "## Run", "",
         f"From {t0} to {t1} ({hours:.2f} hours; limit 14). {hw}. Photographs downloaded: {used / 1e9:.2f} GB "
         f"(counter outputs/confirm/download_bytes.json; limit 24 GB). Free space on D: at the end "
         f"{shutil.disk_usage(ROOT).free / 1e9:.1f} GB. Bootstrap: 5,000 replicates for the estimates of H1 to H6, 2,000 "
         "for all other estimates; 10,000 permutations for H6; seed 20261121.", "",
         "| step | seconds |", "|---|---|"]
    L += [f"| {k} | {v:,} |" for k, v in secs.items()]
    # ---------------------------------------------------------------- counts, failures, deviations
    L += ["", "## Counts per set, family and stratum", "",
          "Phase 1: the stratum of every phase-1 observation (A0 to A3 research grade by identification time; B1 and B2 "
          "needs_id by label support; T undefined: research grade in the snapshot but not reconstructed; failed: no "
          "history after 3 retries). Phase 2: photographs after the registered cap rule (no family was reduced by it). "
          "Stratum-count reports written between the phases: docs/reports/N18_strata_<set>.md.", ""]
    devs = []
    for s, lab in SETS.items():
        r = pd.read_csv(OUT / s / "stratum_report.csv")
        pf = pd.read_csv(OUT / s / "photo_failures.csv")
        p1 = json.loads((OUT / s / "phase1.json").read_text(encoding="utf-8"))["frame_and_sample_sizes"]
        L += [f"### {s}: {lab}", "",
              "| family | frame | phase 1 | A0 | A1 | A2 | A3 | B1 | B2 | T undefined | failed history | phase 2 | "
              "photographs ok | photograph failures |", "|---" * 15 + "|"]
        for _, x in r.iterrows():
            f = x["family"]
            q = pf[pf["family"] == f]
            L.append(f"| {f} | {p1[f][0]:,} | {p1[f][1]:,} | {int(x['A0']):,} | {int(x['A1']):,} | {int(x['A2']):,} | "
                     f"{int(x['A3']):,} | {int(x['B1']):,} | {int(x['B2']):,} | {int(x['excluded_T_undefined']):,} | "
                     f"{int(x['failed_history']):,} | {int(q['selected'].sum()):,} | {int(q['ok'].sum()):,} | "
                     f"{int(q['failed'].sum()):,} |")
            if x["failed_history"] > 0.02 * p1[f][1]:
                devs.append(f"{s}, {f}: {int(x['failed_history'])} of {p1[f][1]:,} phase-1 histories not obtained after "
                            f"3 retries ({x['failed_history'] / p1[f][1]:.1%}; the stratum of these observations is unknown)")
        for _, q in pf[pf["failed_share"] > 0.02].iterrows():
            devs.append(f"{s}, {q['family']}, stratum {q['stratum']}: {int(q['failed'])} of {int(q['selected'])} "
                        f"photographs failed ({q['failed_share']:.1%})")
        hj = json.loads((OUT / s / "histories.json").read_text(encoding="utf-8"))
        L += ["", f"Histories: {hj['returned']:,} of {hj['requested']:,} returned in {hj['requests']} requests; failed "
              f"request batches: {len(hj['failed'])}; hidden identifications excluded: {hj['hidden']}; share of "
              f"snapshot research-grade observations reconstructed as research grade on 2026-10-27: "
              f"{hj['research_rg_today_share']:.4f}. Exact duplicate photographs dropped (lowest observation id kept): "
              f"{info[s]['exact_duplicates_dropped']}. Analysis rows: {info[s]['rows']:,}; research grade with T: "
              f"{info[s]['research_with_T']:,}.", ""]
    L += ["## Deviations", ""] + ([f"- {d}" for d in devs] or ["- none"]) + [""]
    # ---------------------------------------------------------------- hypotheses
    L += ["## H1 to H6 (BioCLIP 2.5 Huge; Holm over H1 to H6 at one-sided 0.05)", "",
          "Bounds are one-sided 95% bounds (5th and 95th percentiles of the replicates); p is the one-sided p-value "
          "(share of the 5,000 replicates at or below 0; H6: 10,000 permutations); the H6 interval comes from 5,000 "
          "bootstrap replicates over families.", "",
          "| Holm order | hypothesis | set | estimate | 95% interval | lower bound | upper bound | p | companion | "
          "companion lower bound | companion upper bound | Holm threshold | rejected | grade |", "|---" * 14 + "|"]
    for r in dec.sort_values("holm_order").itertuples():
        comp = f"{r.companion_name} {f3(r.companion)}" if isinstance(r.companion_name, str) else "-"
        L.append(f"| {r.holm_order} | {r.hypothesis} | {r.set} | {r.estimate_name} {f3(r.estimate)} | [{f3(r.lo95)}, "
                 f"{f3(r.hi95)}] | {f3(r.lower_bound)} | {f3(r.upper_bound)} | {fp(r.p)} | {comp} | "
                 f"{f3(r.companion_lower_bound)} | {f3(r.companion_upper_bound)} | {r.holm_threshold:.4f} | "
                 f"{'yes' if r.rejected else 'no'} | {r.grade} |")
    g = est["eight_W"]
    ga = g[(g["model"] == "Z25") & (g["quantity"] == "G_all (5000 replicates)")].iloc[0]
    L += ["", f"H4 range (section 9): G_sup {f3(dec.loc[dec['hypothesis'] == 'H4', 'estimate'].iloc[0])} and G_all "
          f"{ci(ga)} (5,000 replicates). H6: {h6['families_used']} families, left out: "
          f"{', '.join(h6['families_left_out']) or 'none'}; bootstrap replicates with undefined rho: "
          f"{h6.get('boot_undefined', 0)}.", "",
          "## Secondary models (no family-wise control; rejected = one-sided p at most 0.05; 2,000 replicates)", "",
          "| model | analogue of | set | estimate | 95% interval | lower bound | p | companion | companion lower bound | "
          "rejected | grade |", "|---" * 11 + "|"]
    for r in sec.itertuples():
        comp = f"{r.companion_name} {f3(r.companion)}" if isinstance(r.companion_name, str) else "-"
        L.append(f"| {NAMES[r.model]} | {r.analogue_of} | {r.set} | {r.estimate_name} {f3(r.estimate)} | [{f3(r.lo95)}, "
                 f"{f3(r.hi95)}] | {f3(r.lower_bound)} | {fp(r.p)} | {comp} | {f3(r.companion_lower_bound)} | "
                 f"{'yes' if r.rejected else 'no'} | {r.grade} |")
    # ---------------------------------------------------------------- all pooled estimates per set
    L += ["", "## Pooled estimates per set (sections 7 and 10)", "",
          "Value [95% interval] for every model; 2,000 replicates unless the quantity names 5,000; families left out by "
          "the not-estimable rule in the last column. Full tables: outputs/confirm/<set>/estimates.csv.", ""]
    for s in SETS:
        e = est[s]
        pooled = e[e["unit"].isin(["pooled", "animals", "plants", "families"]) | e["unit"].str.startswith("without ")]
        qs = list(dict.fromkeys(zip(pooled["quantity"], pooled["unit"])))
        L += [f"### {s}", "", "| quantity | unit | " + " | ".join(NAMES[m] for m in MODELS) + " | families left out |",
              "|---" * (len(MODELS) + 3) + "|"]
        for q, u in qs:
            cells, left = [], set()
            for m in MODELS:
                r = pooled[(pooled["model"] == m) & (pooled["quantity"] == q) & (pooled["unit"] == u)]
                cells.append(ci(r.iloc[0]) if len(r) else "-")
                if len(r) and isinstance(r.iloc[0]["families_left_out"], str):
                    left |= {f"{NAMES[m]}: {r.iloc[0]['families_left_out']}"}
            L.append(f"| {q} | {u} | " + " | ".join(cells) + f" | {'; '.join(sorted(left)) or '-'} |")
        L += ["", "Further values (analysis.json): " + "; ".join(
            f"{NAMES[m]}: families with lower bound of Delta above 0 {info[s].get(f'{m}_families_lower_bound_above_0')}, "
            f"tipping point to 0 {f3(info[s].get(f'{m}_tipping_point_to_0'))}, to 1.0 "
            f"{f3(info[s].get(f'{m}_tipping_point_to_1'))}, share of slow errors whose predicted species was proposed "
            f"{f3(info[s].get(f'{m}_share_slow_errors_proposed'))}" for m in MODELS if f"{m}_tipping_point_to_0" in info[s])
            + ".", ""]
    # ---------------------------------------------------------------- per family
    L += ["## Delta and ER per family (heterogeneity; every model)", ""]
    for s in SETS:
        e = est[s]
        fams = info[s]["families"]
        L += [f"### {s}", "", "| family | " + " | ".join(f"{NAMES[m]} Delta | {NAMES[m]} ER" for m in MODELS) + " |",
              "|---" * (2 * len(MODELS) + 1) + "|"]
        for f in fams:
            cells = []
            for m in MODELS:
                for q in ("Delta", "ER"):
                    r = e[(e["model"] == m) & (e["quantity"] == q) & (e["unit"] == f)]
                    cells.append(ci(r.iloc[0]) + (" (not estimable)" if len(r) and r.iloc[0]["status"] == "not estimable" else "")
                                 if len(r) else "-")
            L.append(f"| {f} | " + " | ".join(cells) + " |")
        L.append("")
    # ---------------------------------------------------------------- C3
    L += ["## C3 (BioCLIP 2.5 Huge; estimation only, no family-wise control)", "",
          "| set | b0 | b3 | b_obs | rho | band of rho |", "|---|---|---|---|---|---|"]
    for s in SETS:
        e = est[s]
        row = {q: e[(e["model"] == "Z25") & (e["quantity"] == q) & (e["unit"] == "pooled")] for q in ("b0", "b3", "b_obs", "rho")}
        if all(len(v) for v in row.values()):
            L.append(f"| {s} | " + " | ".join(ci(row[q].iloc[0]) for q in ("b0", "b3", "b_obs", "rho"))
                     + f" | {info[s].get('rho_band', 'n/a')} |")
    L += ["", "The registered C3 is that of the eight families (eight_W; eight_W2 as the second window); the rows of the "
          "other sets are reported because the analysis step computes them for every set.", "",
          f"Covariates of b3: {', '.join(info['eight_W']['b3_covariates'])}; species x 10-degree cell fixed effects. "
          "Missing values (median imputed): " + ", ".join(f"{k} {v}" for k, v in info["eight_W"]["b3_missing_values"].items())
          + f"; rows without an activity stratum: {info['eight_W']['b3_rows_without_activity_stratum']}.", "",
          "Identifier availability (section 7.3, item 5): scale per family (population / sampled observations with a "
          "history) and sources:", ""]
    for s in SETS:
        ia = info[s]["identifier_availability"]
        L.append(f"- {s}: sources {', '.join(ia['sources']) or 'the set only'}; scale "
                 + ", ".join(f"{f} {v['scale']:.1f}" for f, v in ia["families"].items())
                 + f"; rows with a defined identifier experience: {info[s]['ident_experience_rows_defined']:,}.")
    qt = pd.read_csv(OUT / "eight_W/q_tertiles.csv")
    e = est["eight_W"]
    bi = e[(e["model"] == "Z25") & (e["quantity"] == "b_int") & (e["unit"] == "pooled")].iloc[0]
    con = e[(e["model"] == "Z25") & (e["quantity"] == "Delta Q tertile 3 minus tertile 1") & (e["unit"] == "pooled")].iloc[0]
    L += ["", f"Within-family moderation by Q (eight_W; key secondary analysis): rows with Q "
          f"{info['eight_W']['q_rows_with_Q']:,}; b_int pooled {ci(bi)}; contrast Delta(T3) - Delta(T1) {ci(con)}.", "",
          "| tertile | unit | rows | slow rows | weighted share slow | weighted median Q | Delta [95%] | ER [95%] | status |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in qt.itertuples():
        L.append(f"| {r.tertile} | {r.unit} | {r.rows:,} | {r.slow_rows:,} | {f3(r.weighted_share_slow)} | "
                 f"{f3(r.weighted_median_Q)} | {f3(r.Delta)} [{f3(r.Delta_lo95)}, {f3(r.Delta_hi95)}] | {f3(r.ER)} "
                 f"[{f3(r.ER_lo95)}, {f3(r.ER_hi95)}] | {r.status} |")
    L += ["", "Per-family b_int and contrasts: outputs/confirm/eight_W/estimates.csv.", ""]
    # ---------------------------------------------------------------- H6 detail and the 14 families
    L += ["## H6 detail: Delta (BioCLIP 2.5 Huge) and the share of fast observations per family", "",
          f"rho = {f3(h6['rho'])}, permutation p = {fp(h6['p'])}, 95% interval over families [{f3(h6['rho_lo95'])}, "
          f"{f3(h6['rho_hi95'])}].", "", "| family | set | Delta [95%] | fast share |", "|---|---|---|---|"]
    for s in ("new_W", "replication_W"):
        e = est[s]
        for f in info[s]["families"]:
            r = e[(e["model"] == "Z25") & (e["quantity"] == "Delta") & (e["unit"] == f)].iloc[0]
            L.append(f"| {f} | {s} | {ci(r)} | {f3(h6['fast_share'][f])} |")
    rel = jt["relation_across_families"]
    L += ["", "## Eight and six new families together (section 10, heterogeneity; secondary)", "",
          f"Relation across the {rel['families_used']} families between Delta (BioCLIP 2.5 Huge) and the share of fast "
          f"observations: rho = {f3(rel['rho'])}, one-sided permutation p = {fp(rel['p'])}.", "",
          "| quantity | unit | " + " | ".join(NAMES[m] for m in MODELS) + " |", "|---" * (len(MODELS) + 2) + "|"]
    for q, u in [("Delta", "animals"), ("ER", "animals"), ("Delta", "plants"), ("ER", "plants"), ("Delta", "pooled"),
                 ("ER", "pooled"), ("median family Delta", "families"), ("Delta", "Polyporaceae"), ("ER", "Polyporaceae")]:
        cells = []
        for m in MODELS:
            r = ej[(ej["model"] == m) & (ej["quantity"] == q) & (ej["unit"] == u)]
            cells.append(ci(r.iloc[0]) if len(r) else "-")
        L.append(f"| {q} | {u} | " + " | ".join(cells) + " |")
    L += ["", "Full table: outputs/confirm/joint_14/estimates_joint.csv.", ""]
    # ---------------------------------------------------------------- not estimable
    L += ["## Not-estimable listing", ""]
    for s in SETS:
        ne = info[s]["not_estimable"]
        lo = info[s]["pooled_with_families_left_out"]
        L.append(f"- {s}: estimates not estimable: {len(ne)}" + (" (" + "; ".join(f"{NAMES.get(x['model'], x['model'])} "
                 f"{x['quantity']} {x['unit']}" for x in ne) + ")" if ne else "") + f"; pooled estimates with families "
                 f"left out: {len(lo)}" + (" (" + "; ".join(f"{NAMES.get(x['model'], x['model'])} {x['quantity']}: "
                 f"{x['families_left_out']}" for x in lo) + ")" if lo else "") + ".")
    L += [f"- H6: families left out: {', '.join(h6['families_left_out']) or 'none'}.", ""]
    (ROOT / "docs/reports/confirmatory_results.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print(f"written; {len(L)} lines; deviations: {devs}")


if __name__ == "__main__":
    main()
