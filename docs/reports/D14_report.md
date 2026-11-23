# D14 - Sensitivity of the confirmatory results to the two failure deviations (post hoc)

Decision D14 in docs/PLAN.md (post hoc, written after the confirmatory results were seen; commit 2cc268b, before any part of D14 was run). The registered results (docs/reports/confirmatory_results.md) stay primary; everything below is post hoc. Script: scripts/d14_run.py; outputs in outputs/D14/. No decision rule; the results are described.

## (a) rho of H6 without the families with a failure deviation (BioCLIP 2.5 Huge)

One-sided permutation p from 10,000 permutations (a generator with seed 20261121 for every row); family values of N18 (outputs/confirm/h6.json).

| families | n | rho | p |
|---|---|---|---|
| registered | 36 | 0.574 | 0.00010 |
| without Ardeidae | 35 | 0.536 | 0.00040 |
| without Coccinellidae | 35 | 0.542 | 0.00060 |
| without both | 34 | 0.500 | 0.00190 |
| leave-one-out minimum (left out: Ardeidae) | 35 | 0.536 | 0.00040 |
| leave-one-out maximum (left out: Syrphidae) | 35 | 0.643 | 0.00010 |

Leave-one-family-out over the 36 families: rho from 0.536 to 0.643; p from 0.00010 to 0.00070.

## (b) Ardeidae: the two failed history batches

Batching in N18: the replication phase-1 sample (45,000 rows, families in the order of the frame) was sent to the API in its row order in 225 batches of 200 observations. Ardeidae, the first family, holds rows 0 to 1,499, that is batches 0 to 6 and the first 100 rows of batch 7. Batches 0 and 2 (rows 0-199 and 400-599, Ardeidae only) were not obtained after 3 retries in N18; batch 1 between them was.

Re-request (one per batch, registered API rules, raw responses in outputs/D14/api_raw/, not tracked): batch 0: ok after 1 attempt(s); 200 observations returned; batch 2: ok after 1 attempt(s); 200 observations returned. Hidden identifications: 0. Newly obtained observations with a history: 400 of 400.

Stratum counts of the newly obtained observations against those already obtained in N18:

| stratum | already obtained | newly obtained |
|---|---|---|
| A0 | 946 | 360 |
| A1 | 90 | 20 |
| A2 | 50 | 16 |
| A3 | 14 | 4 |
| excluded_T_undefined | 0 | 0 |
| failed | 0 | 0 |

Chi-square test over A0, A1, A2, A3: statistic 4.969, 3 degrees of freedom, p = 0.1741.

Phase 2 among the newly obtained observations (all of A1 to A3, A0 with fraction 0.5; seed 20261123): A0 180 of 360; A1 20 of 20; A2 16 of 16; A3 4 of 4. Photographs: 219 of 220 downloaded (24,879,969 bytes); predictions of the four models.

Ardeidae Delta and ER (weights of the full phase-1 sample of 1,500: frame size / 1,500 divided by the realized phase-2 fraction of the stratum in the original or the new part; 2,000 observer-bootstrap replicates). Rows: original 627, new 219 (research grade with T).

| model | rows | Delta [95%] | ER [95%] |
|---|---|---|---|
| BioCLIP 2.5 Huge | original rows only (N18) | 19.362 [7.532, 34.012] | 1.788 [1.227, 4.658] |
| BioCLIP 2.5 Huge | full phase-1 sample | 18.442 [6.327, 34.509] | 1.706 [1.177, 4.374] |
| BioCLIP 2 | original rows only (N18) | 12.861 [6.010, 20.730] | 1.346 [1.154, 1.827] |
| BioCLIP 2 | full phase-1 sample | 12.490 [7.045, 19.472] | 1.319 [1.172, 1.786] |
| first BioCLIP | original rows only (N18) | 14.960 [6.408, 24.143] | 1.274 [1.111, 1.501] |
| first BioCLIP | full phase-1 sample | 16.514 [9.707, 24.782] | 1.299 [1.168, 1.517] |
| BT-CLIP-O | original rows only (N18) | 8.435 [1.962, 15.793] | 1.138 [1.031, 1.286] |
| BT-CLIP-O | full phase-1 sample | 9.407 [3.452, 17.177] | 1.150 [1.053, 1.304] |

The point values on the original rows reproduce the N18 Ardeidae Delta (19.362); the intervals differ from N18 because this bootstrap resamples the Ardeidae observers only, with another generator.

Ardeidae share of fast observations: N18 0.8600; full phase-1 sample 0.8707.

H6 recomputed with the full-sample Ardeidae Delta and fast share: rho = 0.574 [0.270, 0.783] (5,000 bootstrap replicates over families), one-sided permutation p = 0.00010 (10,000 permutations, seed 20261121), 36 families. Registered: rho = 0.574, p = 0.00010.

## (c) Coccinellidae

The failed photograph (1 of 21 in stratum A3) was not requested again, as registered.

Run time of (a) and (b): 2.2 minutes.
