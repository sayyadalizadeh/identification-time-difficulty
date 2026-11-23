# D15 - Robustness of the relation across families and shape of the gradient by group (post hoc)

Decision D15 in docs/PLAN.md (post hoc, written after the confirmatory results were seen; registered in commit c79ade7 before any part of D15 was run). Everything below is post hoc and descriptive; the registered results (docs/reports/confirmatory_results.md) stay primary. BioCLIP 2.5 Huge. Script: scripts/n20_run.py; outputs in outputs/D15/. Permutation p-values are one-sided, (1 + number of permuted statistics at or above the observed) / (1 + 10,000), generator with seed 20261121 for each test.

Families: 36 (Animalia 20, Plantae 15, Fungi 1). Family values: Delta_f and the share of fast observations from outputs/confirm/h6.json; ER_f from the per-family outputs; E_ref,f = E_slow,f / ER_f with E_slow,f = (Delta_f / 100) ER_f / (ER_f - 1).

## (a) Within kingdoms (Delta_f against the share of fast observations)

| families | n | rho | p | 95% interval (5,000 bootstrap replicates over families) | replicates with undefined rho |
|---|---|---|---|---|---|
| animals | 20 | 0.627 | 0.0018 | [0.231, 0.868] | 0 |
| plants | 15 | 0.086 | 0.3826 | [-0.572, 0.683] | 0 |

## (b) ER_f against the share of fast observations

rho = 0.490, p = 0.0018 (36 families).

## (c) Reference error and partial correlation

Spearman rho between E_ref,f and the share of fast observations: 0.018 (p for rho > 0: 0.4556; 36 families).

Partial Spearman correlation between Delta_f and the share of fast observations given E_ref,f (Pearson correlation of the residuals of the ranks): 0.574, p = 0.0002 (permutation of the share of fast observations; 36 families).

## (d) Stratified permutation within kingdom

| variant | families (animals, plants) | rho animals | rho plants | statistic (sum of n x rho) | statistic / n | p |
|---|---|---|---|---|---|---|
| Polyporaceae excluded | 20, 15 | 0.627 | 0.086 | 13.827 | 0.395 | 0.0118 |
| Polyporaceae with the plants | 20, 16 | 0.627 | 0.024 | 12.918 | 0.359 | 0.0160 |

## (e) Delta and ER of A1, A2 and A3 against A0 per group

Within each set and group: research-grade analysis rows of N18 with their weights; strata from T (A0 < 1 day, A1 1-30, A2 30-365, A3 365 days or more); reference = A0 rows of the same species; equal family weights; 2,000 observer-cluster bootstrap replicates (seed 20261121 for each set and group).

| set | group | families | stratum | rows (stratum / A0) | Delta [95%] | ER [95%] | families left out |
|---|---|---|---|---|---|---|---|
| eight_W (H1) | animals | 4 | A1 | 4,627 / 19,279 | 6.260 [5.242, 7.318] | 2.024 [1.819, 2.254] | none |
| eight_W (H1) | animals | 4 | A2 | 1,722 / 19,279 | 10.959 [8.937, 13.057] | 2.379 [2.070, 2.755] | none |
| eight_W (H1) | animals | 4 | A3 | 516 / 19,279 | 11.265 [8.055, 14.435] | 2.425 [1.938, 3.069] | none |
| eight_W (H1) | plants | 4 | A1 | 7,193 / 7,605 | 0.799 [0.213, 1.359] | 1.290 [1.072, 1.597] | none |
| eight_W (H1) | plants | 4 | A2 | 6,057 / 7,605 | 0.910 [0.367, 1.586] | 1.340 [1.125, 1.724] | none |
| eight_W (H1) | plants | 4 | A3 | 1,834 / 7,605 | 1.954 [0.983, 3.131] | 1.846 [1.392, 2.782] | none |
| new_W (H2) | animals | 3 | A1 | 4,335 / 9,593 | 3.584 [2.427, 4.802] | 1.508 [1.330, 1.696] | none |
| new_W (H2) | animals | 3 | A2 | 1,689 / 9,593 | 12.261 [9.964, 14.537] | 2.576 [2.211, 2.982] | none |
| new_W (H2) | animals | 3 | A3 | 826 / 9,593 | 14.410 [10.981, 19.173] | 5.402 [2.469, 6.701] | none |
| new_W (H2) | plants | 2 | A1 | 3,194 / 2,674 | 0.196 [-1.376, 1.620] | 1.034 [0.793, 1.318] | none |
| new_W (H2) | plants | 2 | A2 | 2,184 / 2,674 | 0.927 [-0.906, 2.431] | 1.143 [0.879, 1.428] | none |
| new_W (H2) | plants | 2 | A3 | 764 / 2,674 | 2.689 [-1.117, 5.685] | 1.401 [0.856, 1.978] | none |
| eight_W2 (H5) | animals | 4 | A1 | 2,112 / 8,091 | 6.541 [4.966, 8.141] | 2.602 [2.117, 3.179] | none |
| eight_W2 (H5) | animals | 4 | A2 | 757 / 8,091 | 11.399 [8.323, 14.496] | 3.506 [2.625, 4.751] | none |
| eight_W2 (H5) | animals | 4 | A3 | 213 / 8,091 | 22.158 [12.288, 31.665] | 6.287 [3.489, 10.935] | none |
| eight_W2 (H5) | plants | 4 | A1 | 3,957 / 3,539 | 0.709 [-0.220, 1.672] | 1.138 [0.959, 1.369] | none |
| eight_W2 (H5) | plants | 4 | A2 | 2,327 / 3,539 | 1.145 [-0.436, 2.934] | 1.260 [0.917, 1.862] | none |
| eight_W2 (H5) | plants | 4 | A3 | 587 / 3,539 | 4.993 [0.793, 9.524] | 2.185 [1.148, 4.156] | none |

