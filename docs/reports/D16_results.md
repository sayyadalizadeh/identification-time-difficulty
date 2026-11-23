# D16 - Exposure test of BioCLIP 2.5 Huge (post hoc): results

Decision D16 in docs/PLAN.md (post hoc, written after the confirmatory results were seen; commit 0a5843e, before any part of D16 was run). Development half only. Task N21 stopped D16 at its download limit (docs/reports/D16_report.md, unchanged); task N22 completed it with the design unchanged. Scripts: scripts/d16_run.py (N21) and scripts/d16_complete.py (N22); outputs in outputs/D16/ (row tables, raw responses and photographs not tracked).

## Download limit of task N21

Task N21 passed its download limit of 1.5 GB: the photographs of set B came to 1,505,970,832 bytes, 5,970,832 bytes above the limit (the budget was checked before each batch of 400 photographs), and the 31.5 MB of raw API responses of the histories were not counted against the limit.

## Data

Set A: research-grade observations of the D4 sample (window W 2024-07-01 to 2024-09-30, eight families, development half) with T < 1 day and the stored first-photograph correctness of the three models: 13,429 rows.

Set B (N21): development-half observations of the eight families observed 2026-08-28 to 2026-10-20; frame manifest checks observations.csv.gz PASS, photos.csv.gz PASS, taxa.csv.gz PASS; 673,473 development-half rows of the eight families in the window before the photograph and label filters; simple random sample of up to 1,500 research-grade frame rows per family (seed 20261124): Fabaceae 1,500 of 27,732; Asteraceae 1,500 of 78,235; Columbidae 1,500 of 17,287; Lamiaceae 1,500 of 14,050; Nymphalidae 1,500 of 60,053; Anatidae 1,500 of 35,899; Rosaceae 1,500 of 17,590; Sciuridae 1,500 of 16,592.

Histories (N21): 60 requests, 11,993 returned, failed batches 0, hidden identifications 0; T reconstructed for 11,989; T < 1 day: 9,305. N22 made no API request; it recomputed T from the saved responses (controls: all 60 batches present PASS; rows with T < 1 day equal to N21 PASS; rows with T defined equal to N21 PASS).

Photographs (medium size) of the 9,305 rows with T < 1 day: 8,798 rows with a photograph obtained in N21; 2 rows whose photograph failed after 3 retries in N21 (not retried); 505 rows downloaded in N22 (Sciuridae 505), 505 obtained and 0 failed, 101,635,117 bytes (101,635,117 bytes counted in the N22 ledger). One Columbidae photograph (photo id 730742096) is the first photograph of two sampled observations with different species; both rows are kept, as in the registered code. SHA-256 of every photograph checked against its manifest before prediction: PASS. Rows of set B with predictions: 9,303.

Model checks (pinned weight file, SHA-256): BioCLIP 2.5 Huge folder_exists PASS, selected_file_is_loaded_file PASS, bytes_equal_to_pin PASS, sha256_equal_to_pin PASS; BioCLIP 2 folder_exists PASS, selected_file_is_loaded_file PASS, bytes_equal_to_pin PASS, sha256_equal_to_pin PASS; first BioCLIP folder_exists PASS, selected_file_is_loaded_file PASS, bytes_equal_to_pin PASS, sha256_equal_to_pin PASS.

## Accuracy per set and family (species level, unweighted, rows with T < 1 day)

