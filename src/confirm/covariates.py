"""Covariates of plan draft 3, section 5, that need the snapshot: observed_on of the sampled observations, the
observer-activity stratum and the queue load (D13 addendum 1, item 1).

Definitions (reused, not changed):
- Observer-activity stratum (G-IG8.0 D5; earlier gate code inputs/earlier_gates/code/scripts/IG8_0_feasibility_count.py,
  functions prior_before and prior_activity): A = number of snapshot observations of the observer (any grade, taxon
  or place) with a valid observed_on on a strictly earlier day than the observed_on of the focal observation;
  S0 = 0-9, S1 = 10-99, S2 = 100-999, S3 = 1,000 or more.
- Queue load (D2; scripts/d02_build.py, definition in lines 8-11 of its docstring, implementation in the snapshot scan
  and lines 233-237): log(1 + number of snapshot observations of the same family and the same 10-degree cell
  (floor(latitude / 10), floor(longitude / 10)) whose observed_on falls in the same ISO week as the observed_on of the
  focal observation; focal included). Family of a snapshot observation: its taxon is the family or has the family in
  its ancestry. Rows without coordinates or without a valid observed_on are not counted; a focal row without
  coordinates has no queue load (NaN).
One pass over observations.csv.gz; the snapshot files read are checked against their SHA-256 manifest in the same run.
"""
import csv
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc

from src.confirm import acquisition as A

S_BOUNDS = np.array([10, 100, 1000])
S_NAMES = np.array(["S0", "S1", "S2", "S3"])
DAY_OFF = 400_000          # day numbers (days since 1970-01-01) are shifted by this offset in the integer keys
DAY_BITS = 20              # 2**20 > DAY_OFF + any day before the year 3700
NODAY = -10 ** 9            # focal observation without a valid observed_on


def iso_week_keys(days):
    """ISO year * 100 + ISO week for day numbers (days since 1970-01-01), as in scripts/d02_build.py."""
    days = np.asarray(days, np.int64)
    if not len(days):
        return np.zeros(0, np.int64)
    u, inv = np.unique(days, return_inverse=True)
    cal = pd.DatetimeIndex(u.astype("datetime64[D]")).isocalendar()
    keys = cal["year"].to_numpy().astype(np.int64) * 100 + cal["week"].to_numpy().astype(np.int64)
    return keys[inv]


def activity_stratum(a):
    """Stratum name of the prior activity A (NaN or negative A gives '')."""
    a = np.asarray(a, float)
    s = S_NAMES[np.searchsorted(S_BOUNDS, np.where(np.isfinite(a), a, 0), side="right")].astype(object)
    s[~np.isfinite(a) | (a < 0)] = ""
    return s


def prior_activity(obs_keys, obs_counts, observer, day):
    """obs_keys: sorted unique keys observer * 2**DAY_BITS + (day + DAY_OFF) with their counts. Returns for each
    (observer, day) query the number of observations of that observer on strictly earlier days."""
    cum = np.concatenate([[0], np.cumsum(obs_counts, dtype=np.int64)])
    o = np.asarray(observer, np.int64)
    q = (o << DAY_BITS) + (np.asarray(day, np.int64) + DAY_OFF)
    first = np.searchsorted(obs_keys, o << DAY_BITS, side="left")
    pos = np.searchsorted(obs_keys, q, side="left")
    return cum[pos] - cum[first]


def queue_key(fam_code, lat, lon, iso_week):
    """Integer key of (family code, 10-degree cell, ISO week)."""
    la = np.floor(np.asarray(lat, float) / 10).astype(np.int64) + 10
    lo = np.floor(np.asarray(lon, float) / 10).astype(np.int64) + 20
    return ((np.asarray(fam_code, np.int64) * 20 + la) * 40 + lo) * 1_000_000 + np.asarray(iso_week, np.int64)


def _days(col):
    """Day numbers of an observed_on string column; invalid dates give -1 and a False mask."""
    ts = pc.strptime(col, format="%Y-%m-%d", unit="s", error_is_null=True)
    ok = pc.is_valid(ts).to_numpy(zero_copy_only=False)
    d = pc.fill_null(pc.cast(ts, pa.int64()), 0).to_numpy(zero_copy_only=False) // 86400
    ok &= (d > -DAY_OFF) & (d < (1 << DAY_BITS) - DAY_OFF)
    return np.where(ok, d, -1), ok


