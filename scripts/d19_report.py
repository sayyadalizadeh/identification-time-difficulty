"""D19 report (post hoc): writes docs/reports/D19_report.md from the outputs of d19_snapshot.py and d19_part_a/b/c.py.

The report states the results of every item with its definition; D19 has no decision rule, so no item is graded.
Run time and bytes written are taken from the logs and the output folders.
"""
import json
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd

import d19_common as C

O = C.OUT
REP = C.ROOT / "docs" / "reports" / "D19_report.md"
MN = C.MODEL_NAMES
SETNAME = {"eight_W": "eight families, W (H1)", "eight_W2": "eight families, W2 (H5)", "new_W": "six new families, W (H2)",
           "replication_W": "30 replication families, W"}


def f3(x, k=3):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return str(x)
    return "n/a" if not np.isfinite(x) else f"{x:,.{k}f}"


def civ(v, lo, hi, k=3):
    return f"{f3(v, k)} [{f3(lo, k)}, {f3(hi, k)}]"


def table(df, cols=None):
    cols = cols or list(df.columns)
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in df[cols].itertuples(index=False):
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def log_minutes(p):
    t = Path(p).read_text(encoding="utf-8")
    m = re.findall(r"\(([\d.]+) min\)", t)
    return float(m[-1]) if m else np.nan


