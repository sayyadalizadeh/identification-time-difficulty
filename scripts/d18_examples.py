"""D18 with D18 addendum 1 (post hoc, docs/PLAN.md): illustrative panel of example photographs of quickly and slowly
identified observations. Not an analysis. Development half only; stored data only; no download.

Pool (addendum 1, a): research-grade rows of the D4 sample (window W: outputs/D6/rows.parquet for T and stratum,
outputs/D4/d4_sample.csv for the first photo and the snapshot licence, outputs/D4/predictions.parquet) and of the D13
rehearsal (window W2: outputs/D13/W2/phase2.parquet rows selected in phase 2, outputs/D13/W2/predictions.parquet), with
the stored medium first photographs (photo folders and manifests) and the stored API responses (observation id and image
attribution). Every input file is checked against the tier-1 SHA-256 manifest of N23; every drawn photograph against its
photo manifest.

Implementation details fixed before the run:
- Eligible observation: pooled row with a stored prediction of BioCLIP 2.5 Huge (model Z25) and a snapshot licence CC0
  or CC BY (addendum 1, b).
- Sides (addendum 1, c, applied per species): fast side = A0; slow side = A3 if the species has at least two eligible A3
  observations, otherwise A2 and A3 together.
- Species (addendum 1, d): among species with at least two eligible observations on each side, the largest number of
  eligible observations on the two sides together (fast plus slow); ties broken by the lower taxon id.
- Families (addendum 1, e): the first two families with such a species in the order Columbidae, Anatidae, Sciuridae,
  Nymphalidae (animals) and Fabaceae, Rosaceae, Lamiaceae, Asteraceae (plants); this order is checked against the
  per-family Delta of H1. If a group has fewer than two such families, no panel is built and this is reported.
- Draw (D18): one generator numpy.random.default_rng(20261124), used in panel order (animal families, then plant
  families) and, within a family, for the fast and then the slow side; candidates ordered by observation_uuid and
  permuted; the first two whose stored photograph is present (manifest status ok, file present, SHA-256 equal to the
  manifest) are used; skipped draws are reported as replacements.
Outputs: outputs/figures/Fig_examples.pdf and .png (300 dpi), outputs/figures/examples_selection.csv (no user names),
outputs/figures/examples_attribution.txt (user names or logins; git-ignored, never tracked), docs/reports/D18_report.md,
outputs/N25/d18_log.json. A rule that cannot be met ends with a message and a report, without a figure.
Usage: python scripts/d18_examples.py --plan-commit <D18 commit> --addendum-commit <addendum 1 commit>
"""
import os
THREADS = 20
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = str(THREADS)
import argparse  # noqa: E402
import gzip  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402
from PIL import Image  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.halves import is_locked  # noqa: E402

FIG = ROOT / "outputs/figures"
LOG = ROOT / "outputs/N25"
REPORT = ROOT / "docs/reports/D18_report.md"
TIER1 = ROOT / "outputs/retained/manifests/tier1_sha256.csv"
E1 = "inputs/earlier_gates/outputs/G-IG8.0/e1_species_primary.csv"
GROUPS = {"animals": ["Columbidae", "Anatidae", "Sciuridae", "Nymphalidae"],
          "plants": ["Fabaceae", "Rosaceae", "Lamiaceae", "Asteraceae"]}
SEED = 20261124
OK_LIC = {"CC0": "CC0", "CC-BY": "CC BY"}
SRC = {"W": {"photos": ROOT / "outputs/D4/photos", "raw": ROOT / "outputs/D4/api_raw_d4"},
       "W2": {"photos": ROOT / "outputs/D13/W2/photos", "raw": ROOT / "outputs/D13/W2/api_raw"}}
INK = "#222222"


class RuleNotMet(Exception):
    """The registered rule cannot be applied; D18 ends without a figure."""


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 24), b""):
            h.update(b)
    return h.hexdigest()


def norm_lic(s):
    """Licence code as CC0 / CC BY, or None for any other licence."""
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return None
    return OK_LIC.get(str(s).strip().upper().replace("_", "-"))


