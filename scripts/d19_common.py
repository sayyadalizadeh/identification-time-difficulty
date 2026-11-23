"""Shared code of D19 (post hoc analyses requested by pre-submission reviews; docs/PLAN.md, D19).

Every output of D19 is post hoc; the registered confirmatory results stay the primary results.

- Paths, seed (20261124) and thread counts of D19.
- load_rows(set): the analysis rows of one confirmatory set as in scripts/confirm_run.py (prepare_rows without the
  covariates, the identifier measures and the guard log): phase-2 rows with a prediction, exact SHA-256 duplicates
  dropped with the frozen function confirm_run.exact_duplicates (lowest observation id kept); the parsed histories are
  returned with the rows. Only stored files of outputs/confirm/<set>/ are read; nothing there is written.
- Design: the species grouping of src/confirm/analysis.py (family|species of research rows).
- contrast(): Delta and ER of the frozen estimator src/confirm/estimators.c1 for given slow and fast masks, pooled with
  equal family weights and by group (animals, plants), with 95% percentile intervals of the observer-cluster bootstrap
  (weight matrix from estimators.boot_matrix).
"""
import os

THREADS = 20
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, str(THREADS))
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from src import d6_lib as L  # noqa: E402
from src.confirm import acquisition as A  # noqa: E402
from src.confirm import analysis as AN  # noqa: E402
from src.confirm import estimators as E  # noqa: E402
import confirm_run as CR  # noqa: E402  (frozen; only its function exact_duplicates is used)

SEED = 20261124
OUT = ROOT / "outputs" / "D19"
CONF = ROOT / "outputs" / "confirm"
SETS = ["eight_W", "eight_W2", "new_W", "replication_W"]
MODELS = ["Z25", "Z2", "Z1", "BT-CLIP-O"]
MODEL_NAMES = {"Z25": "BioCLIP 2.5 Huge", "Z2": "BioCLIP 2", "Z1": "first BioCLIP", "BT-CLIP-O": "BT-CLIP-O"}
HYP = {"eight_W": "H1", "new_W": "H2", "eight_W2": "H5"}
ANIMALS, PLANTS = AN.ANIMALS, AN.PLANTS
DAY = L.DAY_NS


def spec(name):
    return json.loads((CONF / f"spec_{name}.json").read_text(encoding="utf-8"))


def save_json(p, obj):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=1, default=str)


def save_csv(df, p):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False, lineterminator="\n")


class Log:
    """Readable log with explicit PASS/FAIL controls (rule 4)."""

    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lines, self.fails = [], []
        self.t0 = time.time()

    def __call__(self, *x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        self.lines.append(s)
        self.path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")

    def check(self, name, ok, detail=""):
        self(f"CHECK {name}: {'PASS' if ok else 'FAIL'} {detail}")
        if not ok:
            self.fails.append(name)
        return ok


# ---------------------------------------------------------------- rows of one set
def load_rows(name):
    """Analysis rows of one set (as confirm_run.prepare_rows, without covariates and identifier measures) and the
    parsed histories {uuid: record}."""
    o = CONF / name
    p2 = pd.read_parquet(o / "phase2.parquet")
    pr = pd.read_parquet(o / "predictions.parquet")
    rec, _ = A.parse_histories(o / "api_raw")
    d = p2.merge(pr.drop(columns=["family", "grade", "species", "genus_label"]), on="observation_uuid", how="inner")
    man = pd.read_csv(o / "photos/manifest.csv").set_index("photo_id")
    drop = CR.exact_duplicates(d, man, rec)
    d = d[~drop].reset_index(drop=True)
    for col in ("support", "support_other", "agreeing", "disagreeing_now", "T_within_horizon", "disagreement", "vision"):
        if col not in d:
            d[col] = np.nan
    d["genus"] = d["genus_label"]
    return d, rec


class Design:
    """Family and species codes of a set's rows, exactly as in src/confirm/analysis.analyse."""

    def __init__(self, d):
        self.fam, self.fams = AN._codes(d["family"])
        self.F = len(self.fams)
        self.isR = (d["grade"] == "research").to_numpy()
        self.T = d["T"].to_numpy(float)
        self.tdef = self.isR & np.isfinite(self.T)
        self.slow, self.fast = self.tdef & (self.T >= 1), self.tdef & (self.T < 1)
        spv = np.where(self.isR, d["species"].fillna(-1).to_numpy(), -1).astype(np.int64)
        key = pd.Series([f"{f}|{s}" for f, s in zip(self.fam, spv)])
        self.sp_idx, sp_u = AN._codes(key)
        self.sp_fam = np.array([int(k.split("|")[0]) for k in sp_u])
        self.groups = {"animals": [j for j, f in enumerate(self.fams) if f in ANIMALS],
                       "plants": [j for j, f in enumerate(self.fams) if f in PLANTS]}
        self.w = d["w"].to_numpy(float)
        self.observer = d["observer_id"].to_numpy()


def ci(x):
    lo, hi = E.interval(x)
    return float(np.asarray(x, float)[0]), lo, hi


def contrast(W, D, e, slow, fast, units=("pooled", "animals", "plants")):
    """Delta and ER (point and 95% percentile interval) pooled with equal family weights and by group, with the
    frozen c1 estimator and the not-estimable rule; returns (list of dict rows, c1 result)."""
    r = E.c1(W, D.sp_idx, D.sp_fam, e, slow, fast, D.F)
    rows = []
    for u in units:
        if u == "pooled":
            dl, er, left = r["Delta"], r["ER"], AN._left(D.fams, r["est"])
        else:
            ix = D.groups[u]
            if not ix:
                continue
            gm = np.zeros(D.F, bool)
            gm[ix] = r["est"][ix]
            dl, er, left = E.pool_mean(r["Delta_f"], gm)[0], E.pool_ratio(r["E_slow"], r["E_ref"], gm), \
                AN._left(D.fams, r["est"], ix)
        d0, dlo, dhi = ci(dl)
        e0, elo, ehi = ci(er)
        rows.append({"unit": u, "Delta": d0, "Delta_lo95": dlo, "Delta_hi95": dhi, "ER": e0, "ER_lo95": elo,
                     "ER_hi95": ehi, "families_left_out": ";".join(left)})
    return rows, r


def wshare(w, mask, within):
    s = float((w * within).sum())
    return float((w * (mask & within)).sum()) / s if s > 0 else np.nan


def fmt(x, k=3):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "n/a"
    return f"{x:,.{k}f}"
