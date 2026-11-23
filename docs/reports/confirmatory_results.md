# Confirmatory results

Registration: https://osf.io/yzcs9 (with its update note on the corrected freeze). Original code freeze: f3d452832935f5e9d8f829dc6f588e58cb4c2a5b; corrected freeze: 966fa55500ba48d892c9c2ed403b5ad8dea9d1aa (docs/reports/code_freeze_v2.md); registration lock: commit 990e22b. Driver: scripts/confirm_driver.py, confirmatory mode, every step through scripts/confirm_run.py; single run.

## Run

From 2026-11-22 12:39 to 2026-11-22 22:19 (9.67 hours; limit 14). CPU threads 20 per numerical step (scripts/confirm_run.py) | processor Intel64 Family 6 Model 198 Stepping 2, GenuineIntel | 24 logical processors | Python 3.10.22 | seed 20261121. Photographs downloaded: 20.22 GB (counter outputs/confirm/download_bytes.json; limit 24 GB). Free space on D: at the end 49.0 GB. Bootstrap: 5,000 replicates for the estimates of H1 to H6, 2,000 for all other estimates; 10,000 permutations for H6; seed 20261121.

| step | seconds |
|---|---|
| frame frames_eight_locked.parquet | 353 |
| frame frames_new_replication_both.parquet | 491 |
| eight_W phase1 | 3 |
| eight_W covariates | 113 |
| eight_W histories | 4,351 |
| eight_W report-strata | 1 |
| eight_W phase2 | 1 |
| eight_W download | 6,419 |
| eight_W predict | 1,298 |
| eight_W2 phase1 | 2 |
| eight_W2 covariates | 93 |
| eight_W2 histories | 2,895 |
| eight_W2 report-strata | 1 |
| eight_W2 phase2 | 1 |
| eight_W2 download | 2,907 |
| eight_W2 predict | 577 |
| new_W phase1 | 3 |
| new_W covariates | 95 |
| new_W histories | 2,536 |
| new_W report-strata | 1 |
| new_W phase2 | 1 |
| new_W download | 3,850 |
| new_W predict | 745 |
| replication_W phase1 | 4 |
| replication_W covariates | 94 |
| replication_W histories | 2,398 |
| replication_W report-strata | 1 |
| replication_W phase2 | 1 |
| replication_W download | 3,299 |
| replication_W predict | 585 |
| eight_W analyse | 613 |
| eight_W2 analyse | 351 |
| new_W analyse | 343 |
| replication_W analyse | 175 |
| h6 | 2 |
| analyse-joint | 165 |
| decide | 1 |

## Counts per set, family and stratum

Phase 1: the stratum of every phase-1 observation (A0 to A3 research grade by identification time; B1 and B2 needs_id by label support; T undefined: research grade in the snapshot but not reconstructed; failed: no history after 3 retries). Phase 2: photographs after the registered cap rule (no family was reduced by it). Stratum-count reports written between the phases: docs/reports/N18_strata_<set>.md.

### eight_W: eight families, locked half, window W

| family | frame | phase 1 | A0 | A1 | A2 | A3 | B1 | B2 | T undefined | failed history | phase 2 | photographs ok | photograph failures |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Anatidae | 41,543 | 12,000 | 10,332 | 986 | 316 | 107 | 174 | 71 | 14 | 0 | 6,733 | 6,732 | 1 |
| Asteraceae | 291,476 | 12,000 | 3,226 | 1,494 | 1,481 | 572 | 4,516 | 706 | 4 | 1 | 8,124 | 8,124 | 0 |
| Columbidae | 21,345 | 12,000 | 10,545 | 852 | 330 | 121 | 89 | 55 | 8 | 0 | 6,674 | 6,670 | 4 |
| Fabaceae | 97,230 | 12,000 | 4,323 | 2,041 | 1,773 | 352 | 2,947 | 553 | 10 | 1 | 8,355 | 8,353 | 2 |
| Lamiaceae | 54,220 | 12,000 | 4,526 | 2,138 | 1,421 | 441 | 3,085 | 383 | 6 | 0 | 8,188 | 8,188 | 0 |
| Nymphalidae | 114,041 | 12,000 | 9,047 | 1,008 | 483 | 130 | 1,002 | 326 | 3 | 1 | 6,972 | 6,972 | 0 |
| Rosaceae | 93,376 | 12,000 | 3,137 | 1,522 | 1,385 | 471 | 4,777 | 700 | 7 | 1 | 8,034 | 8,034 | 0 |
| Sciuridae | 18,870 | 12,000 | 8,660 | 1,789 | 594 | 158 | 577 | 213 | 9 | 0 | 7,372 | 7,372 | 0 |

Histories: 95,996 of 96,000 returned in 480 requests; failed request batches: 0; hidden identifications excluded: 1; share of snapshot research-grade observations reconstructed as research grade on 2026-10-27: 0.9992. Exact duplicate photographs dropped (lowest observation id kept): 28. Analysis rows: 60,417; research grade with T: 48,833.

### eight_W2: eight families, locked half, window W2

| family | frame | phase 1 | A0 | A1 | A2 | A3 | B1 | B2 | T undefined | failed history | phase 2 | photographs ok | photograph failures |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Anatidae | 83,610 | 8,000 | 7,324 | 389 | 108 | 13 | 103 | 59 | 3 | 1 | 2,797 | 2,797 | 0 |
| Asteraceae | 64,433 | 8,000 | 2,731 | 965 | 530 | 129 | 3,251 | 393 | 1 | 0 | 3,811 | 3,811 | 0 |
| Columbidae | 25,816 | 8,000 | 7,289 | 488 | 105 | 25 | 60 | 28 | 3 | 2 | 2,851 | 2,851 | 0 |
| Fabaceae | 34,796 | 8,000 | 2,585 | 943 | 672 | 197 | 3,110 | 493 | 0 | 0 | 4,014 | 4,014 | 0 |
| Lamiaceae | 17,798 | 8,000 | 4,261 | 1,258 | 591 | 111 | 1,564 | 207 | 8 | 0 | 3,914 | 3,914 | 0 |
| Nymphalidae | 24,234 | 8,000 | 5,849 | 538 | 248 | 112 | 935 | 311 | 7 | 0 | 3,244 | 3,244 | 0 |
| Rosaceae | 25,160 | 8,000 | 2,221 | 795 | 535 | 151 | 3,846 | 451 | 1 | 0 | 3,752 | 3,751 | 1 |
| Sciuridae | 14,354 | 8,000 | 6,512 | 700 | 296 | 63 | 351 | 69 | 8 | 1 | 3,187 | 3,186 | 1 |

Histories: 63,996 of 64,000 returned in 320 requests; failed request batches: 0; hidden identifications excluded: 0; share of snapshot research-grade observations reconstructed as research grade on 2026-10-27: 0.9994. Exact duplicate photographs dropped (lowest observation id kept): 10. Analysis rows: 27,558; research grade with T: 21,583.

### new_W: six new families, both halves, window W

| family | frame | phase 1 | A0 | A1 | A2 | A3 | B1 | B2 | T undefined | failed history | phase 2 | photographs ok | photograph failures |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Araneidae | 69,990 | 10,000 | 5,262 | 1,417 | 643 | 122 | 1,576 | 971 | 6 | 3 | 6,257 | 6,255 | 2 |
| Colubridae | 34,274 | 10,000 | 7,876 | 990 | 324 | 570 | 79 | 147 | 14 | 0 | 5,993 | 5,993 | 0 |
| Pinaceae | 46,038 | 10,000 | 2,755 | 1,657 | 1,195 | 459 | 3,506 | 421 | 6 | 1 | 6,162 | 6,161 | 1 |
| Poaceae | 107,165 | 10,000 | 2,594 | 1,537 | 991 | 305 | 4,172 | 393 | 8 | 0 | 5,775 | 5,775 | 0 |
| Polyporaceae | 34,921 | 10,000 | 1,636 | 1,022 | 1,010 | 295 | 5,211 | 819 | 5 | 2 | 5,527 | 5,527 | 0 |
| Ranidae | 42,599 | 10,000 | 6,056 | 1,929 | 725 | 135 | 545 | 598 | 11 | 1 | 6,579 | 6,579 | 0 |

Histories: 59,993 of 60,000 returned in 300 requests; failed request batches: 0; hidden identifications excluded: 0; share of snapshot research-grade observations reconstructed as research grade on 2026-10-27: 0.9987. Exact duplicate photographs dropped (lowest observation id kept): 11. Analysis rows: 36,279; research grade with T: 28,403.

### replication_W: 30 replication families, both halves, window W (research-grade frame)

| family | frame | phase 1 | A0 | A1 | A2 | A3 | B1 | B2 | T undefined | failed history | phase 2 | photographs ok | photograph failures |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Acrididae | 29,324 | 1,500 | 611 | 416 | 400 | 71 | 0 | 0 | 2 | 0 | 1,193 | 1,193 | 0 |
| Apiaceae | 43,032 | 1,500 | 785 | 371 | 273 | 70 | 0 | 0 | 1 | 0 | 1,106 | 1,106 | 0 |
| Apocynaceae | 30,276 | 1,500 | 1,031 | 270 | 146 | 52 | 0 | 0 | 0 | 1 | 984 | 984 | 0 |
| Ardeidae | 67,342 | 1,500 | 946 | 90 | 50 | 14 | 0 | 0 | 0 | 400 | 627 | 627 | 0 |
| Asparagaceae | 22,256 | 1,500 | 779 | 342 | 319 | 57 | 0 | 0 | 3 | 0 | 1,108 | 1,108 | 0 |
| Caprifoliaceae | 29,890 | 1,500 | 760 | 383 | 250 | 107 | 0 | 0 | 0 | 0 | 1,120 | 1,120 | 0 |
| Caryophyllaceae | 30,756 | 1,500 | 778 | 315 | 346 | 59 | 0 | 0 | 1 | 1 | 1,109 | 1,109 | 0 |
| Chrysomelidae | 13,663 | 1,500 | 941 | 324 | 171 | 63 | 0 | 0 | 1 | 0 | 1,028 | 1,027 | 1 |
| Coccinellidae | 42,234 | 1,500 | 1,125 | 284 | 69 | 21 | 0 | 0 | 1 | 0 | 936 | 935 | 1 |
| Cyperaceae | 9,055 | 1,500 | 643 | 363 | 375 | 117 | 0 | 0 | 2 | 0 | 1,177 | 1,177 | 0 |
| Erebidae | 79,856 | 1,500 | 1,045 | 211 | 190 | 54 | 0 | 0 | 0 | 0 | 977 | 977 | 0 |
| Ericaceae | 70,077 | 1,500 | 919 | 351 | 187 | 42 | 0 | 0 | 1 | 0 | 1,040 | 1,040 | 0 |
| Fagaceae | 24,850 | 1,500 | 723 | 374 | 301 | 101 | 0 | 0 | 1 | 0 | 1,138 | 1,137 | 1 |
| Formicidae | 13,036 | 1,500 | 943 | 308 | 200 | 45 | 0 | 0 | 3 | 1 | 1,025 | 1,025 | 0 |
| Geometridae | 41,397 | 1,500 | 1,119 | 226 | 128 | 26 | 0 | 0 | 1 | 0 | 940 | 940 | 0 |
| Hesperiidae | 51,508 | 1,500 | 938 | 318 | 192 | 50 | 0 | 0 | 2 | 0 | 1,029 | 1,029 | 0 |
| Laridae | 43,547 | 1,500 | 1,048 | 244 | 177 | 27 | 0 | 0 | 4 | 0 | 972 | 972 | 0 |
| Libellulidae | 96,769 | 1,500 | 1,176 | 192 | 79 | 52 | 0 | 0 | 1 | 0 | 911 | 911 | 0 |
| Lycaenidae | 44,923 | 1,500 | 974 | 190 | 113 | 220 | 0 | 0 | 3 | 0 | 1,010 | 1,010 | 0 |
| Malvaceae | 19,838 | 1,500 | 679 | 358 | 326 | 137 | 0 | 0 | 0 | 0 | 1,161 | 1,161 | 0 |
| Noctuidae | 53,477 | 1,500 | 901 | 294 | 161 | 141 | 0 | 0 | 2 | 1 | 1,046 | 1,046 | 0 |
| Onagraceae | 29,692 | 1,500 | 839 | 411 | 182 | 64 | 0 | 0 | 4 | 0 | 1,077 | 1,077 | 0 |
| Pentatomidae | 33,660 | 1,500 | 1,147 | 204 | 85 | 62 | 0 | 0 | 1 | 1 | 925 | 925 | 0 |
| Pieridae | 42,864 | 1,500 | 849 | 321 | 248 | 79 | 0 | 0 | 2 | 1 | 1,072 | 1,072 | 0 |
| Plantaginaceae | 46,271 | 1,500 | 763 | 346 | 317 | 71 | 0 | 0 | 3 | 0 | 1,116 | 1,116 | 0 |
| Polygonaceae | 32,251 | 1,500 | 632 | 328 | 334 | 203 | 0 | 0 | 3 | 0 | 1,181 | 1,181 | 0 |
| Ranunculaceae | 29,248 | 1,500 | 674 | 363 | 378 | 83 | 0 | 0 | 2 | 0 | 1,161 | 1,161 | 0 |
| Syrphidae | 41,152 | 1,500 | 1,111 | 202 | 151 | 34 | 0 | 0 | 2 | 0 | 943 | 943 | 0 |
| Tettigoniidae | 19,929 | 1,500 | 878 | 296 | 249 | 76 | 0 | 0 | 1 | 0 | 1,060 | 1,060 | 0 |
| Vespidae | 31,800 | 1,500 | 1,206 | 156 | 67 | 70 | 0 | 0 | 1 | 0 | 896 | 896 | 0 |

Histories: 44,594 of 45,000 returned in 225 requests; failed request batches: 2; hidden identifications excluded: 0; share of snapshot research-grade observations reconstructed as research grade on 2026-10-27: 0.9989. Exact duplicate photographs dropped (lowest observation id kept): 1. Analysis rows: 31,064; research grade with T: 31,064.

## Deviations

- replication_W, Ardeidae: 400 of 1,500 phase-1 histories not obtained after 3 retries (26.7%; the stratum of these observations is unknown)
- replication_W, Coccinellidae, stratum A3: 1 of 21 photographs failed (4.8%)

## H1 to H6 (BioCLIP 2.5 Huge; Holm over H1 to H6 at one-sided 0.05)

Bounds are one-sided 95% bounds (5th and 95th percentiles of the replicates); p is the one-sided p-value (share of the 5,000 replicates at or below 0; H6: 10,000 permutations); the H6 interval comes from 5,000 bootstrap replicates over families.

| Holm order | hypothesis | set | estimate | 95% interval | lower bound | upper bound | p | companion | companion lower bound | companion upper bound | Holm threshold | rejected | grade |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | H1 | eight_W | Delta 4.408 | [3.893, 4.968] | 3.976 | 4.879 | 0 (no replicate at or below 0) | ER 1.941 | 1.827 | 2.101 | 0.0083 | yes | strong |
| 2 | H2 | new_W | Delta 4.167 | [2.987, 4.791] | 3.129 | 4.682 | 0 (no replicate at or below 0) | ER 1.548 | 1.377 | 1.633 | 0.0100 | yes | strong |
| 3 | H3 | eight_W | O 0.259 | [0.184, 0.332] | 0.196 | 0.319 | 0 (no replicate at or below 0) | R 1.061 | 1.045 | 1.076 | 0.0125 | yes | small |
| 4 | H4 | eight_W | G_sup 0.506 | [0.431, 0.583] | 0.443 | 0.570 | 0 (no replicate at or below 0) | - | n/a | n/a | 0.0167 | yes | shown |
| 5 | H5 | eight_W2 | Delta 4.620 | [3.699, 5.561] | 3.851 | 5.398 | 0 (no replicate at or below 0) | ER 2.027 | 1.799 | 2.293 | 0.0250 | yes | strong |
| 6 | H6 | new_W + replication_W | rho 0.574 | [0.270, 0.783] | n/a | n/a | < 0.0001 | - | n/a | n/a | 0.0500 | yes | shown |

H4 range (section 9): G_sup 0.506 and G_all 2.406 [2.222, 2.590] (5,000 replicates). H6: 36 families, left out: none; bootstrap replicates with undefined rho: 0.

## Secondary models (no family-wise control; rejected = one-sided p at most 0.05; 2,000 replicates)

| model | analogue of | set | estimate | 95% interval | lower bound | p | companion | companion lower bound | rejected | grade |
|---|---|---|---|---|---|---|---|---|---|---|
| BioCLIP 2 | H1 | eight_W | Delta 5.692 | [5.058, 6.325] | 5.162 | 0 (no replicate at or below 0) | ER 1.758 | 1.670 | yes | strong |
| BioCLIP 2 | H2 | new_W | Delta 5.224 | [3.726, 6.013] | 3.939 | 0 (no replicate at or below 0) | ER 1.465 | 1.319 | yes | strong |
| BioCLIP 2 | H5 | eight_W2 | Delta 6.556 | [5.430, 7.780] | 5.637 | 0 (no replicate at or below 0) | ER 1.961 | 1.786 | yes | strong |
| BioCLIP 2 | H3 | eight_W | O 0.426 | [0.335, 0.522] | 0.352 | 0 (no replicate at or below 0) | R 1.063 | 1.051 | yes | small |
| BioCLIP 2 | H4 | eight_W | G_sup 0.697 | [0.608, 0.792] | 0.621 | 0 (no replicate at or below 0) | - | n/a | yes | shown |
| first BioCLIP | H1 | eight_W | Delta 9.521 | [8.471, 10.521] | 8.616 | 0 (no replicate at or below 0) | ER 1.357 | 1.319 | yes | strong |
| first BioCLIP | H2 | new_W | Delta 4.071 | [2.770, 6.078] | 3.053 | 0 (no replicate at or below 0) | ER 1.097 | 1.072 | yes | present |
| first BioCLIP | H5 | eight_W2 | Delta 11.512 | [9.750, 13.089] | 10.103 | 0 (no replicate at or below 0) | ER 1.380 | 1.328 | yes | strong |
| first BioCLIP | H3 | eight_W | O 0.578 | [0.419, 0.738] | 0.447 | 0 (no replicate at or below 0) | R 1.022 | 1.017 | yes | small |
| first BioCLIP | H4 | eight_W | G_sup 0.944 | [0.790, 1.099] | 0.812 | 0 (no replicate at or below 0) | - | n/a | yes | shown |
| BT-CLIP-O | H1 | eight_W | Delta 3.810 | [3.177, 4.550] | 3.305 | 0 (no replicate at or below 0) | ER 1.068 | 1.059 | yes | present |
| BT-CLIP-O | H2 | new_W | Delta 2.980 | [1.543, 3.698] | 1.760 | 0 (no replicate at or below 0) | ER 1.046 | 1.027 | yes | present |
| BT-CLIP-O | H5 | eight_W2 | Delta 3.734 | [2.563, 4.960] | 2.745 | 0 (no replicate at or below 0) | ER 1.064 | 1.047 | yes | present |
| BT-CLIP-O | H3 | eight_W | O 0.133 | [-0.032, 0.313] | -0.009 | 0.0620 | R 1.002 | 1.000 | no | not shown |
| BT-CLIP-O | H4 | eight_W | G_sup 0.038 | [-0.141, 0.219] | -0.107 | 0.3435 | - | n/a | no | not shown |

