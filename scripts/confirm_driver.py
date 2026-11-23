"""Driver of the confirmatory run (plan draft 3; corrected freeze N18a): every step through scripts/confirm_run.py.

Sets, in this order (values from configs/confirmatory.yaml, sets and windows):
  eight_W        eight families, locked half, window W (H1, H3, H4)
  eight_W2       eight families, locked half, window W2 (H5)
  new_W          six new families, both halves, window W (H2; H6)
  replication_W  30 replication families, both halves, window W, research-grade frame (H6)
Frames: one snapshot pass for the eight families (W and W2, locked half) and one for the 36 other families (W, both
halves). Per set: phase1, covariates, histories, report-strata, then (pre-approval) phase2, download, predict. After all
sets: analyse (each set), h6 (new_W + replication_W), analyse-joint (eight_W + new_W: groups and the relation over the
14 families, secondary), decide (Holm over H1 to H6 and the grading).

Pre-approval between the phases (plan section 4.3; N18): after a set's stratum-count report the run continues to
phase 2 if the download already made + the set's projected bytes after the registered cap rule + the projected bytes of
the later sets (outputs/D12/projections.csv) stay within the download limit of the configuration and at least
min_free_bytes would remain free on the disk; otherwise it stops before the set's downloads. Reductions by the cap rule
are allowed. Between the phases the driver reads only the stratum counts and the projected budget.
API failures: a history step stops after 30 minutes of failure; the driver then waits 60 minutes and resumes, at most
three times; after the third wait a further stop ends the run.
Every completed step is marked by its output file and is skipped on a restart; one line per step is written to
outputs/confirm/progress.md.

Usage: python scripts/confirm_driver.py --mode confirmatory --snapshot <folder> --manifest <csv> --hf-cache <folder>
"""
import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.confirm.config import load_config  # noqa: E402

OUT = ROOT / "outputs/confirm"
ELIG = "inputs/earlier_gates/outputs/G-IG8.0/e1_species_primary.csv"
MODELS = ["Z25", "Z2", "Z1", "BT-CLIP-O"]
SETS = ["eight_W", "eight_W2", "new_W", "replication_W"]
PROJECTION_ROWS = {"eight_W": "Eight families, W", "eight_W2": "Eight families, W2", "new_W": "Six new families, W",
                   "replication_W": "30 replication families, W"}
DONE = {"phase1": "phase1.parquet", "covariates": "covariates.parquet", "histories": "strata.parquet",
        "report-strata": "stratum_report.csv", "phase2": "phase2.parquet", "download": "photo_failures.csv",
        "predict": "predictions.parquet", "analyse": "estimates.csv"}
DEV_SOURCES = {  # stored development-half histories of the same window (identifier availability, N18a item f)
    "W": [{"api_raw": "outputs/D4/api_raw_d4", "table": "outputs/D4/d4_sample.csv"}],
    "W2": [{"api_raw": "outputs/D6/api_raw_w2", "table": "outputs/D6/w2_sample.csv"},
           {"api_raw": "outputs/D12/A_W2/api_raw", "table": "outputs/D12/A_W2/phase1.parquet"},
           {"api_raw": "outputs/D13/W2/api_raw", "table": "outputs/D13/W2/phase1.parquet"}]}


class StopRun(Exception):
    """The run stops (reason in the message)."""


def planned_fraction(shares, f_A0, f_B1, families, research_only=False):
    """Expected phase-2 share of phase 1 per family from development stratum shares (as in the dry run D12 and D13);
    families without development shares use the mean over the eight families."""
    sh = pd.read_csv(ROOT / shares).set_index("family")
    out = {}
    for f in families:
        r = sh.loc[f] if f in sh.index else sh.mean(numeric_only=True)
        u = r["research_T_undefined"] / r["research_rows"]
        sR = r["popR"] / (r["popR"] + r["popN"]) if "popR" in r else \
            r["frame_research"] / (r["frame_research"] + r["frame_needs_id"])
        ra = u + (1 - u) * (r["share_A0"] * f_A0 + r["share_A1"] + r["share_A2"] + r["share_A3"])
        nb = r["share_B1"] * (f_B1 or 0) + r["share_B2"]
        out[f] = float(ra if research_only else sR * ra + (1 - sR) * nb)
    return out


