"""Decisions of the confirmatory plan, draft 3 (sections 8 and 9): Holm's procedure over H1 to H6 at one-sided
alpha = 0.05 and the grading of each hypothesis; the same grading for the secondary models without family-wise
control (section 6: 'the same grading as the primary model'; section 8: no family-wise control).

Inputs (all from the outputs of the analyse and h6 steps):
- H1 (eight families, window W), H2 (six new families, window W) and H5 (eight families, window W2): pooled Delta and
  ER of BioCLIP 2.5 Huge with 5,000 replicates (quantities 'Delta (5000 replicates)' and 'ER (5000 replicates)');
- H3: O and R at S* with 5,000 replicates (eight families, window W); H4: G_sup at S* with 5,000 replicates;
- H6: the permutation p-value of the Spearman correlation over the 36 independent families (h6.json).
p-values: one-sided, the share of replicates at or below 0 (H1 to H5) and the permutation p-value (H6). Bounds are the
one-sided 95% bounds (5th and 95th percentiles). Minimum effects: 1.0 point and 1.15 (section 9).
"""
import numpy as np
import pandas as pd

from src.confirm import estimators as E

C1_HYP = {"H1": "eight_W", "H2": "new_W", "H5": "eight_W2"}


def _row(est, model, quantity, unit="pooled"):
    r = est[(est["model"] == model) & (est["quantity"] == quantity) & (est["unit"] == unit)]
    if len(r) != 1:
        raise RuntimeError(f"expected one row for {model} / {quantity} / {unit}, found {len(r)}")
    return r.iloc[0]


def primary_rows(est_by_part, h6, model="Z25", rep_label="5000 replicates", s_star_label=""):
    """One row per hypothesis with estimate, 95% interval, one-sided bounds, p-value and the companion scale."""
    rows = []
    for h, part in C1_HYP.items():
        d = _row(est_by_part[part], model, f"Delta ({rep_label})")
        er = _row(est_by_part[part], model, f"ER ({rep_label})")
        rows.append({"hypothesis": h, "set": part, "estimate_name": "Delta", "estimate": d.value, "lo95": d.lo95,
                     "hi95": d.hi95, "lower_bound": d.lo_one_sided, "upper_bound": d.hi_one_sided, "p": d.p_one_sided,
                     "companion_name": "ER", "companion": er.value, "companion_lo95": er.lo95,
                     "companion_hi95": er.hi95, "companion_lower_bound": er.lo_one_sided,
                     "companion_upper_bound": er.hi_one_sided,
                     "families_left_out": d.get("families_left_out", "")})
    o = _row(est_by_part["eight_W"], model, f"O{s_star_label} ({rep_label})")
    r = _row(est_by_part["eight_W"], model, f"R{s_star_label} ({rep_label})")
    rows.append({"hypothesis": "H3", "set": "eight_W", "estimate_name": "O", "estimate": o.value, "lo95": o.lo95,
                 "hi95": o.hi95, "lower_bound": o.lo_one_sided, "upper_bound": o.hi_one_sided, "p": o.p_one_sided,
                 "companion_name": "R", "companion": r.value, "companion_lo95": r.lo95, "companion_hi95": r.hi95,
                 "companion_lower_bound": r.lo_one_sided, "companion_upper_bound": r.hi_one_sided,
                 "families_left_out": o.get("families_left_out", "")})
    g = _row(est_by_part["eight_W"], model, f"G_sup{s_star_label} ({rep_label})")
    rows.append({"hypothesis": "H4", "set": "eight_W", "estimate_name": "G_sup", "estimate": g.value, "lo95": g.lo95,
                 "hi95": g.hi95, "lower_bound": g.lo_one_sided, "upper_bound": g.hi_one_sided, "p": g.p_one_sided,
                 "families_left_out": g.get("families_left_out", "")})
    rows.append({"hypothesis": "H6", "set": "new_W + replication_W", "estimate_name": "rho", "estimate": h6["rho"],
                 "lo95": h6.get("rho_lo95", np.nan), "hi95": h6.get("rho_hi95", np.nan), "p": h6["p"],
                 "families_left_out": ";".join(h6.get("families_left_out", []))})
    return pd.DataFrame(rows)


