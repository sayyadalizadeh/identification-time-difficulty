# Corrected code freeze of the confirmatory pipeline

Corrected freeze commit: 966fa55500ba48d892c9c2ed403b5ad8dea9d1aa. First freeze: f3d452832935f5e9d8f829dc6f588e58cb4c2a5b (docs/reports/code_freeze.md, unchanged). The correction was made before any confirmatory data were requested or read: configs/registration_lock.json has never existed, and the guard refuses locked-half observers and the new and replication families in every run so far (task N18 stopped before the lock). The validation on development data is D13 addendum 2 (docs/reports/D13_report.md). The registration audit is docs/reports/registration_audit.md. No tag is set. Script: scripts/n18a_code_freeze_v2.py.

## Files and SHA-256 at the corrected freeze commit

| file | SHA-256 | working tree equal |
|---|---|---|
| scripts/confirm_driver.py | 4c772155a1d31629d1606cb406dc081679432c56bc6cd74d4ff582764315be78 | yes |
| scripts/confirm_run.py | 535b8fd3c4cad0f0eb366e5f1b7589f639391ec9dcd3c21f40d93e1566a36def | yes |
| src/confirm/__init__.py | 70e1b5e8e787a849f2d76fcc3d1e46b227e9d754790e7fa321a314b18cb055fc | yes |
| src/confirm/config.py | 907a12215da7948602ffeeac63bb3fa0f2bd54efaab62f74aba9f1bb5c6dee0d | yes |
| src/confirm/guard.py | 2d782a7d4cb65be02e506e92a6bb2e8f91803f72c94ae313ac4994b3ed992f80 | yes |
| src/confirm/acquisition.py | 6b1c20a6a25a34d2da4cd01af9e35d82d901648905e9b0158f728cc9ea1dd8c6 | yes |
| src/confirm/covariates.py | 9e9c53da522b26b7a19dbd48ee9d1336abae85d0c2c65e6c89b7aacda444e6e9 | yes |
| src/confirm/infer.py | 16d3df588c61d3519ebc08bd58f32d058e3ac0e3f08645ba6e947fb3dbd8927e | yes |
| src/confirm/estimators.py | 7852ba18c2c1ad9b5b5763a186f356eb79f218b35aef739f157d4c1d512efa4d | yes |
| src/confirm/analysis.py | a79c8ddc8f821ad067f6008df3c4c4edd4fc717b98a1e78a76c3b5663de3dcae | yes |
| src/confirm/decide.py | 8baa4ab2f3f0d5da0bf5d3364b359be6d52ba1187b1c14f3d7a642e316614044 | yes |
| src/d6_lib.py | 794c3fb1fb7d496233a3f061453f0901be944cb7d0893e65944289e28e6ae23f | yes |
| src/moderation.py | b288c6efa7aaac543a8b68ad351a8776eb1d593ab46e8285456d342b15221968 | yes |
| src/halves.py | 7c82b2f6d2fc7a79046c8de0fc34f87b6f92beae745a6e0f585127c749335499 | yes |
| src/zeroshot.py | fecbcb1a8725096a76e4cb4fa78c7d98bf3efb9498a61eed3b4618cb3c832488 | yes |
| configs/confirmatory.yaml | 6f10e4b1e29710d133457beaebae3f6171b524821a85d7aed3c5db5037570594 | yes |
| configs/model_pins.json | f43760d768b18e109a4dea790621c5a03ec2392b498e0ad63d7ae03438a6a4ba | yes |
| tests/test_config.py | 5808421f6b49d03553b0f26d9480de2ca1d941aad12568055fc712d1667a5460 | yes |
| tests/test_estimators.py | 3b5bc6b862a18ef1d05a03a09e5cf7d56397349e38ee785f4b9473ca17895a20 | yes |
| tests/test_guard.py | f96a59e70d93b4130aae846a7e73b138cd7da2f0ba0f2a60721d4c4009cbad63 | yes |
| tests/test_addendum1.py | 601a5305925173747cf4e14098a6c8a7a43b5362ada2cb7923c690960c519b5a | yes |
| tests/test_freeze_v2.py | 53b32a948741388f960dc6f7ee91bd3bceaf463953854612cb3c2f8e3e6f09d4 | yes |
| docs/plan_blocks/confirmatory_plan_draft3.md | 6f413237143bfaed666bc1ed67c6e6fe10f4c2473ee51fdf73e15ac1bd9ce6db | yes |
| inputs/earlier_gates/outputs/G-IG8.0/e1_species_primary.csv (copied input, not tracked) | bd40a682d576335edf62da8d8f53954509fb5624b277b98937cbfbebaccc826e | matches inputs/MANIFEST.csv |
| inputs/earlier_gates/code/docs/manifests/inat_snapshot_2026-10-27_sha256.csv (copied input, not tracked) | bfae8294a5b2ef73caf6ba74ac6b5463869679ce2ad85ffaef71ef8f73acbed4 | matches inputs/MANIFEST.csv |
| outputs/D6/part1_shares.csv (development output, not tracked) | 8fa9fd7ade59d82512944aff48466c603bee9faab0f13570204506766c3088de | - |
| outputs/D6/part2_shares.csv (development output, not tracked) | 5b814648639c9e40cc8d3e9137c7829e19c5b37afe9cb5fe6bffdbd4fa46326a | - |
| outputs/D12/projections.csv (development output, not tracked) | f4edb8585a091aeef961040945e43ab31295367a28f0edef2d190c940e225b56 | - |
| outputs/frames/frames_dev_D12.parquet (development output, not tracked) | cc572e7b5f284d40662924481bc99e64c31156b86e3772366374d45620bfa3c5 | - |
| outputs/D4/d4_sample.csv (development output, not tracked) | 107d97bc850a573154de9f16814025ad24e9f1cbfd074c0c2943216fa8137187 | - |
| outputs/D6/w2_sample.csv (development output, not tracked) | 881a18861469fae2c82ff09a52883fc3b007f82759fb5fc823f1ba982b9e7035 | - |
| outputs/D12/A_W2/phase1.parquet (development output, not tracked) | d9165a7bf13d2c76dea4deeaeab38d9fbfde654f27b5fe0f0cf12226aeff602a | - |
| outputs/D13/W2/phase1.parquet (development output, not tracked) | a6356c0fbe1491c9c0fc5eead15885325fd2652efc70aaefa3ca3a410cc7669b | - |
| outputs/D4/api_raw_d4/ (119 files, digest of names and SHA-256; not tracked) | 07ebaf7aee8acf90e908d25f519c86e6b9935afb9276f86480a8e91292ed7654 | - |
| outputs/D6/api_raw_w2/ (40 files, digest of names and SHA-256; not tracked) | 172fac4abe551d1afe6127802288867ae1433530023087e40efc70cdeb0b9987 | - |
| outputs/D12/A_W2/api_raw/ (12 files, digest of names and SHA-256; not tracked) | fc2999b281c90b583e12435dc66743234baa7da2cb687d7fc4ee17c7471b659f | - |
| outputs/D13/W2/api_raw/ (320 files, digest of names and SHA-256; not tracked) | 8a02763b458b1516a298e028eccf70702ac4f8683b3bcd1bd9b6eb3b1d43a1a3 | - |

