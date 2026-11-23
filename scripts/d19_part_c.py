"""D19 Part C (post hoc): GPU analyses on the stored window-W photographs of the eight families (locked half), plus
item A8 (preprocessing of each model from its loaded configuration) and the supplement of item B10.

- Rows: the predicted rows of outputs/confirm/eight_W (same order and batches per family as the registered predict
  step); every photograph is checked against its SHA-256 in the photo manifest before use.
- Models are loaded offline with the code of the run (src/zeroshot.py, src/confirm/infer.py), each weight file
  checked against configs/model_pins.json; DINOv2-base from the pinned folder, weight file checked against the pin.
- Baseline: BioCLIP 2.5 Huge, registered family label spaces and texts, centre crop; its top-1 predictions must equal
  the stored predictions (check).
- C1: candidates = all eligible species of the eight families in the same kingdom (animals: Nymphalidae, Anatidae,
  Columbidae, Sciuridae; plants: Asteraceae, Fabaceae, Lamiaceae, Rosaceae), registered texts.
- C2a: letterbox: the whole photograph padded with black to a square (centred), then the model's own transform
  (resize to the input resolution; the centre crop of a square image keeps it whole), same normalisation.
- C2b: texts "a photo of " followed by the species name only.
- C3: DINOv2-base embeddings (pooler output: the class token after the final layer norm), the model's own image
  processor; one multinomial logistic regression (L2, scikit-learn lbfgs) per family on standardised embeddings;
  C chosen from 0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1 by mean held-out accuracy in 5-fold cross-validation grouped by
  observer (GroupKFold) on the training data only (ties: smaller C); refit on all training rows. Training rows:
  development-half research-grade observations of the eight families observed before 2024-05-01 from the photo
  folders of the earlier gates (first photographs; species of the snapshot in the registered label space).
- Analysis on the registered analysis rows (exact duplicates dropped): weighted accuracy of research-grade rows
  (mean over families), Delta and ER with 95% intervals of the observer-cluster bootstrap (2,000 replicates, seed
  20261124; one weight matrix for all variants).
- B10 supplement: within-species Spearman correlation between log(1 + T) and the top-1 probability of the baseline
  (softmax of the model's logit scale times the cosine similarities over the family label space).
Caches (embeddings) go to outputs/D19/cache/ (not tracked); results to outputs/D19/C/.
"""
import hashlib
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

import d19_common as C
from d19_common import A, E

OUT = C.OUT / "C"
CACHE = C.OUT / "cache"
CS = [0.001, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0]
PHOTO_DIRS = {"ig8": "iNaturalist_IG8_photos", "ig9": "iNaturalist_IG9_photos", "ig10": "iNaturalist_IG10_photos"}


