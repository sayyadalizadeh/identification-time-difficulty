# D19 report - analyses requested by pre-submission reviews (post hoc)

Decision: docs/PLAN.md, D19 (post hoc, 2026-11-23), registration committed before any computation. Every number in this report is post hoc; the registered confirmatory results (docs/reports/confirmatory_results.md) stay the primary results. D19 fixes no decision rule, so no item is graded. Data: the stored outputs of the confirmatory run (outputs/confirm/), the metadata snapshot of 2026-10-27 and the stored photographs of the earlier gates (development half), each file checked against its SHA-256 manifest in the run that read it; pinned models only; no download, no API request. Seed 20261124 for every resampling; 20 CPU threads per numerical step. Primary model: BioCLIP 2.5 Huge. Delta = 100 x (E_slow - E_ref), ER = E_slow / E_ref (frozen estimator src/confirm/estimators.c1, equal family weights, not-estimable rule); intervals are 95% percentile intervals of the observer-cluster bootstrap.

Scripts: scripts/d19_common.py, d19_snapshot.py, d19_part_a.py, d19_part_b.py, d19_part_c.py, d19_report.py. Tables: outputs/D19/A/, B/, C/ and snapshot/ (csv files tracked; parquet files and caches untracked).

## Controls (PASS/FAIL)

| log | control | result |
|---|---|---|
| snapshot/snapshot_log.txt | manifest observations.csv.gz | PASS (7 s) |
| snapshot/snapshot_log.txt | manifest photos.csv.gz | PASS (11 s) |
| snapshot/snapshot_log.txt | manifest taxa.csv.gz | PASS (0 s) |
| snapshot/snapshot_log.txt | 44 families found once in the eligible-species table | PASS 44 |
| snapshot/snapshot_log.txt | A10 frame rows of window W equal the stored frames (88 family x grade cells) | PASS mismatches 0 |
| A/part_a_log.txt | A0 recomputed pooled and per-family Delta and ER equal the stored estimates (4 models x 4 sets) | PASS largest absolute difference 1.78e-15 |
| A/part_a_log.txt | A4 recomputed rho over the 14 families equals the stored rho | PASS 0.810989 |
| A/part_a_log.txt | A12 provenance file SHA-256 equals the value recorded in D17 | PASS (7 s) |
| B/part_b_log.txt | eight_W: T recomputed from the stored histories equals the stored T (research rows with T) | PASS rows 48,833 |
| B/part_b_log.txt | eight_W: every observation has a first identification by another user at or before research grade | PASS rows with T_wait > T: 0 |
| B/part_b_log.txt | eight_W: main contrast reproduces the stored Delta | PASS 4.408045 vs 4.408045 |
| B/part_b_log.txt | eight_W2: T recomputed from the stored histories equals the stored T (research rows with T) | PASS rows 21,583 |
| B/part_b_log.txt | eight_W2: every observation has a first identification by another user at or before research grade | PASS rows with T_wait > T: 0 |
| B/part_b_log.txt | eight_W2: main contrast reproduces the stored Delta | PASS 4.620106 vs 4.620106 |
| B/part_b_log.txt | new_W: T recomputed from the stored histories equals the stored T (research rows with T) | PASS rows 28,403 |
| B/part_b_log.txt | new_W: every observation has a first identification by another user at or before research grade | PASS rows with T_wait > T: 0 |
| B/part_b_log.txt | new_W: main contrast reproduces the stored Delta | PASS 4.167124 vs 4.167124 |
| B/part_b_log.txt | B7 family Delta of the 36 H6 families equal h6.json | PASS |
| B/part_b_log.txt | B7 Spearman rho over the 36 families equals h6.json | PASS 0.573745 |
| C/part_c_log.txt | taxa.csv.gz equals its manifest | PASS |
| C/part_c_log.txt | predict-step rows equal the stored predictions table (order) | PASS rows 60,445 |
| C/part_c_log.txt | DINOv2-base weight file equals the pin (bytes and SHA-256) | PASS |
| C/part_c_log.txt | baseline predictions equal the stored predictions of BioCLIP 2.5 Huge | PASS agreement 1.000000 (0 rows differ) |
| C/part_c_log.txt | C3 training observers are all development half | PASS |
| C/part_c_log.txt | stored predictions reproduce the registered Delta | PASS 4.408045 vs 4.408045 |

## Part A - numbers from stored outputs (post hoc)

### A1 (post hoc). Share of slow weight dropped because a species lacks a fast or a slow phase-2 observation

Point values recomputed from the stored analysis rows with the frozen estimator (BioCLIP 2.5 Huge; the share does not depend on the model). Dropped slow weight = weight of slow rows whose species has no fast row, divided by all slow weight of the family; pooled = mean over families (the stored quantity 'dropped share of slow weight'). In a bootstrap replicate, a species whose fast rows are not drawn loses its slow weight; the stored interval of the replicates therefore lies at or above the point value.

| set | recomputed | stored value [95% interval] |
|---|---|---|
| eight families, W (H1) | 0.017 | 0.017 [0.024, 0.033] |
| eight families, W2 (H5) | 0.062 | 0.062 [0.076, 0.094] |
| six new families, W (H2) | 0.021 | 0.021 [0.021, 0.065] |
| 30 replication families, W | 0.041 | 0.041 [0.053, 0.069] |

| set | family | share | slow_species | slow_species_without_fast | fast_species_without_slow | slow_rows | slow_rows_dropped |
|---|---|---|---|---|---|---|---|
| eight_W | Anatidae | 0.000 | 64 | 0 | 7 | 1404 | 0 |
| eight_W | Asteraceae | 0.054 | 296 | 62 | 18 | 3547 | 192 |
| eight_W | Columbidae | 0.000 | 34 | 0 | 1 | 1301 | 0 |
| eight_W | Fabaceae | 0.029 | 209 | 40 | 9 | 4163 | 119 |
| eight_W | Lamiaceae | 0.008 | 109 | 17 | 1 | 3997 | 33 |
| eight_W | Nymphalidae | 0.025 | 139 | 9 | 22 | 1621 | 40 |
| eight_W | Rosaceae | 0.018 | 134 | 11 | 3 | 3377 | 60 |
| eight_W | Sciuridae | 0.000 | 38 | 0 | 0 | 2539 | 0 |
| eight_W2 | Anatidae | 0.000 | 58 | 0 | 12 | 510 | 0 |
| eight_W2 | Asteraceae | 0.130 | 251 | 85 | 22 | 1624 | 211 |
| eight_W2 | Columbidae | 0.000 | 31 | 0 | 4 | 615 | 0 |
| eight_W2 | Fabaceae | 0.096 | 195 | 54 | 10 | 1811 | 174 |
| eight_W2 | Lamiaceae | 0.050 | 96 | 24 | 2 | 1958 | 98 |
| eight_W2 | Nymphalidae | 0.180 | 111 | 17 | 29 | 898 | 162 |
| eight_W2 | Rosaceae | 0.033 | 111 | 24 | 8 | 1478 | 49 |
| eight_W2 | Sciuridae | 0.006 | 32 | 3 | 0 | 1059 | 6 |
| new_W | Araneidae | 0.000 | 46 | 0 | 0 | 2180 | 0 |
| new_W | Colubridae | 0.051 | 70 | 2 | 8 | 1884 | 97 |
| new_W | Pinaceae | 0.026 | 42 | 2 | 0 | 3309 | 87 |
| new_W | Poaceae | 0.029 | 106 | 13 | 3 | 2833 | 81 |
| new_W | Polyporaceae | 0.006 | 27 | 1 | 0 | 2326 | 13 |
| new_W | Ranidae | 0.015 | 22 | 2 | 1 | 2786 | 43 |
| replication_W | Acrididae | 0.012 | 35 | 3 | 1 | 887 | 11 |
| replication_W | Apiaceae | 0.024 | 42 | 9 | 2 | 714 | 17 |
| replication_W | Apocynaceae | 0.049 | 37 | 8 | 2 | 467 | 23 |
| replication_W | Ardeidae | 0.039 | 22 | 1 | 7 | 154 | 6 |
| replication_W | Asparagaceae | 0.028 | 54 | 9 | 7 | 718 | 20 |
| replication_W | Caprifoliaceae | 0.009 | 33 | 3 | 0 | 740 | 7 |
| replication_W | Caryophyllaceae | 0.006 | 32 | 2 | 1 | 720 | 4 |
| replication_W | Chrysomelidae | 0.027 | 28 | 1 | 1 | 557 | 15 |
| replication_W | Coccinellidae | 0.005 | 35 | 2 | 4 | 373 | 2 |
| replication_W | Cyperaceae | 0.000 | 26 | 0 | 0 | 855 | 0 |
| replication_W | Erebidae | 0.040 | 61 | 8 | 8 | 455 | 18 |
| replication_W | Ericaceae | 0.059 | 72 | 15 | 4 | 580 | 34 |
| replication_W | Fagaceae | 0.027 | 44 | 4 | 0 | 776 | 21 |
| replication_W | Formicidae | 0.007 | 56 | 2 | 5 | 553 | 4 |
| replication_W | Geometridae | 0.005 | 41 | 2 | 0 | 380 | 2 |
| replication_W | Hesperiidae | 0.079 | 29 | 4 | 3 | 560 | 44 |
| replication_W | Laridae | 0.000 | 30 | 0 | 2 | 448 | 0 |
| replication_W | Libellulidae | 0.031 | 58 | 5 | 9 | 323 | 10 |
| replication_W | Lycaenidae | 0.270 | 36 | 3 | 9 | 523 | 141 |
| replication_W | Malvaceae | 0.069 | 56 | 16 | 2 | 821 | 57 |
| replication_W | Noctuidae | 0.139 | 46 | 6 | 2 | 596 | 83 |
| replication_W | Onagraceae | 0.002 | 23 | 1 | 2 | 657 | 1 |
| replication_W | Pentatomidae | 0.020 | 24 | 2 | 0 | 351 | 7 |
| replication_W | Pieridae | 0.188 | 32 | 6 | 4 | 648 | 122 |
| replication_W | Plantaginaceae | 0.025 | 41 | 8 | 2 | 734 | 18 |
| replication_W | Polygonaceae | 0.018 | 40 | 6 | 1 | 865 | 16 |
| replication_W | Ranunculaceae | 0.040 | 55 | 11 | 0 | 824 | 33 |
| replication_W | Syrphidae | 0.000 | 26 | 0 | 1 | 387 | 0 |
| replication_W | Tettigoniidae | 0.000 | 23 | 0 | 0 | 621 | 0 |
| replication_W | Vespidae | 0.003 | 24 | 1 | 8 | 293 | 1 |

### A2 (post hoc). Pooled E_slow and E_ref beside Delta and ER, and the raw error rates

E_slow and E_ref are means over the estimable families; Delta = 100 x (E_slow - E_ref) and ER = E_slow / E_ref. Raw rates: error of all fast (T < 1 day) and all slow (T >= 1 day) research-grade rows, weighted by the phase-2 weights and pooled over the families of the set (equal-family means in the last two columns).

Why Delta and ER differ from the raw contrast: E_ref is the fast error of the same species, weighted by each species' share of the slow weight, and families count equally, whereas the raw contrast compares all fast with all slow rows, so it mixes species and families of different difficulty and different shares of slow observations.

| set | model | E_slow_pooled | E_ref_pooled | Delta | ER | raw_fast_error_weighted | raw_slow_error_weighted | raw_difference_points | raw_ratio | raw_fast_error_equal_family | raw_slow_error_equal_family |
|---|---|---|---|---|---|---|---|---|---|---|---|
| eight families, W (H1) | BioCLIP 2.5 Huge | 0.0909 | 0.0469 | 4.408 | 1.9408 | 0.0332 | 0.0529 | 1.968 | 1.5925 | 0.0343 | 0.0927 |
| eight families, W (H1) | BioCLIP 2 | 0.1320 | 0.0751 | 5.692 | 1.7579 | 0.0570 | 0.0819 | 2.496 | 1.4380 | 0.0576 | 0.1341 |
| eight families, W (H1) | first BioCLIP | 0.3617 | 0.2665 | 9.521 | 1.3573 | 0.2276 | 0.2638 | 3.619 | 1.1590 | 0.2456 | 0.3648 |
| eight families, W (H1) | BT-CLIP-O | 0.5951 | 0.5570 | 3.810 | 1.0684 | 0.5170 | 0.5405 | 2.347 | 1.0454 | 0.5378 | 0.5967 |
| eight families, W2 (H5) | BioCLIP 2.5 Huge | 0.0912 | 0.0450 | 4.620 | 2.0272 | 0.0456 | 0.0863 | 4.078 | 1.8952 | 0.0414 | 0.1048 |
| eight families, W2 (H5) | BioCLIP 2 | 0.1338 | 0.0682 | 6.556 | 1.9612 | 0.0671 | 0.1256 | 5.857 | 1.8734 | 0.0615 | 0.1484 |
| eight families, W2 (H5) | first BioCLIP | 0.4177 | 0.3026 | 11.512 | 1.3804 | 0.3080 | 0.3935 | 8.548 | 1.2775 | 0.2899 | 0.4289 |
| eight families, W2 (H5) | BT-CLIP-O | 0.6176 | 0.5802 | 3.734 | 1.0644 | 0.6306 | 0.5991 | -3.155 | 0.9500 | 0.6179 | 0.6252 |
| six new families, W (H2) | BioCLIP 2.5 Huge | 0.1177 | 0.0761 | 4.167 | 1.5477 | 0.0593 | 0.1003 | 4.093 | 1.6899 | 0.0700 | 0.1301 |
| six new families, W (H2) | BioCLIP 2 | 0.1646 | 0.1123 | 5.224 | 1.4650 | 0.0978 | 0.1440 | 4.628 | 1.4733 | 0.1041 | 0.1758 |
| six new families, W (H2) | first BioCLIP | 0.4605 | 0.4198 | 4.071 | 1.0970 | 0.3816 | 0.4339 | 5.232 | 1.1371 | 0.3741 | 0.4681 |
| six new families, W (H2) | BT-CLIP-O | 0.6708 | 0.6410 | 2.980 | 1.0465 | 0.6474 | 0.6493 | 0.184 | 1.0028 | 0.6433 | 0.6763 |
| 30 replication families, W | BioCLIP 2.5 Huge | 0.0761 | 0.0528 | 2.326 | 1.4403 | 0.0316 | 0.0732 | 4.158 | 2.3153 | 0.0341 | 0.0819 |
| 30 replication families, W | BioCLIP 2 | 0.1016 | 0.0747 | 2.689 | 1.3598 | 0.0513 | 0.0992 | 4.780 | 1.9310 | 0.0539 | 0.1085 |
| 30 replication families, W | first BioCLIP | 0.3203 | 0.2687 | 5.160 | 1.1920 | 0.2302 | 0.3081 | 7.796 | 1.3387 | 0.2392 | 0.3299 |
| 30 replication families, W | BT-CLIP-O | 0.5153 | 0.4956 | 1.971 | 1.0398 | 0.5069 | 0.5263 | 1.940 | 1.0383 | 0.4742 | 0.5200 |

### A3 (post hoc). Tipping points and the lower bounds of the table of H1 to H6

The tipping points of the run (analysis.json) are computed from the one-sided 95% lower bound (5th percentile) of Delta in the 2,000-replicate bootstrap of the analyse step: tipping point to 0 = lower bound / 100, to 1.0 = (lower bound - 1.0) / 100 (src/confirm/analysis.py, lines 141 to 144). The lower bounds of the hypothesis table (H1, H2, H5) come from the separate 5,000-replicate bootstrap; the tipping points that these bounds imply are given beside them. The manuscript itself was not read: the table of H1 to H6 is taken from docs/reports/confirmatory_results.md.

| set | hypothesis | model | tipping_point_to_0 | tipping_point_to_1 | bootstrap_of_tipping_point | Delta_lower_bound_2000 | Delta_lower_bound_5000 (Table of H1 to H6) | tipping_point_to_0_from_5000 | tipping_point_to_1_from_5000 | ER_lower_bound_5000 |
|---|---|---|---|---|---|---|---|---|---|---|
| eight families, W (H1) | H1 | BioCLIP 2.5 Huge | 0.0399 | 0.0299 | 2000 replicates | 3.9854 | 3.9759 | 0.0398 | 0.0298 | 1.8266 |
| eight families, W (H1) | H1 | BioCLIP 2 | 0.0516 | 0.0416 | 2000 replicates | 5.1617 | - | - | - | - |
| eight families, W (H1) | H1 | first BioCLIP | 0.0862 | 0.0762 | 2000 replicates | 8.6158 | - | - | - | - |
| eight families, W (H1) | H1 | BT-CLIP-O | 0.0331 | 0.0231 | 2000 replicates | 3.3052 | - | - | - | - |
| eight families, W2 (H5) | H5 | BioCLIP 2.5 Huge | 0.0383 | 0.0283 | 2000 replicates | 3.8264 | 3.8507 | 0.0385 | 0.0285 | 1.7992 |
| eight families, W2 (H5) | H5 | BioCLIP 2 | 0.0564 | 0.0464 | 2000 replicates | 5.6373 | - | - | - | - |
| eight families, W2 (H5) | H5 | first BioCLIP | 0.1010 | 0.0910 | 2000 replicates | 10.1033 | - | - | - | - |
| eight families, W2 (H5) | H5 | BT-CLIP-O | 0.0275 | 0.0175 | 2000 replicates | 2.7455 | - | - | - | - |
| six new families, W (H2) | H2 | BioCLIP 2.5 Huge | 0.0317 | 0.0217 | 2000 replicates | 3.1731 | 3.1293 | 0.0313 | 0.0213 | 1.3772 |
| six new families, W (H2) | H2 | BioCLIP 2 | 0.0394 | 0.0294 | 2000 replicates | 3.9394 | - | - | - | - |
| six new families, W (H2) | H2 | first BioCLIP | 0.0305 | 0.0205 | 2000 replicates | 3.0528 | - | - | - | - |
| six new families, W (H2) | H2 | BT-CLIP-O | 0.0176 | 0.0076 | 2000 replicates | 1.7601 | - | - | - | - |

### A4 (post hoc). Spearman correlation over the 14 families of H1 and H2

| rho | families | permutations | P-value (stored) | sidedness | two-sided P (D19, seed 20261124) |
|---|---|---|---|---|---|
| 0.8110 | 14 | 10000 | 0.00100 | one-sided, alternative rho > 0: p = (1 + number of permuted rho >= observed) / (1 + n_perm) | 0.00100 |

