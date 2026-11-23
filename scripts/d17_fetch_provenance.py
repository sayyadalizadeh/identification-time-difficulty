"""D17 (post hoc, docs/PLAN.md): download of dataset/metadata/provenance.parquet of imageomics/TreeOfLife-200M at
commit 97e2340877d3 into outputs/tmp/tol200m_97e2340/ (git-ignored, deposit-excluded), with range requests so that
the download is resumable. Every byte is added to the task ledger (outputs/N22/ledger.json, limit 11.0 GB); before each
request the remaining budget is checked against the exact size of the requested range.
Usage: python scripts/d17_fetch_provenance.py --first-bytes 104857600   (measured start: speed of the first 100 MB)
       python scripts/d17_fetch_provenance.py --rest                    (the remaining bytes)
       python scripts/d17_fetch_provenance.py --verify                  (size against the listing, SHA-256)
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.budget_ledger import Ledger  # noqa: E402

REPO = "imageomics/TreeOfLife-200M"
COMMIT = "97e2340877d3a2ccad78078431fa68f404ed4870"
PATH = "dataset/metadata/provenance.parquet"
URL = f"https://huggingface.co/datasets/{REPO}/resolve/{COMMIT}/{PATH}"
SIZE = 10_286_368_327  # repository listing of task N21 (inputs/cards/hf_dataset_tree_listings_2026-11-22.json)
DEST = ROOT / "outputs/tmp/tol200m_97e2340/provenance.parquet"
LOG = ROOT / "outputs/N22/provenance_fetch.json"
UA = {"User-Agent": "research-script/1.0"}


def load_log():
    return json.loads(LOG.read_text(encoding="utf-8")) if LOG.exists() else {"parts": []}


def save_log(d):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.write_text(json.dumps(d, indent=1), encoding="utf-8", newline="\n")


def fetch_range(start, end, led, info):
    """Bytes start..end (inclusive) appended to DEST; the file must already hold exactly `start` bytes."""
    n = end - start + 1
    led.check(n, f"provenance bytes {start}-{end}")
    have = DEST.stat().st_size if DEST.exists() else 0
    if have != start:
        raise SystemExit(f"partial file holds {have} bytes, expected {start}")
    t0 = time.time()
    got = 0
    with requests.get(URL, headers=dict(UA, Range=f"bytes={start}-{end}"), stream=True, timeout=120) as r:
        if r.status_code != 206:
            raise SystemExit(f"range request answered {r.status_code}")
        first = r.history[0].headers if r.history else r.headers
        info.setdefault("linked_size", first.get("x-linked-size"))
        info.setdefault("linked_etag", first.get("x-linked-etag"))
        with open(DEST, "ab") as f:
            for chunk in r.iter_content(8 << 20):
                f.write(chunk)
                got += len(chunk)
                if got > n:
                    raise SystemExit("server sent more bytes than requested")
    sec = time.time() - t0
    led.add("provenance.parquet", got, requests=1 + len(r.history))
    part = {"start": start, "end": end, "bytes": got, "seconds": round(sec, 1), "MB_per_s": round(got / sec / 1e6, 2)}
    info["parts"].append(part)
    save_log(info)
    if got != n:
        raise SystemExit(f"range {start}-{end}: {got} of {n} bytes received (rerun --rest to resume)")
    return part


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--first-bytes", type=int)
    ap.add_argument("--rest", action="store_true")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args()
    DEST.parent.mkdir(parents=True, exist_ok=True)
    led = Ledger(ROOT / "outputs/N22/ledger.json", 11_000_000_000)
    info = load_log()
    if a.first_bytes:
        p = fetch_range(0, a.first_bytes - 1, led, info)
        info["estimate_minutes_whole_file"] = round(SIZE / (p["bytes"] / p["seconds"]) / 60, 1)
        save_log(info)
    if a.rest:
        have = DEST.stat().st_size
        if have < SIZE:
            fetch_range(have, SIZE - 1, led, info)
    if a.verify:
        size = DEST.stat().st_size
        h = hashlib.sha256()
        with open(DEST, "rb") as f:
            for chunk in iter(lambda: f.read(16 << 20), b""):
                h.update(chunk)
        etag = (info.get("linked_etag") or "").strip('"')
        info["verify"] = {"bytes": size, "listing_bytes": SIZE, "size_equal": size == SIZE, "sha256": h.hexdigest(),
                          "server_linked_etag": etag, "sha256_equal_etag": h.hexdigest() == etag}
        save_log(info)
        if size != SIZE:
            raise SystemExit("size differs from the listing")
    print(json.dumps({k: v for k, v in info.items()}, indent=1))
    print("ledger:", json.dumps(led.d))


if __name__ == "__main__":
    main()
