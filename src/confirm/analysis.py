"""Analysis of one window of one set (plan draft 3, sections 7 to 10) on a table of phase-2 rows.

Input rows (one per photographed observation): family, observer_id, grade ('research' / 'needs_id'), species, genus
code (genus), w (phase-2 weight), stratum, T, rg_<S> and created_before_<S> for every date, support, support_other,
disagreement, vision, agreeing, disagreeing_now, T_within_horizon, cell, week (ISO week of observed_on), width,
height, n_photos, ident_avail, queue_load, activity_stratum (S0 to S3), proposed (set of species proposed in the
history), dup_group (perceptual-duplicate group or -1), Q (optional), and per model m: c_<m> (species correct),
g_<m> (genus correct), p_<m> (predicted species).
Output: a long table (model, quantity, unit, value, lo95, hi95, lo_one_sided, hi_one_sided, p_one_sided, status,
families_left_out) where unit is a family, 'pooled', a group or a sensitivity label. status is 'not estimable' when
the point value cannot be computed; families_left_out lists the families left out of a pooled estimate by the
not-estimable rule (plan draft 3, section 7.1; D13 addendum 1, item 2). All estimates use the weights; the
observer-cluster bootstrap resamples observers with all their rows and fixed weights; Q, its tertiles, the median
split and the duplicate groups are fixed.
"""
import numpy as np
import pandas as pd

from src.confirm import estimators as E

ANIMALS = ["Nymphalidae", "Anatidae", "Columbidae", "Sciuridae", "Araneidae", "Colubridae", "Ranidae"]
PLANTS = ["Asteraceae", "Fabaceae", "Lamiaceae", "Rosaceae", "Poaceae", "Pinaceae"]
# covariates of b3 (plan section 5; D13 addendum 1, item 1): numeric columns, then the activity dummies S1 to S3
B3_NUMERIC = ["week", "width", "height", "n_photos", "vision", "ident_avail", "queue_load"]
B3_STRATA = ["S1", "S2", "S3"]


class Out:
    def __init__(self):
        self.rows = []

    def add(self, model, quantity, unit, x, left_out=()):
        x = np.asarray(x, float)
        lo, hi = E.interval(x)
        l1, h1, p = E.one_sided(x)
        self.rows.append({"model": model, "quantity": quantity, "unit": unit, "value": float(x[0]), "lo95": lo,
                          "hi95": hi, "lo_one_sided": l1, "hi_one_sided": h1, "p_one_sided": p,
                          "status": "estimable" if np.isfinite(x[0]) else "not estimable",
                          "families_left_out": ";".join(left_out)})

    def fam(self, model, quantity, fams, X):
        for j, f in enumerate(fams):
            self.add(model, quantity, f, X[:, j])


def _left(fams, mask, among=None):
    """Names of the families not in mask (restricted to the indices in among)."""
    ix = range(len(fams)) if among is None else among
    return [fams[j] for j in ix if not mask[j]]


def _codes(v):
    u, inv = np.unique(np.asarray(v), return_inverse=True)
    return inv, u


