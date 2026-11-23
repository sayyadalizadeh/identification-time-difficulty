# Reproduction

## Software environment

From docs/environment/package_versions.txt: Python 3.10.22 on Windows; packages pinned in requirements.txt. The
builds torch 2.11.0+cu128 and torchvision 0.26.0+cu128 come from the PyTorch package index for CUDA 12.8. GPU work used
one NVIDIA GPU with 16 GB; numerical scripts fix 20 CPU threads; every resampling uses a fixed seed (20261121 for the
confirmatory run; the seed of each post hoc analysis is stated in its report, 20261124 for D19). Scripts are run from the repository root with
`python scripts/<script>.py [arguments]`.

## External inputs (not in this repository)

1. iNaturalist Open Data export of 2026-10-27: observations.csv.gz, photos.csv.gz and taxa.csv.gz, passed with
   --snapshot <folder> and checked against a SHA-256 manifest passed with --manifest <csv>.
2. Identification histories of the sampled observations from the iNaturalist API v1, at most one request per second.
   The raw responses contain user names and logins and are not published.
3. First photographs (medium size) of the sampled observations, retrieved by photo id under their licences
   (data/analysed_observations.csv lists photo id and licence). Photographs are not redistributed.
4. Model weights of the revisions pinned in configs/model_pins.json (repository, revision, file, bytes, SHA-256; the
   file marked loaded_file is the one loaded), placed in a local Hugging Face cache passed with --hf-cache <folder>
   and loaded offline.
5. Tables of earlier exploratory work referred to as inputs/... in the code (the species table of the label spaces and
   stored development-half histories) are not included; see configs/confirmatory.yaml and the docstrings.

## Order of the scripts

Confirmatory run (registered; docs/PLAN.md, docs/reports/code_freeze_v2.md):

1. `scripts/confirm_driver.py --mode confirmatory --snapshot <folder> --manifest <csv> --hf-cache <folder>` runs every
   step of scripts/confirm_run.py in the registered order: frames; per set (eight_W, eight_W2, new_W, replication_W)
   phase1, covariates, histories, report-strata, phase2, download, predict; then analyse (each set), h6,
   analyse-joint and decide. Outputs: outputs/confirm/.
2. `scripts/n18_report.py --lock-commit <commit>` writes docs/reports/confirmatory_results.md from outputs/confirm/.
3. `scripts/n18a_code_freeze_v2.py --commit <commit> --git <git>` writes docs/reports/code_freeze_v2.md.

Post hoc analyses (each registered in docs/PLAN.md before it was run):

| decision | scripts, in order |
|---|---|
| D14 | scripts/d14_run.py --snapshot <folder> --hf-cache <folder>; scripts/d14_report.py --plan-commit <commit> |
| D15 | scripts/n20_run.py |
| D16 | scripts/d16_run.py --snapshot <folder> --manifest <csv> --hf-cache <folder>; scripts/d16_report.py --plan-commit <commit>; scripts/d16_complete.py --snapshot <folder> --hf-cache <folder>; scripts/d16_results_report.py --plan-commit <commit> |
| D17 | scripts/d17_fetch_provenance.py (--first-bytes, --rest, --verify); scripts/d17_membership.py; scripts/d17_report.py --plan-commit <commit> |
| D18 | scripts/d18_examples.py --plan-commit <commit> --addendum-commit <commit> |
| D19 | scripts/d19_snapshot.py; scripts/d19_part_a.py; scripts/d19_part_b.py; scripts/d19_part_c.py; scripts/d19_report.py (arguments: see each docstring) |

Arguments not listed here: see the docstring of each script.

## What can be recomputed from the files of this repository alone

No script runs on the included files alone: every script also reads row-level tables, histories, photographs or
model weights that are not included. The following can be recomputed or checked without the external inputs:

- every number of docs/reports/confirmatory_results.md and of the hypothesis table: they are read from
  outputs/confirm/decisions.csv, decisions_secondary.csv, <set>/estimates.csv, joint_14/estimates_joint.csv,
  eight_W/q_tertiles.csv, <set>/stratum_report.csv, <set>/photo_failures.csv and h6.json;
- the Holm procedure over H1 to H6 from the p-values in decisions.csv (src/confirm/decide.py);
- the point value of rho of H6 from the family values delta and fast_share of outputs/confirm/h6.json, and the
  leave-one-family-out values of rho of D14 (a); the permutation p-value and the bootstrap interval are recomputed up
  to Monte Carlo error unless the same generator and seed are used;
- the point values of rho by kingdom in D15 (a), from h6.json and the kingdom column of
  outputs/D19/snapshot/families_taxonomy.csv;
- the random-effects pooling and the meta-regression of D19 item B7, from outputs/D19/B/B7_family_inputs_14.csv and
  B7_family_inputs_36.csv;
- every table of docs/reports/D19_report.md, read from the csv and json files of outputs/D19/;
- the unweighted species-level accuracy per set, family and model (outputs/confirm/<set>/accuracy.csv) from
  data/analysed_observations.csv (research-grade strata A0 to A3), to within 0.001: accuracy.csv was computed before
  the exact duplicates (1 to 28 rows per set) were dropped.

Delta, ER and the other weighted estimates cannot be recomputed from data/analysed_observations.csv, because it does
not hold the reference species of each row or the identification time T.