def check_inputs(ctl):
    man = pd.read_csv(TIER1).set_index("path")
    files = ["outputs/D6/rows.parquet", "outputs/D4/d4_sample.csv", "outputs/D4/predictions.parquet",
             "outputs/D4/photos/manifest.csv", "outputs/D13/W2/phase2.parquet", "outputs/D13/W2/predictions.parquet",
             "outputs/D13/W2/photos/manifest.csv", E1, "outputs/confirm/eight_W/estimates.csv",
             "configs/confirmatory.yaml"]
    for w in SRC.values():
        files += [p.relative_to(ROOT).as_posix() for p in sorted(w["raw"].glob("*.json.gz"))]
    bad = [r for r in files if r not in man.index or sha256(ROOT / r) != man.loc[r, "sha256"]]
    ctl["input files equal to the tier-1 manifest"] = (not bad, f"{len(files) - len(bad)} of {len(files)}")
    if bad:
        raise RuleNotMet(f"inputs differ from the tier-1 manifest: {bad[:5]}")


def pool(ctl):
    """Pooled research-grade rows of W (D4) and W2 (D13) with stratum, T, photo, snapshot licence and prediction."""
    rows = pd.read_parquet(ROOT / "outputs/D6/rows.parquet",
                           columns=["observation_uuid", "family", "sample_grade", "observer_id", "species", "T", "stratum"])
    smp = pd.read_csv(ROOT / "outputs/D4/d4_sample.csv", usecols=["observation_uuid", "first_photo_id", "extension",
                                                                   "license"])
    pr = pd.read_parquet(ROOT / "outputs/D4/predictions.parquet")
    pr = pr[pr["model"] == "Z25"].set_index("observation_uuid")
    w = rows[rows["sample_grade"] == "research"].merge(smp, on="observation_uuid", how="left")
    w["pred"] = w["observation_uuid"].map(pr["pred_species"])
    w["true"] = w["observation_uuid"].map(pr["true_species"])
    w["pred_photo"] = w["observation_uuid"].map(pr["photo_id"])
    w["window"] = "W"
    p2 = pd.read_parquet(ROOT / "outputs/D13/W2/phase2.parquet",
                         columns=["observation_uuid", "observer_id", "family", "grade", "species", "first_photo_id",
                                  "extension", "license_code", "T", "stratum", "selected"])
    ctl["D13 grade values known"] = (set(p2["grade"].unique()) <= {"research", "needs_id"},
                                     ", ".join(sorted(map(str, p2["grade"].unique()))))
    p13 = pd.read_parquet(ROOT / "outputs/D13/W2/predictions.parquet",
                          columns=["observation_uuid", "species", "p_Z25"]).set_index("observation_uuid")
    # D13 stores the licence as an index into frame.licences of configs/confirmatory.yaml (0 = CC0, 1 = CC-BY, ...);
    # the first run of N25 read these integers as text codes, so no W2 row was eligible (coding error, corrected here)
    licences = yaml.safe_load((ROOT / "configs/confirmatory.yaml").read_text(encoding="utf-8"))["frame"]["licences"]
    ctl["D13 licence codes are indices of frame.licences"] = (
        set(p2["license_code"].unique()) <= set(range(len(licences))), ", ".join(f"{i} = {x}" for i, x in enumerate(licences)))
    p2["license_code"] = p2["license_code"].map(dict(enumerate(licences)))
    v = p2[(p2["grade"] == "research") & p2["selected"]].rename(columns={"license_code": "license"})
    v = v.assign(pred=v["observation_uuid"].map(p13["p_Z25"]), true=v["observation_uuid"].map(p13["species"]),
                 pred_photo=v["first_photo_id"], window="W2")
    cols = ["observation_uuid", "observer_id", "family", "species", "T", "stratum", "first_photo_id", "extension",
            "license", "pred", "true", "pred_photo", "window"]
    allr = pd.concat([w[cols], v[cols]], ignore_index=True)
    allr = allr[allr["pred"].notna() & allr["stratum"].isin(["A0", "A2", "A3"])].copy()
    allr["species"] = allr["species"].astype(int)
    ctl["no locked observer in the pool"] = (int(sum(is_locked(int(o)) for o in allr["observer_id"].unique())) == 0,
                                             f"{allr['observer_id'].nunique():,} observers")
    ctl["prediction photo = first photo; community species = row species"] = (
        bool((allr["pred_photo"].astype(np.int64) == allr["first_photo_id"].astype(np.int64)).all()
             and (allr["true"].astype(int) == allr["species"]).all()), f"{len(allr):,} rows")
    ctl["no observation in both windows"] = (not allr["observation_uuid"].duplicated().any(), "")
    if not all(ctl[k][0] for k in ctl):
        raise RuleNotMet("a check of the pooled rows failed")
    allr["lic"] = allr["license"].map(norm_lic)
    return allr