def snapshot_covariates(snapshot, manifest, family_ids, rows, info):
    """family_ids: {family taxon id: name}; rows: DataFrame with observation_uuid, observer_id, family, latitude,
    longitude (the sampled observations). Returns a DataFrame (observation_uuid, observed_on, prior_activity,
    activity_stratum, queue_n, queue_load) in the order of rows; info is filled with counts and timings."""
    snap = Path(snapshot)
    man = {Path(r["path"]).name: r for r in csv.DictReader(open(manifest, encoding="utf-8"))}
    for fn in ("observations.csv.gz", "taxa.csv.gz"):
        t = time.time()
        ok = (snap / fn).stat().st_size == int(man[fn]["size"]) and A.sha256_file(snap / fn) == man[fn]["sha256"]
        info[f"manifest_{fn}"] = {"PASS": bool(ok), "seconds": round(time.time() - t, 1)}
        if not ok:
            raise RuntimeError(f"{fn} differs from its manifest")
    tax = A.taxonomy(snap)
    fam_of, _, _ = A.species_genus_maps(tax, family_ids)
    names = list(dict.fromkeys(family_ids.values()))
    code = {n: i for i, n in enumerate(names)}
    tax_fam = np.full(tax["tid"].max() + 1, -1, np.int32)
    for t_, f in fam_of.items():
        tax_fam[t_] = code[f]
    info["taxa_in_the_families"] = len(fam_of)
    sample_obs = pa.array(np.unique(rows["observer_id"].to_numpy(np.int64)))
    index = pd.Index(rows["observation_uuid"])
    if not index.is_unique:
        raise RuntimeError("observation_uuid not unique in the rows")
    focal_day = np.full(len(rows), NODAY, np.int64)
    a_keys, a_cnt, q_keys, q_cnt = [], [], [], []
    n_rows = n_fam = n_queue = n_act = 0
    t1 = time.time()
    types = {"observation_uuid": pa.string(), "observer_id": pa.int64(), "taxon_id": pa.int64(),
             "observed_on": pa.string(), "latitude": pa.float64(), "longitude": pa.float64()}
    for b in A._batches(snap / "observations.csv.gz", types):
        n_rows += b.num_rows
        day, dok = _days(b.column("observed_on"))
        # (a) daily counts of the sampled observers and observed_on of the sampled observations
        mo = pc.is_in(b.column("observer_id"), value_set=sample_obs).fill_null(False).to_numpy(zero_copy_only=False)
        ma = mo & dok
        if ma.any():
            n_act += int(ma.sum())
            o = A._int(b.column("observer_id"), -1)[ma]
            k, n = np.unique((o << DAY_BITS) + (day[ma] + DAY_OFF), return_counts=True)
            a_keys.append(k)
            a_cnt.append(n)
        if mo.any():
            k = np.flatnonzero(mo)
            ix = index.get_indexer(pc.take(b.column("observation_uuid"), pa.array(k)).to_numpy(zero_copy_only=False))
            hit = ix >= 0
            focal_day[ix[hit]] = np.where(dok[k[hit]], day[k[hit]], NODAY)
        # (b) queue counts: rows of the families with coordinates and a valid observed_on
        t_ = A._int(b.column("taxon_id"), 0)
        t_ = np.where((t_ > 0) & (t_ < len(tax_fam)), t_, 0)
        f = tax_fam[t_]
        mf = f >= 0
        n_fam += int(mf.sum())
        lat = b.column("latitude").to_numpy(zero_copy_only=False)
        lon = b.column("longitude").to_numpy(zero_copy_only=False)
        mq = mf & dok & np.isfinite(lat) & np.isfinite(lon)
        if mq.any():
            n_queue += int(mq.sum())
            k, n = np.unique(queue_key(f[mq], lat[mq], lon[mq], iso_week_keys(day[mq])), return_counts=True)
            q_keys.append(k)
            q_cnt.append(n)
    info["scan_minutes"] = round((time.time() - t1) / 60, 2)
    info.update({"snapshot_rows_read": n_rows, "snapshot_rows_in_families": n_fam,
                 "snapshot_rows_counted_for_queue (coordinates and valid observed_on)": n_queue,
                 "snapshot_rows_of_sampled_observers_with_valid_observed_on": n_act})

    def reduce(keys, cnts):
        if not keys:
            return np.zeros(0, np.int64), np.zeros(0, np.int64)
        k, inv = np.unique(np.concatenate(keys), return_inverse=True)
        return k, np.bincount(inv, weights=np.concatenate(cnts)).astype(np.int64)

    ak, ac = reduce(a_keys, a_cnt)
    qk, qc = reduce(q_keys, q_cnt)
    out = pd.DataFrame({"observation_uuid": rows["observation_uuid"].to_numpy()})
    has_day = focal_day != NODAY
    info["rows"] = int(len(rows))
    info["rows_without_valid_observed_on"] = int((~has_day).sum())
    out["observed_on"] = pd.to_datetime(np.where(has_day, focal_day, 0), unit="D").strftime("%Y-%m-%d")
    out.loc[~has_day, "observed_on"] = None
    act = prior_activity(ak, ac, rows["observer_id"].to_numpy(np.int64), np.where(has_day, focal_day, 0)).astype(float)
    act[~has_day] = np.nan
    out["prior_activity"] = act
    out["activity_stratum"] = activity_stratum(act)
    lat, lon = rows["latitude"].to_numpy(float), rows["longitude"].to_numpy(float)
    fc = rows["family"].map(code).to_numpy()
    has_loc = np.isfinite(lat) & np.isfinite(lon) & has_day & pd.notna(fc)
    qn = np.full(len(rows), np.nan)
    if has_loc.any():
        key = queue_key(fc[has_loc].astype(np.int64), lat[has_loc], lon[has_loc],
                        iso_week_keys(focal_day[has_loc]))
        pos = np.minimum(np.searchsorted(qk, key), max(len(qk) - 1, 0))
        found = (qk[pos] == key) if len(qk) else np.zeros(len(key), bool)
        qn[has_loc] = np.where(found, qc[pos] if len(qc) else 0, 0)
        info["focal_rows_with_queue_count_0"] = int((~found).sum())
    info["focal_rows_without_coordinates"] = int((~has_loc & has_day).sum())
    out["queue_n"] = qn
    out["queue_load"] = np.log1p(qn)
    info["activity_stratum_counts"] = out["activity_stratum"].value_counts().to_dict()
    return out
