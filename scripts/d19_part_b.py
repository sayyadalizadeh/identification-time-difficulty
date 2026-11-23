"""D19 Part B (post hoc): light analyses on the stored identification histories, snapshot tables and predictions.

Sets eight_W (H1), eight_W2 (H5) and new_W (H2); four models (BioCLIP 2.5 Huge primary); Delta and ER of the frozen
c1 estimator with 95% percentile intervals of the observer-cluster bootstrap (2,000 replicates, seed 20261124, one
weight matrix per set shared by every contrast of the set); pooled with equal family weights and by group.

Definitions fixed in this script (D19 items):
- History fields use the identifications created before the cutoff of the run (2026-10-27, UTC), as in the run.
- B1: T_wait = days from the creation of the observation to the first identification by a user other than the
  observer (any identification, current or withdrawn); T_res = T - T_wait. Slow (T >= 1 day) observations are split
  into "looked at early" (T_wait < 1 day) and "waited" (T_wait >= 1 day); each is contrasted with A0.
- B2: observer's identification at creation = the observer's earliest identification if it was created within one
  hour of the creation of the observation; categories: none (no such identification), above species rank
  (rank level above 10), species rank (rank level 10 or below).
- B3: vision assistance = the identification flag vision; shares of observations with any vision-assisted
  identification created up to the research-grade time; contrast within observations with no vision-assisted
  identification at all (whole history up to the cutoff).
- B4: one photograph only (n_photos of the snapshot equal to 1).
- B5: withdrawn = any identification with current false; non-ancestor = any identification above species rank whose
  taxon is not an ancestor of the final species (ancestry of the snapshot taxonomy); contrasts without each and
  without either.
- B6: fast = T below 6 h, 12 h, 48 h and 7 days (slow = T at or above the threshold); quantile contrast: within each
  family, research-grade rows with T ordered by T (ties broken by a random key, seed 20261124); position = (cumulative
  weight - weight / 2) / total weight; fastest fifth = position below 0.2, slowest fifth = position at or above 0.8.
- B7: random-effects summaries (REML) of the family Delta and log ER over the 14 families of window W, variances from
  the stored 95% interval widths ((hi - lo) / 3.92) squared, because the bootstrap replicates were not kept; a version
  with a random effect for taxonomic class; for H6 a precision-weighted meta-regression of family Delta on the fast
  share with family and class random effects; Spearman rho leaving out one class at a time.
- B8: resolving identifier = the user of the identification at which the research-grade consensus of the run (N2)
  first holds; two-way (pigeonhole) cluster bootstrap: observers and resolving identifiers resampled independently,
  row weight times both multiplicities (2,000 replicates).
- B9: prior exposure = the observer has a research-grade observation of the same species observed before 2024-05-01
  in the snapshot (pairs from d19_snapshot.py).
- B11: accuracy of research-grade rows per stratum, mean over the eight families with equal weights; rank 1 = most
  accurate; Kendall's W of the model ranks over the four strata.
Outputs: outputs/D19/B/.
"""
import json
import time

import numpy as np
import pandas as pd
from scipy import optimize, stats

import d19_common as C
from d19_common import E, L

OUT = C.OUT / "B"
HOUR = 3600 * 10**9


# ---------------------------------------------------------------- per-row history fields
def resolve(r, sp_id):
    """(T in days, user, time) of the identification at which N2 first holds (as src/d6_lib.t_days)."""
    last = {}
    for x in r["ids"]:
        if x[0] >= L.CUTOFF:
            break
        last[x[2]] = x
        spl = [y for y in last.values() if y[4] <= 10]
        if L.n2(spl, sp_id):
            return (x[0] - r["created_ns"]) / L.DAY_NS, x[2], x[0]
    return np.nan, None, None