def choose(el, name, kingdom, delta, ctl):
    """Species per family and the families of the panel (addendum 1, c to e)."""
    order_ok = all([f for f in delta.index if kingdom[f] == k][:4] == fams for k, fams in
                   (("Animalia", GROUPS["animals"]), ("Plantae", GROUPS["plants"])))
    ctl["family order = decreasing Delta of H1 within each group"] = (
        order_ok, "; ".join(f"{f} {v:.2f}" for f, v in delta.items()))
    if not order_ok:
        raise RuleNotMet("the family order of addendum 1 differs from the per-family Delta of H1")
    table, picked, notes = [], {}, []
    for g, fams in GROUPS.items():
        got = []
        for f in fams:
            e = el[el["family"] == f]
            c = pd.DataFrame({"A0": e[e["stratum"] == "A0"].groupby("species").size(),
                              "A2": e[e["stratum"] == "A2"].groupby("species").size(),
                              "A3": e[e["stratum"] == "A3"].groupby("species").size()}).fillna(0).astype(int)
            c["slow_side"] = np.where(c["A3"] >= 2, "A3", "A2+A3")
            c["slow"] = np.where(c["A3"] >= 2, c["A3"], c["A2"] + c["A3"])
            c["n"] = c["A0"] + c["slow"]
            c = c[(c["A0"] >= 2) & (c["slow"] >= 2)].reset_index(names="species").sort_values(
                ["n", "species"], ascending=[False, True])
            for k, x in enumerate(c.head(3).itertuples(index=False)):
                table.append({"family": f, "rank": k + 1, "taxon_id": int(x.species), "species": name[int(x.species)],
                              "A0": int(x.A0), "A2": int(x.A2), "A3": int(x.A3), "slow_side": x.slow_side,
                              "fast+slow": int(x.n)})
            if len(got) < 2:
                if len(c):
                    got.append(f)
                    picked[f] = (int(c.iloc[0]["species"]), c.iloc[0]["slow_side"])
                else:
                    notes.append(f"{f}: no species with two eligible observations on each side; replaced by the next "
                                 f"family of the {g}")
        if len(got) < 2:
            raise RuleNotMet(f"fewer than two {g} families with a valid species")
    return picked, table, notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-commit", required=True)
    ap.add_argument("--addendum-commit", required=True)
    a = ap.parse_args()
    t0 = time.time()
    ctl, info = {}, {"licences": {}, "species": [], "replacements_families": [], "skipped": []}
    sel = None
    try:
        check_inputs(ctl)
        e1 = pd.read_csv(ROOT / E1)
        kingdom = dict(zip(e1["family"], e1["kingdom"]))
        name = dict(zip(e1["species_taxon_id"].astype(int), e1["species"]))
        est = pd.read_csv(ROOT / "outputs/confirm/eight_W/estimates.csv")
        delta = est[(est["model"] == "Z25") & (est["quantity"] == "Delta") & ~est["unit"].isin(
            ["pooled", "animals", "plants", "families"])].set_index("unit")["value"].sort_values(ascending=False)
        allr = pool(ctl)
        el = allr[allr["lic"].notna()]
        info["licences"] = {"pooled rows A0, A2, A3 with a prediction": int(len(allr)),
                            "of which CC0 or CC BY in the snapshot": int(len(el)),
                            "W": int((el["window"] == "W").sum()), "W2": int((el["window"] == "W2").sum())}
        picked, info["species"], info["replacements_families"] = choose(el, name, kingdom, delta, ctl)

        # draw
        mans = {k: pd.read_csv(v["photos"] / "manifest.csv").set_index("photo_id") for k, v in SRC.items()}
        rng = np.random.default_rng(SEED)
        drawn = []
        for f, (sp, slow) in picked.items():
            for side, strata in (("fast", ["A0"]), ("slow", slow.split("+"))):
                c = el[(el["family"] == f) & (el["species"] == sp) & el["stratum"].isin(strata)].sort_values(
                    "observation_uuid").reset_index(drop=True)
                got = 0
                for k, i in enumerate(rng.permutation(len(c))):
                    x = c.iloc[i]
                    pid, m = int(x["first_photo_id"]), mans[x["window"]]
                    fp = SRC[x["window"]]["photos"] / f"{pid}.{x['extension']}"
                    if not (pid in m.index and m.loc[pid, "status"] == "ok" and fp.exists()
                            and sha256(fp) == m.loc[pid, "sha256"]):
                        info["skipped"].append({"family": f, "side": side, "draw": k + 1, "photo_id": pid})
                        continue
                    drawn.append({"family": f, "sp": sp, "side": side, "slow_side": slow, "draw": k + 1, "x": x, "file": fp})
                    got += 1
                    if got == 2:
                        break
                ctl[f"two photographs drawn: {f}, {side} side"] = (got == 2, f"{len(c)} candidates")
                if got < 2:
                    raise RuleNotMet(f"fewer than two stored photographs for {f}, {side} side")

        # API records (observation id, licence, attribution)
        need = {(d["x"]["observation_uuid"], int(d["x"]["first_photo_id"])) for d in drawn}
        api = {}
        for k, s in SRC.items():
            for p in sorted(s["raw"].glob("*.json.gz")):
                dd = json.load(gzip.open(p, "rt", encoding="utf-8"))
                for o in dd["results"] if "results" in dd else dd.get("response", {}).get("results", []):
                    u = o.get("user") or {}
                    for ph in o.get("photos") or []:
                        if (o["uuid"], int(ph["id"])) in need:
                            api[(o["uuid"], int(ph["id"]))] = {
                                "obs_id": int(o["id"]), "lic": norm_lic(ph.get("license_code")),
                                "attribution": ph.get("attribution"),
                                "who": (u.get("name") or "").strip() or u.get("login"), "owner": u.get("id")}
        ctl["every drawn photograph found in the stored responses"] = (len(api) == len(need), f"{len(api)} of {len(need)}")
        rows, att = [], []
        for d in drawn:
            x, r_ = d["x"], api.get((d["x"]["observation_uuid"], int(d["x"]["first_photo_id"])), {})
            T = float(x["T"])
            ok_T = {"A0": T < 1, "A2": 30 <= T < 365, "A3": T >= 365}[x["stratum"]]
            ctl.setdefault("stratum agrees with T for every drawn row", [True, ""])
            ctl["stratum agrees with T for every drawn row"][0] &= bool(ok_T)
            ctl.setdefault("photo owner = sample observer for every drawn row", [True, ""])
            ctl["photo owner = sample observer for every drawn row"][0] &= (r_.get("owner") == int(x["observer_id"]))
            rows.append({"family": d["family"], "species": name[d["sp"]], "side": d["side"],
                         "slow_side_rule": d["slow_side"], "stratum": x["stratum"], "window": x["window"],
                         "observation_id": r_.get("obs_id"), "observation_uuid": x["observation_uuid"],
                         "photo_id": int(x["first_photo_id"]), "licence": x["lic"],
                         "licence_in_response": r_.get("lic") or "other",
                         "days_to_research_grade": round(T, 3),
                         "model_prediction": name.get(int(x["pred"]), str(int(x["pred"]))),
                         "correct": "yes" if int(x["pred"]) == int(x["true"]) else "no", "draw": d["draw"]})
            att.append(f"{d['family']} | {name[d['sp']]} | {x['stratum']} ({x['window']}) | photo {int(x['first_photo_id'])} "
                       f"| © {r_.get('who')}, {x['lic']} | response attribution: {r_.get('attribution')}")
        ctl = {k: (bool(v[0]), v[1]) for k, v in ctl.items()}
        if not all(v[0] for v in ctl.values()):
            raise RuleNotMet("a check of the drawn rows failed")
        sel = pd.DataFrame(rows)
        sel.to_csv(FIG / "examples_selection.csv", index=False, lineterminator="\n", encoding="utf-8")
        (FIG / "examples_attribution.txt").write_text(
            "Attribution of the images of Fig_examples (D18, addendum 1). Contains user names or logins: never tracked "
            "or deposited.\n" + "\n".join(att) + "\n", encoding="utf-8", newline="\n")
        panel(sel, drawn)
        status = "done: panel built"
    except RuleNotMet as ex:
        status = f"ended without a figure: {ex}"
        print("D18:", status)
    report(a, ctl, info, sel, status, time.time() - t0)
    if sel is None:
        sys.exit(2)


