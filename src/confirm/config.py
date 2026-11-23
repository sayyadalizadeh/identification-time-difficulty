"""Configuration of the confirmatory pipeline: configs/confirmatory.yaml and the project paths."""
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG = ROOT / "configs/confirmatory.yaml"


def load_config(path=CONFIG):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def leaves(d, prefix=""):
    """(dotted key, value) for every scalar leaf of a nested dict or list."""
    if isinstance(d, dict):
        for k, v in d.items():
            yield from leaves(v, f"{prefix}{k}.")
    elif isinstance(d, list):
        for i, v in enumerate(d):
            yield from leaves(v, f"{prefix}{i}.")
    else:
        yield prefix.rstrip("."), d