def dev_frame_sizes(window, families):
    fr = pd.read_parquet(ROOT / "outputs/frames/frames_dev_D12.parquet", columns=["family", "window"])
    c = fr[fr["window"] == window].groupby("family").size()
    return {f: int(c.get(f, 0)) for f in families}


def build_specs(cfg, snapshot, manifest, hf_cache):
    """Part specifications of the four sets from the registered values."""
    st = cfg["sets"]
    ext = cfg["inference"]["models"]["external"]["without_families"]
    specs = {}
    for name, key, win, frame in (("eight_W", "eight", "W", "frames/frames_eight_locked.parquet"),
                                  ("eight_W2", "eight", "W2", "frames/frames_eight_locked.parquet"),
                                  ("new_W", "new", "W", "frames/frames_new_replication_both.parquet"),
                                  ("replication_W", "replication", "W", "frames/frames_new_replication_both.parquet")):
        fams = st[key]["families"]
        w = st[key]["windows"][win]
        ro = st[key].get("frame") == "research_only"
        dates = sorted([w["S_star"]] + w["S_secondary"]) if "S_star" in w else []
        shares = "outputs/D6/part2_shares.csv" if win == "W2" else "outputs/D6/part1_shares.csv"
        sp = {"name": name, "out": f"outputs/confirm/{name}", "families": fams, "window": win,
              "frame": f"outputs/confirm/{frame}", "n1": w["n1"], "f_A0": w["f_A0"], "f_B1": w.get("f_B1"),
              "research_only": ro, "exclude": [], "dates": dates, "s_star": w.get("S_star"),
              "planned_fraction": planned_fraction(shares, w["f_A0"], w.get("f_B1"), fams, ro),
              "replicates": cfg["inference_settings"]["bootstrap_replicates_other"],
              "q_window": name == "eight_W", "external_without": [f for f in ext if f in fams],
              "snapshot": snapshot, "manifest": manifest, "hf_cache": hf_cache, "eligible": ELIG, "models": MODELS}
        if name in ("eight_W", "eight_W2", "new_W"):
            sp["replicates_hypotheses"] = cfg["inference_settings"]["bootstrap_replicates_hypotheses"]
        sp["hypothesis_c2"] = name == "eight_W"
        if key == "eight":  # the locked half is joined by the stored development histories of the same window
            sp["ident_sources"] = DEV_SOURCES[win]
            sp["ident_population_extra"] = dev_frame_sizes(win, fams)
        if not sp["external_without"]:
            del sp["external_without"]
        specs[name] = sp
    return specs


def run_with_api_waits(run_once, stopped_by_api, sleep, wait_seconds, max_waits, log):
    """Runs a history step; when it stops because the API failed (after 30 minutes of failure), waits wait_seconds and
    resumes, at most max_waits times. run_once() -> True if the step completed; stopped_by_api() -> True if the last
    failure was an API stop. Raises StopRun otherwise or after the last wait."""
    waits = 0
    while True:
        if run_once():
            return waits
        if not stopped_by_api():
            raise StopRun("history step failed (not an API stop)")
        if waits >= max_waits:
            raise StopRun(f"API failing after {max_waits} waits of {wait_seconds / 60:.0f} minutes")
        waits += 1
        log(f"API stop; wait {waits} of {max_waits} ({wait_seconds / 60:.0f} minutes)")
        sleep(wait_seconds)


def preapprove(report, used_bytes, later_bytes, free_bytes, limit_bytes, min_free_bytes):
    """Pre-approval of phase 2 for one set: returns (go, details). report: stratum_report table with
    projected_bytes_after_cap per family."""
    this = int(report["projected_bytes_after_cap"].sum())
    total = int(used_bytes) + this + int(later_bytes)
    free_after = int(free_bytes) - this - int(later_bytes)
    det = {"projected_bytes_this_set": this, "used_bytes": int(used_bytes), "projected_bytes_later_sets": int(later_bytes),
           "projected_total_bytes": total, "limit_bytes": int(limit_bytes), "free_bytes_now": int(free_bytes),
           "projected_free_bytes_after": free_after, "min_free_bytes": int(min_free_bytes),
           "families_reduced_by_cap_rule": [f for f, r in zip(report["family"], report["cap_rule"])
                                            if r != "registered fractions"]}
    go = total <= limit_bytes and free_after >= min_free_bytes
    det["decision"] = "continue to phase 2" if go else "stop before the downloads of this set"
    return go, det


