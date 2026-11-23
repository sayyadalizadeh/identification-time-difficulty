"""Shared code of decision D6 (docs/PLAN.md, D6 and D6 addendum 1).

- One random generator (seed 20261121) used in the order of Parts 1 to 4; its state is saved after each part and
  loaded by the next one (addendum 1, item 9).
- Identification histories from raw API responses (numeric ids only): research grade with a given species at a moment
  (rule N2 of D4: latest identification per user among those created up to that moment, hidden ones excluded; at least
  two at species rank or below name the species or a taxon below it and they are more than two thirds of those at
  species rank or below); T = days from created_at of the observation to the first identification time at which N2
  holds; identifications created after 2026-10-27 (UTC) are ignored.
- Label support of a needs_id observation as in D5 (distinct users, owner included, with a current identification
  whose taxon is the label genus or lies within it).
- Weighted sums: every estimate is computed from weighted sums per group, obtained for many weight vectors at once as
  (weights matrix) x (sparse design matrix).
"""
import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

SEED = 20261121
FAMILIES = ["Asteraceae", "Fabaceae", "Nymphalidae", "Anatidae", "Lamiaceae", "Rosaceae", "Columbidae", "Sciuridae"]
CUTOFF = pd.Timestamp("2026-10-28T00:00:00Z").value  # identifications created after 2026-10-27 UTC are ignored
DAY_NS = 86400 * 10**9
STRATA_R = ["A0", "A1", "A2", "A3"]
STRATA_N = ["B1", "B2"]


# ---------------------------------------------------------------- generator carried across parts
def rng_new():
    return np.random.default_rng(SEED)


def rng_save(rng, path):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(rng.bit_generator.state, f)


def rng_load(path):
    rng = np.random.default_rng()
    st = json.load(open(path, encoding="utf-8"))
    rng.bit_generator.state = st
    return rng


# ---------------------------------------------------------------- histories
def parse_raw(folder):
    """uuid -> {'owner', 'created_ns', 'ids': [(ts_ns, ident_id, user_id, taxon_id, rank_level, anc, current)]}.
    Hidden identifications are dropped (none in the D4 histories); their number is returned."""
    rec, hidden = {}, 0
    for p in sorted(Path(folder).glob("*.json.gz")):
        d = json.load(gzip.open(p, "rt", encoding="utf-8"))
        res = d["results"] if "results" in d else d.get("response", {}).get("results", [])
        for o in res:
            ids = []
            for i in o.get("identifications") or []:
                if i.get("hidden"):
                    hidden += 1
                    continue
                tx = i.get("taxon") or {}
                rl = tx.get("rank_level")
                ids.append((pd.Timestamp(i["created_at"]).value, i.get("id"), (i.get("user") or {}).get("id"),
                            tx.get("id"), float(rl) if rl is not None else 99.0,
                            frozenset(int(x) for x in (tx.get("ancestor_ids") or [])), i.get("current") is True))
            rec[o["uuid"]] = {"owner": int(o["user"]["id"]), "created_ns": pd.Timestamp(o["created_at"]).value,
                              "ids": sorted(ids, key=lambda x: (x[0], x[1]))}
    return rec, hidden


def n2(spl, sp_id):
    if len(spl) < 2:
        return False
    k = sum(1 for x in spl if x[3] == sp_id or sp_id in x[5])
    return k >= 2 and 3 * k > 2 * len(spl)


def t_days(r, sp_id):
    """Days from creation to the first identification time at which N2 holds for sp_id; NaN if never."""
    last = {}
    for x in r["ids"]:
        if x[0] >= CUTOFF:
            break
        last[x[2]] = x
        spl = [y for y in last.values() if y[4] <= 10]
        if n2(spl, sp_id):
            return (x[0] - r["created_ns"]) / DAY_NS
    return np.nan


def support(r, genus_id):
    users = set()
    for x in r["ids"]:
        if x[6] and (x[3] == genus_id or genus_id in x[5]):
            users.add(int(x[2]))
    return len(users)


def stratum_r(t):
    return np.select([t < 1, t < 30, t < 365, t >= 365], STRATA_R, "")