## Pooled estimates per set (sections 7 and 10)

Value [95% interval] for every model; 2,000 replicates unless the quantity names 5,000; families left out by the not-estimable rule in the last column. Full tables: outputs/confirm/<set>/estimates.csv.

### eight_W

| quantity | unit | BioCLIP 2.5 Huge | BioCLIP 2 | first BioCLIP | BT-CLIP-O | families left out |
|---|---|---|---|---|---|---|
| Delta | pooled | 4.408 [3.900, 4.952] | 5.692 [5.058, 6.325] | 9.521 [8.471, 10.521] | 3.810 [3.177, 4.550] | - |
| ER | pooled | 1.941 [1.811, 2.129] | 1.758 [1.653, 1.876] | 1.357 [1.313, 1.403] | 1.068 [1.057, 1.083] | - |
| dropped share of slow weight | pooled | 0.017 [0.024, 0.033] | 0.017 [0.024, 0.033] | 0.017 [0.024, 0.033] | 0.017 [0.024, 0.033] | - |
| Delta | animals | 7.822 [6.871, 8.776] | 9.792 [8.645, 10.862] | 15.226 [13.610, 16.792] | 5.713 [4.618, 6.790] | - |
| ER | animals | 2.167 [1.981, 2.384] | 1.895 [1.762, 2.025] | 1.438 [1.386, 1.493] | 1.090 [1.072, 1.108] | - |
| Delta | plants | 0.994 [0.595, 1.488] | 1.593 [1.065, 2.228] | 3.816 [2.605, 5.042] | 1.908 [1.157, 2.939] | - |
| ER | plants | 1.372 [1.205, 1.668] | 1.390 [1.243, 1.617] | 1.206 [1.136, 1.288] | 1.040 [1.024, 1.063] | - |
| median family Delta | families | 1.875 [1.289, 2.853] | 2.997 [2.136, 4.017] | 6.768 [5.288, 8.748] | 2.678 [1.657, 3.729] | - |
| Delta population-weighted | pooled | 2.695 [2.193, 3.236] | 3.716 [3.081, 4.358] | 6.697 [5.431, 8.004] | 2.894 [2.126, 3.907] | - |
| Delta leave one family out | without Anatidae | 3.411 [2.934, 3.930] | 4.652 [4.044, 5.251] | 8.299 [7.206, 9.370] | 3.137 [2.515, 3.956] | - |
| Delta leave one family out | without Asteraceae | 4.941 [4.372, 5.546] | 6.277 [5.582, 6.960] | 10.523 [9.376, 11.538] | 4.108 [3.408, 4.860] | - |
| Delta leave one family out | without Columbidae | 3.276 [2.753, 3.801] | 4.235 [3.625, 4.865] | 7.754 [6.685, 8.776] | 2.749 [2.082, 3.510] | - |
| Delta leave one family out | without Fabaceae | 4.859 [4.304, 5.464] | 6.309 [5.589, 7.012] | 10.253 [9.131, 11.295] | 4.277 [3.562, 5.106] | - |
| Delta leave one family out | without Lamiaceae | 4.922 [4.348, 5.549] | 6.345 [5.646, 7.052] | 10.186 [9.035, 11.319] | 3.942 [3.242, 4.777] | - |
| Delta leave one family out | without Nymphalidae | 4.681 [4.146, 5.281] | 5.974 [5.333, 6.670] | 9.642 [8.548, 10.666] | 3.910 [3.220, 4.724] | - |
| Delta leave one family out | without Rosaceae | 4.862 [4.289, 5.461] | 6.180 [5.455, 6.856] | 10.383 [9.288, 11.515] | 4.003 [3.290, 4.797] | - |
| Delta leave one family out | without Sciuridae | 4.313 [3.769, 4.898] | 5.564 [4.893, 6.238] | 9.129 [8.000, 10.180] | 4.359 [3.664, 5.185] | - |
| Delta A1 vs A0 | pooled | 3.530 [2.954, 4.096] | 4.516 [3.785, 5.170] | 8.039 [6.919, 9.165] | 3.059 [2.280, 3.898] | - |
| ER A1 vs A0 | pooled | 1.796 [1.640, 1.986] | 1.642 [1.520, 1.765] | 1.311 [1.264, 1.361] | 1.054 [1.040, 1.070] | - |
| Delta A2 vs A0 | pooled | 5.935 [4.888, 7.041] | 7.345 [6.146, 8.573] | 11.247 [9.639, 12.874] | 5.063 [3.995, 6.315] | - |
| ER A2 vs A0 | pooled | 2.117 [1.893, 2.428] | 1.864 [1.697, 2.060] | 1.401 [1.337, 1.473] | 1.091 [1.072, 1.115] | - |
| Delta A3 vs A0 | pooled | 6.610 [4.861, 8.469] | 10.042 [7.962, 12.284] | 14.902 [12.141, 17.647] | 5.450 [3.427, 7.575] | - |
| ER A3 vs A0 | pooled | 2.294 [1.905, 2.822] | 2.159 [1.886, 2.525] | 1.523 [1.415, 1.647] | 1.103 [1.064, 1.146] | - |
| slope on log(1+T) | pooled | 1.424 [1.255, 1.596] | 1.926 [1.733, 2.114] | 3.082 [2.829, 3.362] | 1.165 [0.992, 1.359] | - |
| Delta median split | pooled | 2.333 [1.990, 2.688] | 3.618 [3.172, 4.038] | 7.250 [6.483, 8.071] | 2.270 [1.776, 2.859] | - |
| ER median split | pooled | 1.702 [1.570, 1.859] | 1.671 [1.569, 1.784] | 1.310 [1.274, 1.353] | 1.042 [1.032, 1.053] | - |
| Delta strong consensus | pooled | 3.669 [2.262, 5.148] | 4.246 [2.421, 6.213] | 10.588 [7.865, 13.462] | 5.289 [2.803, 7.704] | - |
| ER strong consensus | pooled | 1.739 [1.403, 2.341] | 1.555 [1.292, 1.937] | 1.449 [1.317, 1.618] | 1.100 [1.052, 1.151] | - |
| Delta common horizon 540 days | pooled | 4.281 [3.768, 4.825] | 5.426 [4.779, 6.030] | 9.300 [8.253, 10.317] | 3.761 [3.125, 4.507] | - |
| ER common horizon 540 days | pooled | 1.914 [1.784, 2.106] | 1.729 [1.623, 1.848] | 1.349 [1.306, 1.397] | 1.067 [1.055, 1.081] | - |
| Delta without perceptual-duplicate groups | pooled | 4.417 [3.912, 4.967] | 5.665 [5.041, 6.296] | 9.571 [8.530, 10.564] | 3.844 [3.219, 4.586] | - |
| ER without perceptual-duplicate groups | pooled | 1.943 [1.812, 2.132] | 1.755 [1.651, 1.874] | 1.360 [1.315, 1.407] | 1.069 [1.057, 1.083] | - |
| Delta without regime-flagged pairs | pooled | 4.408 [3.900, 4.952] | 5.692 [5.058, 6.325] | 9.521 [8.471, 10.521] | 4.359 [3.664, 5.185] | BT-CLIP-O: Sciuridae |
| ER without regime-flagged pairs | pooled | 1.941 [1.811, 2.129] | 1.758 [1.653, 1.876] | 1.357 [1.313, 1.403] | 1.087 [1.072, 1.104] | BT-CLIP-O: Sciuridae |
| Delta slow with disagreement | pooled | 7.888 [5.587, 10.471] | 11.324 [8.687, 14.091] | 22.306 [18.614, 26.307] | 8.626 [6.072, 11.411] | - |
| ER slow with disagreement | pooled | 2.437 [1.942, 3.249] | 2.289 [1.934, 2.765] | 1.750 [1.603, 1.908] | 1.146 [1.102, 1.199] | - |
| Delta slow without disagreement | pooled | 4.242 [3.721, 4.804] | 5.380 [4.745, 6.013] | 8.916 [7.856, 9.905] | 3.665 [3.029, 4.428] | - |
| ER slow without disagreement | pooled | 1.909 [1.778, 2.093] | 1.720 [1.614, 1.843] | 1.336 [1.292, 1.383] | 1.066 [1.054, 1.081] | - |
| Delta within V0 | pooled | 6.442 [5.251, 7.686] | 8.461 [7.101, 10.006] | 12.386 [10.242, 14.626] | 4.653 [3.060, 6.271] | - |
| ER within V0 | pooled | 2.057 [1.787, 2.463] | 1.900 [1.715, 2.188] | 1.432 [1.345, 1.541] | 1.083 [1.054, 1.115] | - |
| Delta within V1 | pooled | 3.276 [2.698, 3.818] | 4.313 [3.582, 4.967] | 8.054 [6.884, 9.269] | 3.264 [2.537, 4.103] | - |
| ER within V1 | pooled | 1.787 [1.622, 1.988] | 1.629 [1.507, 1.760] | 1.311 [1.262, 1.370] | 1.059 [1.045, 1.074] | - |
| Delta within activity S0 | pooled | 3.415 [1.389, 5.221] | 7.233 [4.514, 9.492] | 6.731 [1.935, 10.820] | 2.730 [-0.834, 5.904] | - |
| ER within activity S0 | pooled | 2.189 [1.356, 3.454] | 2.648 [1.798, 3.602] | 1.264 [1.070, 1.483] | 1.051 [0.985, 1.118] | - |
| Delta within activity S1 | pooled | 3.856 [2.354, 5.234] | 5.277 [3.548, 6.850] | 7.510 [4.036, 10.584] | 2.536 [0.232, 5.333] | - |
| ER within activity S1 | pooled | 2.359 [1.679, 3.500] | 2.024 [1.591, 2.563] | 1.321 [1.162, 1.500] | 1.046 [1.004, 1.101] | - |
| Delta within activity S2 | pooled | 4.527 [3.442, 5.568] | 5.669 [4.403, 6.931] | 8.984 [7.215, 11.374] | 3.351 [1.590, 4.902] | - |
| ER within activity S2 | pooled | 2.081 [1.757, 2.538] | 1.850 [1.616, 2.153] | 1.362 [1.281, 1.488] | 1.060 [1.028, 1.090] | - |
| Delta within activity S3 | pooled | 4.843 [4.084, 5.574] | 5.812 [4.882, 6.665] | 10.304 [8.919, 11.737] | 4.252 [3.329, 5.229] | - |
| ER within activity S3 | pooled | 1.972 [1.786, 2.267] | 1.704 [1.574, 1.876] | 1.375 [1.318, 1.445] | 1.076 [1.059, 1.094] | - |
| Delta genus level with B2 | pooled | 3.737 [3.291, 4.164] | 4.784 [4.275, 5.302] | 8.994 [8.121, 9.903] | 4.277 [3.499, 5.083] | - |
| ER genus level with B2 | pooled | 2.808 [2.484, 3.177] | 2.311 [2.103, 2.543] | 1.555 [1.486, 1.629] | 1.122 [1.099, 1.149] | - |
| Delta genus level with B1 and B2 | pooled | 6.811 [6.211, 7.341] | 8.054 [7.344, 8.685] | 12.637 [11.581, 13.693] | 5.492 [4.616, 6.458] | - |
| ER genus level with B1 and B2 | pooled | 4.049 [3.522, 4.623] | 2.974 [2.664, 3.303] | 1.745 [1.656, 1.847] | 1.159 [1.131, 1.190] | - |
| O at 2024-10-01 | pooled | 0.394 [0.275, 0.517] | 0.667 [0.529, 0.821] | 1.240 [0.977, 1.527] | 0.516 [0.163, 0.875] | - |
| R at 2024-10-01 | pooled | 1.096 [1.066, 1.130] | 1.102 [1.079, 1.128] | 1.048 [1.037, 1.060] | 1.009 [1.003, 1.016] | - |
| L at 2024-10-01 | pooled | 0.245 [0.235, 0.257] | 0.245 [0.235, 0.257] | 0.245 [0.235, 0.257] | 0.245 [0.235, 0.257] | - |
| L_upload at 2024-10-01 | pooled | 0.111 [0.099, 0.124] | 0.111 [0.099, 0.124] | 0.111 [0.099, 0.124] | 0.111 [0.099, 0.124] | - |
| L_ident at 2024-10-01 | pooled | 0.134 [0.129, 0.139] | 0.134 [0.129, 0.139] | 0.134 [0.129, 0.139] | 0.134 [0.129, 0.139] | - |
| O_ident at 2024-10-01 | pooled | 0.429 [0.340, 0.522] | 0.674 [0.567, 0.787] | 1.255 [1.068, 1.443] | 0.552 [0.363, 0.759] | - |
| G_all at 2024-10-01 | pooled | 2.463 [2.263, 2.678] | 3.069 [2.852, 3.303] | 4.376 [4.017, 4.745] | 1.074 [0.692, 1.444] | - |
| G_sup at 2024-10-01 | pooled | 0.563 [0.464, 0.666] | 0.827 [0.707, 0.950] | 1.425 [1.187, 1.689] | 0.343 [0.064, 0.634] | - |
| O | pooled | 0.259 [0.187, 0.338] | 0.426 [0.335, 0.522] | 0.578 [0.419, 0.738] | 0.133 [-0.032, 0.313] | - |
| R | pooled | 1.061 [1.043, 1.081] | 1.063 [1.049, 1.078] | 1.022 [1.016, 1.028] | 1.002 [0.999, 1.006] | - |
| L | pooled | 0.125 [0.119, 0.132] | 0.125 [0.119, 0.132] | 0.125 [0.119, 0.132] | 0.125 [0.119, 0.132] | - |
| L_upload | pooled | 0.048 [0.043, 0.053] | 0.048 [0.043, 0.053] | 0.048 [0.043, 0.053] | 0.048 [0.043, 0.053] | - |
| L_ident | pooled | 0.078 [0.074, 0.081] | 0.078 [0.074, 0.081] | 0.078 [0.074, 0.081] | 0.078 [0.074, 0.081] | - |
| O_ident | pooled | 0.275 [0.215, 0.337] | 0.435 [0.360, 0.509] | 0.694 [0.570, 0.815] | 0.177 [0.046, 0.305] | - |
| G_all | pooled | 2.406 [2.225, 2.608] | 2.940 [2.735, 3.153] | 3.895 [3.594, 4.213] | 0.769 [0.477, 1.061] | - |
| G_sup | pooled | 0.506 [0.432, 0.586] | 0.697 [0.608, 0.792] | 0.944 [0.790, 1.099] | 0.038 [-0.141, 0.219] | - |
| G_sup with S2b | pooled | 0.575 [0.495, 0.661] | 0.789 [0.692, 0.886] | 1.074 [0.914, 1.241] | 0.108 [-0.074, 0.301] | - |
| O without perceptual-duplicate groups | pooled | 0.257 [0.183, 0.336] | 0.428 [0.337, 0.525] | 0.580 [0.418, 0.742] | 0.135 [-0.033, 0.315] | - |
| R without perceptual-duplicate groups | pooled | 1.061 [1.043, 1.082] | 1.063 [1.049, 1.078] | 1.022 [1.016, 1.028] | 1.002 [0.999, 1.006] | - |
| G_all without perceptual-duplicate groups | pooled | 2.399 [2.215, 2.598] | 2.935 [2.729, 3.149] | 3.887 [3.586, 4.211] | 0.766 [0.474, 1.057] | - |
| G_sup without perceptual-duplicate groups | pooled | 0.505 [0.429, 0.585] | 0.699 [0.608, 0.794] | 0.941 [0.786, 1.098] | 0.035 [-0.143, 0.216] | - |
| O without regime-flagged pairs | pooled | 0.259 [0.187, 0.338] | 0.426 [0.335, 0.522] | 0.578 [0.419, 0.738] | 0.109 [-0.070, 0.311] | BT-CLIP-O: Sciuridae |
| R without regime-flagged pairs | pooled | 1.061 [1.043, 1.081] | 1.063 [1.049, 1.078] | 1.022 [1.016, 1.028] | 1.002 [0.999, 1.006] | BT-CLIP-O: Sciuridae |
| G_all without regime-flagged pairs | pooled | 2.406 [2.225, 2.608] | 2.940 [2.735, 3.153] | 3.895 [3.594, 4.213] | 0.782 [0.445, 1.112] | BT-CLIP-O: Sciuridae |
| G_sup without regime-flagged pairs | pooled | 0.506 [0.432, 0.586] | 0.697 [0.608, 0.792] | 0.944 [0.790, 1.099] | -0.022 [-0.213, 0.180] | BT-CLIP-O: Sciuridae |
| O at 2025-10-01 | pooled | 0.124 [0.079, 0.176] | 0.183 [0.132, 0.241] | 0.230 [0.138, 0.321] | 0.038 [-0.059, 0.136] | - |
| R at 2025-10-01 | pooled | 1.028 [1.018, 1.041] | 1.026 [1.019, 1.035] | 1.009 [1.005, 1.012] | 1.001 [0.999, 1.002] | - |
| L at 2025-10-01 | pooled | 0.051 [0.048, 0.055] | 0.051 [0.048, 0.055] | 0.051 [0.048, 0.055] | 0.051 [0.048, 0.055] | - |
| L_upload at 2025-10-01 | pooled | 0.018 [0.015, 0.020] | 0.018 [0.015, 0.020] | 0.018 [0.015, 0.020] | 0.018 [0.015, 0.020] | - |
| L_ident at 2025-10-01 | pooled | 0.034 [0.032, 0.036] | 0.034 [0.032, 0.036] | 0.034 [0.032, 0.036] | 0.034 [0.032, 0.036] | - |
| O_ident at 2025-10-01 | pooled | 0.145 [0.106, 0.187] | 0.201 [0.157, 0.248] | 0.310 [0.237, 0.381] | 0.072 [-0.003, 0.150] | - |
| G_all at 2025-10-01 | pooled | 2.345 [2.166, 2.537] | 2.824 [2.618, 3.034] | 3.704 [3.412, 4.002] | 0.702 [0.448, 0.952] | - |
| G_sup at 2025-10-01 | pooled | 0.445 [0.383, 0.511] | 0.582 [0.509, 0.657] | 0.753 [0.632, 0.867] | -0.030 [-0.147, 0.089] | - |
| b0 | pooled | 2.074 [1.622, 2.610] | - | - | - | - |
| b3 | pooled | 2.251 [1.766, 2.904] | - | - | - | - |
| b_obs | pooled | 2.384 [1.688, 3.123] | - | - | - | - |
| rho | pooled | 1.086 [0.913, 1.339] | - | - | - | - |
| b_int | pooled | 7.253 [1.172, 13.182] | - | - | - | - |
| Delta Q tertile 1 | pooled | 3.985 [3.159, 4.823] | - | - | - | - |
| ER Q tertile 1 | pooled | 1.789 [1.583, 2.082] | - | - | - | - |
| Delta Q tertile 2 | pooled | 5.022 [3.852, 5.981] | - | - | - | - |
| ER Q tertile 2 | pooled | 2.299 [1.884, 2.746] | - | - | - | - |
| Delta Q tertile 3 | pooled | 5.159 [4.092, 6.269] | - | - | - | - |
| ER Q tertile 3 | pooled | 2.217 [1.900, 2.652] | - | - | - | - |
| Delta Q tertile 3 minus tertile 1 | pooled | 1.174 [-0.191, 2.564] | - | - | - | - |
| Delta without Sciuridae | pooled | - | - | - | 4.359 [3.675, 5.227] | - |
| ER without Sciuridae | pooled | - | - | - | 1.087 [1.073, 1.106] | - |
| dropped share of slow weight without Sciuridae | pooled | - | - | - | 0.019 [0.027, 0.037] | - |
| Delta without Sciuridae | animals | - | - | - | 7.626 [6.321, 9.083] | - |
| ER without Sciuridae | animals | - | - | - | 1.142 [1.116, 1.172] | - |
| Delta without Sciuridae | plants | - | - | - | 1.908 [1.142, 2.885] | - |
| ER without Sciuridae | plants | - | - | - | 1.040 [1.024, 1.062] | - |
| median family Delta without Sciuridae | families | - | - | - | 2.890 [1.847, 4.126] | - |
| Delta population-weighted without Sciuridae | pooled | - | - | - | 3.000 [2.207, 4.056] | - |
| Delta leave one family out without Sciuridae | without Anatidae | - | - | - | 3.664 [2.965, 4.575] | - |
| Delta leave one family out without Sciuridae | without Asteraceae | - | - | - | 4.797 [4.014, 5.701] | - |
| Delta leave one family out without Sciuridae | without Columbidae | - | - | - | 3.211 [2.484, 4.096] | - |
| Delta leave one family out without Sciuridae | without Fabaceae | - | - | - | 4.994 [4.222, 5.970] | - |
| Delta leave one family out without Sciuridae | without Lamiaceae | - | - | - | 4.603 [3.819, 5.592] | - |
| Delta leave one family out without Sciuridae | without Nymphalidae | - | - | - | 4.566 [3.859, 5.509] | - |
| Delta leave one family out without Sciuridae | without Rosaceae | - | - | - | 4.674 [3.910, 5.595] | - |
| Delta A1 vs A0 without Sciuridae | pooled | - | - | - | 3.474 [2.707, 4.423] | - |
| ER A1 vs A0 without Sciuridae | pooled | - | - | - | 1.068 [1.053, 1.088] | - |
| Delta A2 vs A0 without Sciuridae | pooled | - | - | - | 5.944 [4.771, 7.289] | - |
| ER A2 vs A0 without Sciuridae | pooled | - | - | - | 1.119 [1.095, 1.147] | - |
| Delta A3 vs A0 without Sciuridae | pooled | - | - | - | 5.942 [3.924, 8.240] | - |
| ER A3 vs A0 without Sciuridae | pooled | - | - | - | 1.126 [1.081, 1.179] | - |
| slope on log(1+T) without Sciuridae | pooled | - | - | - | 1.347 [1.159, 1.563] | - |
| Delta median split without Sciuridae | pooled | - | - | - | 2.702 [2.118, 3.332] | - |
| ER median split without Sciuridae | pooled | - | - | - | 1.055 [1.043, 1.069] | - |
| O at 2024-10-01 without Sciuridae | pooled | - | - | - | 0.589 [0.215, 0.971] | - |
| R at 2024-10-01 without Sciuridae | pooled | - | - | - | 1.012 [1.004, 1.020] | - |
| L at 2024-10-01 without Sciuridae | pooled | - | - | - | 0.249 [0.237, 0.262] | - |
| L_upload at 2024-10-01 without Sciuridae | pooled | - | - | - | 0.104 [0.092, 0.118] | - |
| L_ident at 2024-10-01 without Sciuridae | pooled | - | - | - | 0.145 [0.139, 0.151] | - |
| O_ident at 2024-10-01 without Sciuridae | pooled | - | - | - | 0.617 [0.394, 0.854] | - |
| G_all at 2024-10-01 without Sciuridae | pooled | - | - | - | 1.156 [0.774, 1.552] | - |
| G_sup at 2024-10-01 without Sciuridae | pooled | - | - | - | 0.353 [0.056, 0.654] | - |
| O without Sciuridae | pooled | - | - | - | 0.109 [-0.083, 0.295] | - |
| R without Sciuridae | pooled | - | - | - | 1.002 [0.998, 1.006] | - |
| L without Sciuridae | pooled | - | - | - | 0.126 [0.120, 0.133] | - |
| L_upload without Sciuridae | pooled | - | - | - | 0.043 [0.038, 0.049] | - |
| L_ident without Sciuridae | pooled | - | - | - | 0.083 [0.079, 0.087] | - |
| O_ident without Sciuridae | pooled | - | - | - | 0.196 [0.053, 0.343] | - |
| G_all without Sciuridae | pooled | - | - | - | 0.782 [0.457, 1.113] | - |
| G_sup without Sciuridae | pooled | - | - | - | -0.022 [-0.222, 0.186] | - |
| G_sup with S2b without Sciuridae | pooled | - | - | - | 0.059 [-0.148, 0.270] | - |
| O at 2025-10-01 without Sciuridae | pooled | - | - | - | 0.024 [-0.082, 0.129] | - |
| R at 2025-10-01 without Sciuridae | pooled | - | - | - | 1.000 [0.998, 1.003] | - |
| L at 2025-10-01 without Sciuridae | pooled | - | - | - | 0.052 [0.048, 0.056] | - |
| L_upload at 2025-10-01 without Sciuridae | pooled | - | - | - | 0.015 [0.013, 0.018] | - |
| L_ident at 2025-10-01 without Sciuridae | pooled | - | - | - | 0.037 [0.034, 0.039] | - |
| O_ident at 2025-10-01 without Sciuridae | pooled | - | - | - | 0.078 [-0.007, 0.162] | - |
| G_all at 2025-10-01 without Sciuridae | pooled | - | - | - | 0.733 [0.435, 1.028] | - |
| G_sup at 2025-10-01 without Sciuridae | pooled | - | - | - | -0.071 [-0.210, 0.062] | - |
| Delta (5000 replicates) | pooled | 4.408 [3.893, 4.968] | - | - | - | - |
| ER (5000 replicates) | pooled | 1.941 [1.802, 2.128] | - | - | - | - |
| O (5000 replicates) | pooled | 0.259 [0.184, 0.332] | - | - | - | - |
| R (5000 replicates) | pooled | 1.061 [1.042, 1.080] | - | - | - | - |
| G_sup (5000 replicates) | pooled | 0.506 [0.431, 0.583] | - | - | - | - |
| G_all (5000 replicates) | pooled | 2.406 [2.222, 2.590] | - | - | - | - |