def letterbox(im):
    from PIL import Image
    w, h = im.size
    s = max(w, h)
    canvas = Image.new("RGB", (s, s), (0, 0, 0))
    canvas.paste(im, ((s - w) // 2, (s - h) // 2))
    return canvas


def model_config(m):
    v = m["model"].visual
    cfg = {"transform": str(m["tf"]).replace("\n", " | "), "image_size": str(getattr(v, "image_size", None)),
           "preprocess_cfg": {k: str(x) for k, x in (getattr(v, "preprocess_cfg", None) or {}).items()},
           "logit_scale": float(m["model"].logit_scale.exp().item()), "checks": m.get("checks")}
    return cfg


def dino_load(hf_cache, log):
    import json
    import torch
    from transformers import AutoImageProcessor, AutoModel
    pin = [p for p in json.loads((C.ROOT / "configs/model_pins.json").read_text()) if p["model"] == "DINOv2-base"][0]
    folder = Path(hf_cache) / "models--facebook--dinov2-base" / "snapshots" / pin["revision"]
    wf = folder / pin["file"]
    ok = wf.stat().st_size == pin["bytes"] and A.sha256_file(wf) == pin["sha256"]
    log.check("DINOv2-base weight file equals the pin (bytes and SHA-256)", ok)
    if not ok:
        raise RuntimeError("DINOv2 pin check failed")
    proc = AutoImageProcessor.from_pretrained(str(folder), local_files_only=True)
    model = AutoModel.from_pretrained(str(folder), local_files_only=True).eval().to("cuda")
    return model, proc, {"processor": type(proc).__name__, "processor_config": proc.to_dict(), "revision": pin["revision"]}


def dino_embed(model, proc, blobs, bs=64):
    import torch
    from src import zeroshot as Z
    out = np.zeros((len(blobs), model.config.hidden_size), np.float32)
    with ThreadPoolExecutor(12) as pool:
        for s in range(0, len(blobs), bs):
            ims = list(pool.map(Z.open_rgb, blobs[s:s + bs]))
            x = proc(images=ims, return_tensors="pt")["pixel_values"].to("cuda")
            with torch.no_grad(), torch.autocast(device_type="cuda", dtype=torch.float16):
                out[s:s + len(ims)] = model(pixel_values=x).pooler_output.float().cpu().numpy()
    return out


def cached(name, fn):
    p = CACHE / f"{name}.npy"
    if p.exists():
        return np.load(p)
    x = fn()
    np.save(p, x)
    return x


def norm(x):
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def fit_probe(Xtr, ytr, gtr, log, fam):
    from joblib import Parallel, delayed
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GroupKFold
    folds = list(GroupKFold(n_splits=5).split(Xtr, ytr, gtr))

    def one(c, k):
        tr, te = folds[k]
        m = LogisticRegression(C=c, max_iter=3000, tol=1e-4)
        m.fit(Xtr[tr], ytr[tr])
        return c, k, float((m.predict(Xtr[te]) == ytr[te]).mean())

    res = Parallel(n_jobs=10)(delayed(one)(c, k) for c in CS for k in range(5))
    cv = pd.DataFrame(res, columns=["C", "fold", "accuracy"]).groupby("C")["accuracy"].mean()
    best = float(cv.index[np.flatnonzero(cv.to_numpy() >= cv.max() - 1e-12)[0]])
    m = LogisticRegression(C=best, max_iter=3000, tol=1e-4).fit(Xtr, ytr)
    log(f"  C3 {fam}: CV accuracy by C {dict((float(k), round(v, 4)) for k, v in cv.items())}; chosen C {best}")
    return m, best, cv


def main():
    import torch
    torch.manual_seed(C.SEED)
    log = C.Log(OUT / "part_c_log.txt")
    log("D19 Part C (post hoc); started", time.strftime("%Y-%m-%d %H:%M:%S"), "; GPU", torch.cuda.get_device_name(0),
        "; threads", C.THREADS)
    CACHE.mkdir(parents=True, exist_ok=True)
    from src import zeroshot as Z
    from src.confirm import infer as I
    s = C.spec("eight_W")
    o = C.CONF / "eight_W"
    snap = C.ROOT / s["snapshot"]
    import csv
    man_snap = {Path(r["path"]).name: r for r in csv.DictReader(open(C.ROOT / s["manifest"], encoding="utf-8"))}
    ok = A.sha256_file(snap / "taxa.csv.gz") == man_snap["taxa.csv.gz"]["sha256"]
    log.check("taxa.csv.gz equals its manifest", ok)
    if not ok:
        raise RuntimeError("taxa differs")
    tax = A.taxonomy(snap)
    # rows of the predict step
    p2 = pd.read_parquet(o / "phase2.parquet")
    man = pd.read_csv(o / "photos/manifest.csv").set_index("photo_id")
    okp = man.index[man["status"] == "ok"]
    d = p2[p2["selected"] & p2["first_photo_id"].isin(okp)].reset_index(drop=True)
    pr = pd.read_parquet(o / "predictions.parquet")
    log.check("predict-step rows equal the stored predictions table (order)", (d["observation_uuid"].to_numpy() ==
              pr["observation_uuid"].to_numpy()).all(), f"rows {len(d):,}")
    e1 = pd.read_csv(C.ROOT / s["eligible"])
    fams = list(d["family"].unique())
    spaces = {f: np.sort(e1[(e1["family"] == f) & (e1["eligible_primary"] == "yes")]["species_taxon_id"].astype(np.int64).to_numpy())
              for f in fams}
    texts = {f: [A.species_text(tax, int(x)) for x in sp] for f, sp in spaces.items()}
    names = {f: ["a photo of " + tax["name"][int(x)] for x in sp] for f, sp in spaces.items()}
    kingdom = {f: ("animals" if f in C.ANIMALS else "plants") for f in fams}
    kspace = {k: np.concatenate([spaces[f] for f in fams if kingdom[f] == k]) for k in ("animals", "plants")}
    ktexts = {k: [A.species_text(tax, int(x)) for x in kspace[k]] for k in kspace}
    log("label spaces:", {f: len(v) for f, v in spaces.items()}, "kingdom spaces:", {k: len(v) for k, v in kspace.items()})

    # A8: configurations of the four models (loaded with the run's code); Z25 kept for Part C
    a8 = {}
    for key in ("BT-CLIP-O", "Z1", "Z2", "Z25"):
        m = I.load(key, s["hf_cache"])
        a8[key] = model_config(m)
        log(f"A8 {key}: {a8[key]['transform']}")
        if key != "Z25":
            Z.free_model(m)
    zm = m
    dm, dproc, dinfo = dino_load(s["hf_cache"], log)
    a8["DINOv2-base (C3)"] = dinfo
    C.save_json(C.OUT / "A" / "A8_preprocessing.json", a8)

    # text embeddings
    Tf = {f: Z.embed_texts(zm, texts[f]) for f in fams}
    Tn = {f: Z.embed_texts(zm, names[f]) for f in fams}
    Tk = {k: Z.embed_texts(zm, ktexts[k]) for k in kspace}
    scale = a8["Z25"]["logit_scale"]
    zlb = dict(zm, tf=lambda im: zm["tf"](letterbox(im)))
    pred = {k: np.zeros(len(d), np.int64) for k in ("base", "kingdom", "letterbox", "nameonly", "dinov2")}
    prob = np.zeros(len(d))
    dino_test = np.zeros((len(d), 768), np.float32)
    for f in fams:
        t0 = time.time()
        k = np.flatnonzero((d["family"] == f).to_numpy())
        sub = d.iloc[k]
        need = not all((CACHE / f"{n}_{f}.npy").exists() for n in ("z25_std", "z25_box", "dino_test"))
        blobs = [A.read_checked(o / "photos", int(p), e, man.loc[int(p), "sha256"])
                 for p, e in zip(sub["first_photo_id"], sub["extension"])] if need else None

        def emb(mm):
            x, bad = Z.embed_images(mm, blobs)
            if bad:
                raise RuntimeError(f"{len(bad)} photographs not readable")
            return x
        Is = norm(cached(f"z25_std_{f}", lambda: emb(zm)))
        Ib = norm(cached(f"z25_box_{f}", lambda: emb(zlb)))
        dino_test[k] = cached(f"dino_test_{f}", lambda: dino_embed(dm, dproc, blobs))
        S = Is @ Tf[f].T
        pred["base"][k] = spaces[f][np.argmax(S, axis=1)]
        z = scale * S
        z = np.exp(z - z.max(axis=1, keepdims=True))
        prob[k] = z.max(axis=1) / z.sum(axis=1)
        pred["kingdom"][k] = kspace[kingdom[f]][np.argmax(Is @ Tk[kingdom[f]].T, axis=1)]
        pred["letterbox"][k] = spaces[f][np.argmax(Ib @ Tf[f].T, axis=1)]
        pred["nameonly"][k] = spaces[f][np.argmax(Is @ Tn[f].T, axis=1)]
        log(f"{f}: {len(k):,} photographs in {time.time() - t0:.0f} s")
        del blobs
    agree = float((pred["base"] == pr["p_Z25"].to_numpy()).mean())
    log.check("baseline predictions equal the stored predictions of BioCLIP 2.5 Huge", agree == 1.0,
              f"agreement {agree:.6f} ({int((pred['base'] != pr['p_Z25'].to_numpy()).sum())} rows differ)")
    Z.free_model(zm)

    # C3 training rows
    cand = pd.read_parquet(C.OUT / "snapshot/c3_training_candidates.parquet")
    flow = {"candidate photographs": len(cand)}
    t = cand[cand["observer_id"].notna()]
    flow["found in the snapshot"] = len(t)
    t = t[t["family_manifest"].isin(fams) & (t["family"] == t["family_manifest"])]
    flow["family of the snapshot equal to the manifest family (eight families)"] = len(t)
    t = t[~t["locked"].astype(bool)]
    flow["development half"] = len(t)
    t = t[t["quality_grade"] == "research"]
    flow["research grade in the snapshot"] = len(t)
    t = t[t["observed_on"].astype(str) < "2024-05-01"]
    flow["observed before 2024-05-01"] = len(t)
    t = t[[sp == sp and int(sp) in set(spaces[f]) for sp, f in zip(t["species"], t["family"])]]
    flow["species in the registered label space"] = len(t)
    t = t[t["photo_id"] == t["first_photo_id"]]
    flow["photograph is the first photograph"] = len(t)
    t = t.sort_values(["observation_uuid", "source"]).drop_duplicates("observation_uuid")
    flow["one row per observation"] = len(t)
    log("C3 training flow:", flow)
    log.check("C3 training observers are all development half", not t["locked"].astype(bool).any())
    tr_parts = []
    mans = {g: pd.read_csv(C.ROOT / f"inputs/earlier_gates/code/docs/manifests/{g}_photos_manifest.csv").set_index("photo_id")
            for g in PHOTO_DIRS}
    # file names per folder (photo id -> file names; the folders hold jpg, jpeg, png and gif files)
    files = {}
    for g, dn in PHOTO_DIRS.items():
        mp = {}
        for fn_ in os.listdir(C.ROOT.parent / "Datasets" / dn / "medium"):
            mp.setdefault(fn_.split(".")[0], []).append(fn_)
        files[g] = mp
    for f in fams:
        tf_ = t[t["family"] == f].reset_index(drop=True)

        def train_emb():
            blobs = []
            for p, g in zip(tf_["photo_id"], tf_["source"]):
                fn = files[g].get(str(int(p)), [])
                if len(fn) != 1:
                    raise RuntimeError(f"photograph {p}: {len(fn)} files")
                b = (C.ROOT.parent / "Datasets" / PHOTO_DIRS[g] / "medium" / fn[0]).read_bytes()
                if hashlib.sha256(b).hexdigest() != mans[g].loc[int(p), "sha256"]:
                    raise RuntimeError(f"photograph {p} differs from its manifest")
                blobs.append(b)
            return dino_embed(dm, dproc, blobs)
        X = cached(f"dino_train_{f}", train_emb)
        tr_parts.append((f, tf_, X))
        log(f"C3 training embeddings {f}: {len(tf_):,}")
    del dm
    torch.cuda.empty_cache()
    # probes
    probe_info = []
    for f, tf_, X in tr_parts:
        y = tf_["species"].astype(np.int64).to_numpy()
        g = tf_["observer_id"].astype(np.int64).to_numpy()
        mu, sd = X.mean(axis=0), X.std(axis=0) + 1e-6
        m, best, cv = fit_probe((X - mu) / sd, y, g, log, f)
        k = np.flatnonzero((d["family"] == f).to_numpy())
        pred["dinov2"][k] = m.predict((dino_test[k] - mu) / sd)
        te = d.iloc[k]
        te_r = te[te["grade"] == "research"]
        probe_info.append({"family": f, "training_rows": len(tf_), "training_species": int(len(np.unique(y))),
                           "training_observers": int(len(np.unique(g))), "label_space_species": len(spaces[f]),
                           "chosen_C": best, "cv_accuracy_chosen": float(cv.loc[best]),
                           "test_research_rows_species_not_in_training": int((~te_r["species"].astype(np.int64).isin(set(y))).sum()),
                           "test_research_rows": len(te_r)})
    C.save_csv(pd.DataFrame(probe_info), OUT / "C3_training.csv")
    C.save_json(OUT / "C3_training_flow.json", flow)

    # analysis on the registered analysis rows
    rows, rec = C.load_rows("eight_W")
    pp = pd.DataFrame({"observation_uuid": d["observation_uuid"], **{f"p_{k}": v for k, v in pred.items()}, "prob_top1": prob})
    pp.to_parquet(CACHE / "c_predictions_eight_W.parquet", index=False)
    rows = rows.merge(pp, on="observation_uuid", how="left", validate="one_to_one")
    D = C.Design(rows)
    W = E.boot_matrix(D.observer, D.w, 2000, np.random.default_rng(C.SEED))
    sp = rows["species"].fillna(-1).astype(np.int64).to_numpy()
    res = []
    variants = [("stored Z25 (registered)", rows["p_Z25"].to_numpy()), ("baseline recomputed", rows["p_base"].to_numpy()),
                ("C1 kingdom label space", rows["p_kingdom"].to_numpy()), ("C2a letterbox", rows["p_letterbox"].to_numpy()),
                ("C2b species name only", rows["p_nameonly"].to_numpy()), ("C3 DINOv2-base probe", rows["p_dinov2"].to_numpy())]
    for lab, p in variants:
        c = (D.isR & (p == sp)).astype(float)
        out, r = C.contrast(W, D, 1 - c, D.slow, D.fast)
        # weighted accuracy of research rows, mean over families (and groups)
        acc_f = np.column_stack([(W @ (c * D.isR * (D.fam == j)).astype(np.float32)).astype(float) /
                                 (W @ (D.isR * (D.fam == j)).astype(np.float32)).astype(float) for j in range(D.F)])
        for x in out:
            ix = range(D.F) if x["unit"] == "pooled" else D.groups[x["unit"]]
            a0, alo, ahi = C.ci(np.nanmean(acc_f[:, list(ix)], axis=1))
            x.update({"variant": lab, "accuracy": a0, "accuracy_lo95": alo, "accuracy_hi95": ahi})
            res.append(x)
        for j, f in enumerate(D.fams):
            a0, alo, ahi = C.ci(acc_f[:, j])
            res.append({"variant": lab, "unit": f, "accuracy": a0, "accuracy_lo95": alo, "accuracy_hi95": ahi,
                        "Delta": float(r["Delta_f"][0, j]), "ER": float(r["ER_f"][0, j])})
    C.save_csv(pd.DataFrame(res), OUT / "C_results.csv")
    st = pd.DataFrame(res)
    s0 = st[(st["variant"] == "stored Z25 (registered)") & (st["unit"] == "pooled")].iloc[0]
    est = pd.read_csv(o / "estimates.csv")
    ref = est[(est["model"] == "Z25") & (est["quantity"] == "Delta") & (est["unit"] == "pooled")]["value"].iloc[0]
    log.check("stored predictions reproduce the registered Delta", abs(s0["Delta"] - ref) < 1e-9, f"{s0['Delta']:.6f} vs {ref:.6f}")

    # B10 supplement: within-species Spearman between log(1 + T) and the top-1 probability (research rows with T)
    k = np.flatnonzero(D.tdef)
    g = pd.DataFrame({"sp": D.sp_idx[k], "x": np.log1p(D.T[k]), "y": rows["prob_top1"].to_numpy()[k], "i": k})
    g = g[g.groupby("sp")["sp"].transform("size") >= 3]
    rx = g.groupby("sp")["x"].rank()
    ry = g.groupby("sp")["y"].rank()
    ii = g["i"].to_numpy()
    spc = g["sp"].to_numpy()
    vals = []
    for b in range(W.shape[0]):
        wb = W[b, ii].astype(float)
        sw = pd.Series(wb).groupby(spc).transform("sum").to_numpy()
        ok_ = sw > 0
        mx = (pd.Series(wb * rx.to_numpy()).groupby(spc).transform("sum").to_numpy() / np.where(ok_, sw, 1))
        my = (pd.Series(wb * ry.to_numpy()).groupby(spc).transform("sum").to_numpy() / np.where(ok_, sw, 1))
        cx, cy = rx.to_numpy() - mx, ry.to_numpy() - my
        vals.append(float((wb * cx * cy).sum() / np.sqrt((wb * cx * cx).sum() * (wb * cy * cy).sum())))
    r0, lo, hi = C.ci(np.array(vals))
    C.save_json(OUT / "B10_supplement.json", {"rho_within_species": r0, "lo95": lo, "hi95": hi, "rows": int(len(g)),
                                              "species": int(g["sp"].nunique()), "replicates": W.shape[0] - 1,
                                              "definition": "ranks within species (species with at least 3 research rows with T), "
                                              "weighted Pearson correlation of the within-species centred ranks (phase-2 weights)"})
    log(f"B10 supplement: within-species Spearman {r0:.4f} [{lo:.4f}, {hi:.4f}], rows {len(g):,}")
    log("finished", time.strftime("%Y-%m-%d %H:%M:%S"), f"({(time.time() - log.t0) / 60:.1f} min)")
    log("FAILED CHECKS:", log.fails if log.fails else "none")


if __name__ == "__main__":
    main()