def strata_markdown(name, report, det):
    """Stratum-count report of one set (counts and projected budget only)."""
    cols = ["A0", "A1", "A2", "A3", "B1", "B2", "excluded_T_undefined", "failed_history", "planned", "cap",
            "expected_phase2", "phase2_after_cap", "cap_rule", "projected_bytes_after_cap"]
    L = [f"# N18 - Stratum-count report, set {name}", "",
         "Counts per family and stratum after the identification histories (phase 1), the phase-2 photographs before "
         "and after the registered cap rule, and the projected budget (plan section 4.3). Nothing else of the histories "
         "is shown.", "", "| family | " + " | ".join(cols) + " |", "|---" * (len(cols) + 1) + "|"]
    def fmt(v):
        if isinstance(v, str):
            return v
        if isinstance(v, (list, tuple)):
            return ", ".join(map(str, v)) or "none"
        v = float(v)
        return f"{int(v):,}" if v == int(v) else f"{v:,.1f}"

    for _, r in report.iterrows():
        L.append(f"| {r['family']} | " + " | ".join(fmt(r[c]) for c in cols) + " |")
    L += ["", "| budget item | value |", "|---|---|"]
    L += [f"| {k} | {fmt(v)} |" for k, v in det.items()]
    return "\n".join(L) + "\n"