Further values (analysis.json): BioCLIP 2.5 Huge: families with lower bound of Delta above 0 7, tipping point to 0 0.040, to 1.0 0.030, share of slow errors whose predicted species was proposed 0.056; BioCLIP 2: families with lower bound of Delta above 0 8, tipping point to 0 0.052, to 1.0 0.042, share of slow errors whose predicted species was proposed 0.041; first BioCLIP: families with lower bound of Delta above 0 7, tipping point to 0 0.086, to 1.0 0.076, share of slow errors whose predicted species was proposed 0.017; BT-CLIP-O: families with lower bound of Delta above 0 5, tipping point to 0 0.033, to 1.0 0.023, share of slow errors whose predicted species was proposed 0.006.

### eight_W2

| quantity | unit | BioCLIP 2.5 Huge | BioCLIP 2 | first BioCLIP | BT-CLIP-O | families left out |
|---|---|---|---|---|---|---|
| Delta | pooled | 4.620 [3.676, 5.515] | 6.556 [5.430, 7.780] | 11.512 [9.750, 13.089] | 3.734 [2.563, 4.960] | - |
| ER | pooled | 2.027 [1.757, 2.352] | 1.961 [1.748, 2.237] | 1.380 [1.315, 1.451] | 1.064 [1.044, 1.086] | - |
| dropped share of slow weight | pooled | 0.062 [0.076, 0.094] | 0.062 [0.076, 0.094] | 0.062 [0.076, 0.094] | 0.062 [0.076, 0.094] | - |
| Delta | animals | 8.114 [6.699, 9.603] | 10.598 [8.665, 12.743] | 17.967 [15.464, 20.321] | 5.853 [4.059, 7.813] | - |
| ER | animals | 2.925 [2.452, 3.510] | 2.452 [2.107, 2.926] | 1.545 [1.454, 1.643] | 1.099 [1.068, 1.135] | - |
| Delta | plants | 1.126 [-0.034, 2.172] | 2.514 [1.254, 3.681] | 5.057 [2.727, 7.274] | 1.614 [0.064, 2.984] | - |
| ER | plants | 1.236 [0.993, 1.531] | 1.396 [1.174, 1.672] | 1.184 [1.096, 1.282] | 1.028 [1.001, 1.054] | - |
| median family Delta | families | 3.009 [2.030, 4.359] | 3.451 [2.732, 5.605] | 11.608 [8.765, 14.119] | 2.851 [1.122, 4.584] | - |
| Delta population-weighted | pooled | 5.943 [4.519, 7.347] | 7.693 [6.026, 9.504] | 13.971 [11.629, 16.321] | 6.022 [4.308, 7.792] | - |
| Delta leave one family out | without Anatidae | 3.993 [3.031, 4.875] | 6.063 [4.908, 7.272] | 10.314 [8.515, 11.908] | 2.883 [1.645, 4.063] | - |
| Delta leave one family out | without Asteraceae | 4.969 [3.982, 5.958] | 7.047 [5.809, 8.422] | 12.795 [10.921, 14.426] | 3.679 [2.479, 4.958] | - |
| Delta leave one family out | without Columbidae | 3.781 [2.850, 4.640] | 5.132 [4.007, 6.290] | 9.848 [7.986, 11.579] | 2.648 [1.458, 3.923] | - |
| Delta leave one family out | without Fabaceae | 5.292 [4.312, 6.202] | 7.062 [5.842, 8.373] | 11.762 [9.895, 13.417] | 4.060 [2.812, 5.389] | - |
| Delta leave one family out | without Lamiaceae | 5.044 [4.049, 6.033] | 7.118 [5.845, 8.531] | 12.030 [10.175, 13.779] | 4.041 [2.727, 5.385] | - |
| Delta leave one family out | without Nymphalidae | 4.732 [3.675, 5.710] | 6.952 [5.703, 8.254] | 11.234 [9.467, 12.972] | 3.640 [2.388, 4.905] | - |
| Delta leave one family out | without Rosaceae | 5.172 [4.159, 6.128] | 7.306 [6.045, 8.622] | 13.150 [11.378, 14.816] | 4.366 [3.074, 5.707] | - |
| Delta leave one family out | without Sciuridae | 3.977 [2.970, 4.950] | 5.767 [4.630, 7.049] | 10.963 [9.236, 12.608] | 4.554 [3.262, 5.883] | - |
| Delta A1 vs A0 | pooled | 3.625 [2.687, 4.537] | 4.867 [3.766, 6.108] | 9.455 [7.614, 11.248] | 3.318 [2.116, 4.555] | - |
| ER A1 vs A0 | pooled | 1.786 [1.543, 2.055] | 1.704 [1.520, 1.956] | 1.316 [1.249, 1.392] | 1.056 [1.035, 1.078] | - |
| Delta A2 vs A0 | pooled | 6.272 [4.499, 8.116] | 10.245 [7.962, 12.348] | 14.839 [11.902, 17.571] | 4.994 [2.714, 7.272] | - |
| ER A2 vs A0 | pooled | 2.402 [1.925, 3.086] | 2.526 [2.083, 3.030] | 1.473 [1.365, 1.582] | 1.092 [1.050, 1.137] | - |
| Delta A3 vs A0 | pooled | 13.576 [7.809, 18.635] | 12.764 [7.910, 17.686] | 24.549 [19.980, 29.199] | 6.232 [1.024, 10.954] | - |
| ER A3 vs A0 | pooled | 4.231 [2.675, 6.260] | 2.758 [1.951, 4.138] | 1.800 [1.603, 2.037] | 1.109 [1.018, 1.198] | - |
| slope on log(1+T) | pooled | 1.870 [1.582, 2.178] | 2.640 [2.286, 3.004] | 4.235 [3.804, 4.709] | 1.232 [0.839, 1.606] | - |
| Delta median split | pooled | 2.551 [1.939, 3.130] | 4.004 [3.236, 4.782] | 8.112 [6.719, 9.447] | 2.037 [1.104, 2.951] | - |
| ER median split | pooled | 1.676 [1.476, 1.904] | 1.724 [1.550, 1.931] | 1.302 [1.244, 1.364] | 1.033 [1.018, 1.049] | - |
| Delta strong consensus | pooled | 4.059 [1.839, 6.055] | 6.184 [3.423, 8.803] | 9.724 [4.877, 14.090] | 2.288 [-0.974, 5.573] | - |
| ER strong consensus | pooled | 2.319 [1.455, 3.647] | 2.418 [1.629, 3.668] | 1.411 [1.184, 1.647] | 1.040 [0.984, 1.102] | - |
| Delta common horizon 540 days | pooled | 4.483 [3.584, 5.355] | 6.459 [5.359, 7.634] | 11.296 [9.543, 12.856] | 3.669 [2.523, 4.884] | - |
| ER common horizon 540 days | pooled | 1.996 [1.733, 2.303] | 1.947 [1.739, 2.211] | 1.373 [1.308, 1.442] | 1.063 [1.043, 1.086] | - |
| Delta without perceptual-duplicate groups | pooled | 4.667 [3.699, 5.583] | 6.404 [5.299, 7.606] | 11.407 [9.668, 13.024] | 3.848 [2.685, 5.020] | - |
| ER without perceptual-duplicate groups | pooled | 2.039 [1.764, 2.363] | 1.940 [1.734, 2.210] | 1.377 [1.312, 1.448] | 1.066 [1.046, 1.088] | - |
| Delta without regime-flagged pairs | pooled | 4.620 [3.676, 5.515] | 6.556 [5.430, 7.780] | 11.512 [9.750, 13.089] | 5.049 [3.609, 6.510] | BT-CLIP-O: Lamiaceae;Sciuridae |
| ER without regime-flagged pairs | pooled | 2.027 [1.757, 2.352] | 1.961 [1.748, 2.237] | 1.380 [1.315, 1.451] | 1.099 [1.069, 1.130] | BT-CLIP-O: Lamiaceae;Sciuridae |
| Delta slow with disagreement | pooled | 8.109 [4.442, 11.746] | 14.004 [8.935, 18.669] | 21.184 [15.083, 26.894] | 4.566 [0.681, 8.843] | - |
| ER slow with disagreement | pooled | 2.278 [1.592, 3.157] | 2.652 [1.926, 3.470] | 1.649 [1.436, 1.882] | 1.077 [1.011, 1.153] | - |
| Delta slow without disagreement | pooled | 4.382 [3.435, 5.271] | 6.055 [4.986, 7.234] | 10.932 [9.186, 12.582] | 3.634 [2.454, 4.850] | - |
| ER slow without disagreement | pooled | 1.989 [1.719, 2.323] | 1.896 [1.696, 2.162] | 1.362 [1.296, 1.435] | 1.063 [1.042, 1.085] | - |
| Delta within V0 | pooled | 6.360 [3.755, 8.394] | 9.439 [6.687, 11.890] | 15.211 [11.312, 18.633] | 4.453 [1.803, 6.750] | - |
| ER within V0 | pooled | 1.973 [1.448, 2.546] | 2.119 [1.642, 2.654] | 1.471 [1.328, 1.627] | 1.077 [1.030, 1.118] | - |
| Delta within V1 | pooled | 3.384 [2.254, 4.450] | 5.000 [3.644, 6.595] | 9.561 [7.608, 11.619] | 3.140 [1.703, 4.632] | - |
| ER within V1 | pooled | 1.869 [1.525, 2.270] | 1.797 [1.567, 2.175] | 1.329 [1.257, 1.417] | 1.054 [1.029, 1.080] | - |
| Delta within activity S0 | pooled | 7.322 [3.814, 11.256] | 5.766 [2.441, 9.314] | 13.073 [5.413, 19.881] | -2.989 [-9.344, 3.540] | - |
| ER within activity S0 | pooled | 3.143 [1.864, 5.747] | 1.972 [1.335, 3.189] | 1.514 [1.180, 1.922] | 0.952 [0.857, 1.063] | - |
| Delta within activity S1 | pooled | 2.060 [-0.449, 4.328] | 2.754 [-0.476, 5.608] | 0.619 [-3.958, 7.412] | 1.933 [-1.516, 5.615] | - |
| ER within activity S1 | pooled | 1.567 [0.919, 2.568] | 1.451 [0.941, 2.151] | 1.018 [0.894, 1.241] | 1.031 [0.977, 1.090] | - |
| Delta within activity S2 | pooled | 4.369 [2.519, 6.234] | 7.026 [4.602, 9.658] | 10.831 [7.470, 14.962] | 3.493 [1.044, 5.838] | - |
| ER within activity S2 | pooled | 2.017 [1.481, 2.792] | 2.004 [1.568, 2.704] | 1.382 [1.242, 1.585] | 1.062 [1.018, 1.106] | - |
| Delta within activity S3 | pooled | 5.287 [3.817, 6.580] | 7.592 [5.887, 9.506] | 13.244 [10.866, 15.678] | 4.754 [2.926, 6.494] | - |
| ER within activity S3 | pooled | 2.191 [1.769, 2.679] | 2.120 [1.795, 2.589] | 1.431 [1.343, 1.539] | 1.083 [1.050, 1.116] | - |
| Delta genus level with B2 | pooled | 3.703 [3.045, 4.311] | 5.338 [4.476, 6.206] | 10.297 [8.619, 11.986] | 4.786 [3.342, 6.069] | - |
| ER genus level with B2 | pooled | 2.574 [2.233, 3.128] | 2.503 [2.202, 2.983] | 1.532 [1.427, 1.666] | 1.136 [1.094, 1.175] | - |
| Delta genus level with B1 and B2 | pooled | 8.339 [7.234, 9.275] | 10.184 [8.961, 11.280] | 13.776 [11.949, 15.554] | 6.124 [4.389, 7.409] | - |
| ER genus level with B1 and B2 | pooled | 3.788 [3.243, 5.135] | 3.376 [2.975, 4.233] | 1.647 [1.542, 1.797] | 1.172 [1.121, 1.214] | - |
| O at 2025-04-01 | pooled | 0.544 [0.363, 0.722] | 0.791 [0.572, 1.021] | 0.893 [0.540, 1.268] | -0.421 [-0.826, -0.029] | - |
| R at 2025-04-01 | pooled | 1.120 [1.077, 1.166] | 1.118 [1.082, 1.156] | 1.029 [1.017, 1.043] | 0.993 [0.987, 1.000] | - |
| L at 2025-04-01 | pooled | 0.209 [0.198, 0.221] | 0.209 [0.198, 0.221] | 0.209 [0.198, 0.221] | 0.209 [0.198, 0.221] | - |
| L_upload at 2025-04-01 | pooled | 0.111 [0.100, 0.122] | 0.111 [0.100, 0.122] | 0.111 [0.100, 0.122] | 0.111 [0.100, 0.122] | - |
| L_ident at 2025-04-01 | pooled | 0.099 [0.093, 0.104] | 0.099 [0.093, 0.104] | 0.099 [0.093, 0.104] | 0.099 [0.093, 0.104] | - |
| O_ident at 2025-04-01 | pooled | 0.507 [0.371, 0.635] | 0.754 [0.595, 0.914] | 1.083 [0.841, 1.341] | -0.175 [-0.417, 0.080] | - |
| G_all at 2025-04-01 | pooled | 3.795 [3.422, 4.188] | 4.369 [3.966, 4.752] | 4.996 [4.402, 5.628] | 0.559 [-0.045, 1.167] | - |
| G_sup at 2025-04-01 | pooled | 0.721 [0.563, 0.879] | 0.940 [0.748, 1.131] | 1.154 [0.800, 1.517] | -0.418 [-0.820, -0.025] | - |
| O | pooled | 0.339 [0.217, 0.454] | 0.507 [0.354, 0.657] | 0.461 [0.226, 0.680] | -0.341 [-0.591, -0.103] | - |
| R | pooled | 1.071 [1.045, 1.098] | 1.072 [1.049, 1.096] | 1.015 [1.007, 1.022] | 0.995 [0.991, 0.998] | - |
| L | pooled | 0.100 [0.094, 0.108] | 0.100 [0.094, 0.108] | 0.100 [0.094, 0.108] | 0.100 [0.094, 0.108] | - |
| L_upload | pooled | 0.040 [0.034, 0.046] | 0.040 [0.034, 0.046] | 0.040 [0.034, 0.046] | 0.040 [0.034, 0.046] | - |
| L_ident | pooled | 0.061 [0.057, 0.065] | 0.061 [0.057, 0.065] | 0.061 [0.057, 0.065] | 0.061 [0.057, 0.065] | - |
| O_ident | pooled | 0.330 [0.235, 0.426] | 0.480 [0.358, 0.609] | 0.568 [0.387, 0.752] | -0.169 [-0.336, 0.001] | - |
| G_all | pooled | 3.640 [3.272, 4.004] | 4.198 [3.821, 4.574] | 4.676 [4.151, 5.227] | 0.640 [0.138, 1.136] | - |
| G_sup | pooled | 0.566 [0.450, 0.682] | 0.768 [0.626, 0.915] | 0.834 [0.590, 1.083] | -0.337 [-0.601, -0.078] | - |
| G_sup with S2b | pooled | 0.664 [0.530, 0.800] | 0.898 [0.738, 1.063] | 0.958 [0.691, 1.218] | -0.334 [-0.612, -0.067] | - |
| O without perceptual-duplicate groups | pooled | 0.338 [0.219, 0.453] | 0.497 [0.350, 0.640] | 0.446 [0.212, 0.668] | -0.322 [-0.570, -0.084] | - |
| R without perceptual-duplicate groups | pooled | 1.072 [1.045, 1.098] | 1.071 [1.049, 1.094] | 1.015 [1.007, 1.022] | 0.995 [0.991, 0.999] | - |
| G_all without perceptual-duplicate groups | pooled | 3.643 [3.274, 4.009] | 4.194 [3.811, 4.570] | 4.663 [4.132, 5.213] | 0.659 [0.142, 1.146] | - |
| G_sup without perceptual-duplicate groups | pooled | 0.564 [0.447, 0.681] | 0.758 [0.618, 0.902] | 0.819 [0.577, 1.063] | -0.317 [-0.582, -0.058] | - |
| O without regime-flagged pairs | pooled | 0.339 [0.217, 0.454] | 0.507 [0.354, 0.657] | 0.461 [0.226, 0.680] | -0.159 [-0.478, 0.136] | BT-CLIP-O: Lamiaceae;Sciuridae |
| R without regime-flagged pairs | pooled | 1.071 [1.045, 1.098] | 1.072 [1.049, 1.096] | 1.015 [1.007, 1.022] | 0.997 [0.992, 1.002] | BT-CLIP-O: Lamiaceae;Sciuridae |
| G_all without regime-flagged pairs | pooled | 3.640 [3.272, 4.004] | 4.198 [3.821, 4.574] | 4.676 [4.151, 5.227] | 0.394 [-0.238, 1.040] | BT-CLIP-O: Lamiaceae;Sciuridae |
| G_sup without regime-flagged pairs | pooled | 0.566 [0.450, 0.682] | 0.768 [0.626, 0.915] | 0.834 [0.590, 1.083] | -0.446 [-0.781, -0.121] | BT-CLIP-O: Lamiaceae;Sciuridae |
| O at 2026-04-01 | pooled | 0.099 [0.034, 0.166] | 0.142 [0.072, 0.217] | 0.141 [0.026, 0.251] | -0.122 [-0.242, -0.006] | - |
| R at 2026-04-01 | pooled | 1.020 [1.007, 1.034] | 1.019 [1.010, 1.030] | 1.005 [1.001, 1.008] | 0.998 [0.996, 1.000] | - |
| L at 2026-04-01 | pooled | 0.027 [0.023, 0.032] | 0.027 [0.023, 0.032] | 0.027 [0.023, 0.032] | 0.027 [0.023, 0.032] | - |
| L_upload at 2026-04-01 | pooled | 0.011 [0.007, 0.015] | 0.011 [0.007, 0.015] | 0.011 [0.007, 0.015] | 0.011 [0.007, 0.015] | - |
| L_ident at 2026-04-01 | pooled | 0.016 [0.014, 0.018] | 0.016 [0.014, 0.018] | 0.016 [0.014, 0.018] | 0.016 [0.014, 0.018] | - |
| O_ident at 2026-04-01 | pooled | 0.093 [0.045, 0.150] | 0.126 [0.076, 0.179] | 0.165 [0.086, 0.248] | 0.020 [-0.053, 0.094] | - |
| G_all at 2026-04-01 | pooled | 3.592 [3.233, 3.962] | 4.077 [3.704, 4.446] | 4.599 [4.110, 5.104] | 0.724 [0.275, 1.163] | - |
| G_sup at 2026-04-01 | pooled | 0.517 [0.430, 0.612] | 0.648 [0.542, 0.755] | 0.757 [0.585, 0.926] | -0.253 [-0.409, -0.097] | - |
| b0 | pooled | 4.091 [3.241, 5.087] | - | - | - | - |
| b3 | pooled | 4.731 [3.673, 5.811] | - | - | - | - |
| b_obs | pooled | 4.404 [3.076, 6.148] | - | - | - | - |
| rho | pooled | 1.156 [0.942, 1.374] | - | - | - | - |
| Delta without Sciuridae | pooled | - | - | - | 4.554 [3.247, 5.829] | - |
| ER without Sciuridae | pooled | - | - | - | 1.086 [1.060, 1.112] | - |
| dropped share of slow weight without Sciuridae | pooled | - | - | - | 0.070 [0.086, 0.106] | - |
| Delta without Sciuridae | animals | - | - | - | 8.473 [6.313, 10.744] | - |
| ER without Sciuridae | animals | - | - | - | 1.178 [1.128, 1.231] | - |
| Delta without Sciuridae | plants | - | - | - | 1.614 [0.095, 3.003] | - |
| ER without Sciuridae | plants | - | - | - | 1.028 [1.002, 1.054] | - |
| median family Delta without Sciuridae | families | - | - | - | 4.121 [1.419, 6.085] | - |
| Delta population-weighted without Sciuridae | pooled | - | - | - | 6.548 [4.683, 8.374] | - |
| Delta leave one family out without Sciuridae | without Anatidae | - | - | - | 3.697 [2.341, 4.998] | - |
| Delta leave one family out without Sciuridae | without Asteraceae | - | - | - | 4.626 [3.237, 6.020] | - |
| Delta leave one family out without Sciuridae | without Columbidae | - | - | - | 3.424 [2.078, 4.712] | - |
| Delta leave one family out without Sciuridae | without Fabaceae | - | - | - | 5.071 [3.687, 6.503] | - |
| Delta leave one family out without Sciuridae | without Lamiaceae | - | - | - | 5.049 [3.545, 6.501] | - |
| Delta leave one family out without Sciuridae | without Nymphalidae | - | - | - | 4.581 [3.103, 5.974] | - |
| Delta leave one family out without Sciuridae | without Rosaceae | - | - | - | 5.429 [4.000, 6.856] | - |
| Delta A1 vs A0 without Sciuridae | pooled | - | - | - | 3.955 [2.555, 5.283] | - |
| ER A1 vs A0 without Sciuridae | pooled | - | - | - | 1.072 [1.046, 1.098] | - |
| Delta A2 vs A0 without Sciuridae | pooled | - | - | - | 6.441 [3.993, 8.665] | - |
| ER A2 vs A0 without Sciuridae | pooled | - | - | - | 1.133 [1.082, 1.181] | - |
| Delta A3 vs A0 without Sciuridae | pooled | - | - | - | 6.687 [1.094, 12.417] | - |
| ER A3 vs A0 without Sciuridae | pooled | - | - | - | 1.128 [1.019, 1.247] | - |
| slope on log(1+T) without Sciuridae | pooled | - | - | - | 1.534 [1.138, 1.885] | - |
| Delta median split without Sciuridae | pooled | - | - | - | 2.487 [1.537, 3.464] | - |
| ER median split without Sciuridae | pooled | - | - | - | 1.044 [1.027, 1.062] | - |
| O at 2025-04-01 without Sciuridae | pooled | - | - | - | -0.466 [-0.930, -0.011] | - |
| R at 2025-04-01 without Sciuridae | pooled | - | - | - | 0.992 [0.984, 1.000] | - |
| L at 2025-04-01 without Sciuridae | pooled | - | - | - | 0.215 [0.202, 0.227] | - |
| L_upload at 2025-04-01 without Sciuridae | pooled | - | - | - | 0.108 [0.096, 0.120] | - |
| L_ident at 2025-04-01 without Sciuridae | pooled | - | - | - | 0.107 [0.101, 0.113] | - |
| O_ident at 2025-04-01 without Sciuridae | pooled | - | - | - | -0.231 [-0.505, 0.065] | - |
| G_all at 2025-04-01 without Sciuridae | pooled | - | - | - | 0.628 [-0.031, 1.287] | - |
| G_sup at 2025-04-01 without Sciuridae | pooled | - | - | - | -0.474 [-0.888, -0.047] | - |
| O without Sciuridae | pooled | - | - | - | -0.360 [-0.624, -0.091] | - |
| R without Sciuridae | pooled | - | - | - | 0.994 [0.989, 0.998] | - |
| L without Sciuridae | pooled | - | - | - | 0.104 [0.096, 0.112] | - |
| L_upload without Sciuridae | pooled | - | - | - | 0.039 [0.033, 0.046] | - |
| L_ident without Sciuridae | pooled | - | - | - | 0.065 [0.060, 0.069] | - |
| O_ident without Sciuridae | pooled | - | - | - | -0.174 [-0.350, 0.006] | - |
| G_all without Sciuridae | pooled | - | - | - | 0.714 [0.149, 1.286] | - |
| G_sup without Sciuridae | pooled | - | - | - | -0.388 [-0.659, -0.114] | - |
| G_sup with S2b without Sciuridae | pooled | - | - | - | -0.384 [-0.687, -0.090] | - |
| O at 2026-04-01 without Sciuridae | pooled | - | - | - | -0.141 [-0.282, -0.016] | - |
| R at 2026-04-01 without Sciuridae | pooled | - | - | - | 0.998 [0.995, 1.000] | - |
| L at 2026-04-01 without Sciuridae | pooled | - | - | - | 0.028 [0.023, 0.034] | - |
| L_upload at 2026-04-01 without Sciuridae | pooled | - | - | - | 0.011 [0.007, 0.016] | - |
| L_ident at 2026-04-01 without Sciuridae | pooled | - | - | - | 0.017 [0.015, 0.019] | - |
| O_ident at 2026-04-01 without Sciuridae | pooled | - | - | - | 0.021 [-0.062, 0.102] | - |
| G_all at 2026-04-01 without Sciuridae | pooled | - | - | - | 0.802 [0.302, 1.305] | - |
| G_sup at 2026-04-01 without Sciuridae | pooled | - | - | - | -0.300 [-0.471, -0.135] | - |
| Delta (5000 replicates) | pooled | 4.620 [3.699, 5.561] | - | - | - | - |
| ER (5000 replicates) | pooled | 2.027 [1.762, 2.354] | - | - | - | - |

