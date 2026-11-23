"""Estimators of the confirmatory plan, draft 3 (sections 7 to 10), with phase-2 weights.

Conventions
- A weight matrix W has shape (R + 1, n): row 0 holds the phase-2 weights w of the n rows (point estimate), rows 1..R
  the bootstrap replicates (w times the number of times the row's observer was drawn). Every estimator takes W and
  returns arrays over the R + 1 rows, so the point estimate and the bootstrap use the same code.
- Families are integer codes 0..F-1; species are integer codes 0..S-1 with sp_fam[s] = family code of species s.
- Error e = 1 - species-level correctness; genus correctness g.
- Pooling over families: equal family weights (mean over families); ER and R pool sums of family means (section 7).
- Not-estimable rule (plan draft 3, section 7.1; D13 addendum 1, item 2): a family estimate whose point value cannot
  be computed (not finite) is not estimable; the family is left out of the pooled estimate in the point estimate and
  in every bootstrap replicate, and it is listed. Within a replicate, a family that is estimable at the point but
  undefined in that replicate is skipped in that replicate (nanmean, as before).
Reuses src/d6_lib.py (Design, sums, delta_parts) and src/moderation.py (bint_matrix) with their defaults unchanged.
"""
import warnings

import numpy as np
import scipy.sparse as sp
from scipy.stats import rankdata

from src import d6_lib as L
from src import moderation as MD


# ---------------------------------------------------------------- bootstrap and summaries
def boot_matrix(observer, w, R, rng):
    """(R + 1) x n weights: row 0 = w; rows 1..R = w x multiplicity of the row's observer in a draw of observers
    with replacement (observer-cluster bootstrap with fixed weights, section 8)."""
    obs, oi = np.unique(np.asarray(observer), return_inverse=True)
    W = np.empty((R + 1, len(oi)), np.float32)
    W[0] = w
    for b in range(R):
        W[b + 1] = w * np.bincount(rng.integers(0, len(obs), len(obs)), minlength=len(obs))[oi]
    return W


def interval(x, level=0.95):
    x = np.asarray(x, float)[1:]
    x = x[np.isfinite(x)]
    if not len(x):
        return np.nan, np.nan
    a = 100 * (1 - level) / 2
    return float(np.percentile(x, a)), float(np.percentile(x, 100 - a))


def one_sided(x):
    """One-sided 95% bounds (5th and 95th percentiles of the replicates) and the one-sided p-value of H > 0
    (share of replicates at or below 0, section 8)."""
    r = np.asarray(x, float)[1:]
    r = r[np.isfinite(r)]
    if not len(r):
        return np.nan, np.nan, np.nan
    return float(np.percentile(r, 5)), float(np.percentile(r, 95)), float((r <= 0).mean())


def estimable(Xf):
    """Families whose point estimate (row 0) is finite."""
    return np.isfinite(np.asarray(Xf, float)[0])