def panel(sel, drawn):
    plt.rcParams.update({"font.size": 7.5, "font.family": "DejaVu Sans", "pdf.fonttype": 42})
    fams = list(dict.fromkeys(sel["family"]))
    fig = plt.figure(figsize=(7.0, 9.0))
    left, right, top, bottom = 0.075, 0.995, 0.96, 0.005
    cw, rh = (right - left) / 4, (top - bottom) / len(fams)
    for j, h in enumerate(["fast: A0", "fast: A0", "slow", "slow"]):
        fig.text(left + (j + 0.5) * cw, 0.99, h, ha="center", va="top", fontsize=8.5, fontweight="bold", color=INK)
    for i, f in enumerate(fams):
        y0 = top - (i + 1) * rh
        s = sel[sel["family"] == f].reset_index(drop=True)
        fig.text(0.012, y0 + rh * 0.58, f, rotation=90, ha="left", va="center", fontsize=8.5, fontweight="bold",
                 color=INK)
        fig.text(0.040, y0 + rh * 0.58, s.loc[0, "species"], rotation=90, ha="left", va="center", fontsize=8.5,
                 style="italic", color=INK)
        files = [d["file"] for d in drawn if d["family"] == f]
        for j in range(4):
            x = s.loc[j]
            ax = fig.add_axes([left + j * cw + 0.006, y0 + rh * 0.25, cw - 0.012, rh * 0.71])
            ax.imshow(np.asarray(Image.open(files[j]).convert("RGB")))
            ax.set_axis_off()
            T = x["days_to_research_grade"]
            tt = f"{T:.2f} days" if T < 1 else f"{T:,.0f} days"
            xc = left + (j + 0.5) * cw
            fig.text(xc, y0 + rh * 0.225, f"{x['stratum']}, window {x['window']}: {tt}", ha="center", va="top", color=INK)
            if x["correct"] == "yes":
                fig.text(xc, y0 + rh * 0.155, "model: correct", ha="center", va="top", color=INK)
            else:
                fig.text(xc, y0 + rh * 0.155, "model: wrong, predicted", ha="center", va="top", color=INK)
                fig.text(xc, y0 + rh * 0.09, x["model_prediction"], ha="center", va="top", style="italic", color=INK)
    fig.savefig(FIG / "Fig_examples.pdf")
    fig.savefig(FIG / "Fig_examples.png", dpi=300)
    plt.close(fig)