Further values (analysis.json): BioCLIP 2.5 Huge: families with lower bound of Delta above 0 6, tipping point to 0 0.038, to 1.0 0.028, share of slow errors whose predicted species was proposed 0.090; BioCLIP 2: families with lower bound of Delta above 0 6, tipping point to 0 0.056, to 1.0 0.046, share of slow errors whose predicted species was proposed 0.063; first BioCLIP: families with lower bound of Delta above 0 6, tipping point to 0 0.101, to 1.0 0.091, share of slow errors whose predicted species was proposed 0.020; BT-CLIP-O: families with lower bound of Delta above 0 4, tipping point to 0 0.027, to 1.0 0.017, share of slow errors whose predicted species was proposed 0.017.

### new_W

| quantity | unit | BioCLIP 2.5 Huge | BioCLIP 2 | first BioCLIP | BT-CLIP-O | families left out |
|---|---|---|---|---|---|---|
| Delta | pooled | 4.167 [3.051, 4.831] | 5.224 [3.726, 6.013] | 4.071 [2.770, 6.078] | 2.980 [1.543, 3.698] | - |
| ER | pooled | 1.548 [1.359, 1.656] | 1.465 [1.301, 1.551] | 1.097 [1.065, 1.152] | 1.046 [1.023, 1.058] | - |
| dropped share of slow weight | pooled | 0.021 [0.021, 0.065] | 0.021 [0.021, 0.065] | 0.021 [0.021, 0.065] | 0.021 [0.021, 0.065] | - |
| Delta | animals | 7.376 [5.359, 8.377] | 9.616 [7.020, 10.817] | 6.559 [4.914, 10.058] | 4.150 [1.909, 4.917] | - |
| ER | animals | 2.185 [1.704, 2.413] | 1.863 [1.527, 2.002] | 1.131 [1.097, 1.214] | 1.060 [1.026, 1.072] | - |
| Delta | plants | 0.804 [-0.500, 1.935] | 1.198 [-0.367, 2.760] | 2.285 [-0.246, 4.528] | 1.877 [0.239, 3.532] | - |
| ER | plants | 1.131 [0.928, 1.368] | 1.122 [0.966, 1.319] | 1.063 [0.993, 1.130] | 1.036 [1.004, 1.071] | - |
| median family Delta | families | 2.043 [1.412, 3.026] | 3.423 [2.197, 4.657] | 2.950 [1.619, 6.591] | 1.262 [0.282, 2.578] | - |
| Delta population-weighted | pooled | 4.057 [2.981, 4.700] | 5.428 [3.978, 6.290] | 4.804 [3.459, 6.794] | 2.603 [1.256, 3.292] | - |
| Delta leave one family out | without Araneidae | 4.436 [3.123, 5.217] | 5.267 [3.576, 6.133] | 3.049 [1.668, 5.323] | 3.468 [1.820, 4.340] | - |
| Delta leave one family out | without Colubridae | 2.099 [1.312, 2.810] | 2.879 [1.924, 3.827] | 4.245 [2.638, 5.723] | 1.231 [0.353, 2.095] | - |
| Delta leave one family out | without Pinaceae | 4.878 [3.617, 5.562] | 6.157 [4.465, 6.987] | 4.512 [3.187, 6.733] | 2.994 [1.405, 3.742] | - |
| Delta leave one family out | without Poaceae | 4.802 [3.457, 5.560] | 5.902 [4.227, 6.764] | 4.344 [3.005, 6.636] | 3.406 [1.814, 4.215] | - |
| Delta leave one family out | without Polyporaceae | 4.747 [3.394, 5.462] | 6.249 [4.519, 7.165] | 4.849 [3.477, 7.181] | 3.241 [1.643, 3.998] | - |
| Delta leave one family out | without Ranidae | 4.041 [2.725, 4.696] | 4.892 [3.181, 5.737] | 3.425 [2.029, 5.687] | 3.537 [1.853, 4.401] | - |
| Delta A1 vs A0 | pooled | 2.121 [1.322, 2.931] | 3.201 [2.185, 4.210] | 3.940 [2.435, 5.413] | 1.661 [0.741, 2.599] | - |
| ER A1 vs A0 | pooled | 1.268 [1.160, 1.387] | 1.276 [1.181, 1.375] | 1.101 [1.061, 1.141] | 1.025 [1.011, 1.039] | - |
| Delta A2 vs A0 | pooled | 6.590 [5.301, 7.833] | 6.684 [5.192, 8.168] | 6.166 [4.284, 7.981] | 2.649 [1.300, 3.911] | - |
| ER A2 vs A0 | pooled | 1.772 [1.588, 1.958] | 1.514 [1.386, 1.660] | 1.145 [1.099, 1.191] | 1.042 [1.020, 1.062] | - |
| Delta A3 vs A0 | pooled | 8.334 [5.907, 11.048] | 11.194 [7.200, 13.358] | 7.833 [4.557, 16.517] | 7.571 [4.187, 9.193] | - |
| ER A3 vs A0 | pooled | 2.368 [1.730, 2.782] | 2.259 [1.562, 2.577] | 1.162 [1.091, 1.398] | 1.136 [1.066, 1.170] | - |
| slope on log(1+T) | pooled | 1.516 [1.305, 1.737] | 1.787 [1.524, 2.047] | 1.957 [1.616, 2.286] | 0.797 [0.569, 1.007] | - |
| Delta median split | pooled | 2.681 [2.098, 3.296] | 3.373 [2.610, 4.191] | 4.094 [2.948, 5.277] | 1.559 [0.803, 2.285] | - |
| ER median split | pooled | 1.351 [1.264, 1.453] | 1.306 [1.229, 1.394] | 1.107 [1.076, 1.140] | 1.024 [1.012, 1.035] | - |
| Delta strong consensus | pooled | 3.939 [2.064, 5.595] | 3.399 [0.929, 5.842] | 5.483 [1.817, 9.190] | 2.680 [-0.071, 4.964] | - |
| ER strong consensus | pooled | 1.568 [1.279, 1.929] | 1.277 [1.071, 1.551] | 1.146 [1.047, 1.265] | 1.041 [0.999, 1.079] | - |
| Delta common horizon 540 days | pooled | 3.394 [2.652, 4.145] | 4.269 [3.328, 5.168] | 4.731 [3.326, 6.109] | 2.078 [1.209, 2.929] | - |
| ER common horizon 540 days | pooled | 1.417 [1.311, 1.531] | 1.354 [1.265, 1.444] | 1.117 [1.082, 1.154] | 1.032 [1.018, 1.045] | - |
| Delta without perceptual-duplicate groups | pooled | 4.134 [2.985, 4.791] | 5.231 [3.750, 6.010] | 4.091 [2.771, 6.070] | 2.936 [1.504, 3.653] | - |
| ER without perceptual-duplicate groups | pooled | 1.543 [1.355, 1.650] | 1.465 [1.301, 1.552] | 1.098 [1.065, 1.152] | 1.046 [1.023, 1.058] | - |
| Delta without regime-flagged pairs | pooled | 4.167 [3.051, 4.831] | 5.224 [3.726, 6.013] | 4.071 [2.770, 6.078] | 4.287 [2.225, 5.388] | BT-CLIP-O: Araneidae;Ranidae |
| ER without regime-flagged pairs | pooled | 1.548 [1.359, 1.656] | 1.465 [1.301, 1.551] | 1.097 [1.065, 1.152] | 1.081 [1.040, 1.103] | BT-CLIP-O: Araneidae;Ranidae |
| Delta slow with disagreement | pooled | 10.490 [7.359, 13.333] | 12.985 [9.592, 16.438] | 13.209 [9.132, 17.204] | 6.786 [3.461, 9.509] | - |
| ER slow with disagreement | pooled | 2.094 [1.703, 2.514] | 1.963 [1.665, 2.307] | 1.309 [1.208, 1.413] | 1.104 [1.052, 1.148] | - |
| Delta slow without disagreement | pooled | 3.843 [2.656, 4.494] | 4.784 [3.178, 5.564] | 3.517 [2.209, 5.591] | 2.750 [1.263, 3.485] | - |
| ER slow without disagreement | pooled | 1.513 [1.320, 1.621] | 1.431 [1.259, 1.519] | 1.084 [1.052, 1.140] | 1.043 [1.019, 1.055] | - |
| Delta within V0 | pooled | 4.914 [3.205, 6.683] | 4.986 [3.029, 7.121] | 5.532 [2.988, 8.851] | 1.632 [-0.251, 3.333] | - |
| ER within V0 | pooled | 1.486 [1.295, 1.737] | 1.344 [1.195, 1.527] | 1.131 [1.069, 1.216] | 1.024 [0.996, 1.050] | - |
| Delta within V1 | pooled | 3.429 [2.115, 4.151] | 4.843 [3.213, 5.747] | 3.373 [2.024, 5.620] | 2.905 [1.296, 3.778] | - |
| ER within V1 | pooled | 1.499 [1.278, 1.645] | 1.470 [1.278, 1.587] | 1.081 [1.047, 1.144] | 1.046 [1.020, 1.060] | - |
| Delta within activity S0 | pooled | 6.577 [4.119, 9.158] | 6.288 [2.714, 9.775] | 11.003 [3.772, 16.614] | -1.073 [-3.996, 2.308] | - |
| ER within activity S0 | pooled | 2.105 [1.616, 3.169] | 1.592 [1.213, 2.139] | 1.337 [1.100, 1.600] | 0.986 [0.948, 1.031] | - |
| Delta within activity S1 | pooled | 2.525 [0.167, 4.522] | 3.948 [1.341, 6.512] | 6.482 [3.005, 10.809] | 3.799 [0.998, 5.953] | - |
| ER within activity S1 | pooled | 1.319 [1.017, 1.718] | 1.351 [1.102, 1.713] | 1.170 [1.074, 1.320] | 1.059 [1.015, 1.095] | - |
| Delta within activity S2 | pooled | 2.677 [1.329, 4.367] | 3.519 [1.673, 5.425] | 3.818 [1.311, 6.832] | 3.288 [1.345, 4.866] | - |
| ER within activity S2 | pooled | 1.331 [1.150, 1.643] | 1.296 [1.125, 1.511] | 1.093 [1.031, 1.177] | 1.052 [1.021, 1.078] | - |
| Delta within activity S3 | pooled | 3.939 [2.744, 5.242] | 4.898 [3.501, 6.329] | 4.731 [2.725, 6.767] | 2.305 [0.930, 3.576] | - |
| ER within activity S3 | pooled | 1.491 [1.319, 1.696] | 1.418 [1.281, 1.566] | 1.118 [1.065, 1.173] | 1.035 [1.014, 1.055] | - |
| Delta genus level with B2 | pooled | 3.016 [2.418, 3.591] | 3.907 [3.188, 4.553] | 5.545 [4.351, 6.775] | 1.259 [0.213, 2.256] | - |
| ER genus level with B2 | pooled | 1.980 [1.710, 2.331] | 1.807 [1.608, 2.033] | 1.226 [1.172, 1.283] | 1.032 [1.005, 1.058] | - |
| Delta genus level with B1 and B2 | pooled | 7.351 [6.594, 8.121] | 8.528 [7.622, 9.373] | 9.728 [8.424, 11.047] | 2.946 [1.856, 4.035] | - |
| ER genus level with B1 and B2 | pooled | 3.397 [2.932, 3.998] | 2.726 [2.420, 3.077] | 1.381 [1.319, 1.448] | 1.075 [1.046, 1.105] | - |
| O at 2024-10-01 | pooled | 1.232 [0.978, 1.481] | 1.485 [1.220, 1.762] | 2.016 [1.604, 2.412] | 0.183 [-0.221, 0.623] | - |
| R at 2024-10-01 | pooled | 1.159 [1.122, 1.196] | 1.132 [1.106, 1.160] | 1.053 [1.042, 1.063] | 1.003 [0.997, 1.010] | - |
| L at 2024-10-01 | pooled | 0.273 [0.264, 0.281] | 0.273 [0.264, 0.281] | 0.273 [0.264, 0.281] | 0.273 [0.264, 0.281] | - |
| L_upload at 2024-10-01 | pooled | 0.100 [0.092, 0.109] | 0.100 [0.092, 0.109] | 0.100 [0.092, 0.109] | 0.100 [0.092, 0.109] | - |
| L_ident at 2024-10-01 | pooled | 0.173 [0.167, 0.179] | 0.173 [0.167, 0.179] | 0.173 [0.167, 0.179] | 0.173 [0.167, 0.179] | - |
| O_ident at 2024-10-01 | pooled | 1.156 [0.932, 1.377] | 1.369 [1.144, 1.594] | 1.806 [1.486, 2.146] | 0.123 [-0.208, 0.466] | - |
| G_all at 2024-10-01 | pooled | 4.169 [3.805, 4.581] | 4.964 [4.568, 5.388] | 6.832 [6.277, 7.394] | 0.641 [0.098, 1.248] | - |
| G_sup at 2024-10-01 | pooled | 1.091 [0.905, 1.272] | 1.477 [1.274, 1.688] | 2.636 [2.287, 2.987] | -0.266 [-0.643, 0.128] | - |
| O | pooled | 0.855 [0.670, 1.044] | 0.932 [0.754, 1.118] | 1.135 [0.871, 1.380] | 0.144 [-0.139, 0.425] | - |
| R | pooled | 1.105 [1.081, 1.131] | 1.079 [1.063, 1.097] | 1.029 [1.022, 1.035] | 1.002 [0.998, 1.007] | - |
| L | pooled | 0.153 [0.146, 0.161] | 0.153 [0.146, 0.161] | 0.153 [0.146, 0.161] | 0.153 [0.146, 0.161] | - |
| L_upload | pooled | 0.049 [0.043, 0.055] | 0.049 [0.043, 0.055] | 0.049 [0.043, 0.055] | 0.049 [0.043, 0.055] | - |
| L_ident | pooled | 0.105 [0.100, 0.110] | 0.105 [0.100, 0.110] | 0.105 [0.100, 0.110] | 0.105 [0.100, 0.110] | - |
| O_ident | pooled | 0.785 [0.620, 0.947] | 0.857 [0.702, 1.007] | 1.061 [0.855, 1.265] | 0.093 [-0.158, 0.343] | - |
| G_all | pooled | 4.086 [3.735, 4.475] | 4.727 [4.357, 5.133] | 6.339 [5.823, 6.834] | 0.645 [0.136, 1.168] | - |
| G_sup | pooled | 1.008 [0.849, 1.172] | 1.239 [1.074, 1.410] | 2.143 [1.874, 2.402] | -0.262 [-0.537, 0.029] | - |
| G_sup with S2b | pooled | 1.064 [0.897, 1.237] | 1.281 [1.117, 1.463] | 2.220 [1.939, 2.490] | -0.215 [-0.506, 0.088] | - |
| O without perceptual-duplicate groups | pooled | 0.856 [0.670, 1.044] | 0.938 [0.761, 1.124] | 1.127 [0.864, 1.370] | 0.141 [-0.144, 0.423] | - |
| R without perceptual-duplicate groups | pooled | 1.105 [1.081, 1.132] | 1.080 [1.063, 1.097] | 1.029 [1.022, 1.035] | 1.002 [0.998, 1.007] | - |
| G_all without perceptual-duplicate groups | pooled | 4.077 [3.718, 4.463] | 4.712 [4.340, 5.121] | 6.324 [5.815, 6.816] | 0.649 [0.142, 1.176] | - |
| G_sup without perceptual-duplicate groups | pooled | 1.011 [0.853, 1.173] | 1.243 [1.080, 1.415] | 2.137 [1.869, 2.396] | -0.270 [-0.541, 0.019] | - |
| O without regime-flagged pairs | pooled | 0.855 [0.670, 1.044] | 0.932 [0.754, 1.118] | 1.135 [0.871, 1.380] | 0.200 [-0.210, 0.604] | BT-CLIP-O: Araneidae;Ranidae |
| R without regime-flagged pairs | pooled | 1.105 [1.081, 1.131] | 1.079 [1.063, 1.097] | 1.029 [1.022, 1.035] | 1.004 [0.996, 1.011] | BT-CLIP-O: Araneidae;Ranidae |
| G_all without regime-flagged pairs | pooled | 4.086 [3.735, 4.475] | 4.727 [4.357, 5.133] | 6.339 [5.823, 6.834] | 0.235 [-0.485, 0.937] | BT-CLIP-O: Araneidae;Ranidae |
| G_sup without regime-flagged pairs | pooled | 1.008 [0.849, 1.172] | 1.239 [1.074, 1.410] | 2.143 [1.874, 2.402] | -0.525 [-0.908, -0.147] | BT-CLIP-O: Araneidae;Ranidae |
| O at 2025-10-01 | pooled | 0.541 [0.421, 0.675] | 0.588 [0.468, 0.716] | 0.683 [0.529, 0.831] | 0.066 [-0.092, 0.223] | - |
| R at 2025-10-01 | pooled | 1.064 [1.049, 1.081] | 1.048 [1.038, 1.060] | 1.017 [1.013, 1.021] | 1.001 [0.999, 1.003] | - |
| L at 2025-10-01 | pooled | 0.064 [0.060, 0.070] | 0.064 [0.060, 0.070] | 0.064 [0.060, 0.070] | 0.064 [0.060, 0.070] | - |
| L_upload at 2025-10-01 | pooled | 0.017 [0.014, 0.021] | 0.017 [0.014, 0.021] | 0.017 [0.014, 0.021] | 0.017 [0.014, 0.021] | - |
| L_ident at 2025-10-01 | pooled | 0.047 [0.044, 0.051] | 0.047 [0.044, 0.051] | 0.047 [0.044, 0.051] | 0.047 [0.044, 0.051] | - |
| O_ident at 2025-10-01 | pooled | 0.532 [0.422, 0.662] | 0.544 [0.437, 0.652] | 0.693 [0.564, 0.820] | 0.019 [-0.126, 0.157] | - |
| G_all at 2025-10-01 | pooled | 3.934 [3.593, 4.325] | 4.495 [4.123, 4.878] | 6.032 [5.551, 6.509] | 0.841 [0.385, 1.300] | - |
| G_sup at 2025-10-01 | pooled | 0.856 [0.721, 1.006] | 1.007 [0.870, 1.150] | 1.836 [1.633, 2.038] | -0.067 [-0.258, 0.141] | - |
| b0 | pooled | 2.936 [2.274, 3.629] | - | - | - | - |
| b3 | pooled | 2.709 [2.085, 3.504] | - | - | - | - |
| b_obs | pooled | 2.044 [0.853, 3.343] | - | - | - | - |
| rho | pooled | 0.923 [0.810, 1.095] | - | - | - | - |
| Delta without Ranidae | pooled | - | - | - | 3.537 [1.837, 4.397] | - |
| ER without Ranidae | pooled | - | - | - | 1.062 [1.031, 1.078] | - |
| dropped share of slow weight without Ranidae | pooled | - | - | - | 0.022 [0.022, 0.075] | - |
| Delta without Ranidae | animals | - | - | - | 6.129 [2.762, 7.245] | - |
| ER without Ranidae | animals | - | - | - | 1.112 [1.046, 1.134] | - |
| Delta without Ranidae | plants | - | - | - | 1.877 [0.181, 3.426] | - |
| ER without Ranidae | plants | - | - | - | 1.036 [1.003, 1.068] | - |
| median family Delta without Ranidae | families | - | - | - | 1.674 [0.411, 3.587] | - |
| Delta population-weighted without Ranidae | pooled | - | - | - | 3.093 [1.525, 3.906] | - |
| Delta leave one family out without Ranidae | without Araneidae | - | - | - | 4.287 [2.221, 5.339] | - |
| Delta leave one family out without Ranidae | without Colubridae | - | - | - | 1.491 [0.423, 2.542] | - |
| Delta leave one family out without Ranidae | without Pinaceae | - | - | - | 3.696 [1.779, 4.606] | - |
| Delta leave one family out without Ranidae | without Poaceae | - | - | - | 4.209 [2.219, 5.185] | - |
| Delta leave one family out without Ranidae | without Polyporaceae | - | - | - | 4.003 [2.029, 4.882] | - |
| Delta A1 vs A0 without Ranidae | pooled | - | - | - | 1.985 [0.864, 3.013] | - |
| ER A1 vs A0 without Ranidae | pooled | - | - | - | 1.032 [1.014, 1.050] | - |
| Delta A2 vs A0 without Ranidae | pooled | - | - | - | 3.117 [1.572, 4.515] | - |
| ER A2 vs A0 without Ranidae | pooled | - | - | - | 1.055 [1.027, 1.080] | - |
| Delta A3 vs A0 without Ranidae | pooled | - | - | - | 8.625 [4.506, 10.794] | - |
| ER A3 vs A0 without Ranidae | pooled | - | - | - | 1.183 [1.078, 1.236] | - |
| slope on log(1+T) without Ranidae | pooled | - | - | - | 0.938 [0.669, 1.176] | - |
| Delta median split without Ranidae | pooled | - | - | - | 1.817 [0.952, 2.683] | - |
| ER median split without Ranidae | pooled | - | - | - | 1.031 [1.016, 1.046] | - |
| O at 2024-10-01 without Ranidae | pooled | - | - | - | 0.244 [-0.245, 0.740] | - |
| R at 2024-10-01 without Ranidae | pooled | - | - | - | 1.004 [0.996, 1.013] | - |
| L at 2024-10-01 without Ranidae | pooled | - | - | - | 0.290 [0.281, 0.300] | - |
| L_upload at 2024-10-01 without Ranidae | pooled | - | - | - | 0.103 [0.094, 0.113] | - |
| L_ident at 2024-10-01 without Ranidae | pooled | - | - | - | 0.186 [0.180, 0.193] | - |
| O_ident at 2024-10-01 without Ranidae | pooled | - | - | - | 0.152 [-0.248, 0.558] | - |
| G_all at 2024-10-01 without Ranidae | pooled | - | - | - | 0.992 [0.270, 1.700] | - |
| G_sup at 2024-10-01 without Ranidae | pooled | - | - | - | -0.179 [-0.635, 0.282] | - |
| O without Ranidae | pooled | - | - | - | 0.192 [-0.150, 0.516] | - |
| R without Ranidae | pooled | - | - | - | 1.003 [0.997, 1.009] | - |
| L without Ranidae | pooled | - | - | - | 0.166 [0.159, 0.174] | - |
| L_upload without Ranidae | pooled | - | - | - | 0.048 [0.043, 0.055] | - |
| L_ident without Ranidae | pooled | - | - | - | 0.118 [0.112, 0.124] | - |
| O_ident without Ranidae | pooled | - | - | - | 0.120 [-0.171, 0.392] | - |
| G_all without Ranidae | pooled | - | - | - | 0.953 [0.333, 1.586] | - |
| G_sup without Ranidae | pooled | - | - | - | -0.218 [-0.539, 0.117] | - |
| G_sup with S2b without Ranidae | pooled | - | - | - | -0.156 [-0.506, 0.192] | - |
| O at 2025-10-01 without Ranidae | pooled | - | - | - | 0.087 [-0.112, 0.284] | - |
| R at 2025-10-01 without Ranidae | pooled | - | - | - | 1.001 [0.998, 1.005] | - |
| L at 2025-10-01 without Ranidae | pooled | - | - | - | 0.070 [0.065, 0.076] | - |
| L_upload at 2025-10-01 without Ranidae | pooled | - | - | - | 0.017 [0.013, 0.021] | - |
| L_ident at 2025-10-01 without Ranidae | pooled | - | - | - | 0.054 [0.050, 0.058] | - |
| O_ident at 2025-10-01 without Ranidae | pooled | - | - | - | 0.021 [-0.148, 0.184] | - |
| G_all at 2025-10-01 without Ranidae | pooled | - | - | - | 1.094 [0.537, 1.681] | - |
| G_sup at 2025-10-01 without Ranidae | pooled | - | - | - | -0.078 [-0.320, 0.160] | - |
| Delta (5000 replicates) | pooled | 4.167 [2.987, 4.791] | - | - | - | - |
| ER (5000 replicates) | pooled | 1.548 [1.354, 1.653] | - | - | - | - |