def analyse(rows, models, dates, s_star, R, rng, regime_flags=None, popR=None, popN=None, q_window=False,
            fe=True, sensitivities=True):
    """Returns (long table, info). regime_flags: {(model, family)} flagged pairs. info['q_tertile_figure'] holds the
    table for the figure of the Q tertiles when Q is used."""
    rows = rows.reset_index(drop=True)
    out = Out()
    fam, fams = _codes(rows["family"])
    F = len(fams)
    isR = (rows["grade"] == "research").to_numpy()
    isN = ~isR
    T = rows["T"].to_numpy(float)
    tdef = isR & np.isfinite(T)
    slow, fast = tdef & (T >= 1), tdef & (T < 1)
    st = rows["stratum"].to_numpy()
    spv = np.where(isR, rows["species"].fillna(-1).to_numpy(), -1).astype(np.int64)
    sp_key = pd.Series([f"{f}|{s}" for f, s in zip(fam, spv)])
    sp_idx, sp_u = _codes(sp_key)
    sp_fam = np.array([int(k.split("|")[0]) for k in sp_u])
    W = E.boot_matrix(rows["observer_id"].to_numpy(), rows["w"].to_numpy(float), R, rng)
    info = {"rows": int(len(rows)), "research_with_T": int(tdef.sum()), "families": list(fams), "replicates": R}
    groups = {"animals": [j for j, f in enumerate(fams) if f in ANIMALS],
              "plants": [j for j, f in enumerate(fams) if f in PLANTS]}

    def c1_block(m, e, mask_slow, mask_fast, label, grouping=None):
        si, sf = (sp_idx, sp_fam) if grouping is None else grouping
        r = E.c1(W, si, sf, e, mask_slow, mask_fast, F)
        left = _left(fams, r["est"])
        out.add(m, f"Delta{label}", "pooled", r["Delta"], left)
        out.add(m, f"ER{label}", "pooled", r["ER"], left)
        return r

    for m in models:
        e = 1 - rows[f"c_{m}"].to_numpy(float)
        g = rows[f"g_{m}"].to_numpy(float)
        r = c1_block(m, e, slow, fast, "")
        out.fam(m, "Delta", fams, r["Delta_f"])
        out.fam(m, "ER", fams, r["ER_f"])
        out.add(m, "dropped share of slow weight", "pooled", np.nanmean(r["dropped"], axis=1))
        Df, est = r["Delta_f"], r["est"]
        for gname, ix in groups.items():
            if ix:
                gm = np.zeros(F, bool)
                gm[ix] = est[ix]
                gl = _left(fams, est, ix)
                out.add(m, "Delta", gname, E.pool_mean(Df, gm)[0], gl)
                out.add(m, "ER", gname, E.pool_ratio(r["E_slow"], r["E_ref"], gm), gl)
        out.add(m, "median family Delta", "families", E.pool_median(Df, est)[0], _left(fams, est))
        info[f"{m}_families_lower_bound_above_0"] = int(sum(E.interval(Df[:, j])[0] > 0 for j in range(F)))
        wR = np.array([rows.loc[(fam == j) & isR, "w"].sum() for j in range(F)])
        out.add(m, "Delta population-weighted", "pooled", (Df[:, est] * (wR[est] / wR[est].sum())).sum(axis=1),
                _left(fams, est))
        if F > 2:
            for j, f in enumerate(fams):
                km = est.copy()
                km[j] = False
                out.add(m, "Delta leave one family out", f"without {f}", E.pool_mean(Df, km)[0],
                        _left(fams, est, [i for i in range(F) if i != j]))
        for s in ("A1", "A2", "A3"):
            c1_block(m, e, tdef & (st == s), fast, f" {s} vs A0")
        sf_, sl = E.slope(W, sp_idx, sp_fam, e, T, tdef, F)
        out.add(m, "slope on log(1+T)", "pooled", sl, _left(fams, E.estimable(sf_)))
        ms = E.median_split(rows["w"].to_numpy(float), sp_idx, T, tdef)
        c1_block(m, e, tdef & ms, tdef & ~ms, " median split")
        if sensitivities:
            cons = (rows["agreeing"].fillna(0).to_numpy() >= 3) & (rows["disagreeing_now"].fillna(1).to_numpy() == 0)
            c1_block(m, e, slow & cons, fast & cons, " strong consensus")
            hz = rows["T_within_horizon"].fillna(False).to_numpy(bool)
            c1_block(m, e, slow & hz, fast & hz, " common horizon 540 days")
            nd = rows["dup_group"].fillna(-1).to_numpy() < 0
            c1_block(m, e, slow & nd, fast & nd, " without perceptual-duplicate groups")
            if regime_flags:
                ok = np.array([(m, f) not in regime_flags for f in rows["family"]])
                c1_block(m, e, slow & ok, fast & ok, " without regime-flagged pairs")
            dis = rows["disagreement"].fillna(False).to_numpy(bool)
            c1_block(m, e, slow & dis, fast, " slow with disagreement")
            c1_block(m, e, slow & ~dis, fast, " slow without disagreement")
            vis = rows["vision"].fillna(False).to_numpy(bool)
            c1_block(m, e, slow & ~vis, fast & ~vis, " within V0")
            c1_block(m, e, slow & vis, fast & vis, " within V1")
            # observer activity (plan section 10, item 9; D13 addendum 1): Delta and ER within each stratum
            if "activity_stratum" in rows:
                act = rows["activity_stratum"].fillna("").to_numpy()
                for sname in ("S0", "S1", "S2", "S3"):
                    c1_block(m, e, slow & (act == sname), fast & (act == sname), f" within activity {sname}")
            # tipping point: excess label error among slow observations that brings the bound to 0 and to 1.0
            lo = E.one_sided(r["Delta"])[0]
            info[f"{m}_tipping_point_to_0"] = float(lo / 100)
            info[f"{m}_tipping_point_to_1"] = float((lo - 1.0) / 100)
            # errors on slow observations whose predicted species was proposed by an identifier
            wrong_slow = slow & (e > 0)
            prop = np.array([int(p) in s if isinstance(s, (set, frozenset, list, tuple)) else False
                             for p, s in zip(rows[f"p_{m}"].fillna(-1), rows["proposed"])])
            ws = rows["w"].to_numpy(float)
            info[f"{m}_share_slow_errors_proposed"] = float((ws * (wrong_slow & prop)).sum() / max((ws * wrong_slow).sum(), 1e-12))
            # genus-level C1 with needs_id as the slowest group (I2)
            gk, gu = _codes(pd.Series([f"{f}|{x}" for f, x in zip(fam, rows["genus"].fillna(-1).astype(np.int64))]))
            gf = np.array([int(k.split("|")[0]) for k in gu])
            b2 = isN & (st == "B2")
            c1_block(m, 1 - g, slow | b2, fast, " genus level with B2", (gk, gf))
            c1_block(m, 1 - g, slow | isN, fast, " genus level with B1 and B2", (gk, gf))
        # C2
        for S in dates:
            rgS = rows[f"rg_{S}"].fillna(False).to_numpy(bool)
            cS = rows[f"created_before_{S}"].fillna(False).to_numpy(bool)
            s2 = (rows["support"].fillna(0).to_numpy() >= 2) & isN
            c2 = E.c2(W, fam, F, isR, 1 - e, g, rgS, cS, isN, s2, popR, popN)
            tag = "" if S == s_star else f" at {S}"
            for k in ("O", "R", "L", "L_upload", "L_ident", "O_ident", "G_all", "G_sup"):
                out.add(m, k + tag, "pooled", c2[k], _left(fams, c2[k + "_est"]))
            if S == s_star:
                out.fam(m, "O", fams, c2["O_f"])
                info.setdefault("c2_families_left_out", {})[m] = {
                    k: _left(fams, c2[k + "_est"]) for k in ("O", "R", "L", "L_upload", "L_ident", "O_ident",
                                                              "G_all", "G_sup") if (~c2[k + "_est"]).any()}
                out.fam(m, "G_sup", fams, c2["G_sup_f"])
                s2b = ((rows["support_other"].fillna(0).to_numpy() >= 1) | s2) & isN
                c2b = E.c2(W, fam, F, isR, 1 - e, g, rgS, cS, isN, s2b, popR, popN)
                out.add(m, "G_sup with S2b", "pooled", c2b["G_sup"], _left(fams, c2b["G_sup_est"]))
                if sensitivities:
                    # C2 at S* without perceptual-duplicate groups and without regime-flagged pairs (section 10,
                    # items 6 and 7; N18a): rows of the groups or pairs are removed from every term
                    nd = rows["dup_group"].fillna(-1).to_numpy() < 0
                    subsets = [(" without perceptual-duplicate groups", nd)]
                    if regime_flags:
                        subsets.append((" without regime-flagged pairs",
                                        np.array([(m, f) not in regime_flags for f in rows["family"]])))
                    for lab, kk in subsets:
                        c2s = E.c2(W, fam, F, isR & kk, 1 - e, g, rgS, cS, isN & kk, s2 & kk, popR, popN)
                        for k in ("O", "R", "G_all", "G_sup"):
                            out.add(m, k + lab, "pooled", c2s[k], _left(fams, c2s[k + "_est"]))
    # C3 (primary model only)
    m = models[0]
    e = 1 - rows[f"c_{m}"].to_numpy(float)
    if fe and tdef.sum() > 50:
        cell_idx, _ = _codes(rows["cell"].fillna("none"))
        obs_idx, _ = _codes(rows["observer_id"])
        # all covariates of plan section 5 (D13 addendum 1, item 1); a missing numeric value takes the median of its
        # column; activity enters as dummies S1 to S3 (S0 reference); the 10-degree cell enters as species x cell
        num = [c for c in B3_NUMERIC if c in rows]
        act = rows["activity_stratum"].fillna("").to_numpy() if "activity_stratum" in rows else np.full(len(rows), "")
        cols = [rows[c].astype(float).fillna(rows[c].astype(float).median()).to_numpy(float) for c in num]
        cols += [(act == sname).astype(float) for sname in B3_STRATA]
        cov = np.column_stack(cols)
        info["b3_covariates"] = num + [f"activity {sname}" for sname in B3_STRATA]
        info["b3_missing_values"] = {c: int(rows.loc[tdef, c].isna().sum()) for c in num}
        info["b3_rows_without_activity_stratum"] = int((act[tdef] == "").sum())
        k = np.flatnonzero(tdef)
        fem = E.fe_models(W[:, k], e[k], slow[k].astype(float), sp_idx[k], cell_idx[k], obs_idx[k], cov[k])
        for q in ("b0", "b3", "b_obs", "rho"):
            out.add(m, q, "pooled", fem[q])
        info["rho_band"] = E.c3_band(float(fem["rho"][0]))
    if q_window and "Q" in rows and F == 8:
        Qv = rows["Q"].to_numpy(float)
        b, bp = E.q_moderation(W, fam, F, sp_idx, sp_fam, slow, Qv, e)
        out.fam(m, "b_int", fams, b)
        out.add(m, "b_int", "pooled", bp, _left(fams, E.estimable(b)))
        # tertiles of Q within family among the research rows with T (section 7.3, item 6; D8 definition): Delta and
        # ER per tertile, per family and pooled, with the reference from fast rows of the same species and tertile
        w0 = rows["w"].to_numpy(float)
        ter, cuts = E.q_tertiles(np.where(tdef, Qv, np.nan), fam, F, w0)
        fig = []
        rt = {}
        for t in range(3):
            r = E.c1(W, sp_idx, sp_fam, e, slow & (ter == t), fast & (ter == t), F)
            rt[t] = r
            left = _left(fams, r["est"])
            out.add(m, f"Delta Q tertile {t + 1}", "pooled", r["Delta"], left)
            out.add(m, f"ER Q tertile {t + 1}", "pooled", r["ER"], left)
            out.fam(m, f"Delta Q tertile {t + 1}", fams, r["Delta_f"])
            out.fam(m, f"ER Q tertile {t + 1}", fams, r["ER_f"])
            for j, f in enumerate(list(fams) + ["pooled"]):
                pooled = f == "pooled"
                k = (ter == t) & (np.ones(len(fam), bool) if pooled else (fam == j))
                wk = w0 * k
                dl = r["Delta"] if pooled else r["Delta_f"][:, j]
                er = r["ER"] if pooled else r["ER_f"][:, j]
                qk, wq = Qv[k], w0[k]
                o = np.argsort(qk, kind="stable")
                cw = np.cumsum(wq[o])
                cut = (np.nan, np.nan) if pooled else cuts.get(j, (np.nan, np.nan))
                fig.append({"model": m, "tertile": t + 1, "unit": f, "Q_cut_low": cut[0], "Q_cut_high": cut[1],
                            "rows": int(k.sum()), "slow_rows": int((k & slow).sum()),
                            "weighted_share_slow": float((wk * slow).sum() / wk.sum()) if wk.sum() > 0 else np.nan,
                            "weighted_median_Q": float(qk[o][np.searchsorted(cw, cw[-1] / 2)]) if len(qk) else np.nan,
                            "Delta": float(dl[0]), "Delta_lo95": E.interval(dl)[0], "Delta_hi95": E.interval(dl)[1],
                            "ER": float(er[0]), "ER_lo95": E.interval(er)[0], "ER_hi95": E.interval(er)[1],
                            "status": "estimable" if np.isfinite(dl[0]) else "not estimable",
                            "families_left_out": ";".join(left) if pooled else ""})
        info["q_tertile_figure"] = fig
        # contrast Delta(T3) - Delta(T1), pooled and per family, computed inside every bootstrap replicate
        left31 = sorted(set(_left(fams, rt[0]["est"])) | set(_left(fams, rt[2]["est"])))
        out.add(m, "Delta Q tertile 3 minus tertile 1", "pooled", rt[2]["Delta"] - rt[0]["Delta"], left31)
        out.fam(m, "Delta Q tertile 3 minus tertile 1", fams, rt[2]["Delta_f"] - rt[0]["Delta_f"])
        info["q_rows_with_Q"] = int((tdef & np.isfinite(Qv)).sum())
    return pd.DataFrame(out.rows), info
