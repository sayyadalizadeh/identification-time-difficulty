"""N18a, Step 4: corrected code-freeze record. Writes docs/reports/code_freeze_v2.md and outputs/freeze_v2/unit_tests.txt.

Lists the SHA-256 at the corrected freeze commit of every tracked file the confirmatory run uses (read with 'git show',
and required to equal the working tree), the SHA-256 of the untracked inputs it reads (copied inputs, checked against
inputs/MANIFEST.csv; development outputs; for the stored development histories one digest per folder over the sorted
file names and their SHA-256), the full test-suite result, the changes against the first freeze with their reasons,
and the run order. docs/reports/code_freeze.md is not changed; configs/registration_lock.json is not created.

Usage: python scripts/n18a_code_freeze_v2.py --commit <corrected freeze commit> --git <path of git>
"""
import argparse
import csv
import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIRST = "f3d452832935f5e9d8f829dc6f588e58cb4c2a5b"
TRACKED = ["scripts/confirm_driver.py", "scripts/confirm_run.py", "src/confirm/__init__.py", "src/confirm/config.py",
           "src/confirm/guard.py", "src/confirm/acquisition.py", "src/confirm/covariates.py", "src/confirm/infer.py",
           "src/confirm/estimators.py", "src/confirm/analysis.py", "src/confirm/decide.py", "src/d6_lib.py",
           "src/moderation.py", "src/halves.py", "src/zeroshot.py", "configs/confirmatory.yaml",
           "configs/model_pins.json", "tests/test_config.py", "tests/test_estimators.py", "tests/test_guard.py",
           "tests/test_addendum1.py", "tests/test_freeze_v2.py", "docs/plan_blocks/confirmatory_plan_draft3.md"]
COPIED = ["inputs/earlier_gates/outputs/G-IG8.0/e1_species_primary.csv",
          "inputs/earlier_gates/code/docs/manifests/inat_snapshot_2026-10-27_sha256.csv"]
UNTRACKED = ["outputs/D6/part1_shares.csv", "outputs/D6/part2_shares.csv", "outputs/D12/projections.csv",
             "outputs/frames/frames_dev_D12.parquet", "outputs/D4/d4_sample.csv", "outputs/D6/w2_sample.csv",
             "outputs/D12/A_W2/phase1.parquet", "outputs/D13/W2/phase1.parquet"]