Source: outputs/confirm/joint_14/joint.json (relation_across_families; BioCLIP 2.5 Huge Delta of the joint analysis of eight_W and new_W against the fast share of each family). The smallest attainable P with 10,000 permutations is 1/10,001 = 0.0001. Code:

```
src/confirm/estimators.py:274: def spearman_permutation(x, y, n_perm, rng):
src/confirm/estimators.py:275:     """Spearman rho and the one-sided permutation p-value of rho > 0: (1 + number of permuted rho >= observed) /
src/confirm/estimators.py:276:     (1 + n_perm)."""
src/confirm/estimators.py:277:     x, y = np.asarray(x, float), np.asarray(y, float)
src/confirm/estimators.py:278:     ok = np.isfinite(x) & np.isfinite(y)
src/confirm/estimators.py:279:     x, y = x[ok], y[ok]
src/confirm/estimators.py:280:     rho = spearman(x, y)
src/confirm/estimators.py:281:     perm = np.array([spearman(x, rng.permutation(y)) for _ in range(n_perm)])
src/confirm/estimators.py:282:     return rho, float((1 + (perm >= rho - 1e-12).sum()) / (1 + n_perm)), int(ok.sum())
scripts/confirm_run.py:503:     est, info = AN.analyse(dj, s["models"], [], None, int(s["replicates"]), L.rng_new(), fe=False, sensitivities=False)
scripts/confirm_run.py:504:     dl = est[(est["model"] == s["models"][0]) & (est["quantity"] == "Delta") & est["unit"].isin(fs)]
scripts/confirm_run.py:505:     rel = E.h6(dict(zip(dl["unit"], dl["value"])), fs, int(s["n_perm"]), L.rng_new())
```

### A5 (post hoc). Exact shares behind L(S*)

| set | quantity | share | percent (three decimals) | 95% interval (share) |
|---|---|---|---|---|
| eight families, W (H1) | L(S*) | 0.125430 | 12.543% | [0.119323, 0.132018] |
| eight families, W (H1) | L_upload(S*) | 0.047752 | 4.775% | [0.042804, 0.053464] |
| eight families, W (H1) | L_ident(S*) | 0.077677 | 7.768% | [0.073986, 0.081313] |
| eight families, W2 (H5) | L(S*) | 0.100383 | 10.038% | [0.093524, 0.107789] |
| eight families, W2 (H5) | L_upload(S*) | 0.039516 | 3.952% | [0.033732, 0.045764] |
| eight families, W2 (H5) | L_ident(S*) | 0.060867 | 6.087% | [0.057232, 0.064780] |

L = L_upload + L_ident (12.543% = 4.775% + 7.768% in W; small differences come from rounding).

### A6 (post hoc). Resampling unit of the observer-cluster bootstrap

An observer is drawn once per replicate for the whole analysed set (all families and strata of one window): the multiplicity of each observer multiplies the weights of all of that observer's rows in the set. It is not resampled within each family. Each set (window) is analysed in its own call with its own bootstrap, so the draws of an observer who appears in eight_W and in eight_W2 are independent; in the joint analysis of the 14 families (analyse-joint) the rows of eight_W and new_W are pooled and each observer is drawn once over both.

```
src/confirm/estimators.py:27: def boot_matrix(observer, w, R, rng):
src/confirm/estimators.py:28:     """(R + 1) x n weights: row 0 = w; rows 1..R = w x multiplicity of the row's observer in a draw of observers
src/confirm/estimators.py:29:     with replacement (observer-cluster bootstrap with fixed weights, section 8)."""
src/confirm/estimators.py:30:     obs, oi = np.unique(np.asarray(observer), return_inverse=True)
src/confirm/estimators.py:31:     W = np.empty((R + 1, len(oi)), np.float32)
src/confirm/estimators.py:32:     W[0] = w
src/confirm/estimators.py:33:     for b in range(R):
src/confirm/estimators.py:34:         W[b + 1] = w * np.bincount(rng.integers(0, len(obs), len(obs)), minlength=len(obs))[oi]
src/confirm/estimators.py:35:     return W
src/confirm/analysis.py:75:     W = E.boot_matrix(rows["observer_id"].to_numpy(), rows["w"].to_numpy(float), R, rng)
scripts/confirm_run.py:437:         Wt = E.boot_matrix(d["observer_id"].to_numpy(), d["w"].to_numpy(float), Rp, rng)
scripts/confirm_run.py:500:     dj = pd.concat(rows, ignore_index=True)
scripts/confirm_run.py:501:     if dj["family"].nunique() != sum(r["family"].nunique() for r in rows):
scripts/confirm_run.py:502:         raise RuntimeError("a family occurs in more than one part")
scripts/confirm_run.py:503:     est, info = AN.analyse(dj, s["models"], [], None, int(s["replicates"]), L.rng_new(), fe=False, sensitivities=False)
```

| set | observers | observers with rows in more than one family |
|---|---|---|
| eight families, W (H1) | 21606 | 6888 |
| eight families, W2 (H5) | 12071 | 3252 |
| six new families, W (H2) | 20631 | 3550 |
| 30 replication families, W | 17082 | 4454 |

Observers in both eight_W and eight_W2: 4,407; in both eight_W and new_W: 5,067.

### A7 (post hoc). Failure rates by family and stratum

Histories: a failed history has no stratum (the stratum needs the history), so history failures are given by family and snapshot grade; photographs: by family and stratum. Full tables: outputs/D19/A/A7_history_failures.csv and A7_photo_failures.csv. Summary per set:

| set | history failures | largest family rate (histories) | T undefined | photograph failures | largest family x stratum rate (photographs) | family x stratum cells with a photograph failure |
|---|---|---|---|---|---|---|
| eight families, W (H1) | 4 of 96,000 (0.0000) | Asteraceae 0.0001 | 61 | 7 of 60,452 (0.00012) | Fabaceae A3 0.0028 (1 of 352) | 4 |
| eight families, W2 (H5) | 4 of 64,000 (0.0001) | Columbidae 0.0003 | 31 | 2 of 27,570 (0.00007) | Rosaceae A2 0.0019 (1 of 535) | 2 |
| six new families, W (H2) | 7 of 60,000 (0.0001) | Araneidae 0.0003 | 50 | 3 of 36,293 (0.00008) | Araneidae A3 0.0082 (1 of 122) | 3 |
| 30 replication families, W | 406 of 45,000 (0.0090) | Ardeidae 0.2667 | 48 | 3 of 31,068 (0.00010) | Coccinellidae A3 0.0476 (1 of 21) | 3 |

Family x grade cells with a history failure:

| set | family | grade | phase1 | history_failed | share |
|---|---|---|---|---|---|
| eight_W | Asteraceae | research | 6778 | 1 | 0.0001 |
| eight_W | Fabaceae | needs_id | 3501 | 1 | 0.0003 |
| eight_W | Nymphalidae | research | 10672 | 1 | 0.0001 |
| eight_W | Rosaceae | research | 6523 | 1 | 0.0002 |
| eight_W2 | Anatidae | research | 7838 | 1 | 0.0001 |
| eight_W2 | Columbidae | needs_id | 89 | 1 | 0.0112 |
| eight_W2 | Columbidae | research | 7911 | 1 | 0.0001 |
| eight_W2 | Sciuridae | research | 7580 | 1 | 0.0001 |
| new_W | Araneidae | research | 7453 | 3 | 0.0004 |
| new_W | Pinaceae | needs_id | 3928 | 1 | 0.0003 |
| new_W | Polyporaceae | needs_id | 6031 | 1 | 0.0002 |
| new_W | Polyporaceae | research | 3969 | 1 | 0.0003 |
| new_W | Ranidae | needs_id | 1144 | 1 | 0.0009 |
| replication_W | Apocynaceae | research | 1500 | 1 | 0.0007 |
| replication_W | Ardeidae | research | 1500 | 400 | 0.2667 |
| replication_W | Caryophyllaceae | research | 1500 | 1 | 0.0007 |
| replication_W | Formicidae | research | 1500 | 1 | 0.0007 |
| replication_W | Noctuidae | research | 1500 | 1 | 0.0007 |
| replication_W | Pentatomidae | research | 1500 | 1 | 0.0007 |
| replication_W | Pieridae | research | 1500 | 1 | 0.0007 |

Family x stratum cells with a photograph failure:

| set | family | stratum | selected | ok | failed | share |
|---|---|---|---|---|---|---|
| eight_W | Anatidae | A0 | 5166 | 5165 | 1 | 0.0002 |
| eight_W | Columbidae | A0 | 5272 | 5268 | 4 | 0.0008 |
| eight_W | Fabaceae | A3 | 352 | 351 | 1 | 0.0028 |
| eight_W | Fabaceae | B1 | 1474 | 1473 | 1 | 0.0007 |
| eight_W2 | Rosaceae | A2 | 535 | 534 | 1 | 0.0019 |
| eight_W2 | Sciuridae | A0 | 1954 | 1953 | 1 | 0.0005 |
| new_W | Araneidae | A2 | 643 | 642 | 1 | 0.0016 |
| new_W | Araneidae | A3 | 122 | 121 | 1 | 0.0082 |
| new_W | Pinaceae | A0 | 1378 | 1377 | 1 | 0.0007 |
| replication_W | Chrysomelidae | A3 | 63 | 62 | 1 | 0.0159 |
| replication_W | Coccinellidae | A3 | 21 | 20 | 1 | 0.0476 |
| replication_W | Fagaceae | A0 | 362 | 361 | 1 | 0.0028 |

### A8 (post hoc). Input resolution, resize, crop and normalisation of each model (loaded configurations)

| model | image transform as loaded | logit scale |
|---|---|---|
| BT-CLIP-O | Resize(size=224, interpolation=bicubic, max_size=None, antialias=True); CenterCrop(size=(224, 224)); MaybeConvertMode(); MaybeToTensor(); Normalize(mean=(0.48145466, 0.4578275, 0.40821073), std=(0.26862954, 0.26130258, 0.27577711)) | 74.86 |
| first BioCLIP | Resize(size=224, interpolation=bicubic, max_size=None, antialias=True); CenterCrop(size=(224, 224)); MaybeConvertMode(); MaybeToTensor(); Normalize(mean=[0.48145466, 0.4578275, 0.40821073], std=[0.26862954, 0.26130258, 0.27577711]) | 100.00 |
| BioCLIP 2 | Resize(size=224, interpolation=bicubic, max_size=None, antialias=True); CenterCrop(size=(224, 224)); MaybeConvertMode(); MaybeToTensor(); Normalize(mean=[0.48145466, 0.4578275, 0.40821073], std=[0.26862954, 0.26130258, 0.27577711]) | 100.00 |
| BioCLIP 2.5 Huge | Resize(size=224, interpolation=bicubic, max_size=None, antialias=True); CenterCrop(size=(224, 224)); MaybeConvertMode(); MaybeToTensor(); Normalize(mean=[0.48145466, 0.4578275, 0.40821073], std=[0.26862954, 0.26130258, 0.27577711]) | 98.86 |
| DINOv2-base (C3) | BitImageProcessor: resize shortest edge {'shortest_edge': 256}, resample 3 (bicubic), centre crop {'height': 224, 'width': 224}, rescale 1/255, normalise mean [0.485, 0.456, 0.406] std [0.229, 0.224, 0.225] | - |

All CLIP-type models receive the photograph after EXIF orientation and conversion to RGB (src/zeroshot.open_rgb); one centred view; image encoding under float16 autocast.

### A9 (post hoc). Per family and set: label space, species retained, fast, slow and reference errors, Delta and ER

Label-space size = eligible species of the family; species retained = species with at least one fast and one slow row (they define E_slow and E_ref); fast error = weighted error of all fast rows of the family; E_slow, E_ref as in A2. Delta and ER with the stored 95% intervals (2,000 replicates). Families covered: the three BioCLIP models have predictions for every family of every set; BT-CLIP-O also has predictions for every family, and the registered plan lists Sciuridae (Mammalia) and Ranidae (Amphibia) as outside its training data (sensitivity 'without Sciuridae' in the W sets of the eight families and 'without Ranidae' in new_W).

eight families, W (H1):

| family | model | label_space_species | species_retained | fast_rows | slow_rows | fast error | E_slow | E_ref | Delta [95%] | ER [95%] |
|---|---|---|---|---|---|---|---|---|---|---|
| Anatidae | BioCLIP 2.5 Huge | 71 | 64 | 5161 | 1404 | 0.0634 | 0.1902 | 0.0763 | 11.39 [8.90, 13.81] | 2.492 [2.113, 2.926] |
| Asteraceae | BioCLIP 2.5 Huge | 370 | 234 | 1613 | 3547 | 0.0223 | 0.0373 | 0.0305 | 0.68 [-0.39, 1.76] | 1.223 [0.899, 1.840] |
| Columbidae | BioCLIP 2.5 Huge | 35 | 34 | 5266 | 1301 | 0.0425 | 0.1714 | 0.0481 | 12.33 [10.26, 14.59] | 3.564 [2.914, 4.413] |
| Fabaceae | BioCLIP 2.5 Huge | 241 | 169 | 2161 | 4163 | 0.0268 | 0.0354 | 0.0228 | 1.25 [0.41, 2.10] | 1.549 [1.137, 2.216] |
| Lamiaceae | BioCLIP 2.5 Huge | 113 | 92 | 2263 | 3997 | 0.0075 | 0.0182 | 0.0100 | 0.81 [0.20, 1.40] | 1.811 [1.151, 3.451] |
| Nymphalidae | BioCLIP 2.5 Huge | 169 | 130 | 4523 | 1621 | 0.0347 | 0.1012 | 0.0762 | 2.50 [1.01, 3.97] | 1.328 [1.117, 1.587] |
| Rosaceae | BioCLIP 2.5 Huge | 141 | 123 | 1568 | 3377 | 0.0402 | 0.0558 | 0.0435 | 1.23 [0.25, 2.40] | 1.283 [1.052, 1.741] |
| Sciuridae | BioCLIP 2.5 Huge | 38 | 38 | 4329 | 2539 | 0.0372 | 0.1182 | 0.0674 | 5.07 [3.53, 6.55] | 1.753 [1.470, 2.150] |
| Anatidae | BioCLIP 2 | 71 | 64 | 5161 | 1404 | 0.1157 | 0.2742 | 0.1445 | 12.97 [10.24, 15.66] | 1.897 [1.694, 2.142] |
| Asteraceae | BioCLIP 2 | 370 | 234 | 1613 | 3547 | 0.0391 | 0.0623 | 0.0463 | 1.59 [0.23, 3.02] | 1.344 [1.041, 1.846] |
| Columbidae | BioCLIP 2 | 35 | 34 | 5266 | 1301 | 0.0663 | 0.2314 | 0.0724 | 15.89 [13.52, 18.38] | 3.195 [2.725, 3.730] |
| Fabaceae | BioCLIP 2 | 241 | 169 | 2161 | 4163 | 0.0583 | 0.0633 | 0.0496 | 1.37 [0.33, 2.32] | 1.277 [1.061, 1.541] |
| Lamiaceae | BioCLIP 2 | 113 | 92 | 2263 | 3997 | 0.0150 | 0.0288 | 0.0175 | 1.12 [0.18, 1.87] | 1.642 [1.081, 2.594] |
| Nymphalidae | BioCLIP 2 | 169 | 130 | 4523 | 1621 | 0.0590 | 0.1626 | 0.1254 | 3.72 [1.94, 5.21] | 1.296 [1.141, 1.446] |
| Rosaceae | BioCLIP 2 | 141 | 123 | 1568 | 3377 | 0.0434 | 0.0727 | 0.0499 | 2.28 [1.00, 3.83] | 1.457 [1.181, 2.007] |
| Sciuridae | BioCLIP 2 | 38 | 38 | 4329 | 2539 | 0.0642 | 0.1611 | 0.0952 | 6.59 [4.85, 8.42] | 1.692 [1.473, 1.988] |
| Anatidae | first BioCLIP | 71 | 64 | 5161 | 1404 | 0.3658 | 0.5954 | 0.4147 | 18.07 [14.77, 21.31] | 1.436 [1.347, 1.529] |
| Asteraceae | first BioCLIP | 370 | 234 | 1613 | 3547 | 0.1990 | 0.2355 | 0.2104 | 2.51 [-0.07, 5.61] | 1.119 [0.997, 1.297] |
| Columbidae | first BioCLIP | 35 | 34 | 5266 | 1301 | 0.3747 | 0.6134 | 0.3945 | 21.89 [18.26, 25.04] | 1.555 [1.447, 1.656] |
| Fabaceae | first BioCLIP | 241 | 169 | 2161 | 4163 | 0.2027 | 0.2396 | 0.1956 | 4.40 [2.10, 6.84] | 1.225 [1.100, 1.391] |
| Lamiaceae | first BioCLIP | 113 | 92 | 2263 | 3997 | 0.0950 | 0.1440 | 0.0954 | 4.86 [2.95, 6.54] | 1.510 [1.279, 1.783] |
| Nymphalidae | first BioCLIP | 169 | 130 | 4523 | 1621 | 0.1924 | 0.3276 | 0.2409 | 8.67 [5.56, 12.10] | 1.360 [1.213, 1.560] |
| Rosaceae | first BioCLIP | 141 | 123 | 1568 | 3377 | 0.2334 | 0.2746 | 0.2397 | 3.49 [0.42, 5.91] | 1.146 [1.017, 1.270] |
| Sciuridae | first BioCLIP | 38 | 38 | 4329 | 2539 | 0.3017 | 0.4632 | 0.3405 | 12.27 [9.61, 14.73] | 1.360 [1.271, 1.454] |
| Anatidae | BT-CLIP-O | 71 | 64 | 5161 | 1404 | 0.6175 | 0.6923 | 0.6071 | 8.52 [5.94, 11.05] | 1.140 [1.096, 1.186] |
| Asteraceae | BT-CLIP-O | 370 | 234 | 1613 | 3547 | 0.4879 | 0.5523 | 0.5350 | 1.73 [-0.05, 4.10] | 1.032 [0.999, 1.079] |
| Columbidae | BT-CLIP-O | 35 | 34 | 5266 | 1301 | 0.4746 | 0.6318 | 0.5194 | 11.24 [9.06, 13.98] | 1.216 [1.169, 1.279] |
| Fabaceae | BT-CLIP-O | 241 | 169 | 2161 | 4163 | 0.5234 | 0.5279 | 0.5225 | 0.55 [-0.86, 2.04] | 1.010 [0.984, 1.040] |
| Lamiaceae | BT-CLIP-O | 113 | 92 | 2263 | 3997 | 0.3031 | 0.3749 | 0.3460 | 2.89 [1.35, 4.34] | 1.084 [1.038, 1.130] |
| Nymphalidae | BT-CLIP-O | 169 | 130 | 4523 | 1621 | 0.5096 | 0.5180 | 0.4869 | 3.11 [0.92, 5.29] | 1.064 [1.019, 1.112] |
| Rosaceae | BT-CLIP-O | 141 | 123 | 1568 | 3377 | 0.4688 | 0.5315 | 0.5069 | 2.47 [0.51, 4.88] | 1.049 [1.010, 1.101] |
| Sciuridae | BT-CLIP-O | 38 | 38 | 4329 | 2539 | 0.9178 | 0.9319 | 0.9321 | -0.03 [-1.39, 1.49] | 1.000 [0.985, 1.016] |

