# Data dictionary

Meanings are taken from the code and from docs/PLAN.md. Where a meaning is not stated here, the named script or file
defines it.

## Codes used in several tables

### Models

| code | model | repository and pinned revision |
|---|---|---|
| Z25 | BioCLIP 2.5 Huge (primary model) | imageomics/bioclip-2.5-vith14, see configs/model_pins.json |
| Z2 | BioCLIP 2 | imageomics/bioclip-2, see configs/model_pins.json |
| Z1 | first BioCLIP | imageomics/bioclip, see configs/model_pins.json |
| BT-CLIP-O | BioTrove-CLIP, ViT-B-16 initialised from OpenAI CLIP | BGLab/BioTrove-CLIP, see configs/model_pins.json |
| DINOv2-base | image encoder used only for the linear probe of D19 item C3 | facebook/dinov2-base, see configs/model_pins.json |

All four zero-shot models predict the top-1 species within the label space of the observation's family
(src/confirm/infer.py, src/zeroshot.py).

### Identification time T and strata

T is the number of days from the creation of an observation to the first identification after which, among the
current identifications at species rank or below (one per user), at least two agree with the observation's species
and they are more than two thirds of them (src/d6_lib.py, functions n2 and t_days). Strata (src/confirm/acquisition.py, function stratum):

| stratum | definition |
|---|---|
| A0 | research grade, T < 1 day (fast) |
| A1 | research grade, 1 <= T < 30 days |
| A2 | research grade, 30 <= T < 365 days |
| A3 | research grade, T >= 365 days |
| B1 | needs_id, genus label supported by fewer than 2 users (support as in D5 of docs/PLAN.md) |
| B2 | needs_id, genus label supported by at least 2 users |

"Slow" means research grade with T >= 1 day (A1 to A3); "fast" means A0.

### Sets

| set | content | hypotheses |
|---|---|---|
| eight_W | eight families, locked half of observers, window W | H1, H3, H4 |
| eight_W2 | eight families, locked half, window W2 | H5 |
| new_W | six new families, both halves, window W | H2, H6 |
| replication_W | 30 replication families, both halves, window W, research-grade frame | H6 |

Windows and families: configs/confirmatory.yaml and docs/PLAN.md.

## data/analysed_observations.csv

One row per analysed observation (155,318 rows). Built by the build script of the package from the stored analysis
rows; equal in number to the rows of each set's analysis (outputs/confirm/<set>/analysis.json, key rows).

| column | type | meaning | allowed values |
|---|---|---|---|
| set | text | confirmatory set | eight_W, eight_W2, new_W, replication_W |
| observation_uuid | text | observation identifier of the iNaturalist Open Data export of 2026-10-27 | UUID |
| first_photo_id | integer | iNaturalist photo id of the first photograph (the photograph analysed) | positive integer |
| licence | text | licence of that photograph in the export | CC0, CC-BY, CC-BY-NC |
| family | text | taxonomic family | 44 family names |
| stratum | text | identification-time stratum (above) | A0, A1, A2, A3, B1, B2 |
| phase2_weight | float | weight of the row in the two-phase sample: (frame size / phase-1 size) / realised phase-2 fraction of the stratum (src/confirm/acquisition.py) | > 0 |
| observer_hash | text | first 16 hex characters of a salted SHA-256 digest of the numeric observer id; the salt is not published, so it links rows of the same observer within this table only | 16 hex characters |
| pred_<model> | integer | predicted species (iNaturalist taxon id), top-1 of the model | taxon id |
| correct_species_<model> | integer | 1 if the row is research grade and the prediction equals its species; 0 otherwise, including every needs_id row (B1, B2) (scripts/confirm_run.py, predict step) | 0, 1 |
| correct_genus_<model> | integer | 1 if the genus of the prediction equals the genus label of the row (research grade and needs_id); 0 otherwise | 0, 1 |

<model> is one of Z25, Z2, Z1, BT-CLIP-O. The reference species of research-grade rows and the identification time T
are not in this table.