Further values (analysis.json): BioCLIP 2.5 Huge: families with lower bound of Delta above 0 3, tipping point to 0 0.032, to 1.0 0.022, share of slow errors whose predicted species was proposed 0.069; BioCLIP 2: families with lower bound of Delta above 0 3, tipping point to 0 0.039, to 1.0 0.029, share of slow errors whose predicted species was proposed 0.048; first BioCLIP: families with lower bound of Delta above 0 3, tipping point to 0 0.031, to 1.0 0.021, share of slow errors whose predicted species was proposed 0.015; BT-CLIP-O: families with lower bound of Delta above 0 2, tipping point to 0 0.018, to 1.0 0.008, share of slow errors whose predicted species was proposed 0.007.

### replication_W

| quantity | unit | BioCLIP 2.5 Huge | BioCLIP 2 | first BioCLIP | BT-CLIP-O | families left out |
|---|---|---|---|---|---|---|
| Delta | pooled | 2.326 [1.630, 3.002] | 2.689 [1.981, 3.401] | 5.160 [4.134, 6.364] | 1.971 [1.238, 2.777] | - |
| ER | pooled | 1.440 [1.295, 1.661] | 1.360 [1.255, 1.513] | 1.192 [1.152, 1.245] | 1.040 [1.025, 1.057] | - |
| dropped share of slow weight | pooled | 0.041 [0.053, 0.069] | 0.041 [0.053, 0.069] | 0.041 [0.053, 0.069] | 0.041 [0.053, 0.069] | - |
| median family Delta | families | 1.344 [0.753, 1.881] | 1.643 [1.281, 2.760] | 4.216 [2.542, 5.647] | 1.760 [0.716, 2.745] | - |
| Delta population-weighted | pooled | 3.085 [2.235, 3.849] | 3.422 [2.597, 4.211] | 6.103 [4.881, 7.517] | 2.422 [1.564, 3.317] | - |
| Delta leave one family out | without Acrididae | 2.403 [1.689, 3.105] | 2.710 [1.999, 3.426] | 5.306 [4.235, 6.491] | 1.980 [1.252, 2.796] | - |
| Delta leave one family out | without Apiaceae | 2.409 [1.709, 3.116] | 2.756 [2.050, 3.479] | 5.317 [4.313, 6.519] | 1.985 [1.262, 2.807] | - |
| Delta leave one family out | without Apocynaceae | 2.426 [1.721, 3.124] | 2.720 [2.012, 3.449] | 5.189 [4.149, 6.382] | 2.047 [1.290, 2.856] | - |
| Delta leave one family out | without Ardeidae | 1.739 [1.230, 2.250] | 2.338 [1.625, 3.019] | 4.822 [3.806, 6.004] | 1.748 [1.005, 2.517] | - |
| Delta leave one family out | without Asparagaceae | 2.386 [1.686, 3.084] | 2.735 [2.024, 3.452] | 5.175 [4.141, 6.401] | 1.988 [1.235, 2.793] | - |
| Delta leave one family out | without Caprifoliaceae | 2.398 [1.690, 3.099] | 2.737 [2.024, 3.475] | 5.251 [4.219, 6.465] | 1.977 [1.225, 2.787] | - |
| Delta leave one family out | without Caryophyllaceae | 2.362 [1.653, 3.052] | 2.732 [2.004, 3.463] | 5.196 [4.161, 6.440] | 1.957 [1.230, 2.759] | - |
| Delta leave one family out | without Chrysomelidae | 2.373 [1.654, 3.075] | 2.773 [2.058, 3.507] | 5.181 [4.130, 6.424] | 2.030 [1.291, 2.864] | - |
| Delta leave one family out | without Coccinellidae | 2.216 [1.507, 2.918] | 2.500 [1.770, 3.222] | 4.649 [3.625, 5.850] | 1.797 [1.048, 2.633] | - |
| Delta leave one family out | without Cyperaceae | 2.392 [1.716, 3.075] | 2.751 [2.026, 3.477] | 5.268 [4.215, 6.466] | 1.935 [1.196, 2.757] | - |
| Delta leave one family out | without Erebidae | 2.333 [1.625, 3.032] | 2.683 [1.950, 3.403] | 4.923 [3.880, 6.114] | 1.850 [1.110, 2.638] | - |
| Delta leave one family out | without Ericaceae | 2.268 [1.578, 2.985] | 2.668 [1.959, 3.399] | 5.270 [4.260, 6.502] | 1.913 [1.194, 2.737] | - |
| Delta leave one family out | without Fagaceae | 2.350 [1.650, 3.046] | 2.865 [2.150, 3.558] | 5.430 [4.417, 6.638] | 2.058 [1.320, 2.900] | - |
| Delta leave one family out | without Formicidae | 2.423 [1.713, 3.058] | 2.773 [2.046, 3.463] | 4.994 [3.985, 6.202] | 2.041 [1.304, 2.848] | - |
| Delta leave one family out | without Geometridae | 2.358 [1.645, 3.059] | 2.653 [1.917, 3.399] | 5.082 [4.059, 6.319] | 1.929 [1.203, 2.733] | - |
| Delta leave one family out | without Hesperiidae | 2.337 [1.652, 3.033] | 2.658 [1.928, 3.401] | 5.288 [4.240, 6.480] | 1.961 [1.218, 2.782] | - |
| Delta leave one family out | without Laridae | 2.135 [1.452, 2.808] | 2.452 [1.836, 3.108] | 5.025 [4.008, 6.247] | 1.782 [1.086, 2.597] | - |
| Delta leave one family out | without Libellulidae | 2.185 [1.499, 2.909] | 2.520 [1.807, 3.266] | 4.826 [3.804, 6.025] | 1.967 [1.224, 2.769] | - |
| Delta leave one family out | without Lycaenidae | 2.241 [1.564, 2.932] | 2.730 [1.996, 3.467] | 5.162 [4.183, 6.370] | 2.018 [1.272, 2.814] | - |
| Delta leave one family out | without Malvaceae | 2.357 [1.659, 3.064] | 2.776 [2.062, 3.516] | 5.330 [4.272, 6.541] | 2.034 [1.284, 2.842] | - |
| Delta leave one family out | without Noctuidae | 2.379 [1.680, 3.083] | 2.771 [2.051, 3.485] | 5.237 [4.190, 6.477] | 2.008 [1.280, 2.806] | - |
| Delta leave one family out | without Onagraceae | 2.399 [1.685, 3.085] | 2.737 [2.009, 3.472] | 5.256 [4.194, 6.462] | 1.926 [1.195, 2.734] | - |
| Delta leave one family out | without Pentatomidae | 2.336 [1.624, 3.023] | 2.667 [1.937, 3.406] | 4.709 [3.689, 5.889] | 2.098 [1.364, 2.926] | - |
| Delta leave one family out | without Pieridae | 2.285 [1.585, 2.979] | 2.620 [1.908, 3.328] | 5.076 [4.052, 6.285] | 1.957 [1.221, 2.739] | - |
| Delta leave one family out | without Plantaginaceae | 2.347 [1.638, 3.033] | 2.698 [1.959, 3.442] | 5.414 [4.408, 6.621] | 2.044 [1.305, 2.859] | - |
| Delta leave one family out | without Polygonaceae | 2.434 [1.731, 3.143] | 2.740 [2.011, 3.463] | 5.403 [4.399, 6.630] | 1.999 [1.248, 2.809] | - |
| Delta leave one family out | without Ranunculaceae | 2.407 [1.699, 3.105] | 2.793 [2.073, 3.517] | 5.309 [4.264, 6.506] | 2.130 [1.381, 2.942] | - |
| Delta leave one family out | without Syrphidae | 2.410 [1.705, 3.085] | 2.755 [2.012, 3.477] | 5.410 [4.371, 6.637] | 1.943 [1.194, 2.778] | - |
| Delta leave one family out | without Tettigoniidae | 2.423 [1.718, 3.115] | 2.701 [1.978, 3.426] | 5.171 [4.123, 6.356] | 1.961 [1.212, 2.766] | - |
| Delta leave one family out | without Vespidae | 2.275 [1.594, 2.953] | 2.665 [1.949, 3.409] | 5.123 [4.092, 6.308] | 2.064 [1.323, 2.862] | - |
| Delta A1 vs A0 | pooled | 1.500 [0.892, 2.154] | 1.749 [1.069, 2.483] | 4.475 [3.360, 5.859] | 1.494 [0.628, 2.445] | - |
| ER A1 vs A0 | pooled | 1.376 [1.214, 1.603] | 1.296 [1.174, 1.451] | 1.180 [1.134, 1.244] | 1.030 [1.013, 1.050] | - |
| Delta A2 vs A0 | pooled | 3.400 [2.168, 4.940] | 3.896 [2.610, 5.137] | 6.223 [4.559, 7.991] | 2.647 [1.481, 3.802] | - |
| ER A2 vs A0 | pooled | 1.456 [1.262, 1.841] | 1.425 [1.265, 1.656] | 1.218 [1.157, 1.293] | 1.054 [1.030, 1.079] | - |
| Delta A3 vs A0 | pooled | 4.904 [2.577, 6.843] | 5.987 [3.750, 8.337] | 7.612 [4.976, 10.764] | 2.746 [0.738, 4.972] | - |
| ER A3 vs A0 | pooled | 2.094 [1.501, 2.817] | 1.767 [1.449, 2.406] | 1.267 [1.168, 1.404] | 1.055 [1.015, 1.104] | - |
| slope on log(1+T) | pooled | 0.844 [0.681, 1.013] | 0.978 [0.795, 1.168] | 1.745 [1.489, 2.043] | 0.649 [0.480, 0.853] | - |
| Delta median split | pooled | 1.422 [0.978, 1.809] | 2.093 [1.545, 2.666] | 4.306 [3.348, 5.243] | 1.198 [0.507, 1.844] | - |
| ER median split | pooled | 1.352 [1.231, 1.473] | 1.350 [1.248, 1.475] | 1.176 [1.134, 1.219] | 1.025 [1.011, 1.038] | - |
| Delta strong consensus | pooled | 2.566 [1.154, 4.559] | 3.807 [1.730, 5.953] | 6.578 [3.547, 10.165] | 1.982 [-0.954, 4.182] | - |
| ER strong consensus | pooled | 1.619 [1.255, 2.640] | 1.739 [1.282, 2.299] | 1.297 [1.150, 1.491] | 1.042 [0.980, 1.092] | - |
| Delta common horizon 540 days | pooled | 2.223 [1.567, 2.927] | 2.680 [1.943, 3.382] | 5.091 [4.057, 6.279] | 2.019 [1.288, 2.817] | - |
| ER common horizon 540 days | pooled | 1.415 [1.276, 1.632] | 1.374 [1.258, 1.520] | 1.191 [1.150, 1.243] | 1.041 [1.026, 1.058] | - |
| Delta without perceptual-duplicate groups | pooled | 2.302 [1.612, 2.970] | 2.695 [1.987, 3.401] | 5.180 [4.159, 6.390] | 1.988 [1.259, 2.812] | - |
| ER without perceptual-duplicate groups | pooled | 1.434 [1.289, 1.644] | 1.361 [1.257, 1.515] | 1.193 [1.153, 1.247] | 1.040 [1.025, 1.058] | - |
| Delta without regime-flagged pairs | pooled | 2.326 [1.630, 3.002] | 2.689 [1.981, 3.401] | 5.160 [4.134, 6.364] | 2.251 [1.284, 3.242] | BT-CLIP-O: Acrididae;Apiaceae;Ardeidae;Chrysomelidae;Geometridae;Lycaenidae;Noctuidae;Pentatomidae;Plantaginaceae;Tettigoniidae;Vespidae |
| ER without regime-flagged pairs | pooled | 1.440 [1.295, 1.661] | 1.360 [1.255, 1.513] | 1.192 [1.152, 1.245] | 1.051 [1.029, 1.076] | BT-CLIP-O: Acrididae;Apiaceae;Ardeidae;Chrysomelidae;Geometridae;Lycaenidae;Noctuidae;Pentatomidae;Plantaginaceae;Tettigoniidae;Vespidae |
| Delta slow with disagreement | pooled | 8.471 [5.621, 11.235] | 10.326 [7.305, 13.616] | 17.922 [13.751, 22.283] | 7.814 [4.901, 10.946] | - |
| ER slow with disagreement | pooled | 2.302 [1.781, 3.279] | 2.212 [1.796, 2.906] | 1.638 [1.478, 1.851] | 1.156 [1.094, 1.228] | - |
| Delta slow without disagreement | pooled | 2.051 [1.399, 2.708] | 2.422 [1.696, 3.132] | 4.663 [3.639, 5.849] | 1.784 [1.029, 2.593] | - |
| ER slow without disagreement | pooled | 1.395 [1.258, 1.594] | 1.328 [1.223, 1.477] | 1.174 [1.135, 1.227] | 1.036 [1.021, 1.053] | - |
| Delta within V0 | pooled | 3.284 [1.686, 4.919] | 4.209 [2.717, 6.218] | 7.132 [4.872, 10.306] | 2.279 [0.509, 4.490] | - |
| ER within V0 | pooled | 1.581 [1.269, 2.116] | 1.549 [1.325, 1.998] | 1.262 [1.173, 1.415] | 1.046 [1.010, 1.094] | - |
| Delta within V1 | pooled | 1.889 [1.245, 2.438] | 2.112 [1.310, 2.914] | 4.628 [3.417, 5.975] | 1.847 [0.955, 2.721] | - |
| ER within V1 | pooled | 1.373 [1.239, 1.572] | 1.292 [1.174, 1.469] | 1.175 [1.127, 1.237] | 1.038 [1.019, 1.057] | - |
| Delta within activity S0 | pooled | 4.026 [-0.175, 7.510] | 0.460 [-3.430, 4.120] | 6.489 [-5.286, 12.449] | 4.393 [0.548, 10.166] | BT-CLIP-O: Geometridae; BioCLIP 2.5 Huge: Geometridae; BioCLIP 2: Geometridae; first BioCLIP: Geometridae |
| ER within activity S0 | pooled | 2.595 [0.944, 12.943] | 1.107 [0.460, 2.645] | 1.269 [0.820, 1.626] | 1.088 [1.010, 1.219] | BT-CLIP-O: Geometridae; BioCLIP 2.5 Huge: Geometridae; BioCLIP 2: Geometridae; first BioCLIP: Geometridae |
| Delta within activity S1 | pooled | 0.488 [-1.669, 3.706] | 3.824 [1.374, 6.608] | 6.429 [1.888, 11.975] | 2.543 [-0.366, 5.985] | - |
| ER within activity S1 | pooled | 1.098 [0.728, 2.312] | 1.850 [1.246, 3.059] | 1.271 [1.070, 1.598] | 1.048 [0.993, 1.118] | - |
| Delta within activity S2 | pooled | 2.657 [1.543, 4.230] | 2.533 [0.969, 4.490] | 6.127 [3.878, 8.931] | 2.151 [0.488, 4.011] | - |
| ER within activity S2 | pooled | 1.707 [1.359, 2.650] | 1.367 [1.132, 1.829] | 1.242 [1.146, 1.384] | 1.045 [1.010, 1.086] | - |
| Delta within activity S3 | pooled | 2.554 [1.487, 3.264] | 2.765 [2.009, 3.770] | 4.808 [3.462, 6.426] | 1.491 [0.467, 2.557] | - |
| ER within activity S3 | pooled | 1.539 [1.302, 1.792] | 1.399 [1.281, 1.654] | 1.179 [1.126, 1.252] | 1.031 [1.010, 1.054] | - |
| Delta genus level with B2 | pooled | 1.727 [1.305, 2.158] | 1.108 [0.661, 2.374] | 4.253 [3.431, 5.520] | 2.135 [1.403, 3.049] | - |
| ER genus level with B2 | pooled | 1.804 [1.556, 2.117] | 1.282 [1.162, 1.914] | 1.283 [1.222, 1.405] | 1.074 [1.049, 1.111] | - |
| Delta genus level with B1 and B2 | pooled | 1.727 [1.305, 2.158] | 1.108 [0.661, 2.374] | 4.253 [3.431, 5.520] | 2.135 [1.403, 3.049] | - |
| ER genus level with B1 and B2 | pooled | 1.804 [1.556, 2.117] | 1.282 [1.162, 1.914] | 1.283 [1.222, 1.405] | 1.074 [1.049, 1.111] | - |
| b0 | pooled | 2.511 [1.967, 3.008] | - | - | - | - |
| b3 | pooled | 2.306 [1.684, 2.916] | - | - | - | - |
| b_obs | pooled | 2.179 [1.354, 3.029] | - | - | - | - |
| rho | pooled | 0.918 [0.743, 1.094] | - | - | - | - |

