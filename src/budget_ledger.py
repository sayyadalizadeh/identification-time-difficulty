"""Download ledger of one task: every downloaded byte is added to a JSON file under outputs/, per item, and each
download first checks that its known or bounded size fits in the remaining budget."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class Ledger:
    def __init__(self, path, limit_bytes, min_free_bytes=5_000_000_000):
        self.path = Path(path)
        self.limit = int(limit_bytes)
        self.min_free = int(min_free_bytes)
        self.d = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {"items": {}, "requests": {}}

    def used(self):
        return sum(self.d["items"].values())

    def remaining(self):
        return self.limit - self.used()

    def check(self, next_bytes, what):
        """Raises if the next download (size known or bounded) would pass the budget or the free-space floor."""
        if next_bytes > self.remaining():
            raise SystemExit(f"budget: {what} needs {next_bytes:,} bytes, remaining {self.remaining():,}")
        free = shutil.disk_usage(ROOT).free
        if free - next_bytes < self.min_free:
            raise SystemExit(f"free space: {what} would leave {free - next_bytes:,} bytes on the disk")

    def add(self, item, nbytes, requests=0):
        self.d["items"][item] = self.d["items"].get(item, 0) + int(nbytes)
        self.d["requests"][item] = self.d["requests"].get(item, 0) + int(requests)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.d, indent=1), encoding="utf-8", newline="\n")