eight families, W2 (H5):

| family | model | label_space_species | species_retained | fast_rows | slow_rows | fast error | E_slow | E_ref | Delta [95%] | ER [95%] |
|---|---|---|---|---|---|---|---|---|---|---|
| Anatidae | BioCLIP 2.5 Huge | 71 | 58 | 2197 | 510 | 0.0578 | 0.1549 | 0.0648 | 9.01 [5.63, 12.43] | 2.389 [1.776, 3.228] |
| Asteraceae | BioCLIP 2.5 Huge | 370 | 166 | 819 | 1624 | 0.0317 | 0.0495 | 0.0277 | 2.18 [0.19, 3.70] | 1.786 [1.053, 2.938] |
| Columbidae | BioCLIP 2.5 Huge | 35 | 31 | 2187 | 615 | 0.0380 | 0.1447 | 0.0398 | 10.49 [7.01, 14.09] | 3.636 [2.613, 5.120] |
| Fabaceae | BioCLIP 2.5 Huge | 241 | 141 | 776 | 1811 | 0.0451 | 0.0538 | 0.0546 | -0.08 [-2.73, 2.29] | 0.985 [0.648, 1.671] |
| Lamiaceae | BioCLIP 2.5 Huge | 113 | 72 | 1278 | 1958 | 0.0180 | 0.0371 | 0.0206 | 1.65 [0.28, 2.88] | 1.802 [1.108, 3.275] |
| Nymphalidae | BioCLIP 2.5 Huge | 169 | 94 | 1755 | 898 | 0.0308 | 0.0625 | 0.0241 | 3.84 [1.89, 6.02] | 2.590 [1.582, 5.097] |
| Rosaceae | BioCLIP 2.5 Huge | 141 | 87 | 666 | 1478 | 0.0766 | 0.0959 | 0.0883 | 0.75 [-1.58, 3.00] | 1.085 [0.854, 1.397] |
| Sciuridae | BioCLIP 2.5 Huge | 38 | 29 | 1952 | 1059 | 0.0333 | 0.1311 | 0.0398 | 9.12 [6.44, 11.70] | 3.289 [2.200, 5.143] |
| Anatidae | BioCLIP 2 | 71 | 58 | 2197 | 510 | 0.0833 | 0.2059 | 0.1058 | 10.01 [6.09, 14.00] | 1.946 [1.529, 2.572] |
| Asteraceae | BioCLIP 2 | 370 | 166 | 819 | 1624 | 0.0464 | 0.0764 | 0.0452 | 3.12 [0.88, 5.31] | 1.690 [1.142, 2.775] |
| Columbidae | BioCLIP 2 | 35 | 31 | 2187 | 615 | 0.0576 | 0.2260 | 0.0608 | 16.52 [12.16, 21.44] | 3.719 [2.860, 4.809] |
| Fabaceae | BioCLIP 2 | 241 | 141 | 776 | 1811 | 0.0747 | 0.0965 | 0.0664 | 3.01 [-0.16, 5.64] | 1.453 [0.980, 2.151] |
| Lamiaceae | BioCLIP 2 | 113 | 72 | 1278 | 1958 | 0.0282 | 0.0554 | 0.0292 | 2.62 [1.12, 3.97] | 1.898 [1.323, 3.290] |
| Nymphalidae | BioCLIP 2 | 169 | 94 | 1755 | 898 | 0.0416 | 0.0883 | 0.0505 | 3.78 [1.25, 6.70] | 1.749 [1.186, 3.302] |
| Rosaceae | BioCLIP 2 | 141 | 87 | 666 | 1478 | 0.0961 | 0.1260 | 0.1129 | 1.30 [-1.37, 4.08] | 1.116 [0.898, 1.457] |
| Sciuridae | BioCLIP 2 | 38 | 29 | 1952 | 1059 | 0.0640 | 0.1956 | 0.0749 | 12.08 [8.05, 15.76] | 2.613 [1.875, 3.651] |
| Anatidae | first BioCLIP | 71 | 58 | 2197 | 510 | 0.3405 | 0.5863 | 0.3873 | 19.90 [14.37, 25.64] | 1.514 [1.352, 1.705] |
| Asteraceae | first BioCLIP | 370 | 166 | 819 | 1624 | 0.2698 | 0.3178 | 0.2924 | 2.53 [-2.05, 6.87] | 1.087 [0.936, 1.274] |
| Columbidae | first BioCLIP | 35 | 31 | 2187 | 615 | 0.3525 | 0.6016 | 0.3701 | 23.16 [18.57, 27.77] | 1.626 [1.486, 1.784] |
| Fabaceae | first BioCLIP | 241 | 141 | 776 | 1811 | 0.2861 | 0.3384 | 0.2408 | 9.76 [4.99, 14.20] | 1.405 [1.182, 1.699] |
| Lamiaceae | first BioCLIP | 113 | 72 | 1278 | 1958 | 0.1510 | 0.2446 | 0.1658 | 7.88 [4.83, 11.07] | 1.476 [1.266, 1.762] |
| Nymphalidae | first BioCLIP | 169 | 94 | 1755 | 898 | 0.2165 | 0.3397 | 0.2051 | 13.45 [8.49, 18.13] | 1.656 [1.372, 2.019] |
| Rosaceae | first BioCLIP | 141 | 87 | 666 | 1478 | 0.3829 | 0.4024 | 0.4019 | 0.05 [-5.21, 4.83] | 1.001 [0.880, 1.133] |
| Sciuridae | first BioCLIP | 38 | 29 | 1952 | 1059 | 0.3202 | 0.5109 | 0.3574 | 15.36 [10.22, 20.10] | 1.430 [1.267, 1.614] |
| Anatidae | BT-CLIP-O | 71 | 58 | 2197 | 510 | 0.6868 | 0.6843 | 0.5874 | 9.69 [5.82, 13.78] | 1.165 [1.095, 1.244] |
| Asteraceae | BT-CLIP-O | 370 | 166 | 819 | 1624 | 0.6178 | 0.6001 | 0.5589 | 4.12 [0.61, 7.39] | 1.074 [1.010, 1.138] |
| Columbidae | BT-CLIP-O | 35 | 31 | 2187 | 615 | 0.4874 | 0.6325 | 0.5192 | 11.33 [7.23, 15.48] | 1.218 [1.129, 1.321] |
| Fabaceae | BT-CLIP-O | 241 | 141 | 776 | 1811 | 0.4807 | 0.4722 | 0.4577 | 1.45 [-1.95, 4.52] | 1.032 [0.959, 1.108] |
| Lamiaceae | BT-CLIP-O | 113 | 72 | 1278 | 1958 | 0.6886 | 0.6543 | 0.6385 | 1.58 [-0.52, 3.84] | 1.025 [0.992, 1.061] |
| Nymphalidae | BT-CLIP-O | 169 | 94 | 1755 | 898 | 0.4969 | 0.3682 | 0.3243 | 4.39 [1.33, 7.57] | 1.135 [1.038, 1.253] |
| Rosaceae | BT-CLIP-O | 141 | 87 | 666 | 1478 | 0.5796 | 0.6200 | 0.6270 | -0.69 [-3.18, 1.59] | 0.989 [0.950, 1.026] |
| Sciuridae | BT-CLIP-O | 38 | 29 | 1952 | 1059 | 0.9057 | 0.9088 | 0.9289 | -2.01 [-5.58, 1.01] | 0.978 [0.940, 1.011] |

six new families, W (H2):

| family | model | label_space_species | species_retained | fast_rows | slow_rows | fast error | E_slow | E_ref | Delta [95%] | ER [95%] |
|---|---|---|---|---|---|---|---|---|---|---|
| Araneidae | BioCLIP 2.5 Huge | 47 | 46 | 2631 | 2180 | 0.0217 | 0.0550 | 0.0268 | 2.82 [1.54, 4.03] | 2.051 [1.479, 2.906] |
| Colubridae | BioCLIP 2.5 Huge | 79 | 68 | 3935 | 1884 | 0.1217 | 0.2490 | 0.1039 | 14.51 [8.94, 16.73] | 2.396 [1.631, 2.714] |
| Pinaceae | BioCLIP 2.5 Huge | 42 | 40 | 1377 | 3309 | 0.0799 | 0.0947 | 0.0885 | 0.61 [-1.41, 2.47] | 1.069 [0.862, 1.331] |
| Poaceae | BioCLIP 2.5 Huge | 112 | 93 | 1297 | 2833 | 0.0339 | 0.0443 | 0.0344 | 0.99 [-0.60, 2.27] | 1.289 [0.863, 1.925] |
| Polyporaceae | BioCLIP 2.5 Huge | 27 | 26 | 818 | 2326 | 0.1088 | 0.1595 | 0.1469 | 1.27 [-0.21, 2.69] | 1.086 [0.987, 1.200] |
| Ranidae | BioCLIP 2.5 Huge | 23 | 20 | 3027 | 2786 | 0.0542 | 0.1039 | 0.0559 | 4.80 [2.99, 6.97] | 1.858 [1.518, 2.326] |
| Araneidae | BioCLIP 2 | 47 | 46 | 2631 | 2180 | 0.0509 | 0.1193 | 0.0692 | 5.01 [3.01, 6.79] | 1.724 [1.375, 2.165] |
| Colubridae | BioCLIP 2 | 79 | 68 | 3935 | 1884 | 0.1964 | 0.3386 | 0.1690 | 16.95 [10.04, 19.41] | 2.003 [1.440, 2.207] |
| Pinaceae | BioCLIP 2 | 42 | 40 | 1377 | 3309 | 0.1227 | 0.1428 | 0.1372 | 0.56 [-1.66, 2.88] | 1.041 [0.892, 1.243] |
| Poaceae | BioCLIP 2 | 112 | 93 | 1297 | 2833 | 0.0586 | 0.0774 | 0.0590 | 1.84 [-0.15, 3.60] | 1.311 [0.979, 1.768] |
| Polyporaceae | BioCLIP 2 | 27 | 26 | 818 | 2326 | 0.1064 | 0.1444 | 0.1434 | 0.10 [-1.78, 1.80] | 1.007 [0.884, 1.141] |
| Ranidae | BioCLIP 2 | 23 | 20 | 3027 | 2786 | 0.0895 | 0.1651 | 0.0963 | 6.89 [4.83, 9.65] | 1.715 [1.478, 2.011] |
| Araneidae | first BioCLIP | 47 | 46 | 2631 | 2180 | 0.3048 | 0.4922 | 0.4004 | 9.18 [5.98, 12.27] | 1.229 [1.142, 1.318] |
| Colubridae | first BioCLIP | 79 | 68 | 3935 | 1884 | 0.5377 | 0.7051 | 0.6731 | 3.20 [0.79, 11.68] | 1.047 [1.012, 1.207] |
| Pinaceae | first BioCLIP | 42 | 40 | 1377 | 3309 | 0.4154 | 0.4469 | 0.4283 | 1.87 [-1.74, 5.30] | 1.044 [0.962, 1.129] |
| Poaceae | first BioCLIP | 112 | 93 | 1297 | 2833 | 0.2984 | 0.3285 | 0.3015 | 2.70 [-0.78, 5.85] | 1.090 [0.975, 1.211] |
| Polyporaceae | first BioCLIP | 27 | 26 | 818 | 2326 | 0.2604 | 0.2840 | 0.2823 | 0.18 [-3.17, 3.23] | 1.006 [0.897, 1.125] |
| Ranidae | first BioCLIP | 23 | 20 | 3027 | 2786 | 0.4278 | 0.5060 | 0.4330 | 7.30 [4.11, 11.00] | 1.169 [1.099, 1.244] |
| Araneidae | BT-CLIP-O | 47 | 46 | 2631 | 2180 | 0.6591 | 0.7495 | 0.7442 | 0.54 [-0.82, 1.66] | 1.007 [0.989, 1.023] |
| Colubridae | BT-CLIP-O | 79 | 68 | 3935 | 1884 | 0.4900 | 0.4678 | 0.3506 | 11.72 [5.25, 13.89] | 1.334 [1.112, 1.407] |
| Pinaceae | BT-CLIP-O | 42 | 40 | 1377 | 3309 | 0.5185 | 0.5611 | 0.5321 | 2.90 [0.45, 5.46] | 1.055 [1.008, 1.108] |
| Poaceae | BT-CLIP-O | 112 | 93 | 1297 | 2833 | 0.5204 | 0.5156 | 0.5071 | 0.85 [-1.28, 2.80] | 1.017 [0.976, 1.057] |
| Polyporaceae | BT-CLIP-O | 27 | 26 | 818 | 2326 | 0.6846 | 0.7488 | 0.7321 | 1.67 [-0.70, 4.17] | 1.023 [0.990, 1.058] |
| Ranidae | BT-CLIP-O | 23 | 20 | 3027 | 2786 | 0.9874 | 0.9818 | 0.9799 | 0.19 [-0.53, 0.83] | 1.002 [0.995, 1.009] |

30 replication families, W:

| family | model | label_space_species | species_retained | fast_rows | slow_rows | fast error | E_slow | E_ref | Delta [95%] | ER [95%] |
|---|---|---|---|---|---|---|---|---|---|---|
| Acrididae | BioCLIP 2.5 Huge | 37 | 32 | 306 | 887 | 0.0163 | 0.0171 | 0.0161 | 0.10 [-2.23, 1.88] | 1.061 [0.367, 8.647] |
| Apiaceae | BioCLIP 2.5 Huge | 55 | 33 | 392 | 714 | 0.0434 | 0.0430 | 0.0439 | -0.08 [-2.24, 2.13] | 0.981 [0.598, 1.772] |
| Apocynaceae | BioCLIP 2.5 Huge | 41 | 29 | 516 | 467 | 0.0174 | 0.0135 | 0.0193 | -0.58 [-3.15, 1.38] | 0.701 [0.152, 3.292] |
| Ardeidae | BioCLIP 2.5 Huge | 35 | 21 | 473 | 154 | 0.0719 | 0.4392 | 0.2456 | 19.36 [7.19, 34.79] | 1.788 [1.218, 4.763] |
| Asparagaceae | BioCLIP 2.5 Huge | 85 | 45 | 390 | 718 | 0.0205 | 0.0330 | 0.0269 | 0.60 [-1.52, 2.37] | 1.224 [0.582, 4.483] |
| Caprifoliaceae | BioCLIP 2.5 Huge | 35 | 30 | 380 | 740 | 0.0132 | 0.0177 | 0.0153 | 0.25 [-1.75, 1.91] | 1.160 [0.409, 5.921] |
| Caryophyllaceae | BioCLIP 2.5 Huge | 36 | 30 | 389 | 720 | 0.0103 | 0.0223 | 0.0095 | 1.28 [-0.25, 2.81] | 2.350 [0.861, 21.350] |
| Chrysomelidae | BioCLIP 2.5 Huge | 30 | 27 | 470 | 557 | 0.0468 | 0.1089 | 0.0991 | 0.97 [-0.37, 2.38] | 1.098 [0.962, 1.267] |
| Coccinellidae | BioCLIP 2.5 Huge | 43 | 33 | 562 | 373 | 0.0267 | 0.0755 | 0.0202 | 5.53 [2.72, 8.55] | 3.733 [1.988, 7.889] |
| Cyperaceae | BioCLIP 2.5 Huge | 26 | 26 | 322 | 855 | 0.0342 | 0.0351 | 0.0309 | 0.42 [-2.18, 2.54] | 1.135 [0.574, 2.629] |
| Erebidae | BioCLIP 2.5 Huge | 82 | 53 | 522 | 455 | 0.0096 | 0.0343 | 0.0130 | 2.14 [-0.50, 4.64] | 2.650 [0.847, 34.861] |
| Ericaceae | BioCLIP 2.5 Huge | 85 | 57 | 460 | 580 | 0.0065 | 0.0476 | 0.0074 | 4.02 [1.36, 6.00] | 6.444 [1.589, 231.894] |
| Fagaceae | BioCLIP 2.5 Huge | 44 | 40 | 361 | 776 | 0.0720 | 0.0742 | 0.0577 | 1.65 [-2.00, 4.47] | 1.285 [0.758, 2.208] |
| Formicidae | BioCLIP 2.5 Huge | 61 | 54 | 472 | 553 | 0.0932 | 0.1439 | 0.1487 | -0.48 [-4.73, 5.94] | 0.968 [0.733, 1.655] |
| Geometridae | BioCLIP 2.5 Huge | 46 | 39 | 560 | 380 | 0.0036 | 0.0159 | 0.0018 | 1.40 [0.27, 2.68] | 8.690 [1.947, 84.483] |
| Hesperiidae | BioCLIP 2.5 Huge | 35 | 25 | 469 | 560 | 0.1215 | 0.1667 | 0.1467 | 2.00 [-1.79, 5.67] | 1.136 [0.897, 1.481] |
| Laridae | BioCLIP 2.5 Huge | 34 | 30 | 524 | 448 | 0.0935 | 0.3371 | 0.2584 | 7.87 [3.41, 12.54] | 1.304 [1.122, 2.215] |
| Libellulidae | BioCLIP 2.5 Huge | 77 | 53 | 588 | 323 | 0.0102 | 0.0735 | 0.0092 | 6.43 [3.17, 9.33] | 7.988 [3.062, 34.827] |
| Lycaenidae | BioCLIP 2.5 Huge | 45 | 33 | 487 | 523 | 0.0554 | 0.1099 | 0.0619 | 4.81 [-0.06, 8.23] | 1.777 [0.990, 3.032] |
| Malvaceae | BioCLIP 2.5 Huge | 65 | 40 | 340 | 821 | 0.0471 | 0.0550 | 0.0408 | 1.42 [-1.06, 3.22] | 1.349 [0.821, 2.187] |
| Noctuidae | BioCLIP 2.5 Huge | 53 | 40 | 450 | 596 | 0.0089 | 0.0156 | 0.0076 | 0.80 [-0.69, 2.13] | 2.053 [0.482, 13.706] |
| Onagraceae | BioCLIP 2.5 Huge | 29 | 22 | 420 | 657 | 0.0167 | 0.0183 | 0.0162 | 0.21 [-1.26, 1.82] | 1.129 [0.477, 3.911] |
| Pentatomidae | BioCLIP 2.5 Huge | 25 | 22 | 574 | 351 | 0.0070 | 0.0262 | 0.0056 | 2.05 [0.37, 3.95] | 4.650 [1.332, 41.982] |
| Pieridae | BioCLIP 2.5 Huge | 39 | 26 | 424 | 648 | 0.0330 | 0.0741 | 0.0391 | 3.51 [0.55, 6.43] | 1.897 [1.091, 3.885] |
| Plantaginaceae | BioCLIP 2.5 Huge | 53 | 33 | 382 | 734 | 0.0131 | 0.0279 | 0.0107 | 1.73 [0.05, 3.31] | 2.615 [1.022, 11.840] |
| Polygonaceae | BioCLIP 2.5 Huge | 41 | 34 | 316 | 865 | 0.0285 | 0.0377 | 0.0457 | -0.80 [-4.29, 2.56] | 0.825 [0.410, 2.716] |
| Ranunculaceae | BioCLIP 2.5 Huge | 71 | 44 | 337 | 824 | 0.0267 | 0.0316 | 0.0318 | -0.02 [-2.86, 2.41] | 0.995 [0.464, 3.258] |
| Syrphidae | BioCLIP 2.5 Huge | 29 | 26 | 556 | 387 | 0.0180 | 0.0749 | 0.0761 | -0.11 [-2.61, 2.42] | 0.985 [0.433, 3.533] |
| Tettigoniidae | BioCLIP 2.5 Huge | 24 | 23 | 439 | 621 | 0.0205 | 0.0242 | 0.0291 | -0.49 [-3.19, 1.84] | 0.830 [0.338, 2.607] |
| Vespidae | BioCLIP 2.5 Huge | 34 | 23 | 603 | 293 | 0.0365 | 0.0890 | 0.0509 | 3.81 [-0.59, 7.83] | 1.749 [0.913, 4.054] |
| Acrididae | BioCLIP 2 | 37 | 32 | 306 | 887 | 0.0294 | 0.0479 | 0.0271 | 2.09 [-0.82, 4.57] | 1.772 [0.837, 5.638] |
| Apiaceae | BioCLIP 2 | 55 | 33 | 392 | 714 | 0.0663 | 0.0890 | 0.0815 | 0.74 [-3.57, 4.95] | 1.091 [0.687, 1.938] |
| Apocynaceae | BioCLIP 2 | 41 | 29 | 516 | 467 | 0.0194 | 0.0383 | 0.0203 | 1.80 [-1.19, 4.02] | 1.883 [0.712, 7.640] |
| Ardeidae | BioCLIP 2 | 35 | 21 | 473 | 154 | 0.1268 | 0.5000 | 0.3714 | 12.86 [6.74, 20.61] | 1.346 [1.169, 1.791] |
| Asparagaceae | BioCLIP 2 | 85 | 45 | 390 | 718 | 0.0487 | 0.0659 | 0.0522 | 1.37 [-1.33, 4.05] | 1.262 [0.794, 2.651] |
| Caprifoliaceae | BioCLIP 2 | 35 | 30 | 380 | 740 | 0.0289 | 0.0368 | 0.0238 | 1.30 [-0.62, 3.22] | 1.546 [0.822, 3.543] |
| Caryophyllaceae | BioCLIP 2 | 36 | 30 | 389 | 720 | 0.0129 | 0.0251 | 0.0107 | 1.45 [-0.18, 3.07] | 2.352 [0.909, 18.641] |
| Chrysomelidae | BioCLIP 2 | 30 | 27 | 470 | 557 | 0.0638 | 0.1236 | 0.1209 | 0.27 [-2.01, 2.64] | 1.022 [0.845, 1.257] |
| Coccinellidae | BioCLIP 2 | 43 | 33 | 562 | 373 | 0.0445 | 0.1240 | 0.0421 | 8.19 [4.05, 12.24] | 2.945 [1.698, 5.541] |
| Cyperaceae | BioCLIP 2 | 26 | 26 | 322 | 855 | 0.0466 | 0.0491 | 0.0401 | 0.90 [-1.63, 3.45] | 1.224 [0.715, 2.418] |
| Erebidae | BioCLIP 2 | 82 | 53 | 522 | 455 | 0.0249 | 0.0572 | 0.0285 | 2.87 [-0.04, 5.91] | 2.007 [0.992, 6.486] |
| Ericaceae | BioCLIP 2 | 85 | 57 | 460 | 580 | 0.0043 | 0.0403 | 0.0072 | 3.31 [0.58, 5.04] | 5.617 [1.200, 56.000] |
| Fagaceae | BioCLIP 2 | 44 | 40 | 361 | 776 | 0.1413 | 0.1192 | 0.1434 | -2.42 [-6.60, 1.90] | 0.832 [0.619, 1.173] |
| Formicidae | BioCLIP 2 | 61 | 54 | 472 | 553 | 0.1398 | 0.1712 | 0.1686 | 0.26 [-4.86, 5.67] | 1.016 [0.760, 1.454] |
| Geometridae | BioCLIP 2 | 46 | 39 | 560 | 380 | 0.0018 | 0.0397 | 0.0022 | 3.75 [1.79, 5.70] | 18.000 [4.061, 29.844] |
| Hesperiidae | BioCLIP 2 | 35 | 25 | 469 | 560 | 0.1130 | 0.1589 | 0.1230 | 3.59 [0.57, 6.79] | 1.292 [1.041, 1.651] |
| Laridae | BioCLIP 2 | 34 | 30 | 524 | 448 | 0.1584 | 0.3147 | 0.2190 | 9.57 [-2.12, 20.78] | 1.437 [0.936, 2.848] |
| Libellulidae | BioCLIP 2 | 77 | 53 | 588 | 323 | 0.0340 | 0.1054 | 0.0293 | 7.61 [3.49, 11.47] | 3.593 [1.798, 7.042] |
| Lycaenidae | BioCLIP 2 | 45 | 33 | 487 | 523 | 0.0801 | 0.1990 | 0.1840 | 1.49 [-2.19, 6.07] | 1.081 [0.854, 2.167] |
| Malvaceae | BioCLIP 2 | 65 | 40 | 340 | 821 | 0.0618 | 0.0602 | 0.0584 | 0.18 [-2.98, 2.71] | 1.031 [0.640, 1.721] |
| Noctuidae | BioCLIP 2 | 53 | 40 | 450 | 596 | 0.0178 | 0.0253 | 0.0223 | 0.31 [-2.47, 2.64] | 1.139 [0.414, 4.469] |
| Onagraceae | BioCLIP 2 | 29 | 22 | 420 | 657 | 0.0119 | 0.0244 | 0.0115 | 1.29 [-0.13, 2.97] | 2.126 [0.931, 11.395] |
| Pentatomidae | BioCLIP 2 | 25 | 22 | 574 | 351 | 0.0157 | 0.0494 | 0.0161 | 3.34 [0.91, 6.03] | 3.077 [1.394, 9.569] |
| Pieridae | BioCLIP 2 | 39 | 26 | 424 | 648 | 0.0778 | 0.1464 | 0.0993 | 4.71 [0.28, 8.64] | 1.474 [1.021, 2.115] |
| Plantaginaceae | BioCLIP 2 | 53 | 33 | 382 | 734 | 0.0288 | 0.0545 | 0.0301 | 2.44 [-0.13, 5.04] | 1.810 [0.974, 4.180] |
| Polygonaceae | BioCLIP 2 | 41 | 34 | 316 | 865 | 0.0443 | 0.0730 | 0.0609 | 1.21 [-2.34, 5.21] | 1.199 [0.728, 2.735] |
| Ranunculaceae | BioCLIP 2 | 71 | 44 | 337 | 824 | 0.0386 | 0.0405 | 0.0437 | -0.33 [-4.05, 2.43] | 0.925 [0.440, 2.216] |
| Syrphidae | BioCLIP 2 | 29 | 26 | 556 | 387 | 0.0306 | 0.0879 | 0.0800 | 0.79 [-1.35, 3.53] | 1.099 [0.758, 3.068] |
| Tettigoniidae | BioCLIP 2 | 24 | 23 | 439 | 621 | 0.0364 | 0.0692 | 0.0458 | 2.34 [-0.79, 5.52] | 1.510 [0.873, 3.180] |
| Vespidae | BioCLIP 2 | 34 | 23 | 603 | 293 | 0.0697 | 0.1130 | 0.0790 | 3.40 [-1.57, 8.01] | 1.431 [0.850, 2.422] |
| Acrididae | first BioCLIP | 37 | 32 | 306 | 887 | 0.3529 | 0.3379 | 0.3287 | 0.92 [-5.19, 7.69] | 1.028 [0.863, 1.288] |
| Apiaceae | first BioCLIP | 55 | 33 | 392 | 714 | 0.1964 | 0.2755 | 0.2695 | 0.59 [-3.79, 4.81] | 1.022 [0.872, 1.203] |
| Apocynaceae | first BioCLIP | 41 | 29 | 516 | 467 | 0.1240 | 0.1779 | 0.1347 | 4.32 [-1.52, 9.90] | 1.321 [0.912, 2.046] |
| Ardeidae | first BioCLIP | 35 | 21 | 473 | 154 | 0.3805 | 0.6959 | 0.5463 | 14.96 [6.60, 24.41] | 1.274 [1.116, 1.509] |
| Asparagaceae | first BioCLIP | 85 | 45 | 390 | 718 | 0.2692 | 0.2994 | 0.2522 | 4.73 [-0.92, 10.36] | 1.187 [0.968, 1.479] |
| Caprifoliaceae | first BioCLIP | 35 | 30 | 380 | 740 | 0.1316 | 0.1705 | 0.1455 | 2.50 [-2.53, 7.57] | 1.172 [0.858, 1.717] |
| Caryophyllaceae | first BioCLIP | 36 | 30 | 389 | 720 | 0.0746 | 0.1201 | 0.0790 | 4.11 [0.57, 7.80] | 1.520 [1.054, 2.447] |
| Chrysomelidae | first BioCLIP | 30 | 27 | 470 | 557 | 0.1234 | 0.2269 | 0.1814 | 4.56 [0.67, 8.13] | 1.251 [1.034, 1.533] |
| Coccinellidae | first BioCLIP | 43 | 33 | 562 | 373 | 0.3043 | 0.4825 | 0.2828 | 19.97 [13.63, 26.53] | 1.706 [1.430, 2.082] |
| Cyperaceae | first BioCLIP | 26 | 26 | 322 | 855 | 0.2267 | 0.2421 | 0.2219 | 2.02 [-2.88, 7.95] | 1.091 [0.888, 1.451] |
| Erebidae | first BioCLIP | 82 | 53 | 522 | 455 | 0.1169 | 0.2906 | 0.1704 | 12.02 [5.44, 19.01] | 1.705 [1.252, 2.599] |
| Ericaceae | first BioCLIP | 85 | 57 | 460 | 580 | 0.1283 | 0.2033 | 0.1836 | 1.97 [-4.48, 8.23] | 1.107 [0.800, 1.641] |
| Fagaceae | first BioCLIP | 44 | 40 | 361 | 776 | 0.5125 | 0.4768 | 0.5037 | -2.69 [-8.90, 3.43] | 0.947 [0.835, 1.074] |
| Formicidae | first BioCLIP | 61 | 54 | 472 | 553 | 0.5148 | 0.6011 | 0.5014 | 9.97 [1.58, 16.61] | 1.199 [1.029, 1.366] |
| Geometridae | first BioCLIP | 46 | 39 | 560 | 380 | 0.0643 | 0.1190 | 0.0449 | 7.41 [3.14, 11.09] | 2.651 [1.514, 4.522] |
| Hesperiidae | first BioCLIP | 35 | 25 | 469 | 560 | 0.3006 | 0.4205 | 0.4062 | 1.43 [-4.05, 7.24] | 1.035 [0.909, 1.202] |
| Laridae | first BioCLIP | 34 | 30 | 524 | 448 | 0.4828 | 0.6741 | 0.5835 | 9.06 [3.37, 15.65] | 1.155 [1.054, 1.304] |
| Libellulidae | first BioCLIP | 77 | 53 | 588 | 323 | 0.2177 | 0.3419 | 0.1935 | 14.83 [8.45, 21.45] | 1.766 [1.372, 2.289] |
| Lycaenidae | first BioCLIP | 45 | 33 | 487 | 523 | 0.2177 | 0.4188 | 0.3679 | 5.10 [-1.43, 12.14] | 1.139 [0.961, 1.473] |
| Malvaceae | first BioCLIP | 65 | 40 | 340 | 821 | 0.2000 | 0.1898 | 0.1875 | 0.23 [-4.27, 5.49] | 1.012 [0.805, 1.380] |
| Noctuidae | first BioCLIP | 53 | 40 | 450 | 596 | 0.1689 | 0.1793 | 0.1500 | 2.93 [-1.97, 7.21] | 1.195 [0.890, 1.586] |
| Onagraceae | first BioCLIP | 29 | 22 | 420 | 657 | 0.1405 | 0.1616 | 0.1380 | 2.36 [-1.48, 7.03] | 1.171 [0.906, 1.651] |
| Pentatomidae | first BioCLIP | 25 | 22 | 574 | 351 | 0.3031 | 0.5494 | 0.3671 | 18.24 [11.42, 25.14] | 1.497 [1.281, 1.769] |
| Pieridae | first BioCLIP | 39 | 26 | 424 | 648 | 0.2665 | 0.3669 | 0.2910 | 7.59 [1.50, 13.98] | 1.261 [1.046, 1.551] |
| Plantaginaceae | first BioCLIP | 53 | 33 | 382 | 734 | 0.1099 | 0.1020 | 0.1241 | -2.21 [-7.22, 2.34] | 0.822 [0.554, 1.256] |
| Polygonaceae | first BioCLIP | 41 | 34 | 316 | 865 | 0.1962 | 0.2167 | 0.2358 | -1.90 [-7.69, 3.68] | 0.919 [0.722, 1.202] |
| Ranunculaceae | first BioCLIP | 71 | 44 | 337 | 824 | 0.1840 | 0.2048 | 0.1965 | 0.83 [-5.37, 7.34] | 1.042 [0.777, 1.509] |
| Syrphidae | first BioCLIP | 29 | 26 | 556 | 387 | 0.2230 | 0.2532 | 0.2742 | -2.10 [-8.84, 4.47] | 0.923 [0.699, 1.210] |
| Tettigoniidae | first BioCLIP | 24 | 23 | 439 | 621 | 0.2984 | 0.3800 | 0.3318 | 4.82 [-1.51, 11.09] | 1.145 [0.960, 1.385] |
| Vespidae | first BioCLIP | 34 | 23 | 603 | 293 | 0.3466 | 0.4315 | 0.3692 | 6.23 [-0.48, 13.39] | 1.169 [0.987, 1.410] |
| Acrididae | BT-CLIP-O | 37 | 32 | 306 | 887 | 0.4902 | 0.5639 | 0.5468 | 1.72 [-3.88, 7.38] | 1.031 [0.935, 1.149] |
| Apiaceae | BT-CLIP-O | 55 | 33 | 392 | 714 | 0.6429 | 0.6758 | 0.6601 | 1.56 [-2.95, 6.01] | 1.024 [0.958, 1.096] |
| Apocynaceae | BT-CLIP-O | 41 | 29 | 516 | 467 | 0.4709 | 0.3964 | 0.3989 | -0.25 [-3.98, 3.51] | 0.994 [0.903, 1.094] |
| Ardeidae | BT-CLIP-O | 35 | 21 | 473 | 154 | 0.4524 | 0.6959 | 0.6116 | 8.43 [2.03, 16.02] | 1.138 [1.033, 1.285] |
| Asparagaceae | BT-CLIP-O | 85 | 45 | 390 | 718 | 0.4205 | 0.3854 | 0.3706 | 1.47 [-2.48, 5.71] | 1.040 [0.933, 1.173] |
| Caprifoliaceae | BT-CLIP-O | 35 | 30 | 380 | 740 | 0.4711 | 0.5348 | 0.5168 | 1.80 [-2.25, 5.93] | 1.035 [0.959, 1.121] |
| Caryophyllaceae | BT-CLIP-O | 36 | 30 | 389 | 720 | 0.5604 | 0.6020 | 0.5782 | 2.38 [-0.89, 5.79] | 1.041 [0.986, 1.104] |
| Chrysomelidae | BT-CLIP-O | 30 | 27 | 470 | 557 | 0.4000 | 0.4963 | 0.4938 | 0.25 [-2.00, 2.55] | 1.005 [0.960, 1.053] |
| Coccinellidae | BT-CLIP-O | 43 | 33 | 562 | 373 | 0.2829 | 0.3989 | 0.3289 | 7.01 [3.50, 10.54] | 1.213 [1.105, 1.348] |
| Cyperaceae | BT-CLIP-O | 26 | 26 | 322 | 855 | 0.3292 | 0.3240 | 0.2940 | 3.00 [-0.12, 6.24] | 1.102 [0.996, 1.230] |
| Erebidae | BT-CLIP-O | 82 | 53 | 522 | 455 | 0.3851 | 0.3021 | 0.2473 | 5.48 [2.33, 8.87] | 1.222 [1.091, 1.408] |
| Ericaceae | BT-CLIP-O | 85 | 57 | 460 | 580 | 0.2348 | 0.3535 | 0.3171 | 3.64 [0.59, 6.96] | 1.115 [1.018, 1.264] |
| Fagaceae | BT-CLIP-O | 44 | 40 | 361 | 776 | 0.3546 | 0.3338 | 0.3394 | -0.57 [-4.53, 2.69] | 0.983 [0.875, 1.088] |
| Formicidae | BT-CLIP-O | 61 | 54 | 472 | 553 | 0.4915 | 0.5173 | 0.5178 | -0.05 [-5.10, 4.42] | 0.999 [0.906, 1.094] |
| Geometridae | BT-CLIP-O | 46 | 39 | 560 | 380 | 0.5911 | 0.5503 | 0.5183 | 3.20 [-0.21, 6.91] | 1.062 [0.996, 1.141] |
| Hesperiidae | BT-CLIP-O | 35 | 25 | 469 | 560 | 0.4861 | 0.6434 | 0.6209 | 2.25 [-1.77, 5.87] | 1.036 [0.973, 1.100] |
| Laridae | BT-CLIP-O | 34 | 30 | 524 | 448 | 0.6069 | 0.6741 | 0.5995 | 7.46 [-0.52, 14.62] | 1.124 [0.992, 1.269] |
| Libellulidae | BT-CLIP-O | 77 | 53 | 588 | 323 | 0.7857 | 0.7668 | 0.7459 | 2.09 [-2.81, 6.45] | 1.028 [0.965, 1.088] |
| Lycaenidae | BT-CLIP-O | 45 | 33 | 487 | 523 | 0.4846 | 0.6152 | 0.6090 | 0.62 [-3.24, 4.58] | 1.010 [0.946, 1.081] |
| Malvaceae | BT-CLIP-O | 65 | 40 | 340 | 821 | 0.3706 | 0.3325 | 0.3311 | 0.13 [-3.47, 3.53] | 1.004 [0.904, 1.116] |
| Noctuidae | BT-CLIP-O | 53 | 40 | 450 | 596 | 0.6400 | 0.6589 | 0.6498 | 0.90 [-3.46, 4.93] | 1.014 [0.950, 1.082] |
| Onagraceae | BT-CLIP-O | 29 | 22 | 420 | 657 | 0.2643 | 0.3171 | 0.2844 | 3.27 [-1.36, 7.75] | 1.115 [0.956, 1.307] |
| Pentatomidae | BT-CLIP-O | 25 | 22 | 574 | 351 | 0.3937 | 0.4971 | 0.5142 | -1.71 [-4.66, 1.17] | 0.967 [0.911, 1.024] |
| Pieridae | BT-CLIP-O | 39 | 26 | 424 | 648 | 0.6108 | 0.6597 | 0.6360 | 2.36 [-2.73, 7.63] | 1.037 [0.959, 1.128] |
| Plantaginaceae | BT-CLIP-O | 53 | 33 | 382 | 734 | 0.5105 | 0.6969 | 0.6984 | -0.14 [-2.88, 2.94] | 0.998 [0.960, 1.043] |
| Polygonaceae | BT-CLIP-O | 41 | 34 | 316 | 865 | 0.2690 | 0.3157 | 0.3041 | 1.15 [-1.79, 4.33] | 1.038 [0.943, 1.166] |
| Ranunculaceae | BT-CLIP-O | 71 | 44 | 337 | 824 | 0.3145 | 0.3388 | 0.3654 | -2.66 [-6.41, 0.99] | 0.927 [0.837, 1.030] |
| Syrphidae | BT-CLIP-O | 29 | 26 | 556 | 387 | 0.6978 | 0.6047 | 0.5769 | 2.77 [-0.02, 5.99] | 1.048 [1.000, 1.112] |
| Tettigoniidae | BT-CLIP-O | 24 | 23 | 439 | 621 | 0.4624 | 0.4283 | 0.4058 | 2.25 [-0.88, 5.22] | 1.056 [0.979, 1.137] |
| Vespidae | BT-CLIP-O | 34 | 23 | 603 | 293 | 0.7529 | 0.7808 | 0.7880 | -0.72 [-4.06, 2.71] | 0.991 [0.949, 1.035] |