def fields(d, rec, anc):
    out = []
    for u, g, sp, T in zip(d["observation_uuid"], d["grade"], d["species"], d["T"]):
        r = rec[u]
        ids = [x for x in r["ids"] if x[0] < L.CUTOFF]
        own, cr = r["owner"], r["created_ns"]
        oth = [x for x in ids if x[2] is not None and int(x[2]) != own]
        tw = (oth[0][0] - cr) / L.DAY_NS if oth else np.nan
        mine = [x for x in ids if x[2] is not None and int(x[2]) == own]
        if mine and mine[0][0] - cr <= HOUR:
            cat = "species rank" if mine[0][4] <= 10 else "above species rank"
        else:
            cat = "none"
        late_first = bool(mine) and mine[0][0] - cr > HOUR
        f = {"T_wait": tw, "own_at_creation": cat, "own_first_later_than_1h": late_first,
             "vision_any": any(x[8] for x in ids), "withdrawn_any": any(not x[6] for x in ids),
             "Tr": np.nan, "resolver": None, "resolve_ns": None, "vision_before_rg": False, "nonanc_any": False}
        if g == "research" and sp == sp:
            Tr, us, ts = resolve(r, int(sp))
            f.update({"Tr": Tr, "resolver": us, "resolve_ns": ts})
            if ts is not None:
                f["vision_before_rg"] = any(x[8] for x in ids if x[0] <= ts)
            a = anc.get(int(sp))
            if a is None:
                raise RuntimeError(f"no ancestry for species {int(sp)}")
            f["nonanc_any"] = any(x[4] > 10 and x[3] is not None and int(x[3]) not in a for x in ids)
        out.append(f)
    return pd.DataFrame(out, index=d.index)


# ---------------------------------------------------------------- random effects (REML)
def reml(y, v, X=None, groups=None):
    """Random-effects model y = X b + u_family (+ a_group) + e, var(e) = v (known). REML over tau_f^2 (and tau_g^2).
    Returns dict with b, cov(b), tau_f, tau_g."""
    y, v = np.asarray(y, float), np.asarray(v, float)
    n = len(y)
    X = np.ones((n, 1)) if X is None else X
    Z = None
    if groups is not None:
        gu, gi = np.unique(groups, return_inverse=True)
        Z = np.zeros((n, len(gu)))
        Z[np.arange(n), gi] = 1

    def parts(th):
        tf = np.exp(th[0])
        V = np.diag(v + tf)
        if Z is not None:
            V = V + np.exp(th[1]) * Z @ Z.T
        Vi = np.linalg.inv(V)
        XtViX = X.T @ Vi @ X
        b = np.linalg.solve(XtViX, X.T @ Vi @ y)
        res = y - X @ b
        nll = 0.5 * (np.linalg.slogdet(V)[1] + np.linalg.slogdet(XtViX)[1] + res @ Vi @ res)
        return nll, b, np.linalg.inv(XtViX)

    k = 1 if Z is None else 2
    best = None
    for start in ([-6.0] * k, [0.0] * k, [2.0] * k, [-12.0] * k):
        rr = optimize.minimize(lambda th: parts(th)[0], np.array(start), method="Nelder-Mead",
                               options={"xatol": 1e-8, "fatol": 1e-10, "maxiter": 20000})
        if best is None or rr.fun < best.fun:
            best = rr
    nll, b, cov = parts(best.x)
    return {"b": b, "cov": cov, "tau_f": float(np.sqrt(np.exp(best.x[0]))),
            "tau_g": float(np.sqrt(np.exp(best.x[1]))) if k == 2 else None, "nll": float(nll), "converged": bool(best.success)}