# ---------------------------------------------------------------- weighted sums
class Design:
    """Sparse design matrix: blocks of columns, each block = values of the rows summed per group."""

    def __init__(self, n):
        self.n, self.r, self.c, self.v, self.blocks, self.ncol = n, [], [], [], {}, 0

    def add(self, name, group, values, ngroups, mask=None):
        rows = np.arange(self.n)
        keep = np.ones(self.n, bool) if mask is None else mask.astype(bool)
        keep &= (group >= 0)
        self.r.append(rows[keep])
        self.c.append(self.ncol + group[keep])
        self.v.append(np.asarray(values, float)[keep] if np.ndim(values) else np.full(keep.sum(), float(values)))
        self.blocks[name] = (self.ncol, self.ncol + ngroups)
        self.ncol += ngroups

    def matrix(self):
        return sp.csr_matrix((np.concatenate(self.v).astype(np.float32),
                              (np.concatenate(self.r), np.concatenate(self.c))), shape=(self.n, self.ncol))


def sums(W, D, X):
    """W: (R x n) weights; D: Design; X: its matrix. Returns name -> (R x groups) array."""
    S = np.asarray((X.T @ W.T).T)
    return {k: S[:, a:b] for k, (a, b) in D.blocks.items()}


def fam_sum(x, sp_fam, nf=8):
    """(R x species) -> (R x families)."""
    M = np.zeros((len(sp_fam), nf))
    M[np.arange(len(sp_fam)), sp_fam] = 1
    return np.nan_to_num(x) @ M


def delta_parts(wf, ef, ws, es, sp_fam, nf=8):
    """Per family E_slow, E_ref and the dropped share of slow weight (R x nf; nf = 8 families by default, or any
    other grouping of the species groups given by sp_fam)."""
    with np.errstate(invalid="ignore", divide="ignore"):
        ret = (wf > 0) & (ws > 0)
        wsr = np.where(ret, ws, 0)
        num_s = fam_sum(np.where(ret, es, 0), sp_fam, nf)
        num_r = fam_sum(np.where(ret, ws * ef / np.where(wf > 0, wf, 1), 0), sp_fam, nf)
        den = fam_sum(wsr, sp_fam, nf)
        tot = fam_sum(ws, sp_fam, nf)
        Es = num_s / np.where(den > 0, den, np.nan)
        Er = num_r / np.where(den > 0, den, np.nan)
        drop = 1 - den / np.where(tot > 0, tot, np.nan)
    return Es, Er, drop


def pooled_delta(Es, Er):
    with np.errstate(invalid="ignore"):
        return 100 * np.nanmean(Es - Er, axis=1), np.nansum(Es, axis=1) / np.nansum(np.where(np.isnan(Es), np.nan, Er), axis=1)


def slope(sw, sx, sy, sxy, sxx, sp_fam):
    """Within-species least-squares slope per family (x 100), from weighted sums per species."""
    with np.errstate(invalid="ignore", divide="ignore"):
        ok = sw > 0
        cxy = np.where(ok, sxy - sx * sy / np.where(ok, sw, 1), 0)
        cxx = np.where(ok, sxx - sx * sx / np.where(ok, sw, 1), 0)
        return 100 * fam_sum(cxy, sp_fam) / fam_sum(cxx, sp_fam)


def o_family(n, c, nS, cS):
    with np.errstate(invalid="ignore", divide="ignore"):
        return 100 * (cS / nS - c / n)


def g_family(nR, gR, nS, gS, nN, nS2, gS2, popR, popN):
    """Genus-level overstatement on supported labels (D5): mixing weights from the W population counts."""
    with np.errstate(invalid="ignore", divide="ignore"):
        share = nS2 / nN
        pN = popN[None, :] * share
        wR = popR[None, :] / (popR[None, :] + pN)
        mix = wR * (gR / nR) + (1 - wR) * (gS2 / np.where(nS2 > 0, nS2, np.nan))
        return 100 * (gS / nS - mix)


def ci(x):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return (float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))) if len(x) else (np.nan, np.nan)
