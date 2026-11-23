"""Inference for the four models of the confirmatory plan (section 6).

- BioCLIP models (Z1, Z2, Z25): src/zeroshot.py unchanged (offline, pinned loaded_file, SHA-256 checked).
- External model: an open_clip checkpoint file inside models/ with its architecture name; its pin (repository commit,
  file, bytes, SHA-256) is read from configs/model_pins.json and checked before loading.
- predict_family: top-1 species of every photograph of one family over its label space with the given texts.
"""
import json
import os
import time
from pathlib import Path

import numpy as np

from src import zeroshot as Z
from src.confirm.config import ROOT

PINS = ROOT / "configs/model_pins.json"


def load_external(name):
    """Load the external model whose pin entry has model == name."""
    os.environ["HF_HUB_OFFLINE"] = "1"
    import open_clip
    import torch
    pins = [p for p in json.loads(PINS.read_text(encoding="utf-8")) if p["model"] == name]
    if len(pins) != 1:
        raise RuntimeError(f"{name}: {len(pins)} pin entries")
    pin = pins[0]
    wf = ROOT / pin["local_path"]
    checks = {"bytes_equal_to_pin": wf.stat().st_size == pin["bytes"],
              "sha256_equal_to_pin": Z.sha256_file(wf) == pin["sha256"]}
    if not all(checks.values()):
        raise RuntimeError(f"{name}: pin checks failed {checks}")
    # safe loading (weights_only=True) with numpy scalar and dtype types allowlisted; the checkpoint stores training
    # metadata as numpy scalars; no arbitrary code is executed
    model, _, tf = open_clip.create_model_and_transforms(pin["architecture"], pretrained=None, precision="fp32")
    from numpy._core.multiarray import scalar as np_scalar
    allow = [(np_scalar, "numpy.core.multiarray.scalar"), np_scalar, np.dtype] +         [type(np.dtype(t)) for t in ("float64", "float32", "int64", "int32")]
    with torch.serialization.safe_globals(allow):
        ckpt = torch.load(wf, map_location="cpu", weights_only=True)
    sd = ckpt.get("state_dict", ckpt) if isinstance(ckpt, dict) else ckpt
    sd = {k[7:] if k.startswith("module.") else k: v for k, v in sd.items()}
    res = model.load_state_dict(sd, strict=True)
    checks["state_dict_loaded_strict"] = not res.missing_keys and not res.unexpected_keys
    tok = open_clip.get_tokenizer(pin["architecture"])
    model.eval()
    model.requires_grad_(False)
    dev = torch.device("cuda")
    model.to(dev)
    return {"key": name, "model": model, "tf": tf, "tok": tok, "device": dev, "checks": checks, "pin": pin}


def load(key, hf_cache):
    return Z.load_model(key, hf_cache) if key in Z.MODEL_NAMES else load_external(key)


def predict_family(m, blobs, texts, space):
    """blobs: photograph bytes; texts: label-space texts (same order as space). Returns predicted species ids."""
    T = Z.embed_texts(m, texts)
    I, bad = Z.embed_images(m, blobs)
    if bad:
        raise RuntimeError(f"{len(bad)} photographs not readable")
    return np.asarray(space)[Z.predict(I, T)]


def timed(fn, *a):
    t0 = time.time()
    r = fn(*a)
    return r, time.time() - t0
