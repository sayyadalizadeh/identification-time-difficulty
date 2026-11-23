"""D17 (post hoc, docs/PLAN.md): membership check of the analysed photographs against the training data of
BioCLIP 2.5 Huge (provenance file of TreeOfLife-200M at commit 97e2340877d3).

Stages (each writes its outputs to outputs/D17/, git-ignored):
  --analysed --snapshot <folder> --manifest <csv>
      every photo identifier (all positions) of every observation of the analysed sets, from photos.csv.gz of the
      snapshot (size and SHA-256 checked against its manifest in the same run). Sets: the phase-2 samples (selected
      rows) of the four confirmatory sets (outputs/confirm/<set>/phase2.parquet); the D14 additions (observations whose
      first photograph is in outputs/D14/photos/manifest.csv, found in the raw responses outputs/D14/api_raw/); the D4
      sample (outputs/D6/rows.parquet, all rows); set B of D16 (outputs/D16/sample.parquet, all rows).
      Only photo identifiers are read: no photograph, history or model output.
  --provenance
      the provenance file, read row group by row group and column by column (rule in parse_group below); writes the
      per-source counts and the identifier array.
  --match
      intersections with the analysed photographs and with M1 of the earlier gates
      (inputs/earlier_gates/outputs/G-IG9.0/members_a8f38b4.parquet).
"""
import os
THREADS = 20
for _v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_v] = str(THREADS)
import argparse  # noqa: E402
import csv  # noqa: E402
import gzip  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pyarrow as pa  # noqa: E402
import pyarrow.compute as pc  # noqa: E402
import pyarrow.parquet as pq  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.confirm import acquisition as A  # noqa: E402

pa.set_cpu_count(THREADS)
pa.set_io_thread_count(THREADS)
OUT = ROOT / "outputs/D17"
PROV = ROOT / "outputs/tmp/tol200m_97e2340/provenance.parquet"
M1 = ROOT / "inputs/earlier_gates/outputs/G-IG9.0/members_a8f38b4.parquet"
MAX_M1 = 367_752_438
SETS = ["eight_W", "eight_W2", "new_W", "replication_W"]


