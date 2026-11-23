"""N20: base accuracies (Step 2), D15 (post hoc, docs/PLAN.md) and Fig3b, from the N18 outputs (read only).

Analysis rows of a set = the rows of the N18 analysis: phase-2 rows with a downloaded photograph and a prediction,
exact duplicates dropped with the rule of the frozen code (scripts/confirm_run.py, exact_duplicates); weights w of N18.
Step 2: weighted species-level accuracy on fast (T < 1 day), slow (T >= 1 day) and all research-grade rows, and weighted
genus-level accuracy on B1 and B2 rows, per model, set and family; pooled per set and per group with equal family
weights (groups: animals and plants of plan section 10, Polyporaceae alone; replication families by kingdom).
D15 (a)-(d): family values of N18 (outputs/confirm/h6.json; Delta_f and ER_f of BioCLIP 2.5 Huge from the per-family
outputs; E_ref,f = E_slow,f / ER_f with E_slow,f = (Delta_f / 100) ER_f / (ER_f - 1)). D15 (e): Delta and ER of A1, A2
and A3 against A0 per group within the sets of H1, H2 and H5, 2,000 observer-cluster bootstrap replicates (generator with
seed 20261121 for each set and group). Outputs: docs/reports/N20_tables.md, docs/reports/D15_report.md, outputs/D15/,
outputs/figures/Fig3b.pdf and .png, outputs/figures/captions_Fig3b.md.
Usage: python scripts/n20_run.py
"""
import os
THREADS = 20
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = str(THREADS)
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.stats import rankdata  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.confirm import acquisition as A  # noqa: E402
from src.confirm import estimators as E  # noqa: E402
from src.confirm.config import load_config  # noqa: E402

C = ROOT / "outputs/confirm"
CACHE = ROOT / "outputs/N20"
D15 = ROOT / "outputs/D15"
SETS = ["eight_W", "eight_W2", "new_W", "replication_W"]
MODELS = ["Z25", "Z2", "Z1", "BT-CLIP-O"]
NAMES = {"Z25": "BioCLIP 2.5 Huge", "Z2": "BioCLIP 2", "Z1": "first BioCLIP", "BT-CLIP-O": "BT-CLIP-O"}
SEED = 20261121


def f3(x):
    x = float(x)
    return "n/a" if not np.isfinite(x) else f"{x:.3f}"


def rows_of(s):
    p = CACHE / f"rows_{s}.parquet"
    if p.exists():
        return pd.read_parquet(p)
    import scripts.confirm_run as CR  # frozen code, used read-only
    p2 = pd.read_parquet(C / s / "phase2.parquet")
    pr = pd.read_parquet(C / s / "predictions.parquet")
    d = p2.merge(pr.drop(columns=["family", "grade", "species", "genus_label"]), on="observation_uuid", how="inner")
    man = pd.read_csv(C / s / "photos/manifest.csv").set_index("photo_id")
    rec, _ = A.parse_histories(C / s / "api_raw")
    d = d[~CR.exact_duplicates(d, man, rec)].reset_index(drop=True)
    keep = ["observation_uuid", "observer_id", "family", "grade", "species", "stratum", "T", "w"] + \
        [f"{k}_{m}" for m in MODELS for k in ("c", "g")]
    d = d[keep]
    CACHE.mkdir(parents=True, exist_ok=True)
    d.to_parquet(p, index=False)
    return d


def wmean(v, w):
    return float((v * w).sum() / w.sum()) if w.sum() > 0 else np.nan


def table(L, header, rows):
    L += ["| " + " | ".join(header) + " |", "|---" * len(header) + "|"]
    L += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    L.append("")


def groups_of(fams, cfg, kingdom):
    het = cfg["c3"]["heterogeneity"]
    g = {}
    for f in fams:
        if f in het["animals"]:
            g[f] = "animals"
        elif f in het["plants"]:
            g[f] = "plants"
        elif f in het["alone"]:
            g[f] = f
        else:
            g[f] = {"Animalia": "animals", "Plantae": "plants", "Fungi": "fungi"}[kingdom[f]]
    return g


