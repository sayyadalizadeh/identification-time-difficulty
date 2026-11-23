# IdentificationTime_review

Review package of the study of identification time and the difficulty of citizen-science observations for biodiversity image models. It holds the analysis code, the pre-registered plan, the reports, the aggregated result tables and one row-level table of the analysed observations without user data. It is a fresh export of selected files, not the project repository or its history.

Built on 2026-11-23 from commit b0f11b2a4c5cc124bda217a14555157969616815 of the project repository; every copied file is equal to its committed version (checked when the package was built). FILES.csv lists the bytes and SHA-256 of every file.

Status: Provided for peer review; a versioned archive with a persistent identifier will be created on acceptance.

## Contents

- [DATA_DICTIONARY.md](DATA_DICTIONARY.md): columns and keys of the observation table and of the main result tables, model codes and stratum codes
- [REPRODUCE.md](REPRODUCE.md): software environment, external inputs, order of the scripts, what can be recomputed from this repository alone
- [LICENSE](LICENSE): MIT licence of the code (licences of the tables: section Licences)
- requirements.txt: pinned Python packages

## Folder map

| folder | content |
|---|---|
| configs/ | confirmatory.yaml (settings of the confirmatory run), model_pins.json (model revisions and SHA-256 of the weight files) |
| docs/PLAN.md | the plan with every decision D1 to D19 (registered before each run) |
| docs/reports/ | confirmatory results, corrected code freeze, reports of D14 to D19 |
| docs/environment/ | environment record of the project start and installed package versions |
| src/, scripts/ | the code used by the confirmatory run and by D14 to D19 (list below) |
| outputs/confirm/ | aggregated tables of the confirmatory run (csv and json) |
| outputs/D19/ | aggregated tables of D19 (csv and json; post hoc) |
| data/analysed_observations.csv | one row per analysed observation (columns below) |

## Code files

- confirmatory run (frozen code, docs/reports/code_freeze_v2.md): scripts/confirm_driver.py, scripts/confirm_run.py, src/confirm/__init__.py, src/confirm/config.py, src/confirm/guard.py, src/confirm/acquisition.py, src/confirm/covariates.py, src/confirm/infer.py, src/confirm/estimators.py, src/confirm/analysis.py, src/confirm/decide.py, src/d6_lib.py, src/moderation.py, src/halves.py, src/zeroshot.py
- report of the confirmatory run and of the code freeze: scripts/n18_report.py, scripts/n18a_code_freeze_v2.py
- D14: scripts/d14_run.py, scripts/d14_report.py
- D15: scripts/n20_run.py
- D16: scripts/d16_run.py, scripts/d16_complete.py, scripts/d16_report.py, scripts/d16_results_report.py, src/budget_ledger.py
- D17: scripts/d17_fetch_provenance.py, scripts/d17_membership.py, scripts/d17_report.py
- D18: scripts/d18_examples.py
- D19: scripts/d19_common.py, scripts/d19_snapshot.py, scripts/d19_part_a.py, scripts/d19_part_b.py, scripts/d19_part_c.py, scripts/d19_report.py

## How each reported table is produced

| report | produced by |
|---|---|
| docs/reports/confirmatory_results.md | tables of outputs/confirm/ written by scripts/confirm_driver.py (every step through scripts/confirm_run.py: frames, phase 1, histories, phase 2, photographs, predictions, analyse, joint, h6, decide) and formatted by scripts/n18_report.py |
| docs/reports/code_freeze_v2.md | scripts/n18a_code_freeze_v2.py (SHA-256 of the frozen files at the freeze commit) |
| docs/reports/D14_report.md | scripts/d14_run.py (computation) and scripts/d14_report.py (report) |
| docs/reports/D15_report.md | scripts/n20_run.py (computation and report) |
| docs/reports/D16_report.md | scripts/d16_run.py and scripts/d16_report.py |
| docs/reports/D16_results.md | scripts/d16_run.py, scripts/d16_complete.py and scripts/d16_results_report.py |
| docs/reports/D17_report.md | scripts/d17_fetch_provenance.py, scripts/d17_membership.py, scripts/d17_report.py |
| docs/reports/D18_report.md | scripts/d18_examples.py (illustrative panel; the photographs are not included) |
| docs/reports/D19_report.md | scripts/d19_snapshot.py, d19_part_a.py, d19_part_b.py, d19_part_c.py (computation; tables in outputs/D19/) and scripts/d19_report.py (report) |

The confirmatory results (docs/reports/confirmatory_results.md) are the primary results; D14 to D19 are post hoc. Output folders of D14 to D18 are not included; their numbers are in their reports. The scripts need the data sources below, the identification histories of the API (not included: they contain user names) and the photographs (not included); paths such as inputs/... and the snapshot folder are passed as arguments or refer to files that are not part of this package.

## Result tables

101 csv and json files of outputs/confirm/ and outputs/D19/, copied byte for byte, except: no parquet file, no photograph folder, no raw API response, no cache, no log; the row-level near-duplicate index pairs (phash_pairs.csv) are left out. In the run specifications outputs/confirm/spec_*.json, 4 absolute local folder values (the model cache) were replaced by the text "<absolute local folder; removed from the package>".

## data/analysed_observations.csv

155318 rows: the analysis rows of the four confirmatory sets (phase-2 rows with a prediction, exact duplicates dropped as in the confirmatory run). Columns:

- set: eight_W (H1), eight_W2 (H5), new_W (H2), replication_W
- observation_uuid: observation identifier of the iNaturalist Open Data export
- first_photo_id: photo id of the first photograph (the photograph analysed)
- licence: licence of that photograph in the export (CC0, CC-BY, CC-BY-NC)
- family, stratum: family and identification-time stratum (A0 to A3, B1, B2; docs/PLAN.md)
- phase2_weight: weight of the row in phase 2 of the two-phase sample
- observer_hash: first 16 hex characters of a salted SHA-256 digest of the numeric observer id; the salt is not part of the package, so the digest identifies the same observer within this table only
- pred_<model>: predicted species (taxon id); correct_species_<model>, correct_genus_<model>: 1 if the prediction equals the reference species (genus), 0 otherwise; correct_species is 0 for every needs_id row (strata B1, B2); see DATA_DICTIONARY.md. Models: Z25 BioCLIP 2.5 Huge, Z2 BioCLIP 2, Z1 first BioCLIP, BT-CLIP-O (configs/model_pins.json)

The attribution string of the photographs is not included: the export holds no attribution field, and the attribution given by the API contains user names or logins.

## Data sources

- iNaturalist Open Data export of 2026-10-27 (observations, photos and taxa tables)
- iNaturalist API v1 (identification histories of the sampled observations)
- Model weights of the revisions pinned in configs/model_pins.json

Photographs are not redistributed. Each can be retrieved by its photo id from iNaturalist under its licence.

## Software

Python 3.10.22 on Windows 10; CPU thread count 20 in numerical scripts. Package versions: docs/environment/package_versions.txt.

## Licences

- Code (src/, scripts/): MIT licence (LICENSE).
- Derived tables (outputs/, data/analysed_observations.csv): Creative Commons Attribution 4.0 International (CC BY 4.0).
- Photographs are not included; they keep their own licences on iNaturalist.