Further values (analysis.json): BioCLIP 2.5 Huge: families with lower bound of Delta above 0 9, tipping point to 0 0.018, to 1.0 0.008, share of slow errors whose predicted species was proposed 0.105; BioCLIP 2: families with lower bound of Delta above 0 8, tipping point to 0 0.021, to 1.0 0.011, share of slow errors whose predicted species was proposed 0.058; first BioCLIP: families with lower bound of Delta above 0 11, tipping point to 0 0.043, to 1.0 0.033, share of slow errors whose predicted species was proposed 0.021; BT-CLIP-O: families with lower bound of Delta above 0 4, tipping point to 0 0.013, to 1.0 0.003, share of slow errors whose predicted species was proposed 0.014.

## Delta and ER per family (heterogeneity; every model)

### eight_W

| family | BioCLIP 2.5 Huge Delta | BioCLIP 2.5 Huge ER | BioCLIP 2 Delta | BioCLIP 2 ER | first BioCLIP Delta | first BioCLIP ER | BT-CLIP-O Delta | BT-CLIP-O ER |
|---|---|---|---|---|---|---|---|---|
| Anatidae | 11.387 [8.901, 13.807] | 2.492 [2.113, 2.926] | 12.970 [10.244, 15.657] | 1.897 [1.694, 2.142] | 18.073 [14.767, 21.309] | 1.436 [1.347, 1.529] | 8.525 [5.942, 11.055] | 1.140 [1.096, 1.186] |
| Asteraceae | 0.679 [-0.385, 1.765] | 1.223 [0.899, 1.840] | 1.595 [0.232, 3.023] | 1.344 [1.041, 1.846] | 2.511 [-0.071, 5.608] | 1.119 [0.997, 1.297] | 1.728 [-0.048, 4.099] | 1.032 [0.999, 1.079] |
| Columbidae | 12.332 [10.258, 14.586] | 3.564 [2.914, 4.413] | 15.894 [13.524, 18.380] | 3.195 [2.725, 3.730] | 21.889 [18.260, 25.044] | 1.555 [1.447, 1.656] | 11.241 [9.059, 13.984] | 1.216 [1.169, 1.279] |
| Fabaceae | 1.253 [0.407, 2.099] | 1.549 [1.137, 2.216] | 1.373 [0.331, 2.323] | 1.277 [1.061, 1.541] | 4.400 [2.100, 6.836] | 1.225 [1.100, 1.391] | 0.547 [-0.864, 2.039] | 1.010 [0.984, 1.040] |
| Lamiaceae | 0.813 [0.196, 1.399] | 1.811 [1.151, 3.451] | 1.125 [0.185, 1.874] | 1.642 [1.081, 2.594] | 4.864 [2.945, 6.541] | 1.510 [1.279, 1.783] | 2.890 [1.348, 4.345] | 1.084 [1.038, 1.130] |
| Nymphalidae | 2.497 [1.014, 3.967] | 1.328 [1.117, 1.587] | 3.716 [1.938, 5.211] | 1.296 [1.141, 1.446] | 8.672 [5.557, 12.103] | 1.360 [1.213, 1.560] | 3.114 [0.916, 5.287] | 1.064 [1.019, 1.112] |
| Rosaceae | 1.230 [0.254, 2.397] | 1.283 [1.052, 1.741] | 2.278 [0.998, 3.834] | 1.457 [1.181, 2.007] | 3.491 [0.424, 5.905] | 1.146 [1.017, 1.270] | 2.465 [0.514, 4.882] | 1.049 [1.010, 1.101] |
| Sciuridae | 5.074 [3.531, 6.549] | 1.753 [1.470, 2.150] | 6.587 [4.852, 8.423] | 1.692 [1.473, 1.988] | 12.269 [9.610, 14.731] | 1.360 [1.271, 1.454] | -0.027 [-1.388, 1.494] | 1.000 [0.985, 1.016] |