## outputs/confirm/<set>/estimates.csv (and joint_14/estimates_joint.csv)

Long table written by src/confirm/analysis.py (class Out).

| column | meaning |
|---|---|
| model | model code (above) |
| quantity | estimated quantity (below) |
| unit | pooled (equal family weights), animals, plants, families (median over families), a family name, or "without <family>" (leave-one-family-out) |
| value | point estimate |
| lo95, hi95 | 95% percentile interval of the observer-cluster bootstrap (observers drawn with replacement once per replicate over the whole set) |
| lo_one_sided, hi_one_sided | 5th and 95th percentiles of the bootstrap replicates |
| p_one_sided | one-sided bootstrap p-value of quantity > 0 (src/confirm/estimators.py, function one_sided) |
| status | estimable, or not estimable when the point value is not finite |
| families_left_out | families left out by the not-estimable rule, separated by ";" |

Main quantities (src/confirm/estimators.py; docs/PLAN.md):

| quantity | meaning |
|---|---|
| Delta | 100 x (E_slow - E_ref) in percentage points. E_slow: weighted species-level error of slow rows; E_ref: error of fast rows of the same species, reweighted to the species mix of the slow rows; species without both fast and slow rows are dropped (src/d6_lib.py, delta_parts; estimators.c1) |
| ER | E_slow / E_ref, pooled as a ratio of sums of family means |
| dropped share of slow weight | share of the slow weight in species without a fast row |
| Delta A1 vs A0, A2 vs A0, A3 vs A0 (and ER) | Delta with slow restricted to one stratum |
| slope on log(1+T) | within-species weighted least-squares slope of error on log(1 + T), x 100 |
| Delta median split (and ER) | slow = T above the weighted median of T within its species |
| O, R, L, L_upload, L_ident, O_ident | snapshot quantities at a date S (D4 of docs/PLAN.md): O = accuracy on rows research grade at S minus accuracy on all rows research grade today (points); R = error on all research grade today / error on those research grade at S; L = share of today's research-grade rows not research grade at S, split into late upload (L_upload) and late identification (L_ident); O_ident: see src/confirm/estimators.py, function c2 |
| G_all, G_sup, G_sup with S2b | genus-level overstatement including needs_id rows (D5 of docs/PLAN.md); G_sup keeps needs_id rows with support of at least 2 |
| ... at <date> | the quantity at snapshot date <date>; without a date: S* of the set (configs/confirmatory.yaml) |
| b0, b3, b_obs, b_int, rho | regression coefficients x 100 (species fixed effects; with cell fixed effects and covariates; with observer fixed effects; interaction with queue load Q) and rho = b3 / b0: see src/confirm/estimators.py |
| Delta Q tertile k, Delta Q tertile 3 minus tertile 1 | Delta within tertiles of the queue load Q (D8 of docs/PLAN.md) |
| Delta within V0 / V1, within activity S0 to S3, strong consensus, slow with(out) disagreement, common horizon 540 days, genus level with B2 / with B1 and B2, without perceptual-duplicate groups, without regime-flagged pairs, population-weighted | sensitivity analyses of plan section 10: see src/confirm/analysis.py |
| ... without <family> | the quantity with that family left out of the set |
| (5000 replicates) | the estimate that carries a hypothesis, with 5,000 bootstrap replicates |

## outputs/confirm/h6.json

| key | meaning |
|---|---|
| model | model code of H6 (Z25) |
| delta | {family: Delta of the family} for the 36 families of new_W and replication_W |
| fast_share | {family: share of research-grade observations with T < 1 day} (see scripts/confirm_run.py, h6 step) |
| rho | Spearman correlation of delta and fast_share over the families used |
| p | one-sided permutation p-value of rho > 0: (1 + number of permuted rho >= observed) / (1 + n_perm) |
| n_perm | number of permutations (10,000) |
| rho_lo95, rho_hi95 | 95% percentile interval of rho from n_boot bootstrap replicates over families |
| n_boot, boot_replicates, boot_undefined | bootstrap replicates requested, used, and with undefined rho |
| families_used, families_left_out | number of families used; families left out by the not-estimable rule |