Model weights are checked against configs/model_pins.json at every load; the snapshot files against their SHA-256 manifest when the frames and the snapshot covariates are built.

## Test suite

Full suite (python -m unittest discover -s tests): 49 tests, result OK; per file: test_addendum1 16 (all ok), test_config 2 (all ok), test_estimators 6 (all ok), test_freeze_v2 16 (all ok), test_guard 9 (all ok). Output: outputs/freeze_v2/unit_tests.txt.

## Changes against the first freeze

| file and step | change | reason |
|---|---|---|
| scripts/confirm_run.py, download | the download limit is read from configs/confirmatory.yaml (24 GB for the confirmatory run, 8 GB for dry runs); the confirmatory run counts its bytes in outputs/confirm/download_bytes.json from 0 | the first freeze stopped all downloads at 8 GB counted with the dry-run counter (5.27 GB already used), so the registered photographs (about 20 GB) could not be downloaded (plan section 4.3) |
| scripts/confirm_run.py, analyse | one bootstrap matrix of 5,000 replicates for the estimates that carry a hypothesis (Delta and ER of BioCLIP 2.5 Huge; O, R and G_sup at S* in the eight-family set of window W); 2,000 for all other estimates; the fall-back to 2,000 replicates is removed | plan section 8 (5,000 for H1 to H6, 2,000 otherwise); the first freeze used 5,000 only for Delta and ER |
| scripts/confirm_run.py, decide; src/confirm/decide.py (new) | Holm over H1 to H6 at one-sided 0.05 and the grading of section 9, written to outputs/confirm/decisions.csv; the same grading for the secondary models without family-wise control (decisions_secondary.csv) | plan sections 6, 8 and 9; no frozen step applied them |
| src/confirm/estimators.py, h6 | percentile interval of rho from 5,000 bootstrap replicates that resample the families, drawn after the 10,000 permutations | plan section 9 (rho reported with a bootstrap interval over families) |
| src/confirm/analysis.py | the contrast Delta(T3) - Delta(T1) of the Q tertiles inside every replicate, pooled and per family; C2 (O, R, G_all, G_sup at S*) without perceptual-duplicate groups and without regime-flagged pairs | plan section 9 (contrast with its interval) and section 10, items 6 and 7 (C1 and C2) |
| src/confirm/acquisition.py, identifier_measures; scripts/confirm_run.py, prepare_rows | identifier availability from the set's phase-1 histories plus the stored development histories of the same window (W: D4; W2: D6 Part 2, D12, D13), scaled by population of both halves over sampled observations with a history; identifier experience (median number of earlier identifications in the family) | plan section 7.3, item 5; the first freeze used only the histories of the part's phase-2 rows, scaled by the phase-1 fraction, and no experience |
| scripts/confirm_run.py, exact_duplicates; src/confirm/acquisition.py, parse_histories | exact SHA-256 duplicates keep the observation with the lowest numeric observation id of the API record | plan section 5; the first freeze kept the first row in sample order (lowest uuid) |
| scripts/confirm_run.py, report-strata; src/confirm/acquisition.py, cap_fractions | the stratum report shows the phase-2 photographs before and after the registered cap rule and the projected bytes; phase2 and the report use one cap function | plan section 4.3 (counts and projected budget between the phases) |
| scripts/confirm_run.py, analyse-joint | the eight and the six new families analysed together for the groups of section 10 (animals, plants, Polyporaceae) and the Spearman relation over the 14 families | plan section 10, heterogeneity (groups across both sets; secondary relation over 14 families) |
| scripts/confirm_driver.py (new) | the four sets from the registered values; run order; pre-approval between the phases; after an API stop (30 minutes of failure) a wait of 60 minutes and a resume, at most three times; progress log with thread count and hardware | plan sections 3, 4.3 and 8; task N18 |
| configs/confirmatory.yaml | new block run_settings (download limits and counters, API waits, minimum free space); no registered value changed | settings of the run |
| tests/test_freeze_v2.py (new) | unit tests of the corrections | - |

No registered value, set, size, fraction, threshold or definition of the plan is changed.

## Run order

Driver scripts/confirm_driver.py, confirmatory mode, every step through scripts/confirm_run.py:

1. frame: the eight families (windows W and W2, locked half) and the 36 other families (window W, both halves);
2. for each set in the order eight_W, eight_W2, new_W, replication_W: phase1, covariates, histories, report-strata, pre-approval (counts and projected budget only), phase2, download, predict;
3. analyse (each set), h6 (new_W and replication_W), analyse-joint (eight_W and new_W), decide.

## Registration-lock procedure

configs/registration_lock.json is written only by the confirmatory task, after the registration and its update note. It holds the registration identifier, the code commit of this record and the date; in confirmatory mode the guard allows protected data only with a non-empty registration_id and code_commit.
