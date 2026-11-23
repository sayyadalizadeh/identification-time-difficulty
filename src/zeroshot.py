"""Zero-shot species prediction as in the earlier gates (G-IG9.1, G-IG10.0), for first BioCLIP, BioCLIP 2 and
BioCLIP 2.5 Huge.

- Models are loaded offline (HF_HUB_OFFLINE=1) with open_clip from the local folder of the pinned revision; the weight
  file that open_clip selects must be the file marked loaded_file in configs/model_pins.json, and its SHA-256 is checked
  against the pin before loading (rule 9). Weights in float32; image and text encoding under float16 autocast on CUDA.
- Images: file bytes opened with PIL, EXIF orientation applied, converted to RGB, then the model's own validation
  transform (one centred view). Image embeddings are not normalised by the model; predict() normalises them.
- Texts: "a photo of " + kingdom, phylum, class, order and family names + species name + "." (the species texts of the
  earlier gates); text embeddings normalised.
- Label space: all eligible species of the family, sorted by taxon id; prediction = argmax of the cosine similarity
  (ties: first in label-space order).
"""
import hashlib
import io
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
PINS = ROOT / "configs/model_pins.json"
MODEL_NAMES = {"Z1": "BioCLIP", "Z2": "BioCLIP 2", "Z25": "BioCLIP 2.5 Huge"}
BATCH = 64
LOAD_THREADS = 12
TEXT_BATCH = 256


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path, chunk=8 * 1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def pinned_file(key):
    """The pin entry marked loaded_file for model key Z1, Z2 or Z25."""
    pins = json.loads(PINS.read_text(encoding="utf-8"))
    hits = [p for p in pins if p["model"] == MODEL_NAMES[key] and p.get("loaded_file") is True]
    if len(hits) != 1:
        raise RuntimeError(f"{key}: {len(hits)} pin entries marked loaded_file")
    return hits[0]


def load_model(key, hf_cache, device="cuda"):
    """Load one model offline; returns a dict with model, transform, tokenizer, device and the checks."""
    os.environ["HF_HUB_OFFLINE"] = "1"
    import torch
    import open_clip
    from open_clip.factory import _find_checkpoint_in_dir
    pin = pinned_file(key)
    folder = Path(hf_cache) / ("models--" + pin["repository"].replace("/", "--")) / "snapshots" / pin["revision"]
    wf = folder / pin["file"]
    checks = {"folder_exists": folder.is_dir(),
              "selected_file_is_loaded_file": Path(_find_checkpoint_in_dir(folder)).name == pin["file"],
              "bytes_equal_to_pin": wf.stat().st_size == pin["bytes"],
              "sha256_equal_to_pin": sha256_file(wf) == pin["sha256"]}
    if not all(checks.values()):
        raise RuntimeError(f"{key}: pin checks failed {checks}")
    model, _, tf = open_clip.create_model_and_transforms("local-dir:" + str(folder), precision="fp32")
    tok = open_clip.get_tokenizer("local-dir:" + str(folder))
    model.eval()
    model.requires_grad_(False)
    dev = torch.device(device)
    model.to(dev)
    return {"key": key, "model": model, "tf": tf, "tok": tok, "device": dev, "checks": checks, "pin": pin}


def free_model(m):
    import torch
    del m["model"]
    torch.cuda.empty_cache()


def open_rgb(data):
    """Open file bytes, apply the EXIF orientation, convert to RGB."""
    from PIL import Image, ImageOps
    with Image.open(io.BytesIO(data)) as im:
        return ImageOps.exif_transpose(im).convert("RGB")


def embed_images(m, blobs):
    """Image embeddings (not normalised) for a list of file contents (bytes); returns (array, indices not readable)."""
    import torch
    n = len(blobs)
    out, bad = None, []

    def prep(b):
        try:
            return m["tf"](open_rgb(b))
        except Exception:
            return None

    with ThreadPoolExecutor(LOAD_THREADS) as pool:
        for s in range(0, n, BATCH):
            res = list(pool.map(prep, blobs[s:s + BATCH]))
            idx = [s + i for i, r in enumerate(res) if r is not None]
            bad += [s + i for i, r in enumerate(res) if r is None]
            if idx:
                x = torch.stack([res[i - s] for i in idx]).to(m["device"])
                with torch.no_grad(), torch.autocast(device_type="cuda", dtype=torch.float16):
                    e = m["model"].encode_image(x, normalize=False).float().cpu().numpy()
                if out is None:
                    out = np.zeros((n, e.shape[1]), np.float32)
                out[idx] = e
    return out, bad


def embed_texts(m, texts):
    import torch
    out = []
    for s in range(0, len(texts), TEXT_BATCH):
        tok = m["tok"](texts[s:s + TEXT_BATCH]).to(m["device"])
        with torch.no_grad(), torch.autocast(device_type="cuda", dtype=torch.float16):
            out.append(m["model"].encode_text(tok, normalize=True).float().cpu().numpy())
    return np.concatenate(out)


def predict(I, T):
    """Index of the highest cosine similarity (ties: first in label-space order)."""
    In = I / np.linalg.norm(I, axis=1, keepdims=True)
    return np.argmax(In @ T.T, axis=1)


def label_spaces(eligible_csv, families):
    """{family: array of species taxon ids sorted ascending} from the eligible-species table of the earlier gates."""
    import pandas as pd
    e1 = pd.read_csv(eligible_csv)
    e1 = e1[e1["eligible_primary"] == "yes"]
    return {f: np.sort(e1.loc[e1["family"] == f, "species_taxon_id"].astype(np.int64).to_numpy()) for f in families}


def species_texts(text_csvs):
    """{species taxon id: text} from the species-text tables of the earlier gates."""
    import pandas as pd
    t = pd.concat([pd.read_csv(p) for p in text_csvs], ignore_index=True).drop_duplicates("species_taxon_id")
    return dict(zip(t["species_taxon_id"].astype(np.int64), t["text"]))