### A10 (post hoc). Flow counts for window W per family set

From the snapshot of 2026-10-27 (observations with observed_on from 2024-07-01 to 2024-09-30 and a valid observer id). Stages are cumulative up to 'licence and size filter' (first photograph CC0, CC BY or CC BY-NC, shorter side at least 224 px, every photo id above 367,752,438); the grade columns split the rows that pass the filter. The confirmatory frames are 'research_eligible' + 'needs_id_eligible' of the locked half (eight families) and of both halves (new families); 'needs_id_eligible' does not enter the replication frame (research grade only). Per family: outputs/D19/snapshot/a10_flow.csv.

| set | half | all_in_W | with_photo | all_photo_ids_above_max_M1 | licence_and_size_filter | eligible_species_any_grade | research_eligible | research_other | needs_id_eligible | needs_id_other | casual | other_grade |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| eight | both | 2,022,073 | 2,022,073 | 2,022,072 | 1,940,759 | 1,223,505 | 1,007,014 | 279,223 | 459,928 | 113,637 | 80,957 | 0 |
| eight | locked | 1,013,342 | 1,013,342 | 1,013,342 | 966,700 | 611,366 | 503,501 | 138,512 | 228,600 | 56,264 | 39,823 | 0 |
| new | both | 485,419 | 485,419 | 485,418 | 465,396 | 274,104 | 221,852 | 58,073 | 113,135 | 58,790 | 13,546 | 0 |
| replication | both | 2,739,212 | 2,739,212 | 2,739,210 | 2,615,333 | 1,333,638 | 1,163,973 | 597,610 | 431,237 | 366,266 | 56,247 | 0 |

### A11 (post hoc). C3 coefficients b0, b3 and b_obs (BioCLIP 2.5 Huge)

| set | quantity | value [95%] |
|---|---|---|
| eight families, W (H1) | b0 | 2.074 [1.622, 2.610] |
| eight families, W (H1) | b3 | 2.251 [1.766, 2.904] |
| eight families, W (H1) | b_obs | 2.384 [1.688, 3.123] |
| eight families, W (H1) | rho | 1.086 [0.913, 1.339] |
| eight families, W2 (H5) | b0 | 4.091 [3.241, 5.087] |
| eight families, W2 (H5) | b3 | 4.731 [3.673, 5.811] |
| eight families, W2 (H5) | b_obs | 4.404 [3.076, 6.148] |
| eight families, W2 (H5) | rho | 1.156 [0.942, 1.374] |
| six new families, W (H2) | b0 | 2.936 [2.274, 3.629] |
| six new families, W (H2) | b3 | 2.709 [2.085, 3.504] |
| six new families, W (H2) | b_obs | 2.044 [0.853, 3.343] |
| six new families, W (H2) | rho | 0.923 [0.810, 1.095] |

b0: species fixed effects; b3: species x 10-degree cell fixed effects and the covariates week, width, height, n_photos, vision, ident_avail, queue_load, activity S1, activity S2, activity S3; b_obs: species and observer fixed effects; rho = b3 / b0 (2,000 replicates; slow minus fast in points).

### A12 (post hoc). Fields of the retained provenance file of TreeOfLife-200M (commit 97e2340)

File outputs/retained/tol200m_97e2340/provenance.parquet: SHA-256 equal to the value recorded in D17: yes; 233,055,986 rows in 78 row groups; key-value metadata keys: org.apache.spark.version, org.apache.spark.sql.parquet.row.metadata.

| field | type | values with a YYYY-MM-DD string in row group 1 |
|---|---|---|
| uuid | string | 0 of 2,913,938 |
| source_id | string | 0 of 2,913,938 |
| data_source | string | 0 of 2,913,938 |
| source_url | string | 589 of 2,842,961 |
| license_name | string | 0 of 2,819,728 |
| copyright_owner | string | 2,044 of 2,913,938 |
| license_link | string | 0 of 2,687,501 |
| title | string | 0 of 2,913,938 |
| bibliographicCitation | string | 9 of 72,671 |

No field has a date or time type and no field name refers to a date, so the file holds no date of the record or of the image, and no latest date per source can be given. Some free-text values (URLs, owner strings, citations) contain a date-like string; only row group 1 (2,913,938 rows; sources gbif 2,770,642, eol 71,768, bioscan 70,977, fathomnet 551) was scanned for this count.

## Part B - light analyses (post hoc)

Definitions: scripts/d19_part_b.py (docstring). Sets eight_W (H1), eight_W2 (H5), new_W (H2); observer-cluster bootstrap with 2,000 replicates (seed 20261124; one weight matrix per set, shared by all contrasts of the set). Rows 'main' reproduce the registered point estimates (control above); their intervals differ slightly from the registered ones because the replicates differ. Polyporaceae belongs to neither group. Secondary models: pooled values in the second table of each item; all units in outputs/D19/B/B_contrasts.csv.

### Reference: the registered contrast recomputed with the D19 bootstrap (post hoc)

Primary model (BioCLIP 2.5 Huge):

| contrast | set | Delta pooled | ER pooled | Delta animals | ER animals | Delta plants | ER plants | slow rows | fast rows | share of slow weight | share of fast weight | families left out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| slow vs fast (registered contrast) | eight families, W (H1) | 4.41 [3.88, 4.99] | 1.941 [1.803, 2.133] | 7.82 [6.83, 8.80] | 2.167 [1.980, 2.396] | 0.99 [0.55, 1.50] | 1.372 [1.195, 1.682] | 21949 | 26884 | 1.000 | 1.000 | - |
| slow vs fast (registered contrast) | eight families, W2 (H5) | 4.62 [3.68, 5.56] | 2.027 [1.751, 2.369] | 8.11 [6.65, 9.61] | 2.925 [2.431, 3.528] | 1.13 [0.01, 2.21] | 1.236 [1.002, 1.543] | 9953 | 11630 | 1.000 | 1.000 | - |
| slow vs fast (registered contrast) | six new families, W (H2) | 4.17 [2.99, 4.80] | 1.548 [1.354, 1.660] | 7.38 [5.39, 8.42] | 2.185 [1.710, 2.410] | 0.80 [-0.59, 1.93] | 1.131 [0.917, 1.361] | 15318 | 13085 | 1.000 | 1.000 | - |

Secondary models (pooled):

| contrast | set | BioCLIP 2 Delta | BioCLIP 2 ER | first BioCLIP Delta | first BioCLIP ER | BT-CLIP-O Delta | BT-CLIP-O ER |
|---|---|---|---|---|---|---|---|
| slow vs fast (registered contrast) | eight families, W (H1) | 5.69 [5.07, 6.34] | 1.758 [1.655, 1.890] | 9.52 [8.57, 10.56] | 1.357 [1.315, 1.407] | 3.81 [3.10, 4.65] | 1.068 [1.055, 1.085] |
| slow vs fast (registered contrast) | eight families, W2 (H5) | 6.56 [5.40, 7.79] | 1.961 [1.746, 2.238] | 11.51 [9.74, 13.13] | 1.380 [1.313, 1.452] | 3.73 [2.56, 4.89] | 1.064 [1.044, 1.085] |
| slow vs fast (registered contrast) | six new families, W (H2) | 5.22 [3.73, 5.99] | 1.465 [1.299, 1.551] | 4.07 [2.85, 6.00] | 1.097 [1.067, 1.151] | 2.98 [1.57, 3.68] | 1.046 [1.024, 1.058] |

### B1 (post hoc). Decomposition of T: looked at early against waited

T_wait = days from creation to the first identification by another user; T_res = T - T_wait. Shares are of the slow weight (phase-2 weights, pooled over the families of the set); weighted medians below.

Primary model (BioCLIP 2.5 Huge):

| contrast | set | Delta pooled | ER pooled | Delta animals | ER animals | Delta plants | ER plants | slow rows | fast rows | share of slow weight | share of fast weight | families left out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| slow looked at early (T_wait < 1 day) vs A0 | eight families, W (H1) | 4.20 [3.08, 5.38] | 1.782 [1.550, 2.084] | 6.74 [4.94, 8.63] | 1.847 [1.602, 2.201] | 1.67 [0.33, 2.96] | 1.597 [1.105, 2.257] | 2525 | 26884 | 0.093 | 1.000 | - |
| slow waited (T_wait >= 1 day) vs A0 | eight families, W (H1) | 4.53 [3.95, 5.14] | 2.002 [1.851, 2.218] | 8.12 [7.04, 9.22] | 2.273 [2.053, 2.527] | 0.94 [0.50, 1.46] | 1.354 [1.175, 1.670] | 19424 | 26884 | 0.907 | 1.000 | - |
| slow looked at early (T_wait < 1 day) vs A0 | eight families, W2 (H5) | 3.17 [1.36, 4.79] | 1.697 [1.281, 2.140] | 6.89 [3.88, 9.92] | 2.776 [1.918, 3.679] | -0.55 [-2.26, 0.90] | 0.895 [0.613, 1.197] | 1527 | 11630 | 0.148 | 1.000 | - |
| slow waited (T_wait >= 1 day) vs A0 | eight families, W2 (H5) | 4.95 [3.95, 5.95] | 2.091 [1.807, 2.472] | 8.54 [6.92, 10.18] | 2.977 [2.452, 3.698] | 1.35 [0.19, 2.51] | 1.285 [1.035, 1.626] | 8426 | 11630 | 0.852 | 1.000 | - |
| slow looked at early (T_wait < 1 day) vs A0 | six new families, W (H2) | 5.31 [2.96, 6.61] | 1.712 [1.331, 1.939] | 9.63 [5.94, 11.05] | 2.822 [1.750, 3.219] | 1.05 [-2.17, 4.10] | 1.152 [0.738, 1.688] | 2667 | 13085 | 0.151 | 1.000 | - |
| slow waited (T_wait >= 1 day) vs A0 | six new families, W (H2) | 3.50 [2.61, 4.31] | 1.438 [1.315, 1.560] | 6.03 [4.65, 7.41] | 1.858 [1.627, 2.082] | 0.79 [-0.61, 1.92] | 1.129 [0.912, 1.356] | 12651 | 13085 | 0.849 | 1.000 | - |

Secondary models (pooled):

| contrast | set | BioCLIP 2 Delta | BioCLIP 2 ER | first BioCLIP Delta | first BioCLIP ER | BT-CLIP-O Delta | BT-CLIP-O ER |
|---|---|---|---|---|---|---|---|
| slow looked at early (T_wait < 1 day) vs A0 | eight families, W (H1) | 5.03 [3.72, 6.44] | 1.624 [1.448, 1.829] | 11.24 [9.24, 13.32] | 1.410 [1.332, 1.501] | 3.29 [1.89, 4.97] | 1.060 [1.034, 1.093] |
| slow waited (T_wait >= 1 day) vs A0 | eight families, W (H1) | 5.89 [5.22, 6.58] | 1.801 [1.688, 1.941] | 9.17 [8.10, 10.29] | 1.346 [1.301, 1.400] | 3.96 [3.24, 4.82] | 1.071 [1.058, 1.087] |
| slow looked at early (T_wait < 1 day) vs A0 | eight families, W2 (H5) | 5.45 [3.21, 7.52] | 1.824 [1.452, 2.242] | 12.11 [8.97, 14.96] | 1.422 [1.304, 1.538] | 4.80 [2.57, 6.78] | 1.083 [1.044, 1.120] |
| slow waited (T_wait >= 1 day) vs A0 | eight families, W2 (H5) | 6.67 [5.49, 8.02] | 1.962 [1.743, 2.272] | 11.19 [9.36, 12.95] | 1.366 [1.299, 1.442] | 3.48 [2.22, 4.75] | 1.060 [1.038, 1.083] |
| slow looked at early (T_wait < 1 day) vs A0 | six new families, W (H2) | 7.49 [4.94, 9.09] | 1.709 [1.386, 1.901] | 4.45 [2.28, 8.69] | 1.100 [1.050, 1.213] | 4.43 [1.91, 5.82] | 1.072 [1.029, 1.095] |
| slow waited (T_wait >= 1 day) vs A0 | six new families, W (H2) | 3.98 [2.95, 4.95] | 1.334 [1.238, 1.425] | 4.53 [3.11, 6.00] | 1.112 [1.076, 1.150] | 2.25 [1.28, 3.07] | 1.034 [1.019, 1.047] |

| set | share | within | value | rows | rows_within |
|---|---|---|---|---|---|
| eight families, W (H1) | T_wait < 1 day | slow | 0.0934 | 2525 | 21949 |
| eight families, W (H1) | T_wait >= 1 day | slow | 0.9066 | 19424 | 21949 |
| eight families, W (H1) | weighted median T_wait (days), slow looked at early | slow | 0.1311 | 2525 | 21949 |
| eight families, W (H1) | weighted median T_res (days), slow looked at early | slow | 13.5634 | 2525 | 21949 |
| eight families, W (H1) | weighted median T_wait (days), slow waited | slow | 28.2075 | 19424 | 21949 |
| eight families, W (H1) | weighted median T_res (days), slow waited | slow | 0.0000 | 19424 | 21949 |
| eight families, W2 (H5) | T_wait < 1 day | slow | 0.1484 | 1527 | 9953 |
| eight families, W2 (H5) | T_wait >= 1 day | slow | 0.8516 | 8426 | 9953 |
| eight families, W2 (H5) | weighted median T_wait (days), slow looked at early | slow | 0.1537 | 1527 | 9953 |
| eight families, W2 (H5) | weighted median T_res (days), slow looked at early | slow | 6.1876 | 1527 | 9953 |
| eight families, W2 (H5) | weighted median T_wait (days), slow waited | slow | 10.3871 | 8426 | 9953 |
| eight families, W2 (H5) | weighted median T_res (days), slow waited | slow | 0.0000 | 8426 | 9953 |
| six new families, W (H2) | T_wait < 1 day | slow | 0.1505 | 2667 | 15318 |
| six new families, W (H2) | T_wait >= 1 day | slow | 0.8495 | 12651 | 15318 |
| six new families, W (H2) | weighted median T_wait (days), slow looked at early | slow | 0.0938 | 2667 | 15318 |
| six new families, W (H2) | weighted median T_res (days), slow looked at early | slow | 13.5639 | 2667 | 15318 |
| six new families, W (H2) | weighted median T_wait (days), slow waited | slow | 12.8616 | 12651 | 15318 |
| six new families, W (H2) | weighted median T_res (days), slow waited | slow | 0.0000 | 12651 | 15318 |

### B2 (post hoc). Observer's own identification at creation

Category of the observer's earliest identification if created within one hour of the observation (none, above species rank, species rank); fast and slow rows of the same category are compared.

Primary model (BioCLIP 2.5 Huge):