def step2(cfg, kingdom):
    L = ["# N20 - Base accuracies", "",
         "Weighted means (N18 phase-2 weights) on the N18 analysis rows (script scripts/n20_run.py). Species-level "
         "accuracy on fast (T < 1 day), slow (T >= 1 day) and all research-grade rows; genus-level accuracy on the "
         "needs_id strata B1 (label support 0 or 1) and B2 (support at least 2). Pooled rows: equal family weights over "
         "the families of the set or group. Groups: animals and plants of plan section 10 and Polyporaceae alone; the "
         "replication families by kingdom. No interval is computed.", ""]
    out = []
    for s in SETS:
        d = rows_of(s)
        fams = sorted(d["family"].unique())
        grp = groups_of(fams, cfg, kingdom)
        rs = d[(d["grade"] == "research") & d["T"].notna()]
        for m in MODELS:
            for f in fams:
                r, n = rs[rs["family"] == f], d[(d["family"] == f) & (d["grade"] == "needs_id")]
                fa, sl = r[r["T"] < 1], r[r["T"] >= 1]
                b1, b2 = n[n["stratum"] == "B1"], n[n["stratum"] == "B2"]
                out.append({"set": s, "model": m, "unit": f, "group": grp[f], "acc_fast": wmean(fa[f"c_{m}"], fa["w"]),
                            "acc_slow": wmean(sl[f"c_{m}"], sl["w"]), "acc_all": wmean(r[f"c_{m}"], r["w"]),
                            "genus_B1": wmean(b1[f"g_{m}"], b1["w"]) if len(b1) else np.nan,
                            "genus_B2": wmean(b2[f"g_{m}"], b2["w"]) if len(b2) else np.nan,
                            "n_fast": len(fa), "n_slow": len(sl), "n_B1": len(b1), "n_B2": len(b2)})
    t = pd.DataFrame(out)
    cols = ["acc_fast", "acc_slow", "acc_all", "genus_B1", "genus_B2"]
    pooled = []
    for (s, m), g in t.groupby(["set", "model"], sort=False):
        pooled.append(dict({"set": s, "model": m, "unit": "pooled (all families)"}, **g[cols].mean().to_dict()))
        for gr, gg in g.groupby("group"):
            pooled.append(dict({"set": s, "model": m, "unit": f"group: {gr} ({len(gg)})"}, **gg[cols].mean().to_dict()))
    pt = pd.DataFrame(pooled)
    D15.mkdir(parents=True, exist_ok=True)
    t.to_csv(CACHE / "base_accuracy_family.csv", index=False, lineterminator="\n")
    pt.to_csv(CACHE / "base_accuracy_pooled.csv", index=False, lineterminator="\n")
    hdr = ["set", "model", "unit", "species accuracy, fast", "species accuracy, slow", "species accuracy, all research",
           "genus accuracy, B1", "genus accuracy, B2"]
    L += ["## Pooled per set and per group (all models)", ""]
    table(L, hdr, [[r.set, NAMES[r.model], r.unit] + [f3(getattr(r, c)) for c in cols] for r in pt.itertuples()])
    L += ["## Per family (every model; weighted accuracy with the number of rows in brackets)", ""]
    for m in MODELS:
        L += [f"### {NAMES[m]}", ""]
        tm = t[t["model"] == m]
        table(L, ["set", "family", "group", "fast (n)", "slow (n)", "all research", "genus B1 (n)", "genus B2 (n)"],
              [[r.set, r.unit, r.group, f"{f3(r.acc_fast)} ({r.n_fast:,})", f"{f3(r.acc_slow)} ({r.n_slow:,})",
                f3(r.acc_all), f"{f3(r.genus_B1)} ({r.n_B1:,})", f"{f3(r.genus_B2)} ({r.n_B2:,})"] for r in tm.itertuples()])
    (ROOT / "docs/reports/N20_tables.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    return len(L)


def spearman(x, y):
    return E.spearman(x, y)


def perm_p(stat_fn, y, n, rng, observed):
    cnt = 0
    for _ in range(n):
        if stat_fn(rng.permutation(y)) >= observed - 1e-12:
            cnt += 1
    return (1 + cnt) / (1 + n)


def partial(x, y, z):
    rx, ry, rz = rankdata(x), rankdata(y), rankdata(z)
    Z = np.column_stack([np.ones(len(rz)), rz])
    ex = rx - Z @ np.linalg.lstsq(Z, rx, rcond=None)[0]
    ey = ry - Z @ np.linalg.lstsq(Z, ry, rcond=None)[0]
    return float(np.corrcoef(ex, ey)[0, 1])


def d15_abcd(kingdom):
    h6 = json.loads((C / "h6.json").read_text(encoding="utf-8"))
    est = {s: pd.read_csv(C / s / "estimates.csv") for s in ("new_W", "replication_W")}
    fam = sorted(h6["delta"])
    rows = []
    for f in fam:
        s = "new_W" if f in est["new_W"]["unit"].values else "replication_W"
        e = est[s]
        er = float(e[(e["model"] == "Z25") & (e["quantity"] == "ER") & (e["unit"] == f)]["value"].iloc[0])
        dl = float(h6["delta"][f])
        es = (dl / 100) * er / (er - 1) if np.isfinite(er) and er != 1 else np.nan
        rows.append({"family": f, "kingdom": kingdom[f], "delta": dl, "er": er, "eref": es / er if np.isfinite(es) else np.nan,
                     "fast": float(h6["fast_share"][f])})
    t = pd.DataFrame(rows)
    res = {"families": int(len(t)), "kingdoms": t["kingdom"].value_counts().to_dict()}
    # (a) within kingdoms
    for k, lab in (("Animalia", "animals"), ("Plantae", "plants")):
        tk = t[t["kingdom"] == k]
        r = E.h6(dict(zip(tk["family"], tk["delta"])), dict(zip(tk["family"], tk["fast"])), 10000,
                 np.random.default_rng(SEED), n_boot=5000)
        res[f"a_{lab}"] = {k2: r[k2] for k2 in ("families_used", "rho", "p", "rho_lo95", "rho_hi95", "boot_undefined")}
    # (b) ER_f
    r = E.h6(dict(zip(t["family"], t["er"])), dict(zip(t["family"], t["fast"])), 10000, np.random.default_rng(SEED))
    res["b_ER"] = {k2: r[k2] for k2 in ("families_used", "rho", "p")}
    # (c) E_ref and partial
    ok = t[np.isfinite(t["eref"])]
    r = E.h6(dict(zip(ok["family"], ok["eref"])), dict(zip(ok["family"], ok["fast"])), 10000, np.random.default_rng(SEED))
    res["c_Eref"] = {k2: r[k2] for k2 in ("families_used", "rho", "p")}
    x, y, z = ok["delta"].to_numpy(), ok["fast"].to_numpy(), ok["eref"].to_numpy()
    obs = partial(x, y, z)
    res["c_partial"] = {"families_used": int(len(ok)), "partial_rho": obs,
                        "p": perm_p(lambda yy: partial(x, yy, z), y, 10000, np.random.default_rng(SEED), obs)}
    # (d) stratified permutation within kingdom
    for lab, poly in (("Polyporaceae excluded", None), ("Polyporaceae with the plants", "Plantae")):
        tt = t.copy()
        tt["k"] = tt["kingdom"].replace({"Fungi": poly}) if poly else tt["kingdom"]
        tt = tt[tt["k"].isin(["Animalia", "Plantae"])].reset_index(drop=True)
        idx = {k: np.flatnonzero((tt["k"] == k).to_numpy()) for k in ("Animalia", "Plantae")}
        xd, yf = tt["delta"].to_numpy(), tt["fast"].to_numpy()

        def stat(yy):
            return sum(len(ix) * spearman(xd[ix], yy[ix]) for ix in idx.values())

        o = stat(yf)
        rng = np.random.default_rng(SEED)
        cnt = 0
        for _ in range(10000):
            yp = yf.copy()
            for ix in idx.values():
                yp[ix] = rng.permutation(yf[ix])
            cnt += stat(yp) >= o - 1e-12
        res[f"d_{lab}"] = {"families": {k: int(len(v)) for k, v in idx.items()},
                           "within_rho": {k: spearman(xd[v], yf[v]) for k, v in idx.items()},
                           "statistic": o, "statistic_scaled_rho": o / len(tt), "p": (1 + cnt) / (1 + 10000)}
    t.to_csv(D15 / "family_values.csv", index=False, lineterminator="\n")
    return res, t


def d15_e(cfg):
    het = cfg["c3"]["heterogeneity"]
    out = []
    for s, h in (("eight_W", "H1"), ("new_W", "H2"), ("eight_W2", "H5")):
        d = rows_of(s)
        for g in ("animals", "plants"):
            r = d[d["family"].isin(het[g]) & (d["grade"] == "research") & d["T"].notna()].reset_index(drop=True)
            fam_i, fams = pd.factorize(r["family"])
            key = pd.Series([f"{a}|{b}" for a, b in zip(fam_i, r["species"].astype(np.int64))])
            spi, spu = pd.factorize(key)
            spf = np.array([int(k.split("|")[0]) for k in spu])
            W = E.boot_matrix(r["observer_id"].to_numpy(), r["w"].to_numpy(float), 2000, np.random.default_rng(SEED))
            e = 1 - r["c_Z25"].to_numpy(float)
            T = r["T"].to_numpy(float)
            st = np.select([T < 1, T < 30, T < 365], ["A0", "A1", "A2"], "A3")
            for a in ("A1", "A2", "A3"):
                c = E.c1(W, spi, spf, e, st == a, st == "A0", len(fams))
                left = [fams[j] for j in range(len(fams)) if not c["est"][j]]
                lo, hi = E.interval(c["Delta"])
                elo, ehi = E.interval(c["ER"])
                out.append({"hypothesis set": h, "set": s, "group": g, "families": len(fams), "stratum": a,
                            "slow_rows": int((st == a).sum()), "fast_rows": int((st == "A0").sum()),
                            "Delta": float(c["Delta"][0]), "Delta_lo95": lo, "Delta_hi95": hi,
                            "ER": float(c["ER"][0]), "ER_lo95": elo, "ER_hi95": ehi,
                            "families_left_out": ";".join(left)})
    t = pd.DataFrame(out)
    t.to_csv(D15 / "e_shape_by_group.csv", index=False, lineterminator="\n")
    return t


def fig3b(t):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 8, "axes.edgecolor": "#6b6b6b", "axes.labelcolor": "#222222",
                         "xtick.color": "#6b6b6b", "ytick.color": "#6b6b6b", "axes.spines.top": False,
                         "axes.spines.right": False, "pdf.fonttype": 42, "font.family": "DejaVu Sans"})
    col = {"animals": "#2a78d6", "plants": "#eb6834"}
    mk = {"eight_W": "o", "eight_W2": "s", "new_W": "D"}
    lab = {"eight_W": "eight families, W", "eight_W2": "eight families, W2", "new_W": "six new families, W"}
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.3), sharey=True)
    for ax, g in zip(axes, ("animals", "plants")):
        for k, s in enumerate(("eight_W", "eight_W2", "new_W")):
            r = t[(t["group"] == g) & (t["set"] == s)].set_index("stratum").loc[["A1", "A2", "A3"]]
            x = np.arange(3) + (k - 1) * 0.2
            ax.errorbar(x, r["Delta"], yerr=[r["Delta"] - r["Delta_lo95"], r["Delta_hi95"] - r["Delta"]], fmt=mk[s],
                        ms=5, color=col[g], ecolor=col[g], elinewidth=1.2, capsize=0, label=lab[s],
                        markerfacecolor=col[g] if s != "eight_W2" else "white")
        ax.axhline(0, color="#6b6b6b", lw=0.8)
        ax.grid(axis="y", color="#e3e3e3", lw=0.6)
        ax.set_axisbelow(True)
        ax.set_xticks(range(3))
        ax.set_xticklabels(["A1 (1-30 d)", "A2 (30-365 d)", "A3 (365 d +)"])
        ax.set_title(g, color="#222222")
    axes[0].set_ylabel("Δ against A0 (points)")
    axes[0].legend(frameon=False, loc="upper left")
    fig.tight_layout()
    out = ROOT / "outputs/figures"
    fig.savefig(out / "Fig3b.pdf")
    fig.savefig(out / "Fig3b.png", dpi=300)
    plt.close(fig)
    (out / "captions_Fig3b.md").write_text(
        "# Draft caption of Fig3b\n\n"
        "Draft caption (post hoc, D15(e)): Shape of the gradient by group (BioCLIP 2.5 Huge): Δ of observations "
        "identified in 1 to 30 days (A1), 30 to 365 days (A2) and 365 days or more (A3), each against fast observations "
        "(A0) of the same species, pooled with equal family weights within animals (left) and plants (right), in the sets "
        "of H1 (eight families, W), H5 (eight families, W2; open squares) and H2 (six new families, W); 95% "
        "observer-bootstrap intervals (2,000 replicates; N18 weights). Post hoc analysis.\n\n"
        "Source: outputs/D15/e_shape_by_group.csv (columns Delta, Delta_lo95, Delta_hi95), computed by "
        "scripts/n20_run.py from the N18 analysis rows (outputs/confirm/<set>/phase2.parquet and predictions.parquet).\n",
        encoding="utf-8", newline="\n")