def grade(row, rejected, min_pts=1.0, min_ratio=1.15):
    h = row["hypothesis"]
    if h in ("H1", "H2", "H5"):
        return E.grade_c1(rejected, row["lower_bound"], row["upper_bound"], row["companion_lower_bound"],
                          row["companion_upper_bound"], min_pts, min_ratio)
    if h == "H3":
        return E.grade_h3(rejected, row["lower_bound"], row["upper_bound"], row["companion_lower_bound"],
                          row["companion_upper_bound"], min_pts, min_ratio)
    return E.grade_h4(rejected)  # H4 and H6: shown / not shown


def decide(tab, alpha=0.05):
    """Holm over the hypotheses of tab (one-sided p-values); adds the Holm order, threshold, decision and grade. A
    hypothesis whose p-value is not finite is not rejected and is listed (it cannot be tested)."""
    tab = tab.copy()
    p = {h: (float(v) if np.isfinite(v) else 1.0) for h, v in zip(tab["hypothesis"], tab["p"])}
    hm = E.holm(p, alpha)
    order = sorted(p, key=lambda k: (p[k], k))
    tab["holm_order"] = [order.index(h) + 1 for h in tab["hypothesis"]]
    tab["holm_threshold"] = [hm[h][0] for h in tab["hypothesis"]]
    tab["rejected"] = [bool(hm[h][1]) and np.isfinite(v) for h, v in zip(tab["hypothesis"], tab["p"])]
    tab["grade"] = [grade(r, r["rejected"]) for _, r in tab.iterrows()]
    tab["control"] = "Holm over H1 to H6, one-sided 0.05"
    return tab.sort_values("holm_order").reset_index(drop=True)


def secondary(est_by_part, models, s_star_label="", alpha=0.05):
    """Secondary models: the analogues of H1 to H5 with the same grading; 'rejected' means one-sided p <= alpha
    without family-wise control (2,000 replicates, the count of all non-hypothesis estimates)."""
    rows = []
    for m in models:
        for h, part in C1_HYP.items():
            if part not in est_by_part:
                continue
            d, er = _row(est_by_part[part], m, "Delta"), _row(est_by_part[part], m, "ER")
            rows.append({"model": m, "analogue_of": h, "set": part, "estimate_name": "Delta", "estimate": d.value,
                         "lo95": d.lo95, "hi95": d.hi95, "lower_bound": d.lo_one_sided, "upper_bound": d.hi_one_sided,
                         "p": d.p_one_sided, "companion_name": "ER", "companion": er.value,
                         "companion_lower_bound": er.lo_one_sided, "companion_upper_bound": er.hi_one_sided})
        o, r = _row(est_by_part["eight_W"], m, f"O{s_star_label}"), _row(est_by_part["eight_W"], m, f"R{s_star_label}")
        rows.append({"model": m, "analogue_of": "H3", "set": "eight_W", "estimate_name": "O", "estimate": o.value,
                     "lo95": o.lo95, "hi95": o.hi95, "lower_bound": o.lo_one_sided, "upper_bound": o.hi_one_sided,
                     "p": o.p_one_sided, "companion_name": "R", "companion": r.value,
                     "companion_lower_bound": r.lo_one_sided, "companion_upper_bound": r.hi_one_sided})
        g = _row(est_by_part["eight_W"], m, f"G_sup{s_star_label}")
        rows.append({"model": m, "analogue_of": "H4", "set": "eight_W", "estimate_name": "G_sup", "estimate": g.value,
                     "lo95": g.lo95, "hi95": g.hi95, "lower_bound": g.lo_one_sided, "upper_bound": g.hi_one_sided,
                     "p": g.p_one_sided})
    tab = pd.DataFrame(rows)
    if not len(tab):
        return tab
    tab["rejected"] = [bool(np.isfinite(p) and p <= alpha) for p in tab["p"]]
    tab["grade"] = [grade(dict(r, hypothesis=r["analogue_of"]), r["rejected"]) for _, r in tab.iterrows()]
    tab["control"] = f"none (one-sided {alpha}, secondary)"
    return tab