def pool_mean(Xf, mask=None):
    """Equal-weight mean over the estimable families (mask; default: finite point estimate). Returns (pooled, mask)."""
    Xf = np.asarray(Xf, float)
    m = estimable(Xf) if mask is None else np.asarray(mask, bool)
    if not m.any():
        return np.full(Xf.shape[0], np.nan), m
    with np.errstate(invalid="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return np.nanmean(Xf[:, m], axis=1), m


def pool_median(Xf, mask=None):
    Xf = np.asarray(Xf, float)
    m = estimable(Xf) if mask is None else np.asarray(mask, bool)
    if not m.any():
        return np.full(Xf.shape[0], np.nan), m
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return np.nanmedian(Xf[:, m], axis=1), m


def pool_ratio(num_f, den_f, mask):
    """Ratio of sums over the families in mask (ER and R pooling); den_f is set to NaN where num_f is NaN."""
    m = np.asarray(mask, bool)
    if not m.any():
        return np.full(np.asarray(num_f).shape[0], np.nan)
    with np.errstate(invalid="ignore", divide="ignore"):
        n = np.asarray(num_f, float)[:, m]
        d = np.where(np.isnan(n), np.nan, np.asarray(den_f, float)[:, m])
        return np.nansum(n, axis=1) / np.nansum(d, axis=1)


def _famsum(X, fam, F):
    M = sp.csr_matrix((np.ones(len(fam)), (np.arange(len(fam)), fam)), shape=(len(fam), F))
    return np.asarray(M.T @ X.T).T if X.ndim == 2 else M.T @ X


# ---------------------------------------------------------------- C1 (section 7.1)
def c1(W, sp_idx, sp_fam, e, slow, fast, F):
    """Per family E_slow, E_ref, dropped share of slow weight (R+1 x F) and pooled Delta, ER (R+1)."""
    nsp = len(sp_fam)
    D = L.Design(len(e))
    D.add("wf", sp_idx, 1.0, nsp, fast)
    D.add("ef", sp_idx, e, nsp, fast)
    D.add("ws", sp_idx, 1.0, nsp, slow)
    D.add("es", sp_idx, e, nsp, slow)
    Q = L.sums(W, D, D.matrix())
    Es, Er, drop = L.delta_parts(Q["wf"], Q["ef"], Q["ws"], Q["es"], sp_fam, nf=F)
    # not-estimable rule: a family with no species with both fast and slow rows has no E_slow (and no Delta) at the
    # point estimate; it is left out of Delta and ER in every replicate
    d, est = pool_mean(Es - Er)
    er = pool_ratio(Es, Er, est)
    with np.errstate(invalid="ignore", divide="ignore"):
        er_f = Es / Er
    return {"E_slow": Es, "E_ref": Er, "dropped": drop, "Delta_f": 100 * (Es - Er), "ER_f": er_f,
            "Delta": 100 * d, "ER": er, "est": est}


def slope(W, sp_idx, sp_fam, e, T, mask, F):
    """Within-species weighted least-squares slope of error on log(1 + T), x 100, per family and pooled (mean)."""
    nsp = len(sp_fam)
    x = np.log1p(np.where(mask, T, 0.0))
    D = L.Design(len(e))
    for name, v in (("w", 1.0), ("x", x), ("y", e), ("xy", x * e), ("xx", x * x)):
        D.add(name, sp_idx, v, nsp, mask)
    Q = L.sums(W, D, D.matrix())
    with np.errstate(invalid="ignore", divide="ignore"):
        ok = Q["w"] > 0
        sw = np.where(ok, Q["w"], 1)
        cxy = np.where(ok, Q["xy"] - Q["x"] * Q["y"] / sw, 0)
        cxx = np.where(ok, Q["xx"] - Q["x"] ** 2 / sw, 0)
        b = 100 * L.fam_sum(cxy, sp_fam, F) / L.fam_sum(cxx, sp_fam, F)
    return b, pool_mean(b)[0]


def median_split(w, sp_idx, T, mask):
    """Slow = T above the weighted median of T within its species (point weights; fixed in the bootstrap)."""
    slow = np.zeros(len(T), bool)
    for s in np.unique(sp_idx[mask]):
        k = np.flatnonzero(mask & (sp_idx == s))
        o = k[np.argsort(T[k], kind="stable")]
        cw = np.cumsum(w[o])
        med = T[o][np.searchsorted(cw, cw[-1] / 2)]
        slow[k] = T[k] > med
    return slow


# ---------------------------------------------------------------- C2 (section 7.2)
def c2(W, fam, F, isR, c, g, rgS, createdS, isN, s2, popR=None, popN=None):
    """O, R, L (split into late upload and late identification), O_ident, G_all, G_sup at one date S, per family
    (R+1 x F) and pooled. popR/popN: population counts per family for the genus-level mixing (D4/D5); if None the
    weighted sums of the research and needs_id rows are used (estimated population counts)."""
    def fs(mask, v=1.0):
        return _famsum(W * (mask * v)[None, :].astype(np.float32), fam, F)
    nR, cR = fs(isR), fs(isR, c)
    nS, cS = fs(isR & rgS), fs(isR & rgS, c)
    nI, cI = fs(isR & createdS), fs(isR & createdS, c)
    late_up = fs(isR & ~createdS)
    late_id = fs(isR & createdS & ~rgS)
    gR, gS = fs(isR, g), fs(isR & rgS, g)
    nN, gN = fs(isN), fs(isN, g)
    nS2, gS2 = fs(isN & s2), fs(isN & s2, g)
    with np.errstate(invalid="ignore", divide="ignore"):
        aT, aS, a_id = cR / nR, cS / nS, cI / nI
        out = {"O_f": 100 * (aS - aT), "R_f": (1 - aT) / (1 - aS), "L_f": 1 - nS / nR,
               "L_upload_f": late_up / nR, "L_ident_f": late_id / nR, "O_ident_f": 100 * (aS - a_id)}
        pR = popR[None, :] if popR is not None else nR
        pN = popN[None, :] if popN is not None else nN
        wA = pR / (pR + pN)
        out["G_all_f"] = 100 * (gS / nS - (wA * gR / nR + (1 - wA) * gN / np.where(nN > 0, nN, np.nan)))
        pN2 = pN * nS2 / np.where(nN > 0, nN, np.nan)
        wS = pR / (pR + pN2)
        out["G_sup_f"] = 100 * (gS / nS - (wS * gR / nR + (1 - wS) * gS2 / np.where(nS2 > 0, nS2, np.nan)))
    for k in ("O", "L", "L_upload", "L_ident", "O_ident", "G_all", "G_sup"):
        out[k], out[k + "_est"] = pool_mean(out[k + "_f"])
    mR = estimable(1 - aT) & estimable(1 - aS)
    out["R"] = pool_mean(1 - aT, mR)[0] / pool_mean(1 - aS, mR)[0]
    out["R_est"] = mR
    return out


# ---------------------------------------------------------------- fixed-effects models (section 7.3)
def _demean(v, groups, w, iters=200, tol=1e-10):
    """Weighted alternating projections: remove the weighted means of every grouping in groups from v."""
    v = v.astype(float).copy()
    for _ in range(iters if len(groups) > 1 else 1):
        before = v.copy()
        for gidx, ng in groups:
            sw = np.bincount(gidx, weights=w, minlength=ng)
            m = np.bincount(gidx, weights=w * v, minlength=ng) / np.where(sw > 0, sw, 1)
            v -= m[gidx]
        if len(groups) == 1 or np.max(np.abs(v - before)) < tol:
            break
    return v


def fe_coef(w, y, X, groups):
    """Coefficients of y on X after absorbing the fixed effects in groups (weighted least squares)."""
    ok = w > 0
    w_, y_, X_ = w[ok], y[ok], X[ok]
    g_ = []
    for gidx, ng in groups:
        u, inv = np.unique(gidx[ok], return_inverse=True)
        g_.append((inv, len(u)))
    yt = _demean(y_, g_, w_)
    Xt = np.column_stack([_demean(X_[:, j], g_, w_) for j in range(X_.shape[1])])
    A = Xt.T @ (Xt * w_[:, None])
    b = Xt.T @ (yt * w_)
    try:
        return np.linalg.solve(A, b)
    except np.linalg.LinAlgError:
        return np.linalg.lstsq(A, b, rcond=None)[0]


def fe_models(W, e, slow, sp_idx, cell_idx, obs_idx, covariates):
    """b0 (species FE), b3 (species x cell FE + covariates), b_obs (species and observer FE), x 100, for every row of
    W; rho = b3 / b0. covariates: (n x k) array (columns constant in the data are dropped)."""
    nsp = int(sp_idx.max()) + 1
    spc = sp_idx.astype(np.int64) * (int(cell_idx.max()) + 1) + cell_idx
    cov = covariates[:, np.nanstd(covariates, axis=0) > 0] if covariates.shape[1] else covariates
    out = np.full((W.shape[0], 3), np.nan)
    for r in range(W.shape[0]):
        w = W[r].astype(float)
        out[r, 0] = 100 * fe_coef(w, e, slow[:, None].astype(float), [(sp_idx, nsp)])[0]
        out[r, 1] = 100 * fe_coef(w, e, np.column_stack([slow.astype(float), cov]), [(spc, int(spc.max()) + 1)])[0]
        out[r, 2] = 100 * fe_coef(w, e, slow[:, None].astype(float),
                                  [(sp_idx, nsp), (obs_idx, int(obs_idx.max()) + 1)])[0]
    with np.errstate(invalid="ignore", divide="ignore"):
        return {"b0": out[:, 0], "b3": out[:, 1], "b_obs": out[:, 2], "rho": out[:, 1] / out[:, 0]}


def q_moderation(W, fam, F, sp_idx, sp_fam, slow, Q, e):
    """b_int per family and pooled (D8): Qc = Q minus its weighted family mean (point weights; Q fixed)."""
    w0 = W[0].astype(float)
    Qc = np.full(len(Q), np.nan)
    for f in range(F):
        k = (fam == f) & np.isfinite(Q) & (w0 > 0)
        if k.any():
            Qc[k] = Q[k] - np.average(Q[k], weights=w0[k])
    ok = np.isfinite(Qc)
    Wq = W[:, ok]
    if F == 8:
        b = MD.bint_matrix(Wq, fam[ok], sp_idx[ok], slow[ok].astype(float), Qc[ok], e[ok], len(sp_fam), sp_fam)
    else:
        b = np.full((W.shape[0], F), np.nan)
    return b, pool_mean(b)[0]


def q_tertiles(Q, fam, F, w0):
    """Tertile (0, 1, 2) of Q within each family among the rows with a finite Q and w0 > 0 (D8: cut points are the
    1/3 and 2/3 quantiles of Q over these rows; a row at a cut point goes to the lower tertile); -1 elsewhere.
    Returns (tertile, cut points {family code: (q1, q2)})."""
    Q = np.asarray(Q, float)
    ter = np.full(len(Q), -1)
    cuts = {}
    for f in range(F):
        k = (fam == f) & np.isfinite(Q) & (w0 > 0)
        if not k.any():
            continue
        q1, q2 = np.quantile(Q[k], [1 / 3, 2 / 3])
        cuts[f] = (float(q1), float(q2))
        ter[k] = np.where(Q[k] <= q1, 0, np.where(Q[k] <= q2, 1, 2))
    return ter, cuts


# ---------------------------------------------------------------- family level (H6, heterogeneity)
def spearman(x, y):
    rx, ry = rankdata(x), rankdata(y)
    rx, ry = rx - rx.mean(), ry - ry.mean()
    return float((rx * ry).sum() / np.sqrt((rx ** 2).sum() * (ry ** 2).sum()))


def spearman_permutation(x, y, n_perm, rng):
    """Spearman rho and the one-sided permutation p-value of rho > 0: (1 + number of permuted rho >= observed) /
    (1 + n_perm)."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = np.isfinite(x) & np.isfinite(y)
    x, y = x[ok], y[ok]
    rho = spearman(x, y)
    perm = np.array([spearman(x, rng.permutation(y)) for _ in range(n_perm)])
    return rho, float((1 + (perm >= rho - 1e-12).sum()) / (1 + n_perm)), int(ok.sum())


def h6(delta, fast_share, n_perm, rng, n_boot=0, level=0.95):
    """H6 (section 7.3, item 7) with the not-estimable rule: delta and fast_share are {family: value}; a family whose
    Delta is not estimable (not finite) or has no fast share is left out. Returns a dict with rho, the one-sided
    permutation p-value (n_perm permutations), the number of families used and the families left out; with n_boot > 0
    also the percentile interval of rho from n_boot bootstrap replicates that resample the families with replacement
    (section 9; drawn after the permutations from the same generator; replicates with an undefined rho are skipped
    and counted)."""
    fams = sorted(delta)
    x = np.array([delta[f] for f in fams], float)
    y = np.array([fast_share.get(f, np.nan) for f in fams], float)
    ok = np.isfinite(x) & np.isfinite(y)
    left = [f for f, k in zip(fams, ok) if not k]
    if ok.sum() < 3:
        return {"rho": np.nan, "p": np.nan, "families_used": int(ok.sum()), "families_left_out": left,
                "rho_lo95": np.nan, "rho_hi95": np.nan, "boot_replicates": 0, "boot_undefined": 0}
    rho, p, n = spearman_permutation(x[ok], y[ok], n_perm, rng)
    out = {"rho": rho, "p": p, "families_used": n, "families_left_out": left}
    if n_boot:
        xs, ys = x[ok], y[ok]
        reps = []
        with np.errstate(invalid="ignore", divide="ignore"):
            for _ in range(n_boot):
                k = rng.integers(0, len(xs), len(xs))
                reps.append(spearman(xs[k], ys[k]))
        reps = np.array(reps, float)
        fin = reps[np.isfinite(reps)]
        a = 100 * (1 - level) / 2
        out.update({"rho_lo95": float(np.percentile(fin, a)) if len(fin) else np.nan,
                    "rho_hi95": float(np.percentile(fin, 100 - a)) if len(fin) else np.nan,
                    "boot_replicates": int(n_boot), "boot_undefined": int((~np.isfinite(reps)).sum())})
    return out


# ---------------------------------------------------------------- multiplicity and decision rules (sections 8, 9)
def holm(pvalues, alpha=0.05):
    """pvalues: {name: p}. Returns {name: (threshold, rejected)}; testing stops at the first non-rejection."""
    order = sorted(pvalues, key=lambda k: (pvalues[k], k))
    m, out, go = len(order), {}, True
    for i, k in enumerate(order):
        thr = alpha / (m - i)
        rej = go and pvalues[k] <= thr
        go = go and rej
        out[k] = (thr, rej)
    return out


def grade_c1(rejected, d_lo, d_hi, er_lo, er_hi, min_pts=1.0, min_ratio=1.15):
    if rejected:
        if d_lo >= min_pts and er_lo >= min_ratio:
            return "strong"
        if d_hi < min_pts and er_hi < min_ratio:
            return "small"
        return "present"
    return "negligible" if (d_hi < min_pts and er_hi < min_ratio) else "inconclusive"


def grade_h3(rejected, o_lo, o_hi, r_lo, r_hi, min_pts=1.0, min_ratio=1.15):
    if not rejected:
        return "not shown"
    if o_lo >= min_pts or r_lo >= min_ratio:
        return "material"
    if o_hi < min_pts and r_hi < min_ratio:
        return "small"
    return "present"


def grade_h4(rejected):
    return "shown" if rejected else "not shown"


def c3_band(rho, bands=(0.75, 0.5)):
    if not np.isfinite(rho):
        return "undefined"
    return "largely not explained" if rho >= bands[0] else ("partly explained" if rho >= bands[1] else "mostly explained")


def regime_check(pred, label, max_pred=0.10, min_label=0.02):
    """Species flagged in one model-family pair: prediction share > max_pred and label share < min_label."""
    pred, label = np.asarray(pred), np.asarray(label)
    n = len(pred)
    if not n:
        return []
    ps = {s: c / n for s, c in zip(*np.unique(pred, return_counts=True))}
    ls = {s: c / n for s, c in zip(*np.unique(label, return_counts=True))}
    return sorted(int(s) for s, v in ps.items() if v > max_pred and ls.get(s, 0.0) < min_label)