### eight_W2

| family | BioCLIP 2.5 Huge Delta | BioCLIP 2.5 Huge ER | BioCLIP 2 Delta | BioCLIP 2 ER | first BioCLIP Delta | first BioCLIP ER | BT-CLIP-O Delta | BT-CLIP-O ER |
|---|---|---|---|---|---|---|---|---|
| Anatidae | 9.007 [5.632, 12.428] | 2.389 [1.776, 3.228] | 10.008 [6.095, 14.002] | 1.946 [1.529, 2.572] | 19.900 [14.374, 25.640] | 1.514 [1.352, 1.705] | 9.693 [5.821, 13.783] | 1.165 [1.095, 1.244] |
| Asteraceae | 2.181 [0.186, 3.703] | 1.786 [1.053, 2.938] | 3.121 [0.875, 5.307] | 1.690 [1.142, 2.775] | 2.532 [-2.052, 6.873] | 1.087 [0.936, 1.274] | 4.121 [0.611, 7.390] | 1.074 [1.010, 1.138] |
| Columbidae | 10.491 [7.011, 14.090] | 3.636 [2.613, 5.120] | 16.525 [12.161, 21.438] | 3.719 [2.860, 4.809] | 23.157 [18.567, 27.769] | 1.626 [1.486, 1.784] | 11.334 [7.226, 15.484] | 1.218 [1.129, 1.321] |
| Fabaceae | -0.081 [-2.730, 2.293] | 0.985 [0.648, 1.671] | 3.011 [-0.159, 5.642] | 1.453 [0.980, 2.151] | 9.762 [4.990, 14.201] | 1.405 [1.182, 1.699] | 1.451 [-1.954, 4.524] | 1.032 [0.959, 1.108] |
| Lamiaceae | 1.652 [0.278, 2.882] | 1.802 [1.108, 3.275] | 2.621 [1.119, 3.967] | 1.898 [1.323, 3.290] | 7.885 [4.831, 11.066] | 1.476 [1.266, 1.762] | 1.581 [-0.523, 3.841] | 1.025 [0.992, 1.061] |
| Nymphalidae | 3.837 [1.893, 6.024] | 2.590 [1.582, 5.097] | 3.782 [1.254, 6.699] | 1.749 [1.186, 3.302] | 13.455 [8.490, 18.128] | 1.656 [1.372, 2.019] | 4.393 [1.333, 7.572] | 1.135 [1.038, 1.253] |
| Rosaceae | 0.754 [-1.576, 2.996] | 1.085 [0.854, 1.397] | 1.305 [-1.369, 4.083] | 1.116 [0.898, 1.457] | 0.048 [-5.213, 4.832] | 1.001 [0.880, 1.133] | -0.695 [-3.183, 1.587] | 0.989 [0.950, 1.026] |
| Sciuridae | 9.120 [6.440, 11.702] | 3.289 [2.200, 5.143] | 12.077 [8.050, 15.760] | 2.613 [1.875, 3.651] | 15.357 [10.222, 20.097] | 1.430 [1.267, 1.614] | -2.006 [-5.582, 1.007] | 0.978 [0.940, 1.011] |

### new_W

| family | BioCLIP 2.5 Huge Delta | BioCLIP 2.5 Huge ER | BioCLIP 2 Delta | BioCLIP 2 ER | first BioCLIP Delta | first BioCLIP ER | BT-CLIP-O Delta | BT-CLIP-O ER |
|---|---|---|---|---|---|---|---|---|
| Araneidae | 2.820 [1.543, 4.032] | 2.051 [1.479, 2.906] | 5.010 [3.013, 6.788] | 1.724 [1.375, 2.165] | 9.180 [5.977, 12.267] | 1.229 [1.142, 1.318] | 0.537 [-0.821, 1.659] | 1.007 [0.989, 1.023] |
| Colubridae | 14.510 [8.943, 16.731] | 2.396 [1.631, 2.714] | 16.952 [10.036, 19.406] | 2.003 [1.440, 2.207] | 3.197 [0.792, 11.684] | 1.047 [1.012, 1.207] | 11.722 [5.247, 13.887] | 1.334 [1.112, 1.407] |
| Pinaceae | 0.614 [-1.406, 2.471] | 1.069 [0.862, 1.331] | 0.561 [-1.658, 2.880] | 1.041 [0.892, 1.243] | 1.866 [-1.745, 5.304] | 1.044 [0.962, 1.129] | 2.905 [0.452, 5.458] | 1.055 [1.008, 1.108] |
| Poaceae | 0.993 [-0.604, 2.272] | 1.289 [0.863, 1.925] | 1.836 [-0.145, 3.596] | 1.311 [0.979, 1.768] | 2.704 [-0.785, 5.845] | 1.090 [0.975, 1.211] | 0.849 [-1.275, 2.803] | 1.017 [0.976, 1.057] |
| Polyporaceae | 1.266 [-0.215, 2.692] | 1.086 [0.987, 1.200] | 0.101 [-1.776, 1.803] | 1.007 [0.884, 1.141] | 0.179 [-3.168, 3.234] | 1.006 [0.897, 1.125] | 1.674 [-0.705, 4.173] | 1.023 [0.990, 1.058] |
| Ranidae | 4.799 [2.985, 6.972] | 1.858 [1.518, 2.326] | 6.887 [4.829, 9.652] | 1.715 [1.478, 2.011] | 7.299 [4.112, 11.003] | 1.169 [1.099, 1.244] | 0.190 [-0.535, 0.828] | 1.002 [0.995, 1.009] |

### replication_W

| family | BioCLIP 2.5 Huge Delta | BioCLIP 2.5 Huge ER | BioCLIP 2 Delta | BioCLIP 2 ER | first BioCLIP Delta | first BioCLIP ER | BT-CLIP-O Delta | BT-CLIP-O ER |
|---|---|---|---|---|---|---|---|---|
| Acrididae | 0.098 [-2.234, 1.881] | 1.061 [0.367, 8.647] | 2.089 [-0.816, 4.569] | 1.772 [0.837, 5.638] | 0.917 [-5.186, 7.686] | 1.028 [0.863, 1.288] | 1.717 [-3.885, 7.379] | 1.031 [0.935, 1.149] |
| Apiaceae | -0.083 [-2.240, 2.134] | 0.981 [0.598, 1.772] | 0.742 [-3.573, 4.951] | 1.091 [0.687, 1.938] | 0.593 [-3.790, 4.811] | 1.022 [0.872, 1.203] | 1.564 [-2.947, 6.010] | 1.024 [0.958, 1.096] |
| Apocynaceae | -0.575 [-3.150, 1.380] | 0.701 [0.152, 3.292] | 1.795 [-1.190, 4.018] | 1.883 [0.712, 7.640] | 4.324 [-1.524, 9.901] | 1.321 [0.912, 2.046] | -0.246 [-3.978, 3.512] | 0.994 [0.903, 1.094] |
| Ardeidae | 19.362 [7.191, 34.793] | 1.788 [1.218, 4.763] | 12.861 [6.737, 20.607] | 1.346 [1.169, 1.791] | 14.960 [6.598, 24.406] | 1.274 [1.116, 1.509] | 8.435 [2.028, 16.017] | 1.138 [1.033, 1.285] |
| Asparagaceae | 0.604 [-1.518, 2.367] | 1.224 [0.582, 4.483] | 1.369 [-1.326, 4.053] | 1.262 [0.794, 2.651] | 4.728 [-0.924, 10.360] | 1.187 [0.968, 1.479] | 1.474 [-2.479, 5.707] | 1.040 [0.933, 1.173] |
| Caprifoliaceae | 0.245 [-1.748, 1.912] | 1.160 [0.409, 5.921] | 1.300 [-0.625, 3.215] | 1.546 [0.822, 3.543] | 2.504 [-2.532, 7.571] | 1.172 [0.858, 1.717] | 1.803 [-2.247, 5.932] | 1.035 [0.959, 1.121] |
| Caryophyllaceae | 1.284 [-0.249, 2.813] | 2.350 [0.861, 21.350] | 1.445 [-0.183, 3.065] | 2.352 [0.909, 18.641] | 4.108 [0.571, 7.802] | 1.520 [1.054, 2.447] | 2.379 [-0.890, 5.787] | 1.041 [0.986, 1.104] |
| Chrysomelidae | 0.971 [-0.375, 2.377] | 1.098 [0.962, 1.267] | 0.267 [-2.006, 2.644] | 1.022 [0.845, 1.257] | 4.555 [0.670, 8.131] | 1.251 [1.034, 1.533] | 0.248 [-2.004, 2.549] | 1.005 [0.960, 1.053] |
| Coccinellidae | 5.525 [2.722, 8.547] | 3.733 [1.988, 7.889] | 8.189 [4.054, 12.238] | 2.945 [1.698, 5.541] | 19.970 [13.633, 26.533] | 1.706 [1.430, 2.082] | 7.006 [3.505, 10.536] | 1.213 [1.105, 1.348] |
| Cyperaceae | 0.417 [-2.183, 2.541] | 1.135 [0.574, 2.629] | 0.897 [-1.627, 3.445] | 1.224 [0.715, 2.418] | 2.018 [-2.876, 7.945] | 1.091 [0.888, 1.451] | 3.000 [-0.118, 6.235] | 1.102 [0.996, 1.230] |
| Erebidae | 2.137 [-0.498, 4.641] | 2.650 [0.847, 34.861] | 2.870 [-0.036, 5.908] | 2.007 [0.992, 6.486] | 12.019 [5.444, 19.010] | 1.705 [1.252, 2.599] | 5.479 [2.326, 8.866] | 1.222 [1.091, 1.408] |
| Ericaceae | 4.023 [1.356, 5.998] | 6.444 [1.589, 231.894] | 3.312 [0.582, 5.035] | 5.617 [1.200, 56.000] | 1.969 [-4.480, 8.225] | 1.107 [0.800, 1.641] | 3.642 [0.588, 6.957] | 1.115 [1.018, 1.264] |
| Fagaceae | 1.646 [-1.998, 4.466] | 1.285 [0.758, 2.208] | -2.415 [-6.597, 1.900] | 0.832 [0.619, 1.173] | -2.688 [-8.904, 3.427] | 0.947 [0.835, 1.074] | -0.566 [-4.530, 2.691] | 0.983 [0.875, 1.088] |
| Formicidae | -0.483 [-4.731, 5.943] | 0.968 [0.733, 1.655] | 0.264 [-4.860, 5.672] | 1.016 [0.760, 1.454] | 9.966 [1.585, 16.606] | 1.199 [1.029, 1.366] | -0.048 [-5.103, 4.424] | 0.999 [0.906, 1.094] |
| Geometridae | 1.405 [0.275, 2.675] | 8.690 [1.947, 84.483] | 3.748 [1.790, 5.700] | 18.000 [4.061, 29.844] | 7.414 [3.144, 11.088] | 2.651 [1.514, 4.522] | 3.197 [-0.209, 6.915] | 1.062 [0.996, 1.141] |
| Hesperiidae | 2.000 [-1.792, 5.673] | 1.136 [0.897, 1.481] | 3.590 [0.572, 6.789] | 1.292 [1.041, 1.651] | 1.431 [-4.052, 7.244] | 1.035 [0.909, 1.202] | 2.254 [-1.765, 5.869] | 1.036 [0.973, 1.100] |
| Laridae | 7.866 [3.415, 12.541] | 1.304 [1.122, 2.215] | 9.572 [-2.119, 20.780] | 1.437 [0.936, 2.848] | 9.057 [3.369, 15.647] | 1.155 [1.054, 1.304] | 7.461 [-0.519, 14.615] | 1.124 [0.992, 1.269] |
| Libellulidae | 6.428 [3.174, 9.328] | 7.988 [3.062, 34.827] | 7.609 [3.492, 11.474] | 3.593 [1.798, 7.042] | 14.832 [8.450, 21.449] | 1.766 [1.372, 2.289] | 2.085 [-2.815, 6.452] | 1.028 [0.965, 1.088] |
| Lycaenidae | 4.809 [-0.064, 8.227] | 1.777 [0.990, 3.032] | 1.491 [-2.191, 6.070] | 1.081 [0.854, 2.167] | 5.100 [-1.431, 12.142] | 1.139 [0.961, 1.473] | 0.618 [-3.242, 4.577] | 1.010 [0.946, 1.081] |
| Malvaceae | 1.421 [-1.063, 3.217] | 1.349 [0.821, 2.187] | 0.179 [-2.982, 2.708] | 1.031 [0.640, 1.721] | 0.228 [-4.271, 5.490] | 1.012 [0.805, 1.380] | 0.134 [-3.465, 3.531] | 1.004 [0.904, 1.116] |
| Noctuidae | 0.800 [-0.694, 2.128] | 2.053 [0.482, 13.706] | 0.309 [-2.470, 2.641] | 1.139 [0.414, 4.469] | 2.932 [-1.970, 7.214] | 1.195 [0.890, 1.586] | 0.904 [-3.459, 4.930] | 1.014 [0.950, 1.082] |
| Onagraceae | 0.209 [-1.263, 1.824] | 1.129 [0.477, 3.911] | 1.292 [-0.127, 2.971] | 2.126 [0.931, 11.395] | 2.363 [-1.482, 7.025] | 1.171 [0.906, 1.651] | 3.271 [-1.364, 7.755] | 1.115 [0.956, 1.307] |
| Pentatomidae | 2.054 [0.367, 3.952] | 4.650 [1.332, 41.982] | 3.336 [0.913, 6.033] | 3.077 [1.394, 9.569] | 18.236 [11.416, 25.144] | 1.497 [1.281, 1.769] | -1.706 [-4.664, 1.168] | 0.967 [0.911, 1.024] |
| Pieridae | 3.507 [0.551, 6.428] | 1.897 [1.091, 3.885] | 4.708 [0.282, 8.642] | 1.474 [1.021, 2.115] | 7.593 [1.500, 13.977] | 1.261 [1.046, 1.551] | 2.365 [-2.728, 7.631] | 1.037 [0.959, 1.128] |
| Plantaginaceae | 1.725 [0.052, 3.309] | 2.615 [1.022, 11.840] | 2.438 [-0.126, 5.043] | 1.810 [0.974, 4.180] | -2.212 [-7.221, 2.342] | 0.822 [0.554, 1.256] | -0.144 [-2.882, 2.937] | 0.998 [0.960, 1.043] |
| Polygonaceae | -0.800 [-4.290, 2.557] | 0.825 [0.410, 2.716] | 1.214 [-2.343, 5.214] | 1.199 [0.728, 2.735] | -1.903 [-7.689, 3.683] | 0.919 [0.722, 1.202] | 1.155 [-1.788, 4.333] | 1.038 [0.943, 1.166] |
| Ranunculaceae | -0.017 [-2.858, 2.408] | 0.995 [0.464, 3.258] | -0.326 [-4.049, 2.432] | 0.925 [0.440, 2.216] | 0.834 [-5.371, 7.345] | 1.042 [0.777, 1.509] | -2.656 [-6.414, 0.990] | 0.927 [0.837, 1.030] |
| Syrphidae | -0.115 [-2.608, 2.420] | 0.985 [0.433, 3.533] | 0.788 [-1.351, 3.531] | 1.099 [0.758, 3.068] | -2.102 [-8.844, 4.468] | 0.923 [0.699, 1.210] | 2.772 [-0.018, 5.991] | 1.048 [1.000, 1.112] |
| Tettigoniidae | -0.494 [-3.185, 1.844] | 0.830 [0.338, 2.607] | 2.340 [-0.786, 5.517] | 1.510 [0.873, 3.180] | 4.825 [-1.510, 11.094] | 1.145 [0.960, 1.385] | 2.254 [-0.879, 5.216] | 1.056 [0.979, 1.137] |
| Vespidae | 3.813 [-0.595, 7.829] | 1.749 [0.913, 4.054] | 3.402 [-1.573, 8.006] | 1.431 [0.850, 2.422] | 6.226 [-0.478, 13.385] | 1.169 [0.987, 1.410] | -0.721 [-4.060, 2.709] | 0.991 [0.949, 1.035] |