def report(res, t, te):
    L = ["# D15 - Robustness of the relation across families and shape of the gradient by group (post hoc)", "",
         "Decision D15 in docs/PLAN.md (post hoc, written after the confirmatory results were seen; registered in commit "
         "c79ade7 before any part of D15 was run). Everything below is post hoc and descriptive; the registered results "
         "(docs/reports/confirmatory_results.md) stay primary. BioCLIP 2.5 Huge. Script: scripts/n20_run.py; outputs in "
         "outputs/D15/. Permutation p-values are one-sided, (1 + number of permuted statistics at or above the observed) / "
         "(1 + 10,000), generator with seed 20261121 for each test.", "",
         f"Families: {res['families']} ({', '.join(f'{k} {v}' for k, v in res['kingdoms'].items())}). Family values: "
         "Delta_f and the share of fast observations from outputs/confirm/h6.json; ER_f from the per-family outputs; "
         "E_ref,f = E_slow,f / ER_f with E_slow,f = (Delta_f / 100) ER_f / (ER_f - 1).", "",
         "## (a) Within kingdoms (Delta_f against the share of fast observations)", "",
         "| families | n | rho | p | 95% interval (5,000 bootstrap replicates over families) | replicates with undefined rho |",
         "|---|---|---|---|---|---|"]
    for lab in ("animals", "plants"):
        r = res[f"a_{lab}"]
        L.append(f"| {lab} | {r['families_used']} | {r['rho']:.3f} | {r['p']:.4f} | [{r['rho_lo95']:.3f}, "
                 f"{r['rho_hi95']:.3f}] | {r['boot_undefined']} |")
    b, c, cp = res["b_ER"], res["c_Eref"], res["c_partial"]
    L += ["", "## (b) ER_f against the share of fast observations", "",
          f"rho = {b['rho']:.3f}, p = {b['p']:.4f} ({b['families_used']} families).", "",
          "## (c) Reference error and partial correlation", "",
          f"Spearman rho between E_ref,f and the share of fast observations: {c['rho']:.3f} (p for rho > 0: {c['p']:.4f}; "
          f"{c['families_used']} families).", "",
          f"Partial Spearman correlation between Delta_f and the share of fast observations given E_ref,f (Pearson "
          f"correlation of the residuals of the ranks): {cp['partial_rho']:.3f}, p = {cp['p']:.4f} (permutation of the "
          f"share of fast observations; {cp['families_used']} families).", "",
          "## (d) Stratified permutation within kingdom", "",
          "| variant | families (animals, plants) | rho animals | rho plants | statistic (sum of n x rho) | statistic / n | p |",
          "|---|---|---|---|---|---|---|"]
    for lab in ("Polyporaceae excluded", "Polyporaceae with the plants"):
        r = res[f"d_{lab}"]
        L.append(f"| {lab} | {r['families']['Animalia']}, {r['families']['Plantae']} | {r['within_rho']['Animalia']:.3f} | "
                 f"{r['within_rho']['Plantae']:.3f} | {r['statistic']:.3f} | {r['statistic_scaled_rho']:.3f} | {r['p']:.4f} |")
    L += ["", "## (e) Delta and ER of A1, A2 and A3 against A0 per group", "",
          "Within each set and group: research-grade analysis rows of N18 with their weights; strata from T (A0 < 1 day, "
          "A1 1-30, A2 30-365, A3 365 days or more); reference = A0 rows of the same species; equal family weights; "
          "2,000 observer-cluster bootstrap replicates (seed 20261121 for each set and group).", "",
          "| set | group | families | stratum | rows (stratum / A0) | Delta [95%] | ER [95%] | families left out |",
          "|---|---|---|---|---|---|---|---|"]
    for r in te.itertuples():
        L.append(f"| {r.set} ({getattr(r, '_1')}) | {r.group} | {r.families} | {r.stratum} | {r.slow_rows:,} / "
                 f"{r.fast_rows:,} | {r.Delta:.3f} [{r.Delta_lo95:.3f}, {r.Delta_hi95:.3f}] | {r.ER:.3f} "
                 f"[{r.ER_lo95:.3f}, {r.ER_hi95:.3f}] | {r.families_left_out or 'none'} |")
    L += ["", "## Family values used in (a) to (d)", "", "| family | kingdom | Delta_f | ER_f | E_ref,f | share fast |",
          "|---|---|---|---|---|---|"]
    for r in t.sort_values("fast").itertuples():
        L.append(f"| {r.family} | {r.kingdom} | {r.delta:.3f} | {f3(r.er)} | {f3(r.eref)} | {r.fast:.3f} |")
    L.append("")
    (ROOT / "docs/reports/D15_report.md").write_text("\n".join(L), encoding="utf-8", newline="\n")


def main():
    cfg = load_config()
    e1 = pd.read_csv(ROOT / "inputs/earlier_gates/outputs/G-IG8.0/e1_species_primary.csv").drop_duplicates("family")
    kingdom = dict(zip(e1["family"], e1["kingdom"]))
    n = step2(cfg, kingdom)
    print("N20_tables.md lines:", n)
    res, t = d15_abcd(kingdom)
    (D15 / "abcd.json").write_text(json.dumps(res, indent=1, default=float), encoding="utf-8", newline="\n")
    te = d15_e(cfg)
    fig3b(te)
    report(res, t, te)
    print(json.dumps(res, indent=1, default=float)[:2000])


if __name__ == "__main__":
    main()
