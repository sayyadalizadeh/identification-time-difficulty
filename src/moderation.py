"""Shared code of D9 (moderation of the within-species gradient by the local fast share Q; definitions of D8).

- cells: grid cell (floor(latitude / deg), floor(longitude / deg)) of the public coordinates in stored API responses.
- local_q: Q of each row = share of fast rows among the rows of the same family and cell from other observers, counted
  with multiplicities (phase-1 draws), defined only with a pool of at least min_pool rows.
- bint_matrix: b_int per family for many weight vectors at once (the computation of D8, from weighted sums per species).
- bint_vector: b_int per family for one weight vector (same model, computed directly).
Model: within-species least squares of error on slow, Qc and slow x Qc; b_int = 100 x coefficient of slow x Qc.
"""
import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src import d6_lib as L


def cells(folder, deg):
    out = {}
    for p in sorted(Path(folder).glob("*.json.gz")):
        d = json.load(gzip.open(p, "rt", encoding="utf-8"))
        for o in d.get("results", []):
            loc = o.get("location")
            if loc:
                la, lo = (float(x) for x in loc.split(","))
                out[o["uuid"]] = f"{int(np.floor(la / deg))}|{int(np.floor(lo / deg))}"
    return out


def local_q(fam, cell, observer, fast, mult, min_pool):
    """fam, cell (text or -1 codes), observer, fast (0/1), mult (row multiplicity) -> Q (NaN where undefined).
    Rows with mult = 0 contribute nothing; their Q is still returned (computed from the other rows)."""
    kc, ko = q_codes(fam, cell, observer)
    return q_from_codes(kc, ko, fast, mult, min_pool)


def q_codes(fam, cell, observer):
    """Integer codes of the family-cell groups and of the family-cell-observer groups."""
    key = pd.Series([f"{f}|{c}" for f, c in zip(fam, cell)])
    kc, _ = pd.factorize(key)
    ko, _ = pd.factorize(key + "|" + pd.Series(observer).astype(str))
    return kc, ko


def q_from_codes(kc, ko, fast, mult, min_pool):
    m = np.asarray(mult, float)
    n_c = np.bincount(kc, weights=m)
    f_c = np.bincount(kc, weights=m * fast)
    n_o = np.bincount(ko, weights=m)
    f_o = np.bincount(ko, weights=m * fast)
    pool = n_c[kc] - n_o[ko]
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(pool >= min_pool, (f_c[kc] - f_o[ko]) / np.where(pool > 0, pool, 1), np.nan)


def _solve(C, cy):
    A = np.stack([np.stack([C[(i, j)] for j in range(3)], -1) for i in range(3)], -2)
    b = np.stack([cy[i] for i in range(3)], -1)[..., None]
    coef = np.full(A.shape[:-1], np.nan)
    ok = np.abs(np.linalg.det(A)) > 1e-9
    coef[ok] = np.linalg.solve(A[ok], b[ok])[..., 0]
    return 100 * coef[..., 2]


def bint_matrix(W, fam, spi, slow, Qc, y, nsp, sp_fam):
    """W (R x n) -> b_int (R x 8)."""
    x = [slow, Qc, slow * Qc]
    D = L.Design(len(fam))
    D.add("w", spi, 1.0, nsp)
    D.add("y", spi, y, nsp)
    for i in range(3):
        D.add(f"x{i}", spi, x[i], nsp)
        D.add(f"x{i}y", spi, x[i] * y, nsp)
        for j in range(i, 3):
            D.add(f"x{i}x{j}", spi, x[i] * x[j], nsp)
    S = L.sums(W, D, D.matrix())
    sw = S["w"].astype(float)
    swn = np.where(sw > 0, sw, 1)
    C, cy = {}, {}
    with np.errstate(invalid="ignore", divide="ignore"):
        for i in range(3):
            cy[i] = L.fam_sum(np.where(sw > 0, S[f"x{i}y"] - S[f"x{i}"] * S["y"] / swn, 0), sp_fam)
            for j in range(i, 3):
                C[(i, j)] = C[(j, i)] = L.fam_sum(np.where(sw > 0, S[f"x{i}x{j}"] - S[f"x{i}"] * S[f"x{j}"] / swn, 0),
                                                  sp_fam)
    return _solve(C, cy)


def bint_vector(w, fam, spi, slow, Qc, y, nsp, sp_fam):
    """One weight vector w (n) -> b_int (8); rows with w = 0 or NaN Qc are ignored."""
    ok = (w > 0) & np.isfinite(Qc)
    w, spi, slow, Qc, y = w[ok], spi[ok], slow[ok], Qc[ok], y[ok]
    x = [slow, Qc, slow * Qc]
    sw = np.bincount(spi, weights=w, minlength=nsp)
    swn = np.where(sw > 0, sw, 1)
    sx = [np.bincount(spi, weights=w * v, minlength=nsp) for v in x]
    sy = np.bincount(spi, weights=w * y, minlength=nsp)
    M = np.zeros((nsp, 8))
    M[np.arange(nsp), sp_fam] = 1
    C, cy = {}, {}
    for i in range(3):
        cy[i] = (np.where(sw > 0, np.bincount(spi, weights=w * x[i] * y, minlength=nsp) - sx[i] * sy / swn, 0) @ M)[None]
        for j in range(i, 3):
            v = np.where(sw > 0, np.bincount(spi, weights=w * x[i] * x[j], minlength=nsp) - sx[i] * sx[j] / swn, 0)
            C[(i, j)] = C[(j, i)] = (v @ M)[None]
    return _solve(C, cy)[0]