## C3 (BioCLIP 2.5 Huge; estimation only, no family-wise control)

| set | b0 | b3 | b_obs | rho | band of rho |
|---|---|---|---|---|---|
| eight_W | 2.074 [1.622, 2.610] | 2.251 [1.766, 2.904] | 2.384 [1.688, 3.123] | 1.086 [0.913, 1.339] | largely not explained |
| eight_W2 | 4.091 [3.241, 5.087] | 4.731 [3.673, 5.811] | 4.404 [3.076, 6.148] | 1.156 [0.942, 1.374] | largely not explained |
| new_W | 2.936 [2.274, 3.629] | 2.709 [2.085, 3.504] | 2.044 [0.853, 3.343] | 0.923 [0.810, 1.095] | largely not explained |
| replication_W | 2.511 [1.967, 3.008] | 2.306 [1.684, 2.916] | 2.179 [1.354, 3.029] | 0.918 [0.743, 1.094] | largely not explained |

The registered C3 is that of the eight families (eight_W; eight_W2 as the second window); the rows of the other sets are reported because the analysis step computes them for every set.

Covariates of b3: week, width, height, n_photos, vision, ident_avail, queue_load, activity S1, activity S2, activity S3; species x 10-degree cell fixed effects. Missing values (median imputed): week 0, width 0, height 0, n_photos 0, vision 0, ident_avail 0, queue_load 128; rows without an activity stratum: 0.

Identifier availability (section 7.3, item 5): scale per family (population / sampled observations with a history) and sources:

- eight_W: sources outputs/D4/api_raw_d4; scale Sciuridae 2.5, Anatidae 5.4, Nymphalidae 15.5, Fabaceae 13.0, Columbidae 2.8, Rosaceae 12.4, Asteraceae 38.9, Lamiaceae 7.2; rows with a defined identifier experience: 58,537.
- eight_W2: sources outputs/D6/api_raw_w2, outputs/D12/A_W2/api_raw, outputs/D13/W2/api_raw; scale Lamiaceae 2.1, Anatidae 9.7, Rosaceae 2.8, Nymphalidae 2.8, Columbidae 2.9, Asteraceae 7.5, Fabaceae 4.1, Sciuridae 1.7; rows with a defined identifier experience: 26,745.
- new_W: sources the set only; scale Pinaceae 4.6, Colubridae 3.4, Poaceae 10.7, Ranidae 4.3, Polyporaceae 3.5, Araneidae 7.0; rows with a defined identifier experience: 34,863.
- replication_W: sources the set only; scale Libellulidae 64.5, Laridae 29.0, Malvaceae 13.2, Pentatomidae 22.5, Apiaceae 28.7, Plantaginaceae 30.8, Tettigoniidae 13.3, Ericaceae 46.7, Ardeidae 61.2, Fagaceae 16.6, Cyperaceae 6.0, Chrysomelidae 9.1, Ranunculaceae 19.5, Vespidae 21.2, Asparagaceae 14.8, Polygonaceae 21.5, Hesperiidae 34.3, Coccinellidae 28.2, Geometridae 27.6, Caryophyllaceae 20.5, Erebidae 53.2, Syrphidae 27.4, Pieridae 28.6, Lycaenidae 29.9, Onagraceae 19.8, Formicidae 8.7, Caprifoliaceae 19.9, Acrididae 19.5, Apocynaceae 20.2, Noctuidae 35.7; rows with a defined identifier experience: 28,175.

Within-family moderation by Q (eight_W; key secondary analysis): rows with Q 45,847; b_int pooled 7.253 [1.172, 13.182]; contrast Delta(T3) - Delta(T1) 1.174 [-0.191, 2.564].

| tertile | unit | rows | slow rows | weighted share slow | weighted median Q | Delta [95%] | ER [95%] | status |
|---|---|---|---|---|---|---|---|---|
| 1 | Anatidae | 2,051 | 578 | 0.164 | 0.828 | 9.840 [6.282, 13.569] | 2.274 [1.739, 3.067] | estimable |
| 1 | Asteraceae | 1,793 | 1,250 | 0.535 | 0.390 | 0.728 [-1.180, 2.181] | 1.447 [0.585, 5.250] | estimable |
| 1 | Columbidae | 2,027 | 525 | 0.149 | 0.850 | 11.293 [7.781, 14.838] | 3.540 [2.440, 5.253] | estimable |
| 1 | Fabaceae | 2,177 | 1,612 | 0.588 | 0.389 | 0.841 [-0.907, 2.341] | 1.311 [0.783, 2.404] | estimable |
| 1 | Lamiaceae | 2,112 | 1,494 | 0.547 | 0.454 | 0.583 [-1.464, 1.664] | 1.444 [0.507, 5.692] | estimable |
| 1 | Nymphalidae | 1,923 | 694 | 0.220 | 0.807 | 2.919 [0.691, 5.430] | 1.321 [1.075, 1.941] | estimable |
| 1 | Rosaceae | 1,557 | 1,189 | 0.618 | 0.359 | 2.341 [1.062, 3.673] | 1.950 [1.311, 3.503] | estimable |
| 1 | Sciuridae | 2,220 | 1,180 | 0.362 | 0.624 | 3.335 [0.978, 5.737] | 1.303 [1.080, 1.629] | estimable |
| 1 | pooled | 15,860 | 8,522 | 0.443 | 0.409 | 3.985 [3.159, 4.823] | 1.789 [1.583, 2.082] | estimable |
| 2 | Anatidae | 2,051 | 473 | 0.130 | 0.883 | 12.905 [8.448, 17.592] | 2.787 [2.077, 3.737] | estimable |
| 2 | Asteraceae | 1,471 | 1,113 | 0.609 | 0.452 | 0.650 [-2.309, 2.859] | 1.191 [0.608, 3.246] | estimable |
| 2 | Columbidae | 2,005 | 333 | 0.091 | 0.899 | 14.767 [10.223, 19.142] | 3.888 [2.623, 5.776] | estimable |
| 2 | Fabaceae | 1,757 | 1,157 | 0.491 | 0.486 | 1.869 [0.447, 3.096] | 2.097 [1.190, 4.113] | estimable |
| 2 | Lamiaceae | 1,857 | 1,157 | 0.452 | 0.519 | 1.359 [0.065, 1.966] | 5.133 [1.000, 17.500] | estimable |
| 2 | Nymphalidae | 2,135 | 399 | 0.103 | 0.888 | 0.483 [-2.415, 2.995] | 1.078 [0.687, 1.641] | estimable |
| 2 | Rosaceae | 1,556 | 1,068 | 0.522 | 0.472 | 0.551 [-2.596, 3.217] | 1.126 [0.620, 2.372] | estimable |
| 2 | Sciuridae | 2,198 | 754 | 0.207 | 0.807 | 7.589 [4.835, 10.528] | 3.998 [2.439, 6.359] | estimable |
| 2 | pooled | 15,030 | 6,454 | 0.375 | 0.513 | 5.022 [3.852, 5.981] | 2.299 [1.884, 2.746] | estimable |
| 3 | Anatidae | 2,043 | 236 | 0.061 | 0.947 | 13.687 [8.469, 18.929] | 2.728 [1.930, 3.863] | estimable |
| 3 | Asteraceae | 1,598 | 964 | 0.432 | 0.567 | 1.264 [-1.237, 3.623] | 1.372 [0.730, 3.427] | estimable |
| 3 | Columbidae | 2,013 | 276 | 0.074 | 0.933 | 13.231 [8.337, 18.257] | 3.844 [2.525, 5.540] | estimable |
| 3 | Fabaceae | 1,914 | 1,044 | 0.375 | 0.635 | 1.695 [-0.013, 3.476] | 1.756 [0.996, 3.877] | estimable |
| 3 | Lamiaceae | 1,966 | 1,110 | 0.393 | 0.620 | 0.719 [-0.317, 1.809] | 1.954 [0.733, 8.552] | estimable |
| 3 | Nymphalidae | 1,684 | 350 | 0.116 | 0.909 | 3.549 [1.170, 6.270] | 1.461 [1.149, 2.055] | estimable |
| 3 | Rosaceae | 1,532 | 937 | 0.440 | 0.562 | 1.769 [-0.249, 3.604] | 1.559 [0.936, 3.377] | estimable |
| 3 | Sciuridae | 2,207 | 499 | 0.127 | 0.883 | 5.361 [2.661, 8.224] | 2.309 [1.581, 3.392] | estimable |
| 3 | pooled | 14,957 | 5,416 | 0.308 | 0.677 | 5.159 [4.092, 6.269] | 2.217 [1.900, 2.652] | estimable |

Per-family b_int and contrasts: outputs/confirm/eight_W/estimates.csv.

## H6 detail: Delta (BioCLIP 2.5 Huge) and the share of fast observations per family

rho = 0.574, permutation p = < 0.0001, 95% interval over families [0.270, 0.783].

| family | set | Delta [95%] | fast share |
|---|---|---|---|
| Araneidae | new_W | 2.820 [1.543, 4.032] | 0.707 |
| Colubridae | new_W | 14.510 [8.943, 16.731] | 0.807 |
| Pinaceae | new_W | 0.614 [-1.406, 2.471] | 0.454 |
| Poaceae | new_W | 0.993 [-0.604, 2.272] | 0.478 |
| Polyporaceae | new_W | 1.266 [-0.215, 2.692] | 0.413 |
| Ranidae | new_W | 4.799 [2.985, 6.972] | 0.685 |
| Acrididae | replication_W | 0.098 [-2.234, 1.881] | 0.408 |
| Apiaceae | replication_W | -0.083 [-2.240, 2.134] | 0.524 |
| Apocynaceae | replication_W | -0.575 [-3.150, 1.380] | 0.688 |
| Ardeidae | replication_W | 19.362 [7.191, 34.793] | 0.860 |
| Asparagaceae | replication_W | 0.604 [-1.518, 2.367] | 0.520 |
| Caprifoliaceae | replication_W | 0.245 [-1.748, 1.912] | 0.507 |
| Caryophyllaceae | replication_W | 1.284 [-0.249, 2.813] | 0.519 |
| Chrysomelidae | replication_W | 0.971 [-0.375, 2.377] | 0.628 |
| Coccinellidae | replication_W | 5.525 [2.722, 8.547] | 0.751 |
| Cyperaceae | replication_W | 0.417 [-2.183, 2.541] | 0.429 |
| Erebidae | replication_W | 2.137 [-0.498, 4.641] | 0.697 |
| Ericaceae | replication_W | 4.023 [1.356, 5.998] | 0.613 |
| Fagaceae | replication_W | 1.646 [-1.998, 4.466] | 0.482 |
| Formicidae | replication_W | -0.483 [-4.731, 5.943] | 0.630 |
| Geometridae | replication_W | 1.405 [0.275, 2.675] | 0.746 |
| Hesperiidae | replication_W | 2.000 [-1.792, 5.673] | 0.626 |
| Laridae | replication_W | 7.866 [3.415, 12.541] | 0.701 |
| Libellulidae | replication_W | 6.428 [3.174, 9.328] | 0.785 |
| Lycaenidae | replication_W | 4.809 [-0.064, 8.227] | 0.651 |
| Malvaceae | replication_W | 1.421 [-1.063, 3.217] | 0.453 |
| Noctuidae | replication_W | 0.800 [-0.694, 2.128] | 0.602 |
| Onagraceae | replication_W | 0.209 [-1.263, 1.824] | 0.561 |
| Pentatomidae | replication_W | 2.054 [0.367, 3.952] | 0.766 |
| Pieridae | replication_W | 3.507 [0.551, 6.428] | 0.567 |
| Plantaginaceae | replication_W | 1.725 [0.052, 3.309] | 0.510 |
| Polygonaceae | replication_W | -0.800 [-4.290, 2.557] | 0.422 |
| Ranunculaceae | replication_W | -0.017 [-2.858, 2.408] | 0.450 |
| Syrphidae | replication_W | -0.115 [-2.608, 2.420] | 0.742 |
| Tettigoniidae | replication_W | -0.494 [-3.185, 1.844] | 0.586 |
| Vespidae | replication_W | 3.813 [-0.595, 7.829] | 0.805 |

## Eight and six new families together (section 10, heterogeneity; secondary)

Relation across the 14 families between Delta (BioCLIP 2.5 Huge) and the share of fast observations: rho = 0.811, one-sided permutation p = 0.0010.

| quantity | unit | BioCLIP 2.5 Huge | BioCLIP 2 | first BioCLIP | BT-CLIP-O |
|---|---|---|---|---|---|
| Delta | animals | 7.631 [6.559, 8.285] | 9.716 [8.401, 10.454] | 11.511 [10.455, 13.339] | 5.043 [3.858, 5.686] |
| ER | animals | 2.175 [1.917, 2.312] | 1.881 [1.699, 1.966] | 1.278 [1.250, 1.336] | 1.076 [1.057, 1.087] |
| Delta | plants | 0.930 [0.445, 1.432] | 1.461 [0.865, 2.146] | 3.306 [2.128, 4.422] | 1.897 [1.187, 2.746] |
| ER | plants | 1.243 [1.109, 1.412] | 1.244 [1.137, 1.391] | 1.135 [1.085, 1.187] | 1.039 [1.024, 1.057] |
| Delta | pooled | 4.305 [3.699, 4.710] | 5.492 [4.765, 5.961] | 7.185 [6.469, 8.257] | 3.454 [2.737, 3.972] |
| ER | pooled | 1.725 [1.591, 1.819] | 1.603 [1.494, 1.673] | 1.216 [1.193, 1.257] | 1.058 [1.046, 1.067] |
| median family Delta | families | 1.882 [1.440, 2.838] | 2.997 [2.258, 4.124] | 4.632 [3.922, 7.017] | 2.097 [1.214, 3.064] |
| Delta | Polyporaceae | 1.266 [-0.282, 2.745] | 0.101 [-1.799, 1.854] | 0.179 [-3.092, 3.188] | 1.674 [-0.736, 4.080] |
| ER | Polyporaceae | 1.086 [0.982, 1.201] | 1.007 [0.887, 1.145] | 1.006 [0.900, 1.124] | 1.023 [0.990, 1.058] |

Full table: outputs/confirm/joint_14/estimates_joint.csv.

## Not-estimable listing

- eight_W: estimates not estimable: 0; pooled estimates with families left out: 6 (BT-CLIP-O Delta without regime-flagged pairs: Sciuridae; BT-CLIP-O ER without regime-flagged pairs: Sciuridae; BT-CLIP-O O without regime-flagged pairs: Sciuridae; BT-CLIP-O R without regime-flagged pairs: Sciuridae; BT-CLIP-O G_all without regime-flagged pairs: Sciuridae; BT-CLIP-O G_sup without regime-flagged pairs: Sciuridae).
- eight_W2: estimates not estimable: 0; pooled estimates with families left out: 6 (BT-CLIP-O Delta without regime-flagged pairs: Lamiaceae;Sciuridae; BT-CLIP-O ER without regime-flagged pairs: Lamiaceae;Sciuridae; BT-CLIP-O O without regime-flagged pairs: Lamiaceae;Sciuridae; BT-CLIP-O R without regime-flagged pairs: Lamiaceae;Sciuridae; BT-CLIP-O G_all without regime-flagged pairs: Lamiaceae;Sciuridae; BT-CLIP-O G_sup without regime-flagged pairs: Lamiaceae;Sciuridae).
- new_W: estimates not estimable: 0; pooled estimates with families left out: 6 (BT-CLIP-O Delta without regime-flagged pairs: Araneidae;Ranidae; BT-CLIP-O ER without regime-flagged pairs: Araneidae;Ranidae; BT-CLIP-O O without regime-flagged pairs: Araneidae;Ranidae; BT-CLIP-O R without regime-flagged pairs: Araneidae;Ranidae; BT-CLIP-O G_all without regime-flagged pairs: Araneidae;Ranidae; BT-CLIP-O G_sup without regime-flagged pairs: Araneidae;Ranidae).
- replication_W: estimates not estimable: 0; pooled estimates with families left out: 10 (BioCLIP 2.5 Huge Delta within activity S0: Geometridae; BioCLIP 2.5 Huge ER within activity S0: Geometridae; BioCLIP 2 Delta within activity S0: Geometridae; BioCLIP 2 ER within activity S0: Geometridae; first BioCLIP Delta within activity S0: Geometridae; first BioCLIP ER within activity S0: Geometridae; BT-CLIP-O Delta without regime-flagged pairs: Acrididae;Apiaceae;Ardeidae;Chrysomelidae;Geometridae;Lycaenidae;Noctuidae;Pentatomidae;Plantaginaceae;Tettigoniidae;Vespidae; BT-CLIP-O ER without regime-flagged pairs: Acrididae;Apiaceae;Ardeidae;Chrysomelidae;Geometridae;Lycaenidae;Noctuidae;Pentatomidae;Plantaginaceae;Tettigoniidae;Vespidae; BT-CLIP-O Delta within activity S0: Geometridae; BT-CLIP-O ER within activity S0: Geometridae).
- H6: families left out: none.