| contrast | set | Delta pooled | ER pooled | Delta animals | ER animals | Delta plants | ER plants | slow rows | fast rows | share of slow weight | share of fast weight | families left out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| own identification at creation: none | eight families, W (H1) | 2.71 [-0.54, 5.15] | 1.791 [0.883, 3.822] | 1.39 [-3.87, 5.67] | 1.227 [0.572, 2.742] | 4.04 [1.25, 6.53] | 6.492 [1.815, 17.473] | 1334 | 455 | 0.060 | 0.019 | - |
| own identification at creation: above species rank | eight families, W (H1) | 3.00 [1.93, 4.77] | 1.693 [1.410, 2.612] | 4.35 [2.40, 7.05] | 1.665 [1.309, 2.469] | 1.65 [0.28, 3.55] | 1.779 [1.109, 10.760] | 3648 | 1673 | 0.147 | 0.056 | - |
| own identification at creation: species rank | eight families, W (H1) | 4.84 [4.20, 5.50] | 2.013 [1.845, 2.237] | 8.71 [7.53, 9.92] | 2.245 [2.026, 2.508] | 0.97 [0.50, 1.49] | 1.378 [1.183, 1.709] | 16967 | 24756 | 0.793 | 0.925 | - |
| own identification at creation: none | eight families, W2 (H5) | 2.04 [-2.27, 5.17] | 1.476 [0.690, 3.456] | 3.91 [-3.87, 9.88] | 1.690 [0.638, 6.712] | 0.17 [-3.31, 2.62] | 1.058 [0.106, 2.697] | 744 | 260 | 0.075 | 0.021 | - |
| own identification at creation: above species rank | eight families, W2 (H5) | 0.26 [-4.39, 4.03] | 1.032 [0.619, 1.864] | 5.55 [1.12, 9.62] | 2.000 [1.136, 4.357] | -5.03 [-13.06, 0.95] | 0.525 [0.200, 1.219] | 1769 | 783 | 0.172 | 0.060 | - |
| own identification at creation: species rank | eight families, W2 (H5) | 5.10 [3.94, 6.27] | 2.153 [1.812, 2.592] | 8.66 [6.75, 10.54] | 2.986 [2.398, 3.734] | 1.54 [0.29, 2.79] | 1.342 [1.058, 1.742] | 7440 | 10587 | 0.754 | 0.920 | - |
| own identification at creation: none | six new families, W (H2) | 6.58 [2.10, 9.91] | 2.236 [1.264, 4.060] | 11.58 [5.70, 16.68] | 2.692 [1.586, 5.625] | 0.41 [-8.80, 6.37] | 1.072 [0.296, 4.458] | 987 | 300 | 0.062 | 0.022 | - |
| own identification at creation: above species rank | six new families, W (H2) | 4.98 [2.74, 6.74] | 1.626 [1.297, 2.183] | 8.65 [5.38, 10.37] | 2.445 [1.641, 3.069] | 1.12 [-3.62, 5.65] | 1.194 [0.607, 3.851] | 2958 | 1301 | 0.183 | 0.095 | - |
| own identification at creation: species rank | six new families, W (H2) | 3.15 [2.28, 4.08] | 1.397 [1.273, 1.533] | 5.36 [4.01, 7.00] | 1.749 [1.530, 2.014] | 0.93 [-0.52, 2.18] | 1.155 [0.926, 1.427] | 11373 | 11484 | 0.755 | 0.883 | - |

Secondary models (pooled):

| contrast | set | BioCLIP 2 Delta | BioCLIP 2 ER | first BioCLIP Delta | first BioCLIP ER | BT-CLIP-O Delta | BT-CLIP-O ER |
|---|---|---|---|---|---|---|---|
| own identification at creation: none | eight families, W (H1) | 4.20 [0.05, 8.22] | 1.796 [1.007, 3.738] | 10.61 [3.08, 15.75] | 1.487 [1.118, 1.854] | 4.99 [0.11, 10.26] | 1.092 [1.002, 1.201] |
| own identification at creation: above species rank | eight families, W (H1) | 3.89 [1.93, 5.92] | 1.529 [1.228, 1.990] | 8.79 [5.54, 13.14] | 1.324 [1.190, 1.549] | 4.13 [0.82, 7.21] | 1.076 [1.014, 1.137] |
| own identification at creation: species rank | eight families, W (H1) | 6.12 [5.39, 6.84] | 1.806 [1.688, 1.943] | 9.35 [8.25, 10.58] | 1.351 [1.306, 1.407] | 3.88 [3.10, 4.78] | 1.069 [1.055, 1.086] |
| own identification at creation: none | eight families, W2 (H5) | 2.71 [-2.86, 8.16] | 1.349 [0.734, 2.899] | 2.03 [-8.80, 18.14] | 1.055 [0.799, 1.717] | 4.48 [-3.33, 10.57] | 1.082 [0.947, 1.203] |
| own identification at creation: above species rank | eight families, W2 (H5) | 2.45 [-2.51, 6.61] | 1.259 [0.804, 2.086] | 5.87 [-0.86, 12.09] | 1.165 [0.978, 1.389] | 2.94 [-2.14, 7.49] | 1.047 [0.967, 1.125] |
| own identification at creation: species rank | eight families, W2 (H5) | 7.02 [5.72, 8.66] | 2.011 [1.778, 2.368] | 11.56 [9.73, 13.55] | 1.380 [1.313, 1.465] | 3.71 [2.21, 5.02] | 1.065 [1.038, 1.089] |
| own identification at creation: none | six new families, W (H2) | 5.16 [-1.57, 9.89] | 1.429 [0.913, 2.118] | 0.60 [-5.95, 12.41] | 1.014 [0.875, 1.369] | 1.65 [-3.34, 8.46] | 1.024 [0.954, 1.134] |
| own identification at creation: above species rank | six new families, W (H2) | 4.68 [1.12, 7.44] | 1.336 [1.069, 1.685] | 3.64 [-0.19, 8.50] | 1.084 [0.996, 1.223] | 0.82 [-2.35, 3.65] | 1.013 [0.965, 1.057] |
| own identification at creation: species rank | six new families, W (H2) | 3.85 [2.86, 4.93] | 1.326 [1.230, 1.435] | 4.85 [3.33, 6.36] | 1.122 [1.083, 1.161] | 2.50 [1.59, 3.45] | 1.038 [1.024, 1.053] |

| set | share | within | value | rows | rows_within |
|---|---|---|---|---|---|
| eight families, W (H1) | own identification at creation: none | fast | 0.0188 | 455 | 26884 |
| eight families, W (H1) | own identification at creation: none | slow | 0.0601 | 1334 | 21949 |
| eight families, W (H1) | own identification at creation: above species rank | fast | 0.0564 | 1673 | 26884 |
| eight families, W (H1) | own identification at creation: above species rank | slow | 0.1471 | 3648 | 21949 |
| eight families, W (H1) | own identification at creation: species rank | fast | 0.9247 | 24756 | 26884 |
| eight families, W (H1) | own identification at creation: species rank | slow | 0.7928 | 16967 | 21949 |
| eight families, W (H1) | observer's earliest identification later than 1 h after creation | research with T | 0.0148 | 729 | 48833 |
| eight families, W2 (H5) | own identification at creation: none | fast | 0.0208 | 260 | 11630 |
| eight families, W2 (H5) | own identification at creation: none | slow | 0.0747 | 744 | 9953 |
| eight families, W2 (H5) | own identification at creation: above species rank | fast | 0.0597 | 783 | 11630 |
| eight families, W2 (H5) | own identification at creation: above species rank | slow | 0.1717 | 1769 | 9953 |
| eight families, W2 (H5) | own identification at creation: species rank | fast | 0.9195 | 10587 | 11630 |
| eight families, W2 (H5) | own identification at creation: species rank | slow | 0.7537 | 7440 | 9953 |
| eight families, W2 (H5) | observer's earliest identification later than 1 h after creation | research with T | 0.0108 | 361 | 21583 |
| six new families, W (H2) | own identification at creation: none | fast | 0.0216 | 300 | 13085 |
| six new families, W (H2) | own identification at creation: none | slow | 0.0615 | 987 | 15318 |
| six new families, W (H2) | own identification at creation: above species rank | fast | 0.0949 | 1301 | 13085 |
| six new families, W (H2) | own identification at creation: above species rank | slow | 0.1835 | 2958 | 15318 |
| six new families, W (H2) | own identification at creation: species rank | fast | 0.8835 | 11484 | 13085 |
| six new families, W (H2) | own identification at creation: species rank | slow | 0.7550 | 11373 | 15318 |
| six new families, W (H2) | observer's earliest identification later than 1 h after creation | research with T | 0.0171 | 585 | 28403 |

### B3 (post hoc). Vision assistance

Shares of fast and slow observations with a vision-assisted identification up to the research-grade time, and with any vision-assisted identification; contrasts within observations without one.

Primary model (BioCLIP 2.5 Huge):

| contrast | set | Delta pooled | ER pooled | Delta animals | ER animals | Delta plants | ER plants | slow rows | fast rows | share of slow weight | share of fast weight | families left out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no vision-assisted identification at all | eight families, W (H1) | 6.88 [5.56, 8.24] | 2.123 [1.839, 2.551] | 11.53 [9.48, 13.89] | 2.268 [1.992, 2.774] | 2.23 [0.70, 3.66] | 1.704 [1.167, 2.654] | 4707 | 6364 | 0.194 | 0.206 | - |
| no vision-assisted identification up to research grade | eight families, W (H1) | 6.88 [5.57, 8.25] | 2.126 [1.838, 2.559] | 11.55 [9.49, 13.91] | 2.274 [1.994, 2.780] | 2.21 [0.70, 3.64] | 1.703 [1.168, 2.654] | 4714 | 6392 | 0.194 | 0.208 | - |
| no vision-assisted identification at all | eight families, W2 (H5) | 7.45 [4.52, 9.86] | 2.139 [1.551, 2.794] | 12.09 [8.70, 15.39] | 2.602 [1.986, 3.476] | 2.81 [-1.67, 6.19] | 1.509 [0.801, 2.556] | 2358 | 2809 | 0.234 | 0.238 | - |
| no vision-assisted identification up to research grade | eight families, W2 (H5) | 7.46 [4.54, 9.87] | 2.151 [1.555, 2.822] | 12.15 [8.77, 15.43] | 2.635 [2.010, 3.524] | 2.77 [-1.77, 6.12] | 1.501 [0.793, 2.553] | 2363 | 2827 | 0.234 | 0.239 | - |
| no vision-assisted identification at all | six new families, W (H2) | 4.78 [2.86, 6.75] | 1.479 [1.267, 1.771] | 8.19 [5.70, 11.55] | 1.914 [1.587, 2.346] | 1.75 [-1.62, 4.71] | 1.204 [0.847, 1.771] | 3927 | 3498 | 0.245 | 0.250 | - |
| no vision-assisted identification up to research grade | six new families, W (H2) | 4.78 [2.88, 6.77] | 1.483 [1.271, 1.778] | 8.21 [5.74, 11.58] | 1.922 [1.593, 2.358] | 1.77 [-1.58, 4.72] | 1.206 [0.853, 1.771] | 3940 | 3529 | 0.245 | 0.252 | - |

Secondary models (pooled):

| contrast | set | BioCLIP 2 Delta | BioCLIP 2 ER | first BioCLIP Delta | first BioCLIP ER | BT-CLIP-O Delta | BT-CLIP-O ER |
|---|---|---|---|---|---|---|---|
| no vision-assisted identification at all | eight families, W (H1) | 8.87 [7.49, 10.52] | 1.946 [1.760, 2.259] | 12.15 [10.00, 14.55] | 1.425 [1.337, 1.543] | 4.91 [3.09, 6.68] | 1.088 [1.054, 1.123] |
| no vision-assisted identification up to research grade | eight families, W (H1) | 8.87 [7.50, 10.53] | 1.948 [1.762, 2.255] | 12.20 [10.07, 14.59] | 1.428 [1.341, 1.545] | 4.97 [3.17, 6.76] | 1.089 [1.056, 1.125] |
| no vision-assisted identification at all | eight families, W2 (H5) | 10.71 [7.77, 13.19] | 2.308 [1.773, 2.874] | 16.40 [12.01, 20.08] | 1.519 [1.345, 1.682] | 4.52 [1.69, 6.93] | 1.077 [1.028, 1.123] |
| no vision-assisted identification up to research grade | eight families, W2 (H5) | 10.67 [7.69, 13.14] | 2.306 [1.769, 2.864] | 16.27 [11.86, 20.08] | 1.514 [1.342, 1.676] | 4.49 [1.65, 6.91] | 1.077 [1.027, 1.122] |
| no vision-assisted identification at all | six new families, W (H2) | 4.86 [2.72, 7.36] | 1.339 [1.178, 1.563] | 4.66 [2.10, 8.21] | 1.112 [1.050, 1.207] | 1.65 [-0.43, 3.52] | 1.024 [0.994, 1.053] |
| no vision-assisted identification up to research grade | six new families, W (H2) | 4.91 [2.79, 7.41] | 1.345 [1.182, 1.572] | 4.65 [2.12, 8.20] | 1.112 [1.050, 1.207] | 1.62 [-0.45, 3.46] | 1.024 [0.993, 1.052] |

| set | share | within | value | rows | rows_within |
|---|---|---|---|---|---|
| eight families, W (H1) | vision-assisted identification up to research grade | fast | 0.7924 | 20492 | 26884 |
| eight families, W (H1) | vision-assisted identification up to research grade | slow | 0.8062 | 17235 | 21949 |
| eight families, W (H1) | any vision-assisted identification | fast | 0.7937 | 20520 | 26884 |
| eight families, W (H1) | any vision-assisted identification | slow | 0.8064 | 17242 | 21949 |
| eight families, W2 (H5) | vision-assisted identification up to research grade | fast | 0.7607 | 8803 | 11630 |
| eight families, W2 (H5) | vision-assisted identification up to research grade | slow | 0.7657 | 7590 | 9953 |
| eight families, W2 (H5) | any vision-assisted identification | fast | 0.7622 | 8821 | 11630 |
| eight families, W2 (H5) | any vision-assisted identification | slow | 0.7664 | 7595 | 9953 |
| six new families, W (H2) | vision-assisted identification up to research grade | fast | 0.7484 | 9556 | 13085 |
| six new families, W (H2) | vision-assisted identification up to research grade | slow | 0.7547 | 11378 | 15318 |
| six new families, W (H2) | any vision-assisted identification | fast | 0.7501 | 9587 | 13085 |
| six new families, W (H2) | any vision-assisted identification | slow | 0.7552 | 11391 | 15318 |

### B4 (post hoc). Observations with a single photograph only

Primary model (BioCLIP 2.5 Huge):

| contrast | set | Delta pooled | ER pooled | Delta animals | ER animals | Delta plants | ER plants | slow rows | fast rows | share of slow weight | share of fast weight | families left out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| one photograph only | eight families, W (H1) | 4.29 [3.67, 4.95] | 2.035 [1.838, 2.305] | 7.32 [6.25, 8.49] | 2.213 [1.982, 2.513] | 1.25 [0.62, 1.81] | 1.557 [1.238, 2.041] | 14002 | 18300 | 0.624 | 0.658 | - |
| one photograph only | eight families, W2 (H5) | 4.52 [3.31, 5.67] | 2.092 [1.679, 2.611] | 7.64 [6.09, 9.45] | 3.014 [2.363, 3.943] | 1.40 [-0.36, 2.75] | 1.313 [0.939, 1.820] | 6275 | 7840 | 0.629 | 0.683 | - |
| one photograph only | six new families, W (H2) | 3.84 [2.50, 4.75] | 1.535 [1.311, 1.722] | 7.21 [5.16, 8.56] | 2.252 [1.744, 2.568] | 0.81 [-0.97, 2.48] | 1.138 [0.859, 1.565] | 9051 | 7764 | 0.588 | 0.594 | - |

Secondary models (pooled):

| contrast | set | BioCLIP 2 Delta | BioCLIP 2 ER | first BioCLIP Delta | first BioCLIP ER | BT-CLIP-O Delta | BT-CLIP-O ER |
|---|---|---|---|---|---|---|---|
| one photograph only | eight families, W (H1) | 5.79 [5.01, 6.54] | 1.855 [1.701, 2.022] | 10.10 [8.91, 11.40] | 1.404 [1.349, 1.471] | 3.80 [2.96, 4.74] | 1.069 [1.053, 1.088] |
| one photograph only | eight families, W2 (H5) | 5.58 [4.21, 7.07] | 1.862 [1.575, 2.262] | 11.04 [8.93, 13.10] | 1.378 [1.295, 1.470] | 3.23 [1.83, 4.66] | 1.056 [1.031, 1.083] |
| one photograph only | six new families, W (H2) | 5.09 [3.46, 6.15] | 1.491 [1.297, 1.630] | 4.46 [2.99, 6.67] | 1.112 [1.074, 1.175] | 2.37 [0.65, 3.52] | 1.036 [1.010, 1.055] |

| set | share | within | value | rows | rows_within |
|---|---|---|---|---|---|
| eight families, W (H1) | one photograph only | fast | 0.6577 | 18300 | 26884 |
| eight families, W (H1) | one photograph only | slow | 0.6245 | 14002 | 21949 |
| eight families, W2 (H5) | one photograph only | fast | 0.6831 | 7840 | 11630 |
| eight families, W2 (H5) | one photograph only | slow | 0.6293 | 6275 | 9953 |
| six new families, W (H2) | one photograph only | fast | 0.5941 | 7764 | 13085 |
| six new families, W (H2) | one photograph only | slow | 0.5879 | 9051 | 15318 |

### B5 (post hoc). Reconstruction checks: withdrawn and non-ancestor identifications

Primary model (BioCLIP 2.5 Huge):

| contrast | set | Delta pooled | ER pooled | Delta animals | ER animals | Delta plants | ER plants | slow rows | fast rows | share of slow weight | share of fast weight | families left out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| without observations with a withdrawn identification | eight families, W (H1) | 4.11 [3.57, 4.73] | 1.959 [1.799, 2.184] | 7.37 [6.33, 8.38] | 2.231 [1.996, 2.487] | 0.86 [0.44, 1.41] | 1.331 [1.155, 1.683] | 19697 | 25214 | 0.909 | 0.945 | - |
| without observations with a non-ancestor identification above species rank | eight families, W (H1) | 4.44 [3.91, 5.01] | 1.948 [1.811, 2.141] | 7.88 [6.90, 8.85] | 2.177 [1.988, 2.407] | 0.99 [0.55, 1.50] | 1.372 [1.194, 1.685] | 21871 | 26839 | 0.998 | 0.999 | - |
| without either | eight families, W (H1) | 4.12 [3.58, 4.75] | 1.961 [1.800, 2.187] | 7.40 [6.35, 8.42] | 2.236 [2.001, 2.493] | 0.85 [0.43, 1.40] | 1.327 [1.153, 1.678] | 19677 | 25198 | 0.909 | 0.945 | - |
| without observations with a withdrawn identification | eight families, W2 (H5) | 4.47 [3.50, 5.43] | 2.063 [1.743, 2.446] | 7.65 [6.15, 9.22] | 2.846 [2.312, 3.570] | 1.29 [0.09, 2.30] | 1.303 [1.017, 1.654] | 8751 | 10879 | 0.879 | 0.942 | - |
| without observations with a non-ancestor identification above species rank | eight families, W2 (H5) | 4.62 [3.66, 5.56] | 2.035 [1.757, 2.379] | 8.15 [6.69, 9.65] | 2.958 [2.452, 3.583] | 1.09 [-0.01, 2.18] | 1.228 [0.997, 1.531] | 9898 | 11604 | 0.994 | 0.997 | - |
| without either | eight families, W2 (H5) | 4.48 [3.51, 5.43] | 2.064 [1.742, 2.448] | 7.69 [6.18, 9.26] | 2.852 [2.314, 3.588] | 1.28 [0.07, 2.29] | 1.299 [1.015, 1.651] | 8734 | 10874 | 0.878 | 0.942 | - |
| without observations with a withdrawn identification | six new families, W (H2) | 3.07 [2.27, 3.88] | 1.397 [1.280, 1.523] | 5.50 [4.29, 6.85] | 1.774 [1.568, 2.006] | 0.53 [-0.87, 1.76] | 1.089 [0.876, 1.342] | 12491 | 11849 | 0.839 | 0.916 | - |
| without observations with a non-ancestor identification above species rank | six new families, W (H2) | 4.10 [2.89, 4.72] | 1.542 [1.343, 1.655] | 7.21 [5.17, 8.24] | 2.165 [1.684, 2.386] | 0.83 [-0.55, 1.94] | 1.137 [0.920, 1.371] | 15235 | 13042 | 0.995 | 0.997 | - |
| without either | six new families, W (H2) | 3.07 [2.27, 3.88] | 1.398 [1.281, 1.524] | 5.51 [4.31, 6.87] | 1.776 [1.570, 2.008] | 0.53 [-0.87, 1.76] | 1.089 [0.876, 1.343] | 12486 | 11842 | 0.839 | 0.916 | - |