## Other tables of outputs/confirm/

| file | content |
|---|---|
| decisions.csv | H1 to H6: estimate, interval, bounds, p-value, companion measure, Holm order and decision (src/confirm/decide.py) |
| decisions_secondary.csv | the same rule applied to the secondary models (not part of the decisions) |
| <set>/accuracy.csv | unweighted species-level accuracy (c_<model>) of research-grade rows per family |
| <set>/fast_share.csv | share of fast observations per family |
| <set>/phase2_fractions.csv, stratum_report.csv | phase-1 stratum counts, planned and realised phase-2 fractions, cap rule |
| <set>/photo_failures.csv | selected, downloaded and failed photographs per family and stratum |
| <set>/regime_check.csv | species flagged per model and family (src/confirm/estimators.py, regime_check) |
| <set>/q_tertiles.csv | Delta and ER within tertiles of the queue load Q (eight_W only) |
| <set>/analysis.json, covariates.json, histories.json, phase1.json, preapproval.json, timing.json, rng_*.json | run summaries: rows, families, tipping points, counts, budget, timing, generator states |
| spec_*.json | specification of each step (keys listed in the docstring of scripts/confirm_run.py) |
| joint_14/ | analysis of eight_W and new_W together (14 families) |
| frames/*.parquet.json | counts of the snapshot frames (the frame tables themselves are not included) |

## outputs/D19/ (post hoc)

Every D19 table is post hoc. Item numbers refer to D19 in docs/PLAN.md and to docs/reports/D19_report.md.

| file | item | content |
|---|---|---|
| A/A1_dropped_slow_weight.csv | A1 | dropped share of slow weight per set and family, with species counts |
| A/A2_pooled_errors.csv | A2 | pooled E_slow, E_ref, Delta, ER and raw (unreweighted) error contrasts per set and model |
| A/A3_tipping_points.csv | A3 | tipping points to 0 and to 1 from 2,000 and 5,000 replicates |
| A/A5_L_shares.csv | A5 | L, L_upload, L_ident at S* with intervals |
| A/A7_history_failures.csv, A7_photo_failures.csv | A7 | history and photograph failures per set, family, grade or stratum |
| A/A8_preprocessing.json | A8 | image preprocessing and logit scale of each model |
| A/A9_family_errors.csv | A9 | per family and model: label space, species counts, raw and reweighted errors |
| A/A11_c3_coefficients.csv | A11 | b0, b3, b_obs per set with intervals |
| A/A_summary.json | A | summary values and code excerpts of part A |
| B/B_contrasts.csv | B1 to B6, B9 | Delta and ER of each contrast (columns item, contrast, set, model, unit) with intervals and slow and fast row counts |
| B/B_shares.csv | B1 to B6 | weighted and unweighted shares of rows in each subgroup |
| B/B7_*.csv | B7 | family inputs, random-effects pooling, H6 meta-regression and leave-one-class-out rho |
| B/B8_resolvers.csv | B8 | concentration of resolving identifiers (counts only) |
| B/B11_ranks.csv | B11 | accuracy rank of the four models per stratum |
| C/C_results.csv | C1 to C3 | Delta, ER and accuracy of each variant (column variant) |
| C/C3_training.csv, C3_training_flow.json | C3 | training rows, species, observers and chosen regularisation per family |
| C/B10_supplement.json | B10 | within-species Spearman correlation of log(1 + T) and the top-1 probability |
| snapshot/a10_flow.csv | A10 | frame counts per family, set and filter step |
| snapshot/families_taxonomy.csv | all | family taxon id, kingdom, phylum, class and order |

Column definitions not given here: see the docstrings of scripts/d19_part_a.py, scripts/d19_part_b.py and
scripts/d19_part_c.py.