def re_summary(name, y, v, groups=None):
    r = reml(y, v, None, groups)
    mu, se = float(r["b"][0]), float(np.sqrt(r["cov"][0, 0]))
    k = len(y)
    tau2 = r["tau_f"] ** 2 + (r["tau_g"] ** 2 if r["tau_g"] is not None else 0.0)
    tcrit = stats.t.ppf(0.975, k - 2)
    wfe = 1 / np.asarray(v)
    q = float((wfe * (y - (wfe * y).sum() / wfe.sum()) ** 2).sum())
    i2 = max(0.0, (q - (k - 1)) / q) if q > 0 else 0.0
    return {"quantity": name, "families": k, "estimate": mu, "se": se, "lo95": mu - 1.959964 * se,
            "hi95": mu + 1.959964 * se, "tau_family": r["tau_f"], "tau_class": r["tau_g"],
            "prediction_lo95": mu - tcrit * np.sqrt(tau2 + se ** 2), "prediction_hi95": mu + tcrit * np.sqrt(tau2 + se ** 2),
            "Q": q, "I2": i2, "converged": r["converged"]}


# ---------------------------------------------------------------- main
def main():
    log = C.Log(OUT / "part_b_log.txt")
    log("D19 Part B (post hoc); started", time.strftime("%Y-%m-%d %H:%M:%S"), "; seed", C.SEED, "; threads", C.THREADS)
    spt = pd.read_parquet(C.OUT / "snapshot/species_texts.parquet")
    anc = {int(s): frozenset(int(x) for x in a.split("/") if x) for s, a in zip(spt["species_taxon_id"], spt["ancestry"])}
    expo = pd.read_parquet(C.OUT / "snapshot/b9_exposure_pairs.parquet")
    expo_set = set(zip(expo["observer_id"].astype(np.int64), expo["species"].astype(np.int64)))
    rows, shares, b8, b11, b10 = [], [], [], [], []
    for s in ("eight_W", "eight_W2", "new_W"):
        t0 = time.time()
        d, rec = C.load_rows(s)
        D = C.Design(d)
        f = fields(d, rec, anc)
        d = pd.concat([d, f], axis=1)
        tdef, slow, fast, w = D.tdef, D.slow, D.fast, D.w
        T = D.T
        dT = np.abs(d["Tr"].to_numpy(float)[tdef] - T[tdef])
        log.check(f"{s}: T recomputed from the stored histories equals the stored T (research rows with T)",
                  bool(np.all(dT < 1e-9)) and d.loc[tdef, "resolver"].notna().all(), f"rows {int(tdef.sum()):,}")
        log.check(f"{s}: every observation has a first identification by another user at or before research grade",
                  bool(np.all(d["T_wait"].to_numpy(float)[tdef] <= T[tdef] + 1e-12)),
                  f"rows with T_wait > T: {int((d['T_wait'].to_numpy(float)[tdef] > T[tdef] + 1e-12).sum())}")
        rng = np.random.default_rng(C.SEED)
        W = E.boot_matrix(D.observer, w, 2000, rng)
        tw = d["T_wait"].to_numpy(float)
        own = d["own_at_creation"].to_numpy()
        vany = d["vision_any"].to_numpy(bool)
        vrg = d["vision_before_rg"].to_numpy(bool)
        np1 = (d["n_photos"].to_numpy() == 1)
        wd = d["withdrawn_any"].to_numpy(bool)
        na = d["nonanc_any"].to_numpy(bool)
        ex = np.array([(int(o), int(sp)) in expo_set if g == "research" and sp == sp else False
                       for o, sp, g in zip(d["observer_id"], d["species"], d["grade"])])
        # quantile contrast (fifths within family by T; random tie key)
        key = np.random.default_rng(C.SEED).random(len(d))
        q_fast, q_slow = np.zeros(len(d), bool), np.zeros(len(d), bool)
        for j in range(D.F):
            k = np.flatnonzero(tdef & (D.fam == j))
            o = k[np.lexsort((key[k], T[k]))]
            cw = np.cumsum(w[o])
            pos = (cw - w[o] / 2) / cw[-1]
            q_fast[o[pos < 0.2]] = True
            q_slow[o[pos >= 0.8]] = True
        contrasts = [("main", "slow vs fast (registered contrast)", slow, fast),
                     ("B1", "slow looked at early (T_wait < 1 day) vs A0", slow & (tw < 1), fast),
                     ("B1", "slow waited (T_wait >= 1 day) vs A0", slow & (tw >= 1), fast),
                     ("B2", "own identification at creation: none", slow & (own == "none"), fast & (own == "none")),
                     ("B2", "own identification at creation: above species rank", slow & (own == "above species rank"),
                      fast & (own == "above species rank")),
                     ("B2", "own identification at creation: species rank", slow & (own == "species rank"),
                      fast & (own == "species rank")),
                     ("B3", "no vision-assisted identification at all", slow & ~vany, fast & ~vany),
                     ("B3", "no vision-assisted identification up to research grade", slow & ~vrg, fast & ~vrg),
                     ("B4", "one photograph only", slow & np1, fast & np1),
                     ("B5", "without observations with a withdrawn identification", slow & ~wd, fast & ~wd),
                     ("B5", "without observations with a non-ancestor identification above species rank",
                      slow & ~na, fast & ~na),
                     ("B5", "without either", slow & ~wd & ~na, fast & ~wd & ~na),
                     ("B6", "fast = T < 6 h", tdef & (T >= 0.25), tdef & (T < 0.25)),
                     ("B6", "fast = T < 12 h", tdef & (T >= 0.5), tdef & (T < 0.5)),
                     ("B6", "fast = T < 48 h", tdef & (T >= 2), tdef & (T < 2)),
                     ("B6", "fast = T < 7 days", tdef & (T >= 7), tdef & (T < 7)),
                     ("B6", "slowest fifth vs fastest fifth within family", q_slow, q_fast),
                     ("B9", "prior exposure: yes", slow & ex, fast & ex),
                     ("B9", "prior exposure: no", slow & ~ex, fast & ~ex)]
        for m in C.MODELS:
            e = 1 - d[f"c_{m}"].to_numpy(float)
            for item, lab, ms, mf in contrasts:
                res, r = C.contrast(W, D, e, ms, mf)
                for x in res:
                    x.update({"item": item, "contrast": lab, "set": s, "hypothesis": C.HYP[s], "model": m,
                              "slow_rows": int(ms.sum()), "fast_rows": int(mf.sum()),
                              "slow_weight_share_of_all_slow": C.wshare(w, ms, slow),
                              "fast_weight_share_of_all_fast": C.wshare(w, mf, fast)})
                    rows.append(x)
                if item == "main" and m == "Z25":
                    est = pd.read_csv(C.CONF / s / "estimates.csv")
                    ref = est[(est["model"] == m) & (est["quantity"] == "Delta") & (est["unit"] == "pooled")]["value"].iloc[0]
                    log.check(f"{s}: main contrast reproduces the stored Delta", abs(res[0]["Delta"] - ref) < 1e-9,
                              f"{res[0]['Delta']:.6f} vs {ref:.6f}")
        # shares (weighted by the phase-2 weights, pooled over the families of the set)
        def sh(name, mask, within, wname):
            shares.append({"set": s, "share": name, "within": wname, "weighted_share": C.wshare(w, mask, within),
                           "rows": int((mask & within).sum()), "rows_within": int(within.sum())})
        sh("T_wait < 1 day", tw < 1, slow, "slow")
        sh("T_wait >= 1 day", tw >= 1, slow, "slow")
        for cat in ("none", "above species rank", "species rank"):
            sh(f"own identification at creation: {cat}", own == cat, fast, "fast")
            sh(f"own identification at creation: {cat}", own == cat, slow, "slow")
        sh("observer's earliest identification later than 1 h after creation", d["own_first_later_than_1h"].to_numpy(bool),
           tdef, "research with T")
        for nm, mk in (("vision-assisted identification up to research grade", vrg), ("any vision-assisted identification", vany),
                       ("one photograph only", np1), ("any withdrawn identification", wd),
                       ("any non-ancestor identification above species rank", na), ("prior exposure", ex)):
            sh(nm, mk, fast, "fast")
            sh(nm, mk, slow, "slow")
        # T_wait and T_res (weighted medians among slow)
        for nm, mk in (("looked at early", slow & (tw < 1)), ("waited", slow & (tw >= 1))):
            for var, vals in (("T_wait", tw), ("T_res", T - tw)):
                k = np.flatnonzero(mk)
                o = k[np.argsort(vals[k], kind="stable")]
                cw = np.cumsum(w[o])
                shares.append({"set": s, "share": f"weighted median {var} (days), slow {nm}", "within": "slow",
                               "weighted_share": float(vals[o][np.searchsorted(cw, cw[-1] / 2)]), "rows": int(len(k)),
                               "rows_within": int(slow.sum())})
        # B8: resolving identifiers
        st = d["stratum"].to_numpy()
        res_u = d["resolver"].to_numpy()
        a23 = tdef & np.isin(st, ["A2", "A3"])
        cnt = pd.Series(res_u[a23]).value_counts()
        top10 = set(cnt.index[:10])
        day = pd.to_datetime(pd.Series(d["resolve_ns"]).where(d["resolve_ns"].notna()).astype("float"), unit="ns").dt.date
        rd = pd.DataFrame({"r": res_u, "day": day})[tdef]
        per_day = rd.groupby(["r", "day"]).size()
        rd23 = pd.DataFrame({"r": res_u, "day": day})[a23].groupby(["r", "day"]).size()
        b8.append({"set": s, "A2_A3_rows": int(a23.sum()), "resolving_identifiers_A2_A3": int(cnt.size),
                   "share_A2_A3_resolved_by_top10": float(np.isin(res_u[a23], list(top10)).mean()),
                   "top10_counts": ";".join(str(int(x)) for x in cnt.iloc[:10].to_numpy()),
                   "share_all_research_resolved_by_top10_of_A2_A3": float(np.isin(res_u[tdef], list(top10)).mean()),
                   "max_resolved_by_one_identifier_on_one_day_all_research": int(per_day.max()),
                   "max_resolved_by_one_identifier_on_one_day_A2_A3": int(rd23.max()),
                   "resolving_identifiers_all_research": int(pd.Series(res_u[tdef]).nunique()),
                   "resolver_is_observer_rows": int(sum(1 for u_, u2 in zip(res_u[tdef], d["observation_uuid"].to_numpy()[tdef])
                                                     if pd.notna(u_) and int(u_) == rec[u2]["owner"]))})
        # two-way cluster bootstrap (observer and resolving identifier)
        rng2 = np.random.default_rng(C.SEED)
        obs_u, oi = np.unique(D.observer, return_inverse=True)
        rkey = np.array([int(x) if pd.notna(x) else -1 for x in res_u])
        ru, ri = np.unique(rkey, return_inverse=True)
        W2 = np.empty_like(W)
        W2[0] = w
        nores = rkey < 0
        for b in range(1, W.shape[0]):
            mo = np.bincount(rng2.integers(0, len(obs_u), len(obs_u)), minlength=len(obs_u))[oi]
            mr = np.bincount(rng2.integers(0, len(ru), len(ru)), minlength=len(ru))[ri]
            W2[b] = w * mo * np.where(nores, 1, mr)
        for m in C.MODELS:
            e = 1 - d[f"c_{m}"].to_numpy(float)
            res, _ = C.contrast(W2, D, e, slow, fast)
            for x in res:
                x.update({"item": "B8", "contrast": "slow vs fast, two-way cluster bootstrap (observer x resolving identifier)",
                          "set": s, "hypothesis": C.HYP[s], "model": m, "slow_rows": int(slow.sum()), "fast_rows": int(fast.sum())})
                rows.append(x)
        del W2
        # B11 (eight_W only): accuracy ranks by stratum
        if s == "eight_W":
            acc = {}
            for m in C.MODELS:
                c = d[f"c_{m}"].to_numpy(float)
                for stv in ("A0", "A1", "A2", "A3"):
                    fa = [c[tdef & (st == stv) & (D.fam == j)].mean() for j in range(D.F)]
                    acc[(m, stv)] = float(np.mean(fa))
            for stv in ("A0", "A1", "A2", "A3"):
                vals = {m: acc[(m, stv)] for m in C.MODELS}
                rk = stats.rankdata([-vals[m] for m in C.MODELS])
                for m, rr in zip(C.MODELS, rk):
                    b11.append({"stratum": stv, "model": m, "accuracy_equal_family_mean": vals[m], "rank": float(rr)})
            R = pd.DataFrame(b11).pivot(index="model", columns="stratum", values="rank").loc[C.MODELS]
            msum = R.sum(axis=1).to_numpy()
            mrat, nobj = R.shape[1], R.shape[0]
            kw = 12 * ((msum - msum.mean()) ** 2).sum() / (mrat ** 2 * (nobj ** 3 - nobj))
            b11.append({"stratum": "Kendall W over A0-A3", "model": "all", "accuracy_equal_family_mean": np.nan, "rank": float(kw)})
        # B10 data for the supplement (eight_W rows with T; used by d19_part_c.py if scores are produced there)
        if s == "eight_W":
            d.loc[tdef, ["observation_uuid", "T", "species", "observer_id"]].to_parquet(OUT / "b10_rows_eight_W.parquet", index=False)
        log(f"{s}: done in {(time.time() - t0) / 60:.1f} min")
        del W
    C.save_csv(pd.DataFrame(rows), OUT / "B_contrasts.csv")
    C.save_csv(pd.DataFrame(shares), OUT / "B_shares.csv")
    C.save_csv(pd.DataFrame(b8), OUT / "B8_resolvers.csv")
    C.save_csv(pd.DataFrame(b11), OUT / "B11_ranks.csv")

    # B7: random-effects summaries
    tx = pd.read_csv(C.OUT / "snapshot/families_taxonomy.csv").set_index("family")
    fam_rows = []
    for s in ("eight_W", "new_W", "replication_W"):
        est = pd.read_csv(C.CONF / s / "estimates.csv")
        for q in ("Delta", "ER"):
            e_ = est[(est["model"] == "Z25") & (est["quantity"] == q) & ~est["unit"].isin(["pooled", "animals", "plants", "families"])]
            e_ = e_[e_["unit"].isin(tx.index)]
            for r in e_.itertuples():
                fam_rows.append({"set": s, "family": r.unit, "quantity": q, "value": r.value, "lo95": r.lo95, "hi95": r.hi95})
    fr = pd.DataFrame(fam_rows)
    dW = fr[(fr["quantity"] == "Delta") & fr["set"].isin(["eight_W", "new_W"])].set_index("family")
    eW = fr[(fr["quantity"] == "ER") & fr["set"].isin(["eight_W", "new_W"])].set_index("family")
    fams14 = sorted(dW.index)
    cls = tx.loc[fams14, "class"].to_numpy()
    yD = dW.loc[fams14, "value"].to_numpy()
    vD = ((dW.loc[fams14, "hi95"] - dW.loc[fams14, "lo95"]).to_numpy() / 3.919928) ** 2
    yE = np.log(eW.loc[fams14, "value"].to_numpy())
    vE = ((np.log(eW.loc[fams14, "hi95"]) - np.log(eW.loc[fams14, "lo95"])).to_numpy() / 3.919928) ** 2
    b7 = [re_summary("Delta, 14 families of W", yD, vD), re_summary("Delta, 14 families of W, class random effect", yD, vD, cls),
          re_summary("log ER, 14 families of W", yE, vE), re_summary("log ER, 14 families of W, class random effect", yE, vE, cls)]
    for r in b7:
        if r["quantity"].startswith("log ER"):
            for k_ in ("estimate", "lo95", "hi95", "prediction_lo95", "prediction_hi95"):
                r[k_.replace("estimate", "ER") + ("" if k_ == "estimate" else "_ER")] = float(np.exp(r[k_]))
    # H6 meta-regression over the 36 families
    h6 = json.loads((C.CONF / "h6.json").read_text(encoding="utf-8"))
    d36 = fr[(fr["quantity"] == "Delta") & fr["set"].isin(["new_W", "replication_W"])].set_index("family")
    f36 = sorted(h6["delta"])
    y36 = d36.loc[f36, "value"].to_numpy()
    log.check("B7 family Delta of the 36 H6 families equal h6.json", np.allclose(y36, [h6["delta"][f] for f in f36], atol=1e-9))
    v36 = ((d36.loc[f36, "hi95"] - d36.loc[f36, "lo95"]).to_numpy() / 3.919928) ** 2
    x36 = np.array([h6["fast_share"][f] for f in f36])
    c36 = tx.loc[f36, "class"].to_numpy()
    X = np.column_stack([np.ones(36), x36])
    mr = reml(y36, v36, X, c36)
    b1, se1 = float(mr["b"][1]), float(np.sqrt(mr["cov"][1, 1]))
    mr0 = reml(y36, v36, X, None)
    meta = [{"model": "family and class random effects", "slope_per_unit_fast_share": b1, "se": se1, "lo95": b1 - 1.959964 * se1,
             "hi95": b1 + 1.959964 * se1, "p_two_sided": float(2 * stats.norm.sf(abs(b1 / se1))),
             "intercept": float(mr["b"][0]), "tau_family": mr["tau_f"], "tau_class": mr["tau_g"], "converged": mr["converged"]},
            {"model": "family random effect only", "slope_per_unit_fast_share": float(mr0["b"][1]),
             "se": float(np.sqrt(mr0["cov"][1, 1])), "lo95": float(mr0["b"][1] - 1.959964 * np.sqrt(mr0["cov"][1, 1])),
             "hi95": float(mr0["b"][1] + 1.959964 * np.sqrt(mr0["cov"][1, 1])),
             "p_two_sided": float(2 * stats.norm.sf(abs(mr0["b"][1] / np.sqrt(mr0["cov"][1, 1])))),
             "intercept": float(mr0["b"][0]), "tau_family": mr0["tau_f"], "tau_class": None, "converged": mr0["converged"]}]
    loo = []
    rng = np.random.default_rng(C.SEED)
    for c_ in sorted(set(c36)):
        k = c36 != c_
        rho, p, n = E.spearman_permutation(y36[k], x36[k], 10000, rng)
        loo.append({"class_left_out": c_, "families_left_out": int((~k).sum()), "families_used": n, "rho": rho,
                    "p_one_sided": p})
    rho_all = E.spearman(y36, x36)
    log.check("B7 Spearman rho over the 36 families equals h6.json", abs(rho_all - h6["rho"]) < 1e-12, f"{rho_all:.6f}")
    C.save_csv(pd.DataFrame(b7), OUT / "B7_random_effects.csv")
    C.save_csv(pd.DataFrame(meta), OUT / "B7_h6_meta_regression.csv")
    C.save_csv(pd.DataFrame(loo), OUT / "B7_h6_leave_one_class_out.csv")
    C.save_csv(pd.DataFrame({"family": fams14, "class": cls, "Delta": yD, "var_Delta": vD, "log_ER": yE, "var_log_ER": vE}),
               OUT / "B7_family_inputs_14.csv")
    C.save_csv(pd.DataFrame({"family": f36, "class": c36, "Delta": y36, "var_Delta": v36, "fast_share": x36}),
               OUT / "B7_family_inputs_36.csv")
    log("finished", time.strftime("%Y-%m-%d %H:%M:%S"), f"({(time.time() - log.t0) / 60:.1f} min)")
    log("FAILED CHECKS:", log.fails if log.fails else "none")


if __name__ == "__main__":
    main()