Secondary models (pooled):

| contrast | set | BioCLIP 2 Delta | BioCLIP 2 ER | first BioCLIP Delta | first BioCLIP ER | BT-CLIP-O Delta | BT-CLIP-O ER |
|---|---|---|---|---|---|---|---|
| without observations with a withdrawn identification | eight families, W (H1) | 5.39 [4.74, 6.03] | 1.775 [1.652, 1.915] | 9.15 [8.14, 10.27] | 1.352 [1.307, 1.408] | 3.72 [2.98, 4.57] | 1.067 [1.053, 1.083] |
| without observations with a non-ancestor identification above species rank | eight families, W (H1) | 5.67 [5.04, 6.32] | 1.757 [1.652, 1.888] | 9.48 [8.52, 10.53] | 1.356 [1.314, 1.406] | 3.80 [3.09, 4.64] | 1.068 [1.055, 1.084] |
| without either | eight families, W (H1) | 5.38 [4.72, 6.03] | 1.773 [1.650, 1.912] | 9.14 [8.13, 10.25] | 1.351 [1.307, 1.407] | 3.72 [2.98, 4.56] | 1.067 [1.053, 1.083] |
| without observations with a withdrawn identification | eight families, W2 (H5) | 5.68 [4.62, 6.96] | 1.839 [1.645, 2.129] | 11.13 [9.33, 12.87] | 1.372 [1.305, 1.449] | 3.46 [2.23, 4.65] | 1.060 [1.038, 1.082] |
| without observations with a non-ancestor identification above species rank | eight families, W2 (H5) | 6.56 [5.43, 7.82] | 1.967 [1.754, 2.248] | 11.43 [9.63, 13.08] | 1.378 [1.310, 1.450] | 3.73 [2.55, 4.87] | 1.064 [1.043, 1.086] |
| without either | eight families, W2 (H5) | 5.69 [4.63, 6.98] | 1.841 [1.647, 2.133] | 11.06 [9.27, 12.81] | 1.370 [1.303, 1.447] | 3.47 [2.24, 4.67] | 1.060 [1.038, 1.082] |
| without observations with a withdrawn identification | six new families, W (H2) | 4.11 [3.13, 5.06] | 1.360 [1.263, 1.465] | 4.56 [3.14, 5.97] | 1.116 [1.079, 1.153] | 2.31 [1.44, 3.22] | 1.035 [1.022, 1.050] |
| without observations with a non-ancestor identification above species rank | six new families, W (H2) | 5.16 [3.64, 5.94] | 1.461 [1.293, 1.548] | 3.98 [2.78, 5.93] | 1.095 [1.066, 1.148] | 2.98 [1.58, 3.69] | 1.047 [1.024, 1.058] |
| without either | six new families, W (H2) | 4.11 [3.13, 5.06] | 1.360 [1.263, 1.465] | 4.56 [3.14, 5.96] | 1.116 [1.079, 1.153] | 2.32 [1.44, 3.23] | 1.035 [1.022, 1.050] |

| set | share | within | value | rows | rows_within |
|---|---|---|---|---|---|
| eight families, W (H1) | any withdrawn identification | fast | 0.0546 | 1670 | 26884 |
| eight families, W (H1) | any withdrawn identification | slow | 0.0908 | 2252 | 21949 |
| eight families, W (H1) | any non-ancestor identification above species rank | fast | 0.0012 | 45 | 26884 |
| eight families, W (H1) | any non-ancestor identification above species rank | slow | 0.0023 | 78 | 21949 |
| eight families, W2 (H5) | any withdrawn identification | fast | 0.0576 | 751 | 11630 |
| eight families, W2 (H5) | any withdrawn identification | slow | 0.1206 | 1202 | 9953 |
| eight families, W2 (H5) | any non-ancestor identification above species rank | fast | 0.0029 | 26 | 11630 |
| eight families, W2 (H5) | any non-ancestor identification above species rank | slow | 0.0060 | 55 | 9953 |
| six new families, W (H2) | any withdrawn identification | fast | 0.0838 | 1236 | 13085 |
| six new families, W (H2) | any withdrawn identification | slow | 0.1606 | 2827 | 15318 |
| six new families, W (H2) | any non-ancestor identification above species rank | fast | 0.0027 | 43 | 13085 |
| six new families, W (H2) | any non-ancestor identification above species rank | slow | 0.0054 | 83 | 15318 |

### B6 (post hoc). Threshold sensitivity and within-family quantile contrast

Primary model (BioCLIP 2.5 Huge):

| contrast | set | Delta pooled | ER pooled | Delta animals | ER animals | Delta plants | ER plants | slow rows | fast rows | share of slow weight | share of fast weight | families left out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| fast = T < 6 h | eight families, W (H1) | 3.24 [2.80, 3.70] | 1.799 [1.664, 1.990] | 5.63 [4.97, 6.39] | 2.003 [1.844, 2.209] | 0.84 [0.32, 1.34] | 1.338 [1.112, 1.684] | 27431 | 21402 | 1.000 | 0.761 | - |
| fast = T < 12 h | eight families, W (H1) | 3.48 [3.01, 3.98] | 1.782 [1.650, 1.972] | 6.22 [5.47, 7.10] | 1.997 [1.827, 2.208] | 0.75 [0.25, 1.23] | 1.279 [1.084, 1.558] | 24726 | 24107 | 1.000 | 0.875 | - |
| fast = T < 48 h | eight families, W (H1) | 4.73 [4.18, 5.40] | 1.966 [1.833, 2.159] | 8.46 [7.37, 9.59] | 2.205 [2.010, 2.437] | 1.00 [0.58, 1.55] | 1.362 [1.195, 1.667] | 18689 | 30144 | 0.876 | 1.000 | - |
| fast = T < 7 days | eight families, W (H1) | 5.12 [4.46, 5.92] | 1.949 [1.803, 2.147] | 9.40 [8.05, 10.86] | 2.192 [1.983, 2.447] | 0.84 [0.40, 1.38] | 1.289 [1.129, 1.546] | 14251 | 34582 | 0.700 | 1.000 | - |
| slowest fifth vs fastest fifth within family | eight families, W (H1) | 4.89 [4.16, 5.48] | 2.857 [2.388, 3.619] | 8.41 [7.40, 9.29] | 3.575 [2.998, 4.838] | 1.37 [0.38, 2.21] | 1.685 [1.141, 2.664] | 13885 | 7572 | 0.475 | 0.322 | - |
| fast = T < 6 h | eight families, W2 (H5) | 3.82 [3.00, 4.69] | 1.984 [1.695, 2.377] | 6.25 [4.96, 7.61] | 2.628 [2.163, 3.269] | 1.38 [0.28, 2.46] | 1.353 [1.056, 1.775] | 11843 | 9740 | 1.000 | 0.848 | - |
| fast = T < 12 h | eight families, W2 (H5) | 4.34 [3.40, 5.27] | 2.038 [1.736, 2.430] | 7.66 [6.25, 9.22] | 2.995 [2.451, 3.723] | 1.02 [-0.15, 2.10] | 1.226 [0.968, 1.563] | 10851 | 10732 | 1.000 | 0.928 | - |
| fast = T < 48 h | eight families, W2 (H5) | 4.73 [3.71, 5.77] | 1.985 [1.729, 2.321] | 8.45 [6.74, 10.23] | 2.855 [2.367, 3.485] | 1.02 [-0.12, 2.09] | 1.202 [0.979, 1.481] | 8089 | 13494 | 0.812 | 1.000 | - |
| fast = T < 7 days | eight families, W2 (H5) | 6.23 [4.90, 7.54] | 2.213 [1.899, 2.616] | 11.62 [9.30, 13.84] | 3.475 [2.787, 4.341] | 0.84 [-0.45, 2.11] | 1.150 [0.927, 1.447] | 5779 | 15804 | 0.577 | 1.000 | - |
| slowest fifth vs fastest fifth within family | eight families, W2 (H5) | 5.30 [4.00, 6.78] | 2.672 [1.995, 4.145] | 9.08 [7.74, 11.07] | 5.349 [3.952, 9.289] | 1.52 [-0.84, 3.57] | 1.357 [0.859, 2.434] | 7694 | 2923 | 0.665 | 0.247 | - |
| fast = T < 6 h | six new families, W (H2) | 3.36 [2.40, 4.03] | 1.469 [1.306, 1.593] | 5.53 [4.03, 6.41] | 1.914 [1.573, 2.129] | 1.31 [-0.02, 2.61] | 1.236 [0.997, 1.579] | 18718 | 9685 | 1.000 | 0.731 | - |
| fast = T < 12 h | six new families, W (H2) | 3.83 [2.77, 4.50] | 1.521 [1.344, 1.634] | 6.46 [4.73, 7.43] | 2.052 [1.657, 2.266] | 1.00 [-0.43, 2.21] | 1.171 [0.936, 1.440] | 17046 | 11357 | 1.000 | 0.861 | - |
| fast = T < 48 h | six new families, W (H2) | 4.56 [3.32, 5.20] | 1.597 [1.388, 1.706] | 7.97 [5.81, 9.07] | 2.283 [1.741, 2.499] | 1.35 [0.15, 2.50] | 1.228 [1.023, 1.478] | 12979 | 15424 | 0.848 | 1.000 | - |
| fast = T < 7 days | six new families, W (H2) | 5.67 [4.60, 6.44] | 1.729 [1.531, 1.859] | 10.52 [8.59, 11.81] | 2.722 [2.060, 3.042] | 0.93 [-0.36, 2.14] | 1.148 [0.949, 1.362] | 9514 | 18889 | 0.623 | 1.000 | - |
| slowest fifth vs fastest fifth within family | six new families, W (H2) | 4.58 [3.32, 5.90] | 1.603 [1.398, 1.908] | 8.27 [6.55, 10.07] | 2.384 [1.916, 3.090] | 1.16 [-1.17, 3.90] | 1.160 [0.860, 1.782] | 8262 | 4148 | 0.508 | 0.329 | - |

Secondary models (pooled):

| contrast | set | BioCLIP 2 Delta | BioCLIP 2 ER | first BioCLIP Delta | first BioCLIP ER | BT-CLIP-O Delta | BT-CLIP-O ER |
|---|---|---|---|---|---|---|---|
| fast = T < 6 h | eight families, W (H1) | 4.79 [4.21, 5.41] | 1.734 [1.621, 1.877] | 8.73 [7.86, 9.83] | 1.352 [1.312, 1.413] | 3.06 [2.35, 3.76] | 1.056 [1.042, 1.069] |
| fast = T < 12 h | eight families, W (H1) | 4.92 [4.36, 5.54] | 1.693 [1.594, 1.828] | 8.85 [7.95, 9.93] | 1.341 [1.302, 1.394] | 3.07 [2.40, 3.82] | 1.056 [1.043, 1.070] |
| fast = T < 48 h | eight families, W (H1) | 6.25 [5.56, 6.98] | 1.810 [1.703, 1.941] | 9.93 [8.98, 11.07] | 1.365 [1.326, 1.418] | 3.97 [3.26, 4.85] | 1.071 [1.058, 1.087] |
| fast = T < 7 days | eight families, W (H1) | 6.64 [5.78, 7.52] | 1.786 [1.670, 1.931] | 10.57 [9.47, 11.80] | 1.373 [1.328, 1.427] | 4.42 [3.65, 5.37] | 1.079 [1.065, 1.097] |
| slowest fifth vs fastest fifth within family | eight families, W (H1) | 6.95 [5.99, 7.69] | 2.386 [2.078, 2.769] | 12.83 [11.47, 14.68] | 1.567 [1.491, 1.705] | 3.93 [2.82, 5.14] | 1.072 [1.051, 1.097] |
| fast = T < 6 h | eight families, W2 (H5) | 5.42 [4.49, 6.65] | 1.913 [1.696, 2.253] | 10.24 [8.35, 11.89] | 1.365 [1.288, 1.443] | 2.74 [1.53, 3.86] | 1.047 [1.026, 1.066] |
| fast = T < 12 h | eight families, W2 (H5) | 6.18 [5.14, 7.45] | 1.963 [1.759, 2.281] | 11.15 [9.40, 12.99] | 1.382 [1.313, 1.465] | 3.20 [1.99, 4.30] | 1.054 [1.034, 1.074] |
| fast = T < 48 h | eight families, W2 (H5) | 7.19 [5.93, 8.39] | 2.017 [1.795, 2.288] | 12.32 [10.48, 13.96] | 1.401 [1.332, 1.467] | 3.94 [2.60, 5.15] | 1.068 [1.044, 1.090] |
| fast = T < 7 days | eight families, W2 (H5) | 8.82 [7.23, 10.21] | 2.193 [1.921, 2.486] | 13.95 [11.81, 15.79] | 1.445 [1.366, 1.516] | 4.50 [2.83, 5.96] | 1.079 [1.049, 1.106] |
| slowest fifth vs fastest fifth within family | eight families, W2 (H5) | 7.96 [6.47, 9.65] | 2.742 [2.172, 3.824] | 16.91 [14.50, 19.88] | 1.719 [1.572, 1.933] | 3.51 [1.91, 5.50] | 1.060 [1.032, 1.097] |
| fast = T < 6 h | six new families, W (H2) | 3.72 [2.47, 4.56] | 1.339 [1.210, 1.436] | 4.71 [3.49, 6.34] | 1.120 [1.087, 1.168] | 1.97 [0.73, 2.80] | 1.030 [1.011, 1.044] |
| fast = T < 12 h | six new families, W (H2) | 4.91 [3.58, 5.65] | 1.455 [1.300, 1.544] | 4.74 [3.49, 6.52] | 1.118 [1.086, 1.169] | 2.47 [1.21, 3.24] | 1.038 [1.018, 1.051] |
| fast = T < 48 h | six new families, W (H2) | 5.76 [4.12, 6.55] | 1.517 [1.328, 1.601] | 3.98 [2.73, 6.22] | 1.093 [1.063, 1.155] | 3.56 [2.01, 4.25] | 1.056 [1.031, 1.068] |
| fast = T < 7 days | six new families, W (H2) | 6.75 [5.13, 7.66] | 1.596 [1.394, 1.701] | 7.05 [4.08, 12.37] | 1.166 [1.091, 1.330] | 3.83 [2.30, 4.60] | 1.062 [1.036, 1.076] |
| slowest fifth vs fastest fifth within family | six new families, W (H2) | 7.19 [5.77, 9.03] | 1.692 [1.513, 2.003] | 7.83 [5.79, 10.12] | 1.202 [1.144, 1.273] | 2.99 [1.52, 4.62] | 1.047 [1.023, 1.073] |

### B7 (post hoc). Random-effects summary over the 14 families of W and meta-regression of H6

Family values: BioCLIP 2.5 Huge Delta and log ER of eight_W and new_W (outputs/confirm/<set>/estimates.csv). The bootstrap replicates were not kept, so each family variance is ((upper - lower) / 3.92) squared from the stored 95% interval (on the log scale for ER). REML; 95% confidence interval mu +/- 1.96 SE; 95% prediction interval for a new family mu +/- t(k - 2) x sqrt(tau^2 + SE^2) (with the class variance added in the class model). Classes from the snapshot taxonomy (outputs/D19/snapshot/families_taxonomy.csv).

| quantity | families | estimate [95% CI] | tau family | tau class | prediction interval | on the ER scale | I2 |
|---|---|---|---|---|---|---|---|
| Delta, 14 families of W | 14 | 4.148 [1.739, 6.556] | 4.505 | n/a | [-6.027, 14.322] | - | 0.946 |
| Delta, 14 families of W, class random effect | 14 | 4.396 [1.534, 7.259] | 0.000 | 4.521 | [-5.956, 14.749] | - | 0.946 |
| log ER, 14 families of W | 14 | 0.511 [0.317, 0.705] | 0.342 | n/a | [-0.265, 1.287] | 1.667 [1.373, 2.023]; PI [0.767, 3.621] | 0.929 |
| log ER, 14 families of W, class random effect | 14 | 0.490 [0.271, 0.710] | 0.141 | 0.308 | [-0.287, 1.268] | 1.633 [1.311, 2.034]; PI [0.750, 3.553] | 0.929 |

H6 meta-regression over the 36 families (Delta in points per unit of fast share; precision weights from the interval widths):

| model | slope [95% CI] | p (two-sided) | tau family | tau class |
|---|---|---|---|---|
| family and class random effects | 8.795 [2.985, 14.605] | 0.0030 | 0.867 | 3.022 |
| family random effect only | 11.765 [6.259, 17.270] | 0.0000 | 1.595 | n/a |

Spearman rho of H6 leaving out one class at a time (registered value over 36 families: 0.574):

| class_left_out | families_left_out | families_used | rho | p (one-sided, 10,000 permutations) |
|---|---|---|---|---|
| Agaricomycetes | 1 | 35 | 0.589 | 0.0002 |
| Amphibia | 1 | 35 | 0.563 | 0.0003 |
| Arachnida | 1 | 35 | 0.559 | 0.0007 |
| Aves | 2 | 34 | 0.516 | 0.0013 |
| Insecta | 15 | 21 | 0.539 | 0.0070 |
| Liliopsida | 3 | 33 | 0.585 | 0.0004 |
| Magnoliopsida | 11 | 25 | 0.668 | 0.0004 |
| Pinopsida | 1 | 35 | 0.574 | 0.0004 |
| Reptilia | 1 | 35 | 0.536 | 0.0005 |