def main():
    L = []
    add = L.append
    A = json.loads((O / "A/A_summary.json").read_text(encoding="utf-8"))
    add("# D19 report - analyses requested by pre-submission reviews (post hoc)")
    add("")
    add("Decision: docs/PLAN.md, D19 (post hoc, 2026-11-23), registration committed before any computation. Every "
        "number in this report is post hoc; the registered confirmatory results (docs/reports/confirmatory_results.md) "
        "stay the primary results. D19 fixes no decision rule, so no item is graded. Data: the stored outputs of the "
        "confirmatory run (outputs/confirm/), the metadata snapshot of 2026-10-27 and the stored photographs of the "
        "earlier gates (development half), each file checked against its SHA-256 manifest in the run that read it; "
        "pinned models only; no download, no API request. Seed 20261124 for every resampling; 20 CPU threads per "
        "numerical step. Primary model: BioCLIP 2.5 Huge. Delta = 100 x (E_slow - E_ref), ER = E_slow / E_ref (frozen "
        "estimator src/confirm/estimators.c1, equal family weights, not-estimable rule); intervals are 95% percentile "
        "intervals of the observer-cluster bootstrap.")
    add("")
    add("Scripts: scripts/d19_common.py, d19_snapshot.py, d19_part_a.py, d19_part_b.py, d19_part_c.py, d19_report.py. "
        "Tables: outputs/D19/A/, B/, C/ and snapshot/ (csv files tracked; parquet files and caches untracked).")
    add("")
    # controls
    add("## Controls (PASS/FAIL)")
    add("")
    rows = []
    for p in ("snapshot/snapshot_log.txt", "A/part_a_log.txt", "B/part_b_log.txt", "C/part_c_log.txt"):
        for ln in (O / p).read_text(encoding="utf-8").splitlines():
            if ln.startswith("CHECK "):
                m_ = re.match(r"(.*): (PASS|FAIL)(.*)$", ln[6:])
                name, res = (m_.group(1), m_.group(2) + m_.group(3)) if m_ else (ln[6:], "")
                rows.append({"log": p, "control": name, "result": res.strip()})
    add(table(pd.DataFrame(rows)))
    add("")

    # ---------------------------------------------------------------- Part A
    add("## Part A - numbers from stored outputs (post hoc)")
    add("")
    a1 = pd.read_csv(O / "A/A1_dropped_slow_weight.csv")
    add("### A1 (post hoc). Share of slow weight dropped because a species lacks a fast or a slow phase-2 observation")
    add("")
    add("Point values recomputed from the stored analysis rows with the frozen estimator (BioCLIP 2.5 Huge; the share does "
        "not depend on the model). Dropped slow weight = weight of slow rows whose species has no fast row, divided by "
        "all slow weight of the family; pooled = mean over families (the stored quantity 'dropped share of slow weight'). "
        "In a bootstrap replicate, a species whose fast rows are not drawn loses its slow weight; the stored interval of "
        "the replicates therefore lies at or above the point value.")
    add("")
    p = a1[a1["family"].str.startswith("pooled")].copy()
    p["stored value [95% interval]"] = [civ(v, lo, hi) for v, lo, hi in zip(p["stored_value"], p["stored_lo95"], p["stored_hi95"])]
    p["recomputed"] = p["dropped_share_of_slow_weight"].map(f3)
    add(table(p.assign(set=p["set"].map(SETNAME)), ["set", "recomputed", "stored value [95% interval]"]))
    add("")
    q = a1[~a1["family"].str.startswith("pooled")].copy()
    q["share"] = q["dropped_share_of_slow_weight"].map(f3)
    for c_ in ("slow_species", "slow_species_without_fast", "fast_species_without_slow", "slow_rows", "slow_rows_dropped"):
        q[c_] = q[c_].astype(int)
    add(table(q, ["set", "family", "share", "slow_species", "slow_species_without_fast", "fast_species_without_slow",
                  "slow_rows", "slow_rows_dropped"]))
    add("")
    a2 = pd.read_csv(O / "A/A2_pooled_errors.csv")
    add("### A2 (post hoc). Pooled E_slow and E_ref beside Delta and ER, and the raw error rates")
    add("")
    add("E_slow and E_ref are means over the estimable families; Delta = 100 x (E_slow - E_ref) and ER = E_slow / E_ref. "
        "Raw rates: error of all fast (T < 1 day) and all slow (T >= 1 day) research-grade rows, weighted by the phase-2 "
        "weights and pooled over the families of the set (equal-family means in the last two columns).")
    add("")
    add("Why Delta and ER differ from the raw contrast: E_ref is the fast error of the same species, weighted by each "
        "species' share of the slow weight, and families count equally, whereas the raw contrast compares all fast with all "
        "slow rows, so it mixes species and families of different difficulty and different shares of slow observations.")
    add("")
    t = a2.copy()
    t["set"] = t["set"].map(SETNAME)
    t["model"] = t["model"].map(MN)
    for c_ in ("E_slow_pooled", "E_ref_pooled", "raw_fast_error_weighted", "raw_slow_error_weighted",
               "raw_fast_error_equal_family", "raw_slow_error_equal_family", "ER", "raw_ratio"):
        t[c_] = t[c_].map(lambda x: f3(x, 4))
    t["Delta"] = t["Delta"].map(f3)
    t["raw_difference_points"] = t["raw_difference_points"].map(f3)
    add(table(t, ["set", "model", "E_slow_pooled", "E_ref_pooled", "Delta", "ER", "raw_fast_error_weighted",
                  "raw_slow_error_weighted", "raw_difference_points", "raw_ratio", "raw_fast_error_equal_family",
                  "raw_slow_error_equal_family"]))
    add("")
    a3 = pd.read_csv(O / "A/A3_tipping_points.csv")
    add("### A3 (post hoc). Tipping points and the lower bounds of the table of H1 to H6")
    add("")
    add("The tipping points of the run (analysis.json) are computed from the one-sided 95% lower bound (5th percentile) of "
        "Delta in the 2,000-replicate bootstrap of the analyse step: tipping point to 0 = lower bound / 100, to 1.0 = "
        "(lower bound - 1.0) / 100 (src/confirm/analysis.py, lines 141 to 144). The lower bounds of the hypothesis table "
        "(H1, H2, H5) come from the separate 5,000-replicate bootstrap; the tipping points that these bounds imply are "
        "given beside them. The manuscript itself was not read: the table of H1 to H6 is taken from "
        "docs/reports/confirmatory_results.md.")
    add("")
    t = a3.copy()
    t["set"] = t["set"].map(SETNAME)
    t["model"] = t["model"].map(MN)
    for c_ in t.columns:
        if t[c_].dtype.kind == "f":
            t[c_] = t[c_].map(lambda x: f3(x, 4))
    add(table(t.fillna("-").replace("n/a", "-")))
    add("")
    a4 = A["A4"]
    add("### A4 (post hoc). Spearman correlation over the 14 families of H1 and H2")
    add("")
    add(table(pd.DataFrame([{"rho": f3(a4["rho_stored"], 4), "families": a4["families_used"], "permutations": a4["n_perm"],
                             "P-value (stored)": f3(a4["p_stored"], 5), "sidedness": a4["sidedness"],
                             "two-sided P (D19, seed 20261124)": f3(a4["p_two_sided_D19"], 5)}])))
    add("")
    add("Source: outputs/confirm/joint_14/joint.json (relation_across_families; BioCLIP 2.5 Huge Delta of the joint analysis "
        "of eight_W and new_W against the fast share of each family). The smallest attainable P with 10,000 permutations "
        "is 1/10,001 = 0.0001. Code:")
    add("")
    add("```")
    add("\n".join(a4["code"]))
    add("```")
    add("")
    a5 = pd.read_csv(O / "A/A5_L_shares.csv")
    add("### A5 (post hoc). Exact shares behind L(S*)")
    add("")
    t = a5.copy()
    t["set"] = t["set"].map(SETNAME)
    t["share"] = t["share"].map(lambda x: f"{x:.6f}")
    t["percent (three decimals)"] = t["percent_3_decimals"].map(lambda x: f"{x:.3f}%")
    t["95% interval (share)"] = [f"[{a:.6f}, {b:.6f}]" for a, b in zip(a5["lo95"], a5["hi95"])]
    add(table(t, ["set", "quantity", "share", "percent (three decimals)", "95% interval (share)"]))
    add("")
    add("L = L_upload + L_ident (12.543% = 4.775% + 7.768% in W; small differences come from rounding).")
    add("")
    a6 = A["A6"]
    add("### A6 (post hoc). Resampling unit of the observer-cluster bootstrap")
    add("")
    add("An observer is drawn once per replicate for the whole analysed set (all families and strata of one window): the "
        "multiplicity of each observer multiplies the weights of all of that observer's rows in the set. It is not "
        "resampled within each family. Each set (window) is analysed in its own call with its own bootstrap, so the "
        "draws of an observer who appears in eight_W and in eight_W2 are independent; in the joint analysis of the 14 "
        "families (analyse-joint) the rows of eight_W and new_W are pooled and each observer is drawn once over both.")
    add("")
    add("```")
    add("\n".join(a6["code"]))
    add("```")
    add("")
    add(table(pd.DataFrame([{"set": SETNAME[k], "observers": v, "observers with rows in more than one family":
                             a6["observers_with_rows_in_more_than_one_family"][k]} for k, v in a6["observers_per_set"].items()])))
    add("")
    add(f"Observers in both eight_W and eight_W2: {a6['observers_in_both_eight_W_and_eight_W2']:,}; in both eight_W and "
        f"new_W: {a6['observers_in_both_eight_W_and_new_W']:,}.")
    add("")
    add("### A7 (post hoc). Failure rates by family and stratum")
    add("")
    h = pd.read_csv(O / "A/A7_history_failures.csv")
    ph = pd.read_csv(O / "A/A7_photo_failures.csv")
    add("Histories: a failed history has no stratum (the stratum needs the history), so history failures are given by "
        "family and snapshot grade; photographs: by family and stratum. Full tables: outputs/D19/A/A7_history_failures.csv "
        "and A7_photo_failures.csv. Summary per set:")
    add("")
    srows = []
    for s in C.SETS:
        hh, pp = h[h["set"] == s], ph[ph["set"] == s]
        hm = hh.groupby("family")[["phase1", "history_failed"]].sum()
        hmax = (hm["history_failed"] / hm["phase1"])
        pmax = pp.loc[pp["failed_share"].idxmax()]
        srows.append({"set": SETNAME[s], "history failures": f"{int(hh['history_failed'].sum()):,} of {int(hh['phase1'].sum()):,} "
                      f"({hh['history_failed'].sum() / hh['phase1'].sum():.4f})",
                      "largest family rate (histories)": f"{hmax.idxmax()} {hmax.max():.4f}",
                      "T undefined": int(hh["T_undefined"].sum()),
                      "photograph failures": f"{int(pp['failed'].sum())} of {int(pp['selected'].sum()):,} "
                      f"({pp['failed'].sum() / pp['selected'].sum():.5f})",
                      "largest family x stratum rate (photographs)": f"{pmax['family']} {pmax['stratum']} {pmax['failed_share']:.4f} "
                      f"({int(pmax['failed'])} of {int(pmax['selected'])})",
                      "family x stratum cells with a photograph failure": int((pp["failed"] > 0).sum())})
    add(table(pd.DataFrame(srows)))
    add("")
    hh = h[h["history_failed"] > 0].copy()
    hh["share"] = hh["history_failed_share"].map(lambda x: f"{x:.4f}")
    add("Family x grade cells with a history failure:")
    add("")
    add(table(hh, ["set", "family", "grade", "phase1", "history_failed", "share"]))
    add("")
    pp = ph[ph["failed"] > 0].copy()
    pp["share"] = pp["failed_share"].map(lambda x: f"{x:.4f}")
    add("Family x stratum cells with a photograph failure:")
    add("")
    add(table(pp, ["set", "family", "stratum", "selected", "ok", "failed", "share"]))
    add("")
    add("### A8 (post hoc). Input resolution, resize, crop and normalisation of each model (loaded configurations)")
    add("")
    a8 = json.loads((O / "A/A8_preprocessing.json").read_text(encoding="utf-8"))
    r8 = []
    for k, v in a8.items():
        if k.startswith("DINOv2"):
            pc = v["processor_config"]
            r8.append({"model": k, "image transform as loaded": f"{v['processor']}: resize shortest edge {pc.get('size')}, "
                       f"resample {pc.get('resample')} (bicubic), centre crop {pc.get('crop_size')}, rescale 1/255, normalise "
                       f"mean {pc.get('image_mean')} std {pc.get('image_std')}", "logit scale": "-"})
        else:
            tr_ = re.sub(r"\s+", " ", v["transform"].replace("|", " ")).strip()
            if tr_.startswith("Compose(") and tr_.endswith(")"):
                tr_ = tr_[len("Compose("):-1].strip()
            tr_ = re.sub(r"\) (?=[A-Z])", "); ", tr_)
            r8.append({"model": MN.get(k, k), "image transform as loaded": tr_, "logit scale": f3(v["logit_scale"], 2)})
    add(table(pd.DataFrame(r8)))
    add("")
    add("All CLIP-type models receive the photograph after EXIF orientation and conversion to RGB (src/zeroshot.open_rgb); "
        "one centred view; image encoding under float16 autocast.")
    add("")
    a9 = pd.read_csv(O / "A/A9_family_errors.csv")
    add("### A9 (post hoc). Per family and set: label space, species retained, fast, slow and reference errors, Delta and ER")
    add("")
    add("Label-space size = eligible species of the family; species retained = species with at least one fast and one slow "
        "row (they define E_slow and E_ref); fast error = weighted error of all fast rows of the family; E_slow, E_ref as "
        "in A2. Delta and ER with the stored 95% intervals (2,000 replicates). Families covered: the three BioCLIP models "
        "have predictions for every family of every set; BT-CLIP-O also has predictions for every family, and the "
        "registered plan lists Sciuridae (Mammalia) and Ranidae (Amphibia) as outside its training data (sensitivity "
        "'without Sciuridae' in the W sets of the eight families and 'without Ranidae' in new_W).")
    add("")
    t = a9.copy()
    t["model"] = t["model"].map(MN)
    t["fast error"] = t["fast_error_all_fast_rows"].map(lambda x: f3(x, 4))
    t["E_slow"] = t["E_slow"].map(lambda x: f3(x, 4))
    t["E_ref"] = t["E_ref"].map(lambda x: f3(x, 4))
    t["Delta [95%]"] = [civ(v, lo, hi, 2) for v, lo, hi in zip(a9["Delta"], a9["Delta_lo95"], a9["Delta_hi95"])]
    t["ER [95%]"] = [civ(v, lo, hi, 3) for v, lo, hi in zip(a9["ER"], a9["ER_lo95"], a9["ER_hi95"])]
    for s in C.SETS:
        add(f"{SETNAME[s]}:")
        add("")
        add(table(t[t["set"] == s], ["family", "model", "label_space_species", "species_retained", "fast_rows", "slow_rows",
                                     "fast error", "E_slow", "E_ref", "Delta [95%]", "ER [95%]"]))
        add("")
    add("### A10 (post hoc). Flow counts for window W per family set")
    add("")
    fl = pd.read_csv(O / "snapshot/a10_flow.csv")
    add("From the snapshot of 2026-10-27 (observations with observed_on from 2024-07-01 to 2024-09-30 and a valid observer "
        "id). Stages are cumulative up to 'licence and size filter' (first photograph CC0, CC BY or CC BY-NC, shorter side "
        "at least 224 px, every photo id above 367,752,438); the grade columns split the rows that pass the filter. The "
        "confirmatory frames are 'research_eligible' + 'needs_id_eligible' of the locked half (eight families) and of both "
        "halves (new families); 'needs_id_eligible' does not enter the replication frame (research grade only). Per family: "
        "outputs/D19/snapshot/a10_flow.csv.")
    add("")
    cols = ["all_in_W", "with_photo", "all_photo_ids_above_max_M1", "licence_and_size_filter", "eligible_species_any_grade",
            "research_eligible", "research_other", "needs_id_eligible", "needs_id_other", "casual", "other_grade"]
    g = fl.groupby(["set", "half"])[cols].sum().reset_index()
    g = g[((g["set"] == "eight") & g["half"].isin(["locked", "both"])) | ((g["set"] != "eight") & (g["half"] == "both"))]
    for c_ in cols:
        g[c_] = g[c_].map(lambda x: f"{int(x):,}")
    add(table(g, ["set", "half"] + cols))
    add("")
    add("### A11 (post hoc). C3 coefficients b0, b3 and b_obs (BioCLIP 2.5 Huge)")
    add("")
    a11 = pd.read_csv(O / "A/A11_c3_coefficients.csv")
    t = a11.copy()
    t["set"] = t["set"].map(SETNAME)
    t["value [95%]"] = [civ(v, lo, hi) for v, lo, hi in zip(a11["value"], a11["lo95"], a11["hi95"])]
    add(table(t, ["set", "quantity", "value [95%]"]))
    add("")
    add("b0: species fixed effects; b3: species x 10-degree cell fixed effects and the covariates "
        f"{', '.join(A['A11_b3_covariates']['eight_W'])}; b_obs: species and observer fixed effects; rho = b3 / b0 "
        "(2,000 replicates; slow minus fast in points).")
    add("")
    a12 = A["A12"]
    add("### A12 (post hoc). Fields of the retained provenance file of TreeOfLife-200M (commit 97e2340)")
    add("")
    add(f"File outputs/retained/tol200m_97e2340/provenance.parquet: SHA-256 equal to the value recorded in D17: "
        f"{'yes' if a12['sha256_equal_to_D17'] else 'no'}; {a12['rows']:,} rows in {a12['row_groups']} row groups; "
        f"key-value metadata keys: {', '.join(a12['key_value_metadata_keys'])}.")
    add("")
    sc = a12["first_row_group_date_pattern_scan"]
    add(table(pd.DataFrame([{"field": f["name"], "type": f["type"],
                             "values with a YYYY-MM-DD string in row group 1": f"{sc[f['name']]['values_with_a_YYYY-MM-DD_string']:,} of "
                             f"{sc[f['name']]['non_null']:,}"} for f in a12["fields"]])))
    add("")
    add("No field has a date or time type and no field name refers to a date, so the file holds no date of the record or "
        "of the image, and no latest date per source can be given. Some free-text values (URLs, owner strings, citations) "
        f"contain a date-like string; only row group 1 ({a12['first_row_group_rows']:,} rows; sources "
        f"{', '.join(f'{k} {v:,}' for k, v in a12['first_row_group_sources'].items())}) was scanned for this count.")
    add("")

    # ---------------------------------------------------------------- Part B
    add("## Part B - light analyses (post hoc)")
    add("")
    add("Definitions: scripts/d19_part_b.py (docstring). Sets eight_W (H1), eight_W2 (H5), new_W (H2); observer-cluster "
        "bootstrap with 2,000 replicates (seed 20261124; one weight matrix per set, shared by all contrasts of the set). "
        "Rows 'main' reproduce the registered point estimates (control above); their intervals differ slightly from the "
        "registered ones because the replicates differ. Polyporaceae belongs to neither group. Secondary models: pooled "
        "values in the second table of each item; all units in outputs/D19/B/B_contrasts.csv.")
    add("")
    bc = pd.read_csv(O / "B/B_contrasts.csv")
    shr = pd.read_csv(O / "B/B_shares.csv")

    def btab(items, title, extra=None):
        add(title)
        add("")
        if extra:
            add(extra)
            add("")
        z = bc[bc["item"].isin(items) & (bc["model"] == "Z25")]
        rr = []
        for (cn, s), g_ in z.groupby(["contrast", "set"], sort=False):
            r_ = {"contrast": cn, "set": SETNAME[s]}
            for _, x in g_.iterrows():
                r_[f"Delta {x['unit']}"] = civ(x["Delta"], x["Delta_lo95"], x["Delta_hi95"], 2)
                r_[f"ER {x['unit']}"] = civ(x["ER"], x["ER_lo95"], x["ER_hi95"], 3)
            x0 = g_.iloc[0]
            r_["slow rows"] = int(x0["slow_rows"])
            r_["fast rows"] = int(x0["fast_rows"])
            if "slow_weight_share_of_all_slow" in x0 and np.isfinite(x0["slow_weight_share_of_all_slow"]):
                r_["share of slow weight"] = f3(x0["slow_weight_share_of_all_slow"])
                r_["share of fast weight"] = f3(x0["fast_weight_share_of_all_fast"])
            left = ";".join(sorted(set(";".join(g_["families_left_out"].fillna("")).split(";")) - {""}))
            r_["families left out"] = left or "-"
            rr.append(r_)
        tb = pd.DataFrame(rr).fillna("-")
        add("Primary model (BioCLIP 2.5 Huge):")
        add("")
        add(table(tb))
        add("")
        z2 = bc[bc["item"].isin(items) & (bc["model"] != "Z25") & (bc["unit"] == "pooled")]
        if len(z2):
            rr = []
            for (cn, s), g_ in z2.groupby(["contrast", "set"], sort=False):
                r_ = {"contrast": cn, "set": SETNAME[s]}
                for _, x in g_.iterrows():
                    r_[f"{MN[x['model']]} Delta"] = civ(x["Delta"], x["Delta_lo95"], x["Delta_hi95"], 2)
                    r_[f"{MN[x['model']]} ER"] = civ(x["ER"], x["ER_lo95"], x["ER_hi95"], 3)
                rr.append(r_)
            add("Secondary models (pooled):")
            add("")
            add(table(pd.DataFrame(rr)))
            add("")

    def stab(names):
        z = shr[shr["share"].isin(names)].copy()
        z["value"] = z["weighted_share"].map(lambda x: f3(x, 4))
        z["set"] = z["set"].map(SETNAME)
        add(table(z, ["set", "share", "within", "value", "rows", "rows_within"]))
        add("")

    btab(["main"], "### Reference: the registered contrast recomputed with the D19 bootstrap (post hoc)")
    btab(["B1"], "### B1 (post hoc). Decomposition of T: looked at early against waited",
         "T_wait = days from creation to the first identification by another user; T_res = T - T_wait. Shares are of the "
         "slow weight (phase-2 weights, pooled over the families of the set); weighted medians below.")
    stab(["T_wait < 1 day", "T_wait >= 1 day", "weighted median T_wait (days), slow looked at early",
          "weighted median T_res (days), slow looked at early", "weighted median T_wait (days), slow waited",
          "weighted median T_res (days), slow waited"])
    btab(["B2"], "### B2 (post hoc). Observer's own identification at creation",
         "Category of the observer's earliest identification if created within one hour of the observation (none, above "
         "species rank, species rank); fast and slow rows of the same category are compared.")
    stab([f"own identification at creation: {c_}" for c_ in ("none", "above species rank", "species rank")] +
         ["observer's earliest identification later than 1 h after creation"])
    btab(["B3"], "### B3 (post hoc). Vision assistance",
         "Shares of fast and slow observations with a vision-assisted identification up to the research-grade time, and "
         "with any vision-assisted identification; contrasts within observations without one.")
    stab(["vision-assisted identification up to research grade", "any vision-assisted identification"])
    btab(["B4"], "### B4 (post hoc). Observations with a single photograph only")
    stab(["one photograph only"])
    btab(["B5"], "### B5 (post hoc). Reconstruction checks: withdrawn and non-ancestor identifications")
    stab(["any withdrawn identification", "any non-ancestor identification above species rank"])
    btab(["B6"], "### B6 (post hoc). Threshold sensitivity and within-family quantile contrast")
    b7 = pd.read_csv(O / "B/B7_random_effects.csv")
    add("### B7 (post hoc). Random-effects summary over the 14 families of W and meta-regression of H6")
    add("")
    add("Family values: BioCLIP 2.5 Huge Delta and log ER of eight_W and new_W (outputs/confirm/<set>/estimates.csv). The "
        "bootstrap replicates were not kept, so each family variance is ((upper - lower) / 3.92) squared from the stored "
        "95% interval (on the log scale for ER). REML; 95% confidence interval mu +/- 1.96 SE; 95% prediction interval for "
        "a new family mu +/- t(k - 2) x sqrt(tau^2 + SE^2) (with the class variance added in the class model). Classes "
        "from the snapshot taxonomy (outputs/D19/snapshot/families_taxonomy.csv).")
    add("")
    t = b7.copy()
    t["estimate [95% CI]"] = [civ(a, b, c_) for a, b, c_ in zip(t["estimate"], t["lo95"], t["hi95"])]
    t["prediction interval"] = [f"[{f3(a)}, {f3(b)}]" for a, b in zip(t["prediction_lo95"], t["prediction_hi95"])]
    t["on the ER scale"] = [f"{f3(a)} [{f3(b)}, {f3(c_)}]; PI [{f3(d_)}, {f3(e_)}]" if q_.startswith("log") else "-"
                            for q_, a, b, c_, d_, e_ in zip(t["quantity"], t.get("ER", np.nan), t.get("lo95_ER", np.nan),
                                                            t.get("hi95_ER", np.nan), t.get("prediction_lo95_ER", np.nan),
                                                            t.get("prediction_hi95_ER", np.nan))]
    t["tau family"] = t["tau_family"].map(f3)
    t["tau class"] = t["tau_class"].map(f3)
    t["I2"] = t["I2"].map(f3)
    add(table(t, ["quantity", "families", "estimate [95% CI]", "tau family", "tau class", "prediction interval",
                  "on the ER scale", "I2"]))
    add("")
    mr = pd.read_csv(O / "B/B7_h6_meta_regression.csv")
    t = mr.copy()
    t["slope [95% CI]"] = [civ(a, b, c_) for a, b, c_ in zip(t["slope_per_unit_fast_share"], t["lo95"], t["hi95"])]
    t["p (two-sided)"] = t["p_two_sided"].map(lambda x: f3(x, 4))
    t["tau family"] = t["tau_family"].map(f3)
    t["tau class"] = t["tau_class"].map(f3)
    add("H6 meta-regression over the 36 families (Delta in points per unit of fast share; precision weights from the "
        "interval widths):")
    add("")
    add(table(t, ["model", "slope [95% CI]", "p (two-sided)", "tau family", "tau class"]))
    add("")
    lo = pd.read_csv(O / "B/B7_h6_leave_one_class_out.csv")
    lo["rho"] = lo["rho"].map(lambda x: f3(x, 3))
    lo["p (one-sided, 10,000 permutations)"] = lo["p_one_sided"].map(lambda x: f3(x, 4))
    add("Spearman rho of H6 leaving out one class at a time (registered value over 36 families: 0.574):")
    add("")
    add(table(lo, ["class_left_out", "families_left_out", "families_used", "rho", "p (one-sided, 10,000 permutations)"]))
    add("")
    b8 = pd.read_csv(O / "B/B8_resolvers.csv")
    add("### B8 (post hoc). Resolving identifiers")
    add("")
    t = b8.copy()
    t["set"] = t["set"].map(SETNAME)
    t["share A2+A3 by top 10"] = t["share_A2_A3_resolved_by_top10"].map(lambda x: f3(x, 4))
    t["share of all research rows by these 10"] = t["share_all_research_resolved_by_top10_of_A2_A3"].map(lambda x: f3(x, 4))
    add(table(t, ["set", "A2_A3_rows", "resolving_identifiers_A2_A3", "share A2+A3 by top 10", "top10_counts",
                  "share of all research rows by these 10", "resolving_identifiers_all_research",
                  "max_resolved_by_one_identifier_on_one_day_all_research", "max_resolved_by_one_identifier_on_one_day_A2_A3",
                  "resolver_is_observer_rows"]))
    add("")
    add("Counts are phase-2 analysis rows (not weighted); the ten most active resolving identifiers are those with the most "
        "A2 and A3 rows in the set; one day = UTC date of the resolving identification.")
    add("")
    btab(["B8"], "Delta with the two-way cluster bootstrap (observer and resolving identifier, pigeonhole resampling, "
                 "2,000 replicates):")
    btab(["B9"], "### B9 (post hoc). Prior exposure of the observer to the species",
         "Exposure = a research-grade observation of the same species by the same observer observed before 2024-05-01 in "
         "the snapshot (pairs: outputs/D19/snapshot, not tracked).")
    stab(["prior exposure"])
    add("### B10 (post hoc). Model scores")
    add("")
    add("The confirmatory run stored only the top-1 species of each model (outputs/confirm/<set>/predictions.parquet has "
        "the columns p_, c_ and g_ per model); probabilities or logits are not stored, so B10 cannot be computed from "
        "stored outputs.")
    b10 = O / "C/B10_supplement.json"
    if b10.exists():
        s10 = json.loads(b10.read_text(encoding="utf-8"))
        add("")
        add(f"Supplement from the recomputed baseline of Part C (eight_W, BioCLIP 2.5 Huge, registered label spaces and texts; "
            f"top-1 probability = softmax of the logit scale times the cosine similarities): within-species Spearman "
            f"correlation between log(1 + T) and the top-1 probability {civ(s10['rho_within_species'], s10['lo95'], s10['hi95'], 4)} "
            f"over {s10['rows']:,} research-grade rows of {s10['species']:,} species ({s10['definition']}; "
            f"{s10['replicates']:,} observer-cluster replicates).")
    add("")
    b11 = pd.read_csv(O / "B/B11_ranks.csv")
    add("### B11 (post hoc). Rank agreement among the four models (eight_W)")
    add("")
    kw = b11[b11["model"] == "all"]
    b11 = b11[b11["model"] != "all"]
    t = b11.pivot(index="model", columns="stratum", values="accuracy_equal_family_mean").loc[C.MODELS]
    rk = b11.pivot(index="model", columns="stratum", values="rank").loc[C.MODELS]
    tt = pd.DataFrame({"model": [MN[m] for m in C.MODELS]})
    for stv in ("A0", "A1", "A2", "A3"):
        tt[f"{stv} accuracy (rank)"] = [f"{t.loc[m, stv]:.4f} ({int(rk.loc[m, stv])})" for m in C.MODELS]
    add(table(tt))
    add("")
    add(f"Accuracy of research-grade rows of the stratum, mean over the eight families. Kendall's W of the model ranks over "
        f"the four strata: {f3(kw['rank'].iloc[0], 3)} (1 = identical ranking in every stratum).")
    add("")

    # ---------------------------------------------------------------- Part C
    add("## Part C - GPU analyses (post hoc; window W, eight families, locked half, stored photographs)")
    add("")
    cr = pd.read_csv(O / "C/C_results.csv")
    ct = cr[cr["unit"].isin(["pooled", "animals", "plants"])].copy()
    ct["accuracy [95%]"] = [civ(a, b, c_, 4) for a, b, c_ in zip(ct["accuracy"], ct["accuracy_lo95"], ct["accuracy_hi95"])]
    ct["Delta [95%]"] = [civ(a, b, c_, 2) for a, b, c_ in zip(ct["Delta"], ct["Delta_lo95"], ct["Delta_hi95"])]
    ct["ER [95%]"] = [civ(a, b, c_, 3) for a, b, c_ in zip(ct["ER"], ct["ER_lo95"], ct["ER_hi95"])]
    add("Accuracy = weighted accuracy of research-grade rows (phase-2 weights), mean over families; Delta and ER as above; "
        "one observer-cluster bootstrap (2,000 replicates, seed 20261124) for all variants. Definitions: "
        "scripts/d19_part_c.py (docstring). Per-family values: outputs/D19/C/C_results.csv.")
    add("")
    for lab, vs in (("### C1 (post hoc). Larger label space (all eligible species of the same kingdom over the eight families)",
                     ["stored Z25 (registered)", "baseline recomputed", "C1 kingdom label space"]),
                    ("### C2 (post hoc). Preprocessing (letterbox) and species text (species name only)",
                     ["stored Z25 (registered)", "C2a letterbox", "C2b species name only"]),
                    ("### C3 (post hoc). Independent model: DINOv2-base embeddings with a logistic-regression probe per family",
                     ["stored Z25 (registered)", "C3 DINOv2-base probe"])):
        add(lab)
        add("")
        add(table(ct[ct["variant"].isin(vs)], ["variant", "unit", "accuracy [95%]", "Delta [95%]", "ER [95%]"]))
        add("")
    add("Label-space sizes (registered family spaces and kingdom spaces): see outputs/D19/C/part_c_log.txt.")
    add("")
    tr = pd.read_csv(O / "C/C3_training.csv")
    tr["cv_accuracy_chosen"] = tr["cv_accuracy_chosen"].map(lambda x: f3(x, 4))
    flow = json.loads((O / "C/C3_training_flow.json").read_text(encoding="utf-8"))
    add("C3 training data (development half, photographs of the earlier gates):")
    add("")
    add(table(pd.DataFrame([{"step": k, "rows": f"{v:,}"} for k, v in flow.items()])))
    add("")
    add(table(tr))
    add("")
    # run time and bytes
    add("## Run time and bytes written")
    add("")
    mins = {p: log_minutes(O / p) for p in ("snapshot/snapshot_log.txt", "A/part_a_log.txt", "B/part_b_log.txt", "C/part_c_log.txt")}
    rt = [{"step": k, "minutes": f3(v, 1), "note": "completed"} for k, v in mins.items()]
    # runs that stopped on a coding error (outputs kept; the scripts were corrected and run again)
    for lab, p, note in (("B/part_b_log.txt, first run", O / "part_b_stdout_run1_error.txt",
                          "stopped: missing resolver read as NaN (fixed; rerun)"),
                         ("C/part_c_log.txt, first run", O / "part_c_stdout_run1_error.txt",
                          "stopped: a training photograph stored as .gif was not found by the file lookup (fixed; rerun "
                          "with the cached embeddings of the first run)")):
        if p.exists():
            m0 = re.search(r"started (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)", p.read_text(encoding="utf-8"))
            t0 = time.mktime(time.strptime(m0.group(1), "%Y-%m-%d %H:%M:%S")) if m0 else np.nan
            rt.append({"step": lab, "minutes": f3((p.stat().st_mtime - t0) / 60, 1), "note": note})
    add(table(pd.DataFrame(rt)))
    add("")
    t_start = time.mktime(time.strptime("2026-11-23 20:19:15", "%Y-%m-%d %H:%M:%S"))
    add("The task started at 2026-11-23 20:19 (Step 0); the registration of D19 was committed before any computation. "
        "Parts B and C ran in parallel with each other (CPU and GPU). Wall time from Step 0 to this report: "
        f"{(time.time() - t_start) / 60:.0f} minutes (limit 6 hours).")
    add("")
    tot = sum(f.stat().st_size for f in O.rglob("*") if f.is_file())
    cache = sum(f.stat().st_size for f in (O / "cache").rglob("*") if f.is_file()) if (O / "cache").exists() else 0
    add(f"Bytes written under outputs/D19/: {tot:,} (of which embedding caches {cache:,}); this report and the scripts are "
        f"listed in the commit. Report written {time.strftime('%Y-%m-%d %H:%M')}.")
    add("")
    REP.write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("written", REP, len(L), "lines")


if __name__ == "__main__":
    main()