def wjson(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8", newline="\n")


# ------------------------------------------------------------------ stage 1: analysed observations and their photos
def analysed_observations():
    """DataFrame set, observation_uuid, family, stratum, first_photo_id."""
    parts = []
    for s in SETS:
        d = pd.read_parquet(ROOT / f"outputs/confirm/{s}/phase2.parquet",
                            columns=["observation_uuid", "family", "stratum", "first_photo_id", "selected"])
        d = d[d["selected"].fillna(False).astype(bool)]
        parts.append(d.drop(columns="selected").assign(set=f"{s} phase 2"))
    man = pd.read_csv(ROOT / "outputs/D14/photos/manifest.csv")
    first = set(man["photo_id"].astype(np.int64))
    rows = []
    for f in sorted((ROOT / "outputs/D14/api_raw").glob("*.json.gz")):
        for o in json.loads(gzip.open(f).read()).get("results", []):
            # the D14 first photograph is the first in the snapshot order; the order of the API response can differ,
            # so the observation is the one that holds the photograph at any position
            hit = [int(p["photo"]["id"]) for p in o.get("observation_photos", []) if int(p["photo"]["id"]) in first]
            if hit:
                rows.append({"observation_uuid": o["uuid"], "family": "Ardeidae", "stratum": "D14 addition",
                             "first_photo_id": hit[0]})
    d14 = pd.DataFrame(rows).drop_duplicates("observation_uuid")
    parts.append(d14.assign(set="D14 additions"))
    r = pd.read_parquet(ROOT / "outputs/D6/rows.parquet", columns=["observation_uuid", "family", "stratum"])
    parts.append(r.assign(set="D4 sample", first_photo_id=np.nan))
    b = pd.read_parquet(ROOT / "outputs/D16/sample.parquet", columns=["observation_uuid", "family", "first_photo_id"])
    parts.append(b.assign(set="D16 set B", stratum="sample"))
    out = pd.concat(parts, ignore_index=True)
    return out, {"D14_first_photos_in_manifest": len(first), "D14_observations_found": int(len(d14))}


def stage_analysed(snapshot, manifest):
    t0 = time.time()
    info = {}
    obs, info["d14"] = analysed_observations()
    info["observations_per_set"] = obs.groupby("set").size().to_dict()
    snap = Path(snapshot)
    man = {Path(r["path"]).name: r for r in csv.DictReader(open(manifest, encoding="utf-8"))}
    fn = "photos.csv.gz"
    ok = (snap / fn).stat().st_size == int(man[fn]["size"]) and A.sha256_file(snap / fn) == man[fn]["sha256"]
    info[f"manifest_{fn}"] = ok
    if not ok:
        raise SystemExit(f"{fn} differs from its manifest")
    index = pd.Index(obs["observation_uuid"].unique())
    U, P, Q = [], [], []
    types = {"photo_id": pa.int64(), "observation_uuid": pa.string(), "position": pa.int64()}
    nrows = 0
    for bt in A._batches(snap / fn, types):
        nrows += bt.num_rows
        ix = index.get_indexer(bt.column("observation_uuid").to_numpy(zero_copy_only=False))
        k = np.flatnonzero(ix >= 0)
        if not len(k):
            continue
        ka = pa.array(k)
        U.append(ix[k])
        P.append(A._int(pc.take(bt.column("photo_id"), ka), -1))
        Q.append(A._int(pc.take(bt.column("position"), ka), -1))
    ph = pd.DataFrame({"observation_uuid": index[np.concatenate(U)], "photo_id": np.concatenate(P),
                       "position": np.concatenate(Q)})
    ph.to_parquet(OUT / "analysed_photos.parquet", index=False)
    obs.to_parquet(OUT / "analysed_observations.parquet", index=False)
    # control: the stored first photograph of each observation is among its snapshot photographs
    fp = obs.dropna(subset=["first_photo_id"]).astype({"first_photo_id": np.int64})
    pairs = set(zip(ph["observation_uuid"], ph["photo_id"]))
    info.update({"snapshot_photo_rows_read": nrows, "photo_rows_kept": int(len(ph)),
                 "observations_with_photos": int(ph["observation_uuid"].nunique()),
                 "observations_without_photos": int(len(index) - ph["observation_uuid"].nunique()),
                 "first_photo_found": int(sum((u, p) in pairs for u, p in zip(fp["observation_uuid"], fp["first_photo_id"]))),
                 "first_photo_checked": int(len(fp)), "minutes": round((time.time() - t0) / 60, 1)})
    wjson(OUT / "analysed.json", info)
    print(json.dumps(info, indent=1, default=str))


# ------------------------------------------------------------------ stage 2: the provenance file
# Rule E (the rule of the earlier gates for source_url): host = lower-case text between the first "://" and the next
# "/", ":", "?" or "#"; the host must equal inaturalist-open-data.s3.amazonaws.com; the identifier is the first match of
# "/photos/(digits)/"; more than 18 digits counts as not matching.
# Rule X (every string column, including source_url): the lower-cased value contains "inaturalist"; the identifier is
# the first match of "://<host containing inaturalist>[:port]/photos/(digits)" (any iNaturalist host, trailing "/"
# not required); more than 18 digits counts as not matching.
# A record's iNaturalist photo identifier is that of rule E if any, else the first of rule X over the columns in file
# order. A record 'refers to iNaturalist' if any string column contains "inaturalist" (case-insensitive).
HOST = "inaturalist-open-data.s3.amazonaws.com"
RE_HOST = r"://(?P<h>[^/:?#]*)"
RE_ID = r"/photos/(?P<id>\d+)/"
RE_X = r"://(?P<h>[^/:?#]*inaturalist[^/:?#]*)(?::\d+)?/photos/(?P<id>\d+)"
SOURCE = {"gbif": "GBIF", "eol": "EOL", "bioscan": "BIOSCAN-5M", "fathomnet": "FathomNet"}


def _ids(txt):
    """int64 numpy array of identifier texts; -1 for null or more than 18 digits."""
    ok = pc.fill_null(pc.less_equal(pc.utf8_length(txt), 18), False)
    v = pc.if_else(ok, txt, pa.scalar(None, txt.type))
    return pc.cast(v, pa.int64()).fill_null(-1).to_numpy(zero_copy_only=False)


def parse_group(pf_path, rg, strcols, pubcol):
    """One row group, read column by column. Returns (summary DataFrame rows, identifiers)."""
    pf = pq.ParquetFile(pf_path)

    def col(c):
        x = pf.read_row_group(rg, columns=[c]).column(0).combine_chunks()
        return x.cast(pa.large_string())

    ds = pc.utf8_lower(pc.fill_null(col("data_source"), "(null)")).to_numpy(zero_copy_only=False)
    n = len(ds)
    pid = np.full(n, -1, np.int64)
    url = col("source_url")
    host = pc.utf8_lower(pc.extract_regex(url, RE_HOST).flatten()[0])
    is_e = pc.fill_null(pc.equal(host, pa.scalar(HOST, pa.large_string())), False).to_numpy(zero_copy_only=False)
    k = np.flatnonzero(is_e)
    if len(k):
        pid[k] = _ids(pc.extract_regex(pc.take(url, pa.array(k)), RE_ID).flatten()[0])
    rule_e = pid >= 0
    ref_any = np.zeros(n, bool)
    ref_by_col = {}
    xid = np.full(n, -1, np.int64)
    for c in strcols:
        v = url if c == "source_url" else col(c)
        ref = pc.fill_null(pc.match_substring(v, "inaturalist", ignore_case=True), False).to_numpy(zero_copy_only=False)
        ref_any |= ref
        k = np.flatnonzero(ref)
        ref_by_col[c] = k
        if len(k):
            e = _ids(pc.extract_regex(pc.utf8_lower(pc.take(v, pa.array(k))), RE_X).flatten()[1])
            put = (xid[k] < 0) & (e >= 0)
            xid[k[put]] = e[put]
    use_x = (pid < 0) & (xid >= 0)
    pid[use_x] = xid[use_x]
    pub = (pc.fill_null(col(pubcol), "(null)").to_numpy(zero_copy_only=False) if pubcol else np.full(n, "", object))
    d = pd.DataFrame({"src": ds, "pub": pub, "has": pid >= 0, "e": rule_e, "x_only": use_x, "ref": ref_any,
                      "above": pid > MAX_M1, "pid": pid})
    for c, k in ref_by_col.items():
        r = np.zeros(n, bool)
        r[k] = True
        d[f"ref_{c}"] = r
    agg = {"records": ("has", "size"), "with_id": ("has", "sum"), "rule_E": ("e", "sum"), "rule_X_only": ("x_only", "sum"),
           "refers_inat": ("ref", "sum"), "above_max_M1": ("above", "sum"), "max_id": ("pid", "max")}
    agg.update({f"ref_{c}": (f"ref_{c}", "sum") for c in strcols})
    by_src = d.groupby("src").agg(**agg).reset_index()
    by_pub = d[d["src"] == "gbif"].groupby("pub").agg(**agg).reset_index() if pubcol else None
    return by_src, by_pub, pid[pid >= 0], n


def stage_provenance(workers=4):
    from concurrent.futures import ThreadPoolExecutor
    t0 = time.time()
    pf = pq.ParquetFile(PROV)
    md = pf.metadata
    schema = pf.schema_arrow
    strcols = [f.name for f in schema if pa.types.is_string(f.type) or pa.types.is_large_string(f.type)]
    pubcol = "publisher" if "publisher" in schema.names else None
    info = {"file_bytes": PROV.stat().st_size, "rows": md.num_rows, "row_groups": md.num_row_groups,
            "created_by": md.created_by, "schema": [[f.name, str(f.type)] for f in schema], "string_columns": strcols,
            "publisher_column": pubcol}
    print(json.dumps(info, indent=1), flush=True)
    S, Pb, ids, nread = [], [], [], 0
    with ThreadPoolExecutor(workers) as ex:
        for i, (s, p, x, n) in enumerate(ex.map(lambda g: parse_group(PROV, g, strcols, pubcol), range(md.num_row_groups))):
            S.append(s)
            if p is not None:
                Pb.append(p)
            ids.append(x)
            nread += n
            if i % 50 == 0:
                print(time.strftime("%H:%M:%S"), f"row group {i}", flush=True)

    def combine(parts, key):
        d = pd.concat(parts, ignore_index=True)
        sums = [c for c in d.columns if c not in (key, "max_id")]
        return d.groupby(key).agg({**{c: "sum" for c in sums}, "max_id": "max"}).reset_index()

    src = combine(S, "src")
    src["source"] = src["src"].map(lambda v: SOURCE.get(v, f"other ({v})"))
    src.to_csv(OUT / "provenance_by_source.csv", index=False, lineterminator="\n")
    if Pb:
        combine(Pb, "pub").sort_values("records", ascending=False).to_csv(OUT / "provenance_gbif_by_publisher.csv",
                                                                          index=False, lineterminator="\n")
    allids = np.concatenate(ids)
    u = np.unique(allids)
    pq.write_table(pa.table({"photo_id": u}), OUT / "members_97e2340.parquet")
    m1 = pq.read_table(M1).column("photo_id").to_numpy()
    info.update({"rows_read": nread, "records_with_id": int(len(allids)), "distinct_ids": int(len(u)),
                 "max_id": int(u.max()) if len(u) else None, "distinct_ids_above_max_M1": int((u > MAX_M1).sum()),
                 "M1_distinct": int(len(m1)), "M1_ids_also_in_new": int(np.isin(m1, u, assume_unique=True).sum()),
                 "new_ids_not_in_M1": int((~np.isin(u, m1, assume_unique=True)).sum()),
                 "minutes": round((time.time() - t0) / 60, 1)})
    info["control_rows_read_equal_footer"] = nread == md.num_rows
    wjson(OUT / "provenance.json", info)
    print(json.dumps(info, indent=1, default=str))
    print(src.to_string())


# ------------------------------------------------------------------ stage 3: intersections
def stage_match():
    obs = pd.read_parquet(OUT / "analysed_observations.parquet")
    ph = pd.read_parquet(OUT / "analysed_photos.parquet")
    new = pq.read_table(OUT / "members_97e2340.parquet").column("photo_id").to_numpy()
    m1 = pq.read_table(M1).column("photo_id").to_numpy()
    ph["in_new"] = np.isin(ph["photo_id"].to_numpy(), new)
    ph["in_M1"] = np.isin(ph["photo_id"].to_numpy(), m1)
    ph["first"] = ph.groupby("observation_uuid")["position"].rank(method="first") == 1
    d = obs[["set", "family", "stratum", "observation_uuid"]].merge(ph, on="observation_uuid", how="left")
    d["has_photo"] = d["photo_id"].notna()
    for c in ("in_new", "in_M1", "first"):
        d[c] = d[c].fillna(False).astype(bool)
    g = d.groupby(["set", "family", "stratum"])
    tab = pd.DataFrame({"observations": g["observation_uuid"].nunique(), "photos": g["has_photo"].sum(),
                        "photos_in_new": g["in_new"].sum(), "photos_in_M1": g["in_M1"].sum(),
                        "first_photos_in_new": g.apply(lambda x: int((x["in_new"] & x["first"]).sum())),
                        "observations_with_a_photo_in_new": g.apply(lambda x: x.loc[x["in_new"] == True, "observation_uuid"].nunique()),  # noqa: E712
                        }).reset_index()
    tab.to_csv(OUT / "matches_by_set_family_stratum.csv", index=False, lineterminator="\n")
    hits = d[(d["in_new"] == True) | (d["in_M1"] == True)]  # noqa: E712
    hits[["set", "family", "stratum", "photo_id", "position", "in_new", "in_M1"]].to_csv(
        OUT / "matching_photos.csv", index=False, lineterminator="\n")
    info = {"analysed_observations": int(obs["observation_uuid"].nunique()), "analysed_photos": int(ph["photo_id"].nunique()),
            "photos_in_new": int(ph.loc[ph["in_new"], "photo_id"].nunique()),
            "photos_in_M1": int(ph.loc[ph["in_M1"], "photo_id"].nunique()),
            "min_analysed_photo_id": int(ph["photo_id"].min()), "max_analysed_photo_id": int(ph["photo_id"].max()),
            "analysed_photos_at_or_below_max_M1": int((ph["photo_id"] <= MAX_M1).sum())}
    wjson(OUT / "match.json", info)
    print(json.dumps(info, indent=1))
    print(tab.to_string())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--analysed", action="store_true")
    ap.add_argument("--provenance", action="store_true")
    ap.add_argument("--match", action="store_true")
    ap.add_argument("--snapshot")
    ap.add_argument("--manifest")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.analysed:
        stage_analysed(a.snapshot, a.manifest)
    if a.provenance:
        stage_provenance()
    if a.match:
        stage_match()


if __name__ == "__main__":
    main()