class Driver:
    def __init__(self, a, cfg):
        self.a, self.cfg = a, cfg
        self.rs = cfg["run_settings"]
        OUT.mkdir(parents=True, exist_ok=True)
        self.specs = build_specs(cfg, a.snapshot, a.manifest, a.hf_cache)
        self.paths = {}
        for k, sp in self.specs.items():
            p = OUT / f"spec_{k}.json"
            if not p.exists():
                p.write_text(json.dumps(sp, indent=1), encoding="utf-8", newline="\n")
            self.paths[k] = str(p.relative_to(ROOT)).replace("\\", "/")

    def progress(self, text):
        with open(OUT / "progress.md", "a", encoding="utf-8", newline="\n") as fh:
            fh.write(f"- {time.strftime('%Y-%m-%d %H:%M')} | {text}\n")

    def cmd(self, args, log_name):
        t0 = time.time()
        with open(OUT / log_name, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(f"\n$ confirm_run.py {' '.join(args)}\n")
            fh.flush()
            r = subprocess.run([sys.executable, "scripts/confirm_run.py"] + args + ["--mode", self.a.mode],
                               stdout=fh, stderr=subprocess.STDOUT, cwd=ROOT)
        return r.returncode == 0, time.time() - t0

    def frames(self):
        ev = self.cfg["sets"]
        for name, fams, wins, half in (("frames_eight_locked.parquet", ev["eight"]["families"], ["W", "W2"], "locked"),
                                       ("frames_new_replication_both.parquet",
                                        ev["new"]["families"] + ev["replication"]["families"], ["W"], "both")):
            if (OUT / "frames" / name).exists():
                continue
            ok, sec = self.cmd(["frame", "--families", *fams, "--windows", *wins, "--half", half, "--snapshot",
                                self.a.snapshot, "--manifest", self.a.manifest, "--eligible", ELIG, "--out-dir",
                                "outputs/confirm/frames", "--name", name], "frames_log.txt")
            self.progress(f"frame {name} | {'done' if ok else 'FAILED'} in {sec:.0f} s")
            if not ok:
                raise StopRun(f"frame {name} failed")

    def step(self, name, st):
        out = ROOT / self.specs[name]["out"]
        if (out / DONE[st]).exists():
            return
        if st == "histories":
            def once():
                ok, sec = self.cmd([st, "--spec", self.paths[name]], f"{name}_log.txt")
                self.progress(f"{name} histories | {'done' if ok else 'stopped'} in {sec:.0f} s")
                return ok

            def by_api():
                p = out / "histories_stopped.json"
                return p.exists() and "API" in json.loads(p.read_text(encoding="utf-8")).get("stopped", "")
            run_with_api_waits(once, by_api, time.sleep, 60 * self.rs["api_wait_minutes"], self.rs["api_max_waits"],
                               self.progress)
            return
        ok, sec = self.cmd([st, "--spec", self.paths[name]], f"{name}_log.txt")
        self.progress(f"{name} {st} | {'done' if ok else 'FAILED'} in {sec:.0f} s")
        if not ok:
            raise StopRun(f"{name} {st} failed")

    def gate(self, name, later):
        """Pre-approval between the phases; reads the stratum counts and the projected budget only."""
        out = ROOT / self.specs[name]["out"]
        flag = out / "preapproval.json"
        if flag.exists():
            det = json.loads(flag.read_text(encoding="utf-8"))
            if det["decision"] != "continue to phase 2":
                raise StopRun(f"{name}: pre-approval not given")
            return
        rep = pd.read_csv(out / "stratum_report.csv")
        cp = ROOT / self.rs["download_counter"]["confirmatory"]
        used = json.loads(cp.read_text())["used_bytes"] if cp.exists() else 0
        pj = pd.read_csv(ROOT / "outputs/D12/projections.csv").set_index("part")
        later_b = int(sum(pj.loc[PROJECTION_ROWS[k], "GB"] * 1e9 for k in later))
        go, det = preapprove(rep, used, later_b, shutil.disk_usage(ROOT).free,
                             self.rs["download_limit_bytes"]["confirmatory"], self.rs["min_free_bytes"])
        flag.write_text(json.dumps(det, indent=1), encoding="utf-8", newline="\n")
        (ROOT / "docs/reports" / f"N18_strata_{name}.md").write_text(strata_markdown(name, rep, det), encoding="utf-8",
                                                                     newline="\n")
        self.progress(f"{name} pre-approval | {det['decision']} | projected total {det['projected_total_bytes']:,} "
                      f"bytes")
        if not go:
            raise StopRun(f"{name}: projected budget exceeded; stopped before the downloads")

    def run(self):
        import os
        import platform
        self.progress(f"start | CPU threads 20 per numerical step (scripts/confirm_run.py) | processor "
                      f"{platform.processor()} | {os.cpu_count()} logical processors | Python {platform.python_version()}"
                      f" | seed {self.cfg['seed']}")
        self.frames()
        for i, name in enumerate(SETS):
            for st in ("phase1", "covariates", "histories", "report-strata"):
                self.step(name, st)
            self.gate(name, SETS[i + 1:])
            for st in ("phase2", "download", "predict"):
                self.step(name, st)
        for name in SETS:
            self.step(name, "analyse")
        tasks = [("h6", {"parts": [self.specs[k]["out"] for k in ("new_W", "replication_W")], "model": MODELS[0],
                         "n_perm": self.cfg["inference_settings"]["permutations_H6"],
                         "n_boot": self.cfg["inference_settings"]["bootstrap_replicates_hypotheses"],
                         "out": "outputs/confirm", "name": "h6.json"}, OUT / "h6.json"),
                 ("analyse-joint", {"parts": [self.paths["eight_W"], self.paths["new_W"]], "models": MODELS,
                                    "replicates": self.cfg["inference_settings"]["bootstrap_replicates_other"],
                                    "n_perm": self.cfg["inference_settings"]["permutations_H6"],
                                    "out": "outputs/confirm/joint_14"}, OUT / "joint_14/joint.json"),
                 ("decide", {"parts": {k: self.specs[k]["out"] for k in ("eight_W", "new_W", "eight_W2")},
                             "h6": "outputs/confirm/h6.json", "model": MODELS[0], "secondary_models": MODELS[1:],
                             "replicates": self.cfg["inference_settings"]["bootstrap_replicates_hypotheses"],
                             "out": "outputs/confirm"}, OUT / "decisions.csv")]
        for st, spec, marker in tasks:
            if marker.exists():
                continue
            p = OUT / f"spec_{st}.json"
            p.write_text(json.dumps(spec, indent=1), encoding="utf-8", newline="\n")
            ok, sec = self.cmd([st, "--spec", str(p.relative_to(ROOT)).replace("\\", "/")], "final_log.txt")
            self.progress(f"{st} | {'done' if ok else 'FAILED'} in {sec:.0f} s")
            if not ok:
                raise StopRun(f"{st} failed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", required=True, choices=["confirmatory", "dry-run"])
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--hf-cache", required=True)
    a = ap.parse_args()
    d = Driver(a, load_config())
    try:
        d.run()
        d.progress("run complete")
    except StopRun as e:
        d.progress(f"STOPPED: {e}")
        raise SystemExit(str(e))


if __name__ == "__main__":
    main()