def report(a, ctl, info, sel, status, secs):
    L = ["# D18 - Illustrative panel of example photographs (post hoc)", "",
         f"Decision D18 in docs/PLAN.md (post hoc; registered in commit {a.plan_commit}) and D18 addendum 1 (commit "
         f"{a.addendum_commit}, before any draw). Illustrative figure, not an analysis. Script: scripts/d18_examples.py.",
         "", f"Status: {status}.", "",
         "First attempt under the rule of D18 (task N24): the run stopped at the choice of species, before any draw, "
         "because CC0 or CC BY photographs of stratum A3 were missing in Columbidae and Anatidae; no image or prediction "
         "was looked at and no output was written. Addendum 1 was registered after that.", "",
         "First run under addendum 1 (task N25): coding error. The D13 table stores the licence as an index into the "
         "licence list of configs/confirmatory.yaml (0 = CC0, 1 = CC-BY, 2 = CC-BY-NC); the script read these integers "
         "as text codes, so no W2 row was eligible and the pool held W rows only. The error was corrected and the run "
         "repeated with the same rule and seed; the outputs of the first run are kept in outputs/N25/"
         "run1_licence_code_error/ (not tracked). This report is that of the corrected run.", "",
         "## Implementation details fixed before the run", "",
         "- Eligible observation: research-grade row of the pooled D4 sample (W) and D13 rehearsal (W2, rows selected in "
         "phase 2) with a stored prediction of BioCLIP 2.5 Huge and a snapshot licence CC0 or CC BY.",
         "- Sides per species: fast = A0; slow = A3 if the species has at least two eligible A3 observations, otherwise A2 "
         "and A3 together.",
         "- Species: among species with at least two eligible observations on each side, the largest number of eligible "
         "observations on the two sides together; ties broken by the lower taxon id.",
         "- Families: the first two families with such a species in the registered order of each group.",
         f"- Draw: one generator (seed {SEED}) in panel order and, within a family, fast then slow; candidates ordered by "
         "observation_uuid and permuted; the first two whose stored photograph is present are used.", "",
         "## Controls", "", "| control | result | detail |", "|---|---|---|"]
    L += [f"| {k} | {'PASS' if v[0] else 'FAIL'} | {v[1]} |" for k, v in ctl.items()]
    L += ["", "## Counts", "", "| count | value |", "|---|---|"]
    L += [f"| {k} | {v:,} |" for k, v in info["licences"].items()]
    L += ["", "Family replacements: " + ("; ".join(info["replacements_families"]) or "none") + ".", "",
          "## Species (three largest counts per family, species with at least two eligible observations on each side)", "",
          "| family | rank | taxon id | species | A0 | A2 | A3 | slow side | fast+slow |", "|---|---|---|---|---|---|---|---|---|"]
    L += [f"| {c['family']} | {c['rank']} | {c['taxon_id']} | {c['species']} | {c['A0']} | {c['A2']} | {c['A3']} | "
          f"{c['slow_side']} | {c['fast+slow']} |" for c in info["species"]]
    if sel is not None:
        L += ["", "## Drawn observations", "",
              "| family | species | side | stratum | window | draw | observation id | photo id | licence | days to research "
              "grade | prediction of BioCLIP 2.5 Huge | correct |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        L += [f"| {x.family} | {x.species} | {x.side} | {x.stratum} | {x.window} | {x.draw} | {x.observation_id} | "
              f"{x.photo_id} | {x.licence} | {x.days_to_research_grade} | {x.model_prediction} | {x.correct} |"
              for x in sel.itertuples(index=False)]
        L += ["", "Replacements of drawn photographs that were not present: "
              + ("none." if not info["skipped"] else "; ".join(
                  f"{s['family']} {s['side']} draw {s['draw']} photo {s['photo_id']}" for s in info["skipped"]))]
    L += ["", f"Run time: {secs:.0f} s.", ""]
    REPORT.write_text("\n".join(L), encoding="utf-8", newline="\n")
    LOG.mkdir(parents=True, exist_ok=True)
    (LOG / "d18_log.json").write_text(json.dumps({"status": status, "controls": {k: list(v) for k, v in ctl.items()},
                                                  **info, "seconds": round(secs, 1)}, indent=1, ensure_ascii=False,
                                                 default=str), encoding="utf-8", newline="\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