FOLDERS = ["outputs/D4/api_raw_d4", "outputs/D6/api_raw_w2", "outputs/D12/A_W2/api_raw", "outputs/D13/W2/api_raw"]
CHANGES = [
    ("scripts/confirm_run.py, download", "the download limit is read from configs/confirmatory.yaml (24 GB for the "
     "confirmatory run, 8 GB for dry runs); the confirmatory run counts its bytes in outputs/confirm/download_bytes.json "
     "from 0", "the first freeze stopped all downloads at 8 GB counted with the dry-run counter (5.27 GB already used), "
     "so the registered photographs (about 20 GB) could not be downloaded (plan section 4.3)"),
    ("scripts/confirm_run.py, analyse", "one bootstrap matrix of 5,000 replicates for the estimates that carry a "
     "hypothesis (Delta and ER of BioCLIP 2.5 Huge; O, R and G_sup at S* in the eight-family set of window W); 2,000 "
     "for all other estimates; the fall-back to 2,000 replicates is removed", "plan section 8 (5,000 for H1 to H6, "
     "2,000 otherwise); the first freeze used 5,000 only for Delta and ER"),
    ("scripts/confirm_run.py, decide; src/confirm/decide.py (new)", "Holm over H1 to H6 at one-sided 0.05 and the "
     "grading of section 9, written to outputs/confirm/decisions.csv; the same grading for the secondary models without "
     "family-wise control (decisions_secondary.csv)", "plan sections 6, 8 and 9; no frozen step applied them"),
    ("src/confirm/estimators.py, h6", "percentile interval of rho from 5,000 bootstrap replicates that resample the "
     "families, drawn after the 10,000 permutations", "plan section 9 (rho reported with a bootstrap interval over "
     "families)"),
    ("src/confirm/analysis.py", "the contrast Delta(T3) - Delta(T1) of the Q tertiles inside every replicate, pooled "
     "and per family; C2 (O, R, G_all, G_sup at S*) without perceptual-duplicate groups and without regime-flagged "
     "pairs", "plan section 9 (contrast with its interval) and section 10, items 6 and 7 (C1 and C2)"),
    ("src/confirm/acquisition.py, identifier_measures; scripts/confirm_run.py, prepare_rows", "identifier availability "
     "from the set's phase-1 histories plus the stored development histories of the same window (W: D4; W2: D6 Part 2, "
     "D12, D13), scaled by population of both halves over sampled observations with a history; identifier experience "
     "(median number of earlier identifications in the family)", "plan section 7.3, item 5; the first freeze used only "
     "the histories of the part's phase-2 rows, scaled by the phase-1 fraction, and no experience"),
    ("scripts/confirm_run.py, exact_duplicates; src/confirm/acquisition.py, parse_histories", "exact SHA-256 duplicates "
     "keep the observation with the lowest numeric observation id of the API record", "plan section 5; the first freeze "
     "kept the first row in sample order (lowest uuid)"),
    ("scripts/confirm_run.py, report-strata; src/confirm/acquisition.py, cap_fractions", "the stratum report shows the "
     "phase-2 photographs before and after the registered cap rule and the projected bytes; phase2 and the report use "
     "one cap function", "plan section 4.3 (counts and projected budget between the phases)"),
    ("scripts/confirm_run.py, analyse-joint", "the eight and the six new families analysed together for the groups of "
     "section 10 (animals, plants, Polyporaceae) and the Spearman relation over the 14 families", "plan section 10, "
     "heterogeneity (groups across both sets; secondary relation over 14 families)"),
    ("scripts/confirm_driver.py (new)", "the four sets from the registered values; run order; pre-approval between the "
     "phases; after an API stop (30 minutes of failure) a wait of 60 minutes and a resume, at most three times; progress "
     "log with thread count and hardware", "plan sections 3, 4.3 and 8; task N18"),
    ("configs/confirmatory.yaml", "new block run_settings (download limits and counters, API waits, minimum free "
     "space); no registered value changed", "settings of the run"),
    ("tests/test_freeze_v2.py (new)", "unit tests of the corrections", "-"),
]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", required=True)
    ap.add_argument("--git", required=True)
    a = ap.parse_args()
    git = [a.git, "-C", str(ROOT)]
    full = subprocess.run(git + ["rev-parse", a.commit], capture_output=True, text=True, check=True).stdout.strip()
    rows, same = [], True
    for f in TRACKED:
        h = sha(subprocess.run(git + ["show", f"{full}:{f}"], capture_output=True, check=True).stdout)
        wt = sha((ROOT / f).read_bytes())
        same &= h == wt
        rows.append((f, h, "yes" if h == wt else "NO"))
    man = {r["path_in_inputs"]: r["sha256"] for r in csv.DictReader(open(ROOT / "inputs/MANIFEST.csv", encoding="utf-8"))}
    for f in COPIED:
        h = sha((ROOT / f).read_bytes())
        ok = man.get(f.replace("inputs/", "", 1)) == h
        same &= ok
        rows.append((f + " (copied input, not tracked)", h, "matches inputs/MANIFEST.csv" if ok else "DIFFERS"))
    for f in UNTRACKED:
        rows.append((f + " (development output, not tracked)", sha((ROOT / f).read_bytes()), "-"))
    for d in FOLDERS:
        files = sorted((ROOT / d).glob("*.json.gz"))
        dig = sha("\n".join(f"{p.name} {sha(p.read_bytes())}" for p in files).encode())
        rows.append((f"{d}/ ({len(files)} files, digest of names and SHA-256; not tracked)", dig, "-"))
    if not same:
        raise SystemExit("a listed file differs from the commit or from its manifest; nothing written")
    r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT,
                       capture_output=True, text=True)
    log = r.stdout + r.stderr
    for form in (str(ROOT).replace("\\", "\\\\"), str(ROOT), str(ROOT).replace("\\", "/")):
        log = log.replace(form, "<project root>")
    (ROOT / "outputs/freeze_v2").mkdir(parents=True, exist_ok=True)
    (ROOT / "outputs/freeze_v2/unit_tests.txt").write_text(log.replace("\r\n", "\n"), encoding="utf-8", newline="\n")
    ran = re.search(r"Ran (\d+) tests? in", log)
    passed = r.returncode == 0 and "\nOK" in log
    if not passed:
        raise SystemExit("the test suite does not pass; nothing written")
    per = {}
    for m in re.finditer(r"\(test_(\w+)\.\w+\) \.\.\. (\w+)", log):
        per.setdefault(m.group(1), []).append(m.group(2))
    L = ["# Corrected code freeze of the confirmatory pipeline", "",
         f"Corrected freeze commit: {full}. First freeze: {FIRST} (docs/reports/code_freeze.md, unchanged). The correction "
         "was made before any confirmatory data were requested or read: configs/registration_lock.json has never "
         "existed, and the guard refuses locked-half observers and the new and replication families in every run so far "
         "(task N18 stopped before the lock). The validation on development data is D13 addendum 2 "
         "(docs/reports/D13_report.md). The registration audit is docs/reports/registration_audit.md. No tag is set. "
         "Script: scripts/n18a_code_freeze_v2.py.", "",
         "## Files and SHA-256 at the corrected freeze commit", "",
         "| file | SHA-256 | working tree equal |", "|---|---|---|"]
    L += [f"| {f} | {h} | {s} |" for f, h, s in rows]
    L += ["", "Model weights are checked against configs/model_pins.json at every load; the snapshot files against their "
          "SHA-256 manifest when the frames and the snapshot covariates are built.", "",
          "## Test suite", "",
          f"Full suite (python -m unittest discover -s tests): {ran.group(1) if ran else '?'} tests, result OK; per file: "
          + ", ".join(f"test_{k} {len(v)} ({'all ok' if all(x == 'ok' for x in v) else 'not all ok'})"
                      for k, v in sorted(per.items())) + ". Output: outputs/freeze_v2/unit_tests.txt.", "",
          "## Changes against the first freeze", "", "| file and step | change | reason |", "|---|---|---|"]
    L += [f"| {a_} | {b_} | {c_} |" for a_, b_, c_ in CHANGES]
    L += ["", "No registered value, set, size, fraction, threshold or definition of the plan is changed.", "",
          "## Run order", "",
          "Driver scripts/confirm_driver.py, confirmatory mode, every step through scripts/confirm_run.py:", "",
          "1. frame: the eight families (windows W and W2, locked half) and the 36 other families (window W, both halves);",
          "2. for each set in the order eight_W, eight_W2, new_W, replication_W: phase1, covariates, histories, "
          "report-strata, pre-approval (counts and projected budget only), phase2, download, predict;",
          "3. analyse (each set), h6 (new_W and replication_W), analyse-joint (eight_W and new_W), decide.", "",
          "## Registration-lock procedure", "",
          "configs/registration_lock.json is written only by the confirmatory task, after the registration and its update "
          "note. It holds the registration identifier, the code commit of this record and the date; in confirmatory mode "
          "the guard allows protected data only with a non-empty registration_id and code_commit.", ""]
    (ROOT / "docs/reports/code_freeze_v2.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L)[:3000])


if __name__ == "__main__":
    main()