## Family values used in (a) to (d)

| family | kingdom | Delta_f | ER_f | E_ref,f | share fast |
|---|---|---|---|---|---|
| Acrididae | Animalia | 0.098 | 1.061 | 0.016 | 0.408 |
| Polyporaceae | Fungi | 1.266 | 1.086 | 0.147 | 0.413 |
| Polygonaceae | Plantae | -0.800 | 0.825 | 0.046 | 0.422 |
| Cyperaceae | Plantae | 0.417 | 1.135 | 0.031 | 0.429 |
| Ranunculaceae | Plantae | -0.017 | 0.995 | 0.032 | 0.450 |
| Malvaceae | Plantae | 1.421 | 1.349 | 0.041 | 0.453 |
| Pinaceae | Plantae | 0.614 | 1.069 | 0.089 | 0.454 |
| Poaceae | Plantae | 0.993 | 1.289 | 0.034 | 0.478 |
| Fagaceae | Plantae | 1.646 | 1.285 | 0.058 | 0.482 |
| Caprifoliaceae | Plantae | 0.245 | 1.160 | 0.015 | 0.507 |
| Plantaginaceae | Plantae | 1.725 | 2.615 | 0.011 | 0.510 |
| Caryophyllaceae | Plantae | 1.284 | 2.350 | 0.010 | 0.519 |
| Asparagaceae | Plantae | 0.604 | 1.224 | 0.027 | 0.520 |
| Apiaceae | Plantae | -0.083 | 0.981 | 0.044 | 0.524 |
| Onagraceae | Plantae | 0.209 | 1.129 | 0.016 | 0.561 |
| Pieridae | Animalia | 3.507 | 1.897 | 0.039 | 0.567 |
| Tettigoniidae | Animalia | -0.494 | 0.830 | 0.029 | 0.586 |
| Noctuidae | Animalia | 0.800 | 2.053 | 0.008 | 0.602 |
| Ericaceae | Plantae | 4.023 | 6.444 | 0.007 | 0.613 |
| Hesperiidae | Animalia | 2.000 | 1.136 | 0.147 | 0.626 |
| Chrysomelidae | Animalia | 0.971 | 1.098 | 0.099 | 0.628 |
| Formicidae | Animalia | -0.483 | 0.968 | 0.149 | 0.630 |
| Lycaenidae | Animalia | 4.809 | 1.777 | 0.062 | 0.651 |
| Ranidae | Animalia | 4.799 | 1.858 | 0.056 | 0.685 |
| Apocynaceae | Plantae | -0.575 | 0.701 | 0.019 | 0.688 |
| Erebidae | Animalia | 2.137 | 2.650 | 0.013 | 0.697 |
| Laridae | Animalia | 7.866 | 1.304 | 0.258 | 0.701 |
| Araneidae | Animalia | 2.820 | 2.051 | 0.027 | 0.707 |
| Syrphidae | Animalia | -0.115 | 0.985 | 0.076 | 0.742 |
| Geometridae | Animalia | 1.405 | 8.690 | 0.002 | 0.746 |
| Coccinellidae | Animalia | 5.525 | 3.733 | 0.020 | 0.751 |
| Pentatomidae | Animalia | 2.054 | 4.650 | 0.006 | 0.766 |
| Libellulidae | Animalia | 6.428 | 7.988 | 0.009 | 0.785 |
| Vespidae | Animalia | 3.813 | 1.749 | 0.051 | 0.805 |
| Colubridae | Animalia | 14.510 | 2.396 | 0.104 | 0.807 |
| Ardeidae | Animalia | 19.362 | 1.788 | 0.246 | 0.860 |