| set | family | rows | observers | species | BioCLIP 2.5 Huge | BioCLIP 2 | first BioCLIP |
|---|---|---|---|---|---|---|---|
| A | Anatidae | 2,156 | 1,413 | 70 | 0.932 | 0.884 | 0.627 |
| B | Anatidae | 1,359 | 994 | 71 | 0.932 | 0.889 | 0.645 |
| A | Asteraceae | 1,158 | 865 | 237 | 0.971 | 0.956 | 0.783 |
| B | Asteraceae | 993 | 843 | 212 | 0.969 | 0.956 | 0.753 |
| A | Columbidae | 2,211 | 1,424 | 35 | 0.953 | 0.924 | 0.648 |
| B | Columbidae | 1,347 | 1,077 | 34 | 0.950 | 0.933 | 0.638 |
| A | Fabaceae | 1,350 | 996 | 159 | 0.967 | 0.944 | 0.818 |
| B | Fabaceae | 990 | 806 | 159 | 0.964 | 0.930 | 0.740 |
| A | Lamiaceae | 1,338 | 996 | 91 | 0.983 | 0.979 | 0.900 |
| B | Lamiaceae | 960 | 793 | 87 | 0.985 | 0.979 | 0.851 |
| A | Nymphalidae | 2,114 | 1,648 | 136 | 0.967 | 0.944 | 0.826 |
| B | Nymphalidae | 1,341 | 1,166 | 120 | 0.969 | 0.948 | 0.784 |
| A | Rosaceae | 1,227 | 870 | 124 | 0.961 | 0.939 | 0.764 |
| B | Rosaceae | 1,040 | 789 | 123 | 0.945 | 0.918 | 0.711 |
| A | Sciuridae | 1,875 | 1,467 | 38 | 0.959 | 0.932 | 0.701 |
| B | Sciuridae | 1,273 | 1,074 | 35 | 0.950 | 0.924 | 0.686 |

## D with reference BioCLIP 2 (primary reading)

D_f = gain of BioCLIP 2.5 Huge over the reference in set A minus that in set B, over the species present in both sets, weighted by the set-A species shares; points. 2,000 observer-cluster bootstrap replicates within each set (seed 20261121).

| family | species in both sets | rows A | rows B | D_f [95%] |
|---|---|---|---|---|
| Anatidae | 70 | 2,156 | 1,358 | 0.422 [-1.478, 2.383] |
| Asteraceae | 175 | 1,032 | 925 | 0.172 [-1.822, 2.266] |
| Columbidae | 34 | 2,210 | 1,347 | 1.010 [-0.833, 2.812] |
| Fabaceae | 130 | 1,271 | 941 | -0.731 [-2.862, 1.354] |
| Lamiaceae | 81 | 1,315 | 949 | -0.845 [-2.213, 0.570] |
| Nymphalidae | 107 | 1,925 | 1,313 | 0.320 [-0.717, 1.328] |
| Rosaceae | 116 | 1,207 | 1,030 | -0.549 [-2.557, 1.604] |
| Sciuridae | 35 | 1,862 | 1,273 | 0.470 [-1.244, 2.266] |

D (mean over the eight families, equal weights) = 0.034 [-0.580, 0.697] points.

## D with reference first BioCLIP

D_f = gain of BioCLIP 2.5 Huge over the reference in set A minus that in set B, over the species present in both sets, weighted by the set-A species shares; points. 2,000 observer-cluster bootstrap replicates within each set (seed 20261121).

| family | species in both sets | rows A | rows B | D_f [95%] |
|---|---|---|---|---|
| Anatidae | 70 | 2,156 | 1,358 | 3.645 [0.082, 7.132] |
| Asteraceae | 175 | 1,032 | 925 | -1.650 [-5.937, 3.142] |
| Columbidae | 34 | 2,210 | 1,347 | 0.610 [-2.695, 3.984] |
| Fabaceae | 130 | 1,271 | 941 | -6.884 [-10.973, -2.490] |
| Lamiaceae | 81 | 1,315 | 949 | -8.956 [-12.962, -5.350] |
| Nymphalidae | 107 | 1,925 | 1,313 | -3.910 [-7.999, -0.313] |
| Rosaceae | 116 | 1,207 | 1,030 | -5.053 [-9.227, -0.698] |
| Sciuridae | 35 | 1,862 | 1,273 | -0.317 [-3.979, 3.281] |

D (mean over the eight families, equal weights) = -2.814 [-4.245, -1.299] points.

## Reading fixed in D16 (reference BioCLIP 2)

Rule: no material sign of exposure if the upper bound of the 95% interval is below 1.0 point; a sign of exposure if the lower bound is above 1.0 point; inconclusive otherwise.

Upper bound 0.697: below 1.0 point - met. Lower bound -0.580: above 1.0 point - not met. Reading: no material sign of exposure.

## Limitations stated in D16

Two years of change in cameras and observers between the sets; a partly matched season (set A July to September 2024, set B late August to October 2026); possible exposure of BioCLIP 2 through images republished by EOL.

Run time of the completion in N22: 6.0 minutes.