### B8 (post hoc). Resolving identifiers

| set | A2_A3_rows | resolving_identifiers_A2_A3 | share A2+A3 by top 10 | top10_counts | share of all research rows by these 10 | resolving_identifiers_all_research | max_resolved_by_one_identifier_on_one_day_all_research | max_resolved_by_one_identifier_on_one_day_A2_A3 | resolver_is_observer_rows |
|---|---|---|---|---|---|---|---|---|---|
| eight families, W (H1) | 10129 | 2138 | 0.2473 | 569;456;350;223;206;197;139;136;125;104 | 0.1064 | 7722 | 139 | 96 | 1825 |
| eight families, W2 (H5) | 3884 | 1155 | 0.2201 | 197;158;82;73;68;65;57;57;50;48 | 0.0730 | 4672 | 43 | 43 | 902 |
| six new families, W (H2) | 6767 | 1746 | 0.2789 | 536;245;206;157;154;149;135;128;90;87 | 0.2026 | 5314 | 344 | 75 | 1639 |

Counts are phase-2 analysis rows (not weighted); the ten most active resolving identifiers are those with the most A2 and A3 rows in the set; one day = UTC date of the resolving identification.

Delta with the two-way cluster bootstrap (observer and resolving identifier, pigeonhole resampling, 2,000 replicates):

Primary model (BioCLIP 2.5 Huge):

| contrast | set | Delta pooled | ER pooled | Delta animals | ER animals | Delta plants | ER plants | slow rows | fast rows | families left out |
|---|---|---|---|---|---|---|---|---|---|---|
| slow vs fast, two-way cluster bootstrap (observer x resolving identifier) | eight families, W (H1) | 4.41 [3.55, 5.47] | 1.941 [1.716, 2.340] | 7.82 [6.16, 9.72] | 2.167 [1.846, 2.642] | 0.99 [0.27, 1.86] | 1.372 [1.085, 1.986] | 21949 | 26884 | - |
| slow vs fast, two-way cluster bootstrap (observer x resolving identifier) | eight families, W2 (H5) | 4.62 [3.09, 6.26] | 2.027 [1.589, 2.632] | 8.11 [5.76, 10.83] | 2.925 [2.130, 4.128] | 1.13 [-0.80, 2.83] | 1.236 [0.874, 1.781] | 9953 | 11630 | - |
| slow vs fast, two-way cluster bootstrap (observer x resolving identifier) | six new families, W (H2) | 4.17 [2.25, 5.22] | 1.548 [1.257, 1.730] | 7.38 [4.41, 9.09] | 2.185 [1.537, 2.552] | 0.80 [-1.66, 2.91] | 1.131 [0.781, 1.614] | 15318 | 13085 | - |

Secondary models (pooled):

| contrast | set | BioCLIP 2 Delta | BioCLIP 2 ER | first BioCLIP Delta | first BioCLIP ER | BT-CLIP-O Delta | BT-CLIP-O ER |
|---|---|---|---|---|---|---|---|
| slow vs fast, two-way cluster bootstrap (observer x resolving identifier) | eight families, W (H1) | 5.69 [4.67, 6.83] | 1.758 [1.589, 2.000] | 9.52 [7.63, 11.41] | 1.357 [1.278, 1.447] | 3.81 [2.61, 5.20] | 1.068 [1.046, 1.096] |
| slow vs fast, two-way cluster bootstrap (observer x resolving identifier) | eight families, W2 (H5) | 6.56 [4.67, 8.73] | 1.961 [1.622, 2.509] | 11.51 [8.58, 14.39] | 1.380 [1.269, 1.511] | 3.73 [1.66, 5.66] | 1.064 [1.029, 1.099] |
| slow vs fast, two-way cluster bootstrap (observer x resolving identifier) | six new families, W (H2) | 5.22 [2.96, 6.69] | 1.465 [1.232, 1.627] | 4.07 [2.09, 7.04] | 1.097 [1.048, 1.179] | 2.98 [0.90, 4.13] | 1.046 [1.014, 1.066] |

### B9 (post hoc). Prior exposure of the observer to the species

Exposure = a research-grade observation of the same species by the same observer observed before 2024-05-01 in the snapshot (pairs: outputs/D19/snapshot, not tracked).

Primary model (BioCLIP 2.5 Huge):

| contrast | set | Delta pooled | ER pooled | Delta animals | ER animals | Delta plants | ER plants | slow rows | fast rows | share of slow weight | share of fast weight | families left out |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| prior exposure: yes | eight families, W (H1) | 4.71 [3.89, 5.55] | 1.944 [1.745, 2.251] | 8.47 [7.09, 9.98] | 2.192 [1.948, 2.628] | 0.96 [0.23, 1.71] | 1.333 [1.066, 1.712] | 10019 | 16209 | 0.452 | 0.583 | - |
| prior exposure: no | eight families, W (H1) | 4.20 [3.52, 4.97] | 2.047 [1.830, 2.385] | 7.23 [5.93, 8.67] | 2.193 [1.908, 2.567] | 1.18 [0.68, 1.81] | 1.599 [1.303, 2.240] | 11930 | 10675 | 0.548 | 0.417 | - |
| prior exposure: yes | eight families, W2 (H5) | 5.57 [3.98, 7.48] | 2.130 [1.722, 2.927] | 10.50 [8.06, 13.08] | 3.438 [2.566, 4.584] | 0.64 [-1.36, 3.23] | 1.116 [0.785, 1.867] | 4044 | 6596 | 0.416 | 0.588 | - |
| prior exposure: no | eight families, W2 (H5) | 3.94 [2.77, 4.99] | 1.949 [1.582, 2.344] | 6.30 [4.41, 8.36] | 2.487 [1.879, 3.435] | 1.58 [0.39, 2.56] | 1.389 [1.079, 1.742] | 5909 | 5034 | 0.584 | 0.412 | - |
| prior exposure: yes | six new families, W (H2) | 3.90 [2.73, 5.16] | 1.533 [1.343, 1.763] | 6.16 [4.42, 8.18] | 1.885 [1.583, 2.252] | 1.90 [0.05, 3.53] | 1.338 [1.008, 1.775] | 7121 | 6760 | 0.461 | 0.517 | - |
| prior exposure: no | six new families, W (H2) | 3.77 [2.51, 4.58] | 1.459 [1.275, 1.599] | 7.27 [5.18, 8.58] | 2.072 [1.632, 2.369] | -0.31 [-2.19, 1.35] | 0.951 [0.712, 1.268] | 8197 | 6325 | 0.539 | 0.483 | - |

Secondary models (pooled):

| contrast | set | BioCLIP 2 Delta | BioCLIP 2 ER | first BioCLIP Delta | first BioCLIP ER | BT-CLIP-O Delta | BT-CLIP-O ER |
|---|---|---|---|---|---|---|---|
| prior exposure: yes | eight families, W (H1) | 6.14 [5.16, 7.05] | 1.764 [1.625, 1.946] | 9.44 [8.13, 11.14] | 1.331 [1.282, 1.408] | 4.19 [3.11, 5.17] | 1.075 [1.055, 1.093] |
| prior exposure: no | eight families, W (H1) | 5.52 [4.65, 6.46] | 1.853 [1.684, 2.078] | 9.43 [7.96, 10.86] | 1.384 [1.315, 1.459] | 3.98 [3.04, 5.19] | 1.074 [1.056, 1.097] |
| prior exposure: yes | eight families, W2 (H5) | 8.62 [6.91, 11.09] | 2.272 [1.943, 3.017] | 14.81 [12.34, 17.84] | 1.492 [1.399, 1.628] | 4.14 [2.33, 6.29] | 1.072 [1.040, 1.111] |
| prior exposure: no | eight families, W2 (H5) | 5.44 [3.93, 6.81] | 1.839 [1.543, 2.184] | 8.67 [6.49, 10.93] | 1.285 [1.206, 1.381] | 3.26 [1.77, 4.72] | 1.056 [1.030, 1.082] |
| prior exposure: yes | six new families, W (H2) | 4.41 [3.07, 5.80] | 1.396 [1.261, 1.546] | 4.54 [2.58, 6.69] | 1.115 [1.065, 1.173] | 3.10 [1.82, 4.40] | 1.047 [1.027, 1.068] |
| prior exposure: no | six new families, W (H2) | 5.11 [3.33, 6.18] | 1.427 [1.251, 1.545] | 4.44 [2.89, 6.72] | 1.105 [1.067, 1.169] | 2.14 [0.47, 3.14] | 1.033 [1.007, 1.049] |

| set | share | within | value | rows | rows_within |
|---|---|---|---|---|---|
| eight families, W (H1) | prior exposure | fast | 0.5832 | 16209 | 26884 |
| eight families, W (H1) | prior exposure | slow | 0.4523 | 10019 | 21949 |
| eight families, W2 (H5) | prior exposure | fast | 0.5882 | 6596 | 11630 |
| eight families, W2 (H5) | prior exposure | slow | 0.4158 | 4044 | 9953 |
| six new families, W (H2) | prior exposure | fast | 0.5173 | 6760 | 13085 |
| six new families, W (H2) | prior exposure | slow | 0.4610 | 7121 | 15318 |

### B10 (post hoc). Model scores

The confirmatory run stored only the top-1 species of each model (outputs/confirm/<set>/predictions.parquet has the columns p_, c_ and g_ per model); probabilities or logits are not stored, so B10 cannot be computed from stored outputs.

Supplement from the recomputed baseline of Part C (eight_W, BioCLIP 2.5 Huge, registered label spaces and texts; top-1 probability = softmax of the logit scale times the cosine similarities): within-species Spearman correlation between log(1 + T) and the top-1 probability -0.1954 [-0.2181, -0.1727] over 48,606 research-grade rows of 934 species (ranks within species (species with at least 3 research rows with T), weighted Pearson correlation of the within-species centred ranks (phase-2 weights); 2,000 observer-cluster replicates).

### B11 (post hoc). Rank agreement among the four models (eight_W)

| model | A0 accuracy (rank) | A1 accuracy (rank) | A2 accuracy (rank) | A3 accuracy (rank) |
|---|---|---|---|---|
| BioCLIP 2.5 Huge | 0.9657 (1) | 0.9200 (1) | 0.8867 (1) | 0.8682 (1) |
| BioCLIP 2 | 0.9424 (2) | 0.8842 (2) | 0.8399 (2) | 0.8001 (2) |
| first BioCLIP | 0.7544 (3) | 0.6593 (3) | 0.6046 (3) | 0.5540 (3) |
| BT-CLIP-O | 0.4622 (4) | 0.4059 (4) | 0.3926 (4) | 0.4070 (4) |

Accuracy of research-grade rows of the stratum, mean over the eight families. Kendall's W of the model ranks over the four strata: 1.000 (1 = identical ranking in every stratum).

## Part C - GPU analyses (post hoc; window W, eight families, locked half, stored photographs)

Accuracy = weighted accuracy of research-grade rows (phase-2 weights), mean over families; Delta and ER as above; one observer-cluster bootstrap (2,000 replicates, seed 20261124) for all variants. Definitions: scripts/d19_part_c.py (docstring). Per-family values: outputs/D19/C/C_results.csv.

### C1 (post hoc). Larger label space (all eligible species of the same kingdom over the eight families)

| variant | unit | accuracy [95%] | Delta [95%] | ER [95%] |
|---|---|---|---|---|
| stored Z25 (registered) | pooled | 0.9548 [0.9526, 0.9570] | 4.41 [3.88, 4.99] | 1.941 [1.803, 2.133] |
| stored Z25 (registered) | animals | 0.9407 [0.9372, 0.9443] | 7.82 [6.83, 8.80] | 2.167 [1.980, 2.396] |
| stored Z25 (registered) | plants | 0.9689 [0.9663, 0.9715] | 0.99 [0.55, 1.50] | 1.372 [1.195, 1.682] |
| baseline recomputed | pooled | 0.9548 [0.9526, 0.9570] | 4.41 [3.88, 4.99] | 1.941 [1.803, 2.133] |
| baseline recomputed | animals | 0.9407 [0.9372, 0.9443] | 7.82 [6.83, 8.80] | 2.167 [1.980, 2.396] |
| baseline recomputed | plants | 0.9689 [0.9663, 0.9715] | 0.99 [0.55, 1.50] | 1.372 [1.195, 1.682] |
| C1 kingdom label space | pooled | 0.9532 [0.9509, 0.9554] | 4.59 [4.06, 5.17] | 1.951 [1.815, 2.138] |
| C1 kingdom label space | animals | 0.9396 [0.9361, 0.9433] | 8.16 [7.15, 9.14] | 2.207 [2.016, 2.433] |
| C1 kingdom label space | plants | 0.9667 [0.9641, 0.9695] | 1.02 [0.52, 1.54] | 1.354 [1.167, 1.646] |

### C2 (post hoc). Preprocessing (letterbox) and species text (species name only)

| variant | unit | accuracy [95%] | Delta [95%] | ER [95%] |
|---|---|---|---|---|
| stored Z25 (registered) | pooled | 0.9548 [0.9526, 0.9570] | 4.41 [3.88, 4.99] | 1.941 [1.803, 2.133] |
| stored Z25 (registered) | animals | 0.9407 [0.9372, 0.9443] | 7.82 [6.83, 8.80] | 2.167 [1.980, 2.396] |
| stored Z25 (registered) | plants | 0.9689 [0.9663, 0.9715] | 0.99 [0.55, 1.50] | 1.372 [1.195, 1.682] |
| C2a letterbox | pooled | 0.9347 [0.9318, 0.9376] | 5.82 [5.26, 6.51] | 1.887 [1.779, 2.049] |
| C2a letterbox | animals | 0.9160 [0.9116, 0.9205] | 10.22 [9.20, 11.37] | 2.118 [1.969, 2.306] |
| C2a letterbox | plants | 0.9534 [0.9500, 0.9568] | 1.43 [0.84, 2.06] | 1.358 [1.196, 1.599] |
| C2b species name only | pooled | 0.9544 [0.9522, 0.9566] | 4.43 [3.89, 4.98] | 1.945 [1.804, 2.132] |
| C2b species name only | animals | 0.9400 [0.9364, 0.9436] | 7.86 [6.87, 8.84] | 2.170 [1.981, 2.406] |
| C2b species name only | plants | 0.9687 [0.9662, 0.9712] | 1.00 [0.54, 1.49] | 1.377 [1.190, 1.682] |

### C3 (post hoc). Independent model: DINOv2-base embeddings with a logistic-regression probe per family

| variant | unit | accuracy [95%] | Delta [95%] | ER [95%] |
|---|---|---|---|---|
| stored Z25 (registered) | pooled | 0.9548 [0.9526, 0.9570] | 4.41 [3.88, 4.99] | 1.941 [1.803, 2.133] |
| stored Z25 (registered) | animals | 0.9407 [0.9372, 0.9443] | 7.82 [6.83, 8.80] | 2.167 [1.980, 2.396] |
| stored Z25 (registered) | plants | 0.9689 [0.9663, 0.9715] | 0.99 [0.55, 1.50] | 1.372 [1.195, 1.682] |
| C3 DINOv2-base probe | pooled | 0.7566 [0.7515, 0.7616] | 8.74 [7.71, 9.76] | 1.356 [1.311, 1.412] |
| C3 DINOv2-base probe | animals | 0.7080 [0.7007, 0.7153] | 14.36 [12.82, 15.84] | 1.464 [1.405, 1.526] |
| C3 DINOv2-base probe | plants | 0.8052 [0.7982, 0.8123] | 3.13 [1.92, 4.44] | 1.172 [1.103, 1.267] |

Label-space sizes (registered family spaces and kingdom spaces): see outputs/D19/C/part_c_log.txt.

C3 training data (development half, photographs of the earlier gates):

| step | rows |
|---|---|
| candidate photographs | 96,781 |
| found in the snapshot | 96,781 |
| family of the snapshot equal to the manifest family (eight families) | 96,781 |
| development half | 96,781 |
| research grade in the snapshot | 96,781 |
| observed before 2024-05-01 | 45,680 |
| species in the registered label space | 45,680 |
| photograph is the first photograph | 45,680 |
| one row per observation | 45,680 |

| family | training_rows | training_species | training_observers | label_space_species | chosen_C | cv_accuracy_chosen | test_research_rows_species_not_in_training | test_research_rows |
|---|---|---|---|---|---|---|---|---|
| Fabaceae | 6276 | 233 | 4380 | 241 | 0.3 | 0.7895 | 52 | 6327 |
| Asteraceae | 8833 | 361 | 5884 | 370 | 0.3 | 0.7860 | 28 | 5160 |
| Nymphalidae | 7796 | 165 | 4939 | 169 | 1.0 | 0.5675 | 12 | 6145 |
| Columbidae | 2483 | 35 | 2249 | 35 | 0.3 | 0.7640 | 0 | 6571 |
| Anatidae | 7666 | 71 | 4340 | 71 | 0.01 | 0.7647 | 0 | 6574 |
| Lamiaceae | 4640 | 106 | 4221 | 113 | 0.3 | 0.9155 | 21 | 6263 |
| Rosaceae | 5373 | 136 | 4852 | 141 | 0.3 | 0.8202 | 40 | 4946 |
| Sciuridae | 2613 | 38 | 2409 | 38 | 0.01 | 0.7574 | 0 | 6871 |

## Run time and bytes written

| step | minutes | note |
|---|---|---|
| snapshot/snapshot_log.txt | 6.3 | completed |
| A/part_a_log.txt | 5.0 | completed |
| B/part_b_log.txt | 5.4 | completed |
| C/part_c_log.txt | 9.5 | completed |
| B/part_b_log.txt, first run | 2.4 | stopped: missing resolver read as NaN (fixed; rerun) |
| C/part_c_log.txt, first run | 22.2 | stopped: a training photograph stored as .gif was not found by the file lookup (fixed; rerun with the cached embeddings of the first run) |

The task started at 2026-11-23 20:19 (Step 0); the registration of D19 was committed before any computation. Parts B and C ran in parallel with each other (CPU and GPU). Wall time from Step 0 to this report: 57 minutes (limit 6 hours).

Bytes written under outputs/D19/: 840,988,982 (of which embedding caches 823,955,942); this report and the scripts are listed in the commit. Report written 2026-11-23 21:16.
