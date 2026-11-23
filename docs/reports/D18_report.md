# D18 - Illustrative panel of example photographs (post hoc)

Decision D18 in docs/PLAN.md (post hoc; registered in commit 316601b) and D18 addendum 1 (commit 6a04e63, before any draw). Illustrative figure, not an analysis. Script: scripts/d18_examples.py.

Status: done: panel built.

First attempt under the rule of D18 (task N24): the run stopped at the choice of species, before any draw, because CC0 or CC BY photographs of stratum A3 were missing in Columbidae and Anatidae; no image or prediction was looked at and no output was written. Addendum 1 was registered after that.

First run under addendum 1 (task N25): coding error. The D13 table stores the licence as an index into the licence list of configs/confirmatory.yaml (0 = CC0, 1 = CC-BY, 2 = CC-BY-NC); the script read these integers as text codes, so no W2 row was eligible and the pool held W rows only. The error was corrected and the run repeated with the same rule and seed; the outputs of the first run are kept in outputs/N25/run1_licence_code_error/ (not tracked). This report is that of the corrected run.

## Implementation details fixed before the run

- Eligible observation: research-grade row of the pooled D4 sample (W) and D13 rehearsal (W2, rows selected in phase 2) with a stored prediction of BioCLIP 2.5 Huge and a snapshot licence CC0 or CC BY.
- Sides per species: fast = A0; slow = A3 if the species has at least two eligible A3 observations, otherwise A2 and A3 together.
- Species: among species with at least two eligible observations on each side, the largest number of eligible observations on the two sides together; ties broken by the lower taxon id.
- Families: the first two families with such a species in the registered order of each group.
- Draw: one generator (seed 20261124) in panel order and, within a family, fast then slow; candidates ordered by observation_uuid and permuted; the first two whose stored photograph is present are used.

## Controls

| control | result | detail |
|---|---|---|
| input files equal to the tier-1 manifest | PASS | 449 of 449 |
| D13 grade values known | PASS | needs_id, research |
| D13 licence codes are indices of frame.licences | PASS | 0 = CC0, 1 = CC-BY, 2 = CC-BY-NC |
| no locked observer in the pool | PASS | 14,234 observers |
| prediction photo = first photo; community species = row species | PASS | 32,029 rows |
| no observation in both windows | PASS |  |
| family order = decreasing Delta of H1 within each group | PASS | Columbidae 12.33; Anatidae 11.39; Sciuridae 5.07; Nymphalidae 2.50; Fabaceae 1.25; Rosaceae 1.23; Lamiaceae 0.81; Asteraceae 0.68 |
| two photographs drawn: Columbidae, fast side | PASS | 189 candidates |
| two photographs drawn: Columbidae, slow side | PASS | 2 candidates |
| two photographs drawn: Anatidae, fast side | PASS | 144 candidates |
| two photographs drawn: Anatidae, slow side | PASS | 7 candidates |
| two photographs drawn: Fabaceae, fast side | PASS | 23 candidates |
| two photographs drawn: Fabaceae, slow side | PASS | 13 candidates |
| two photographs drawn: Rosaceae, fast side | PASS | 25 candidates |
| two photographs drawn: Rosaceae, slow side | PASS | 4 candidates |
| every drawn photograph found in the stored responses | PASS | 16 of 16 |
| stratum agrees with T for every drawn row | PASS |  |
| photo owner = sample observer for every drawn row | PASS |  |

## Counts

| count | value |
|---|---|
| pooled rows A0, A2, A3 with a prediction | 32,029 |
| of which CC0 or CC BY in the snapshot | 4,772 |
| W | 2,492 |
| W2 | 2,280 |

Family replacements: none.

## Species (three largest counts per family, species with at least two eligible observations on each side)

| family | rank | taxon id | species | A0 | A2 | A3 | slow side | fast+slow |
|---|---|---|---|---|---|---|---|---|
| Columbidae | 1 | 3017 | Columba livia | 189 | 1 | 2 | A3 | 191 |
| Columbidae | 2 | 3048 | Columba palumbus | 80 | 4 | 0 | A2+A3 | 84 |
| Columbidae | 3 | 2969 | Streptopelia decaocto | 66 | 2 | 0 | A2+A3 | 68 |
| Anatidae | 1 | 6930 | Anas platyrhynchos | 144 | 6 | 1 | A2+A3 | 151 |
| Anatidae | 2 | 6937 | Anas crecca | 16 | 2 | 0 | A2+A3 | 18 |
| Anatidae | 3 | 558439 | Mareca strepera | 16 | 2 | 0 | A2+A3 | 18 |
| Sciuridae | 1 | 46017 | Sciurus carolinensis | 181 | 2 | 0 | A2+A3 | 183 |
| Sciuridae | 2 | 46020 | Sciurus niger | 49 | 1 | 1 | A2+A3 | 51 |
| Sciuridae | 3 | 46001 | Sciurus vulgaris | 38 | 3 | 0 | A2+A3 | 41 |
| Nymphalidae | 1 | 49761 | Anartia jatrophae | 11 | 2 | 0 | A2+A3 | 13 |
| Nymphalidae | 2 | 52925 | Phyciodes tharos | 9 | 2 | 0 | A2+A3 | 11 |
| Nymphalidae | 3 | 123628 | Argynnis paphia | 4 | 2 | 0 | A2+A3 | 6 |
| Fabaceae | 1 | 51875 | Trifolium pratense | 23 | 12 | 1 | A2+A3 | 36 |
| Fabaceae | 2 | 55745 | Trifolium repens | 19 | 13 | 0 | A2+A3 | 32 |
| Fabaceae | 3 | 47435 | Lotus corniculatus | 7 | 10 | 1 | A2+A3 | 18 |
| Rosaceae | 1 | 55891 | Geum urbanum | 25 | 15 | 4 | A3 | 29 |
| Rosaceae | 2 | 53405 | Heteromeles arbutifolia | 14 | 10 | 0 | A2+A3 | 24 |
| Rosaceae | 3 | 63134 | Filipendula ulmaria | 20 | 3 | 0 | A2+A3 | 23 |
| Lamiaceae | 1 | 55851 | Lamium purpureum | 53 | 15 | 0 | A2+A3 | 68 |
| Lamiaceae | 2 | 52764 | Prunella vulgaris | 52 | 11 | 3 | A3 | 55 |
| Lamiaceae | 3 | 55459 | Lamium amplexicaule | 33 | 3 | 0 | A2+A3 | 36 |
| Asteraceae | 1 | 52821 | Achillea millefolium | 16 | 6 | 0 | A2+A3 | 22 |
| Asteraceae | 2 | 52913 | Cichorium intybus | 16 | 1 | 1 | A2+A3 | 18 |
| Asteraceae | 3 | 52989 | Cirsium vulgare | 12 | 5 | 4 | A3 | 16 |

## Drawn observations

| family | species | side | stratum | window | draw | observation id | photo id | licence | days to research grade | prediction of BioCLIP 2.5 Huge | correct |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Columbidae | Columba livia | fast | A0 | W | 1 | 232914141 | 413861886 | CC BY | 0.004 | Columba livia | yes |
| Columbidae | Columba livia | fast | A0 | W2 | 2 | 257422946 | 461782503 | CC0 | 0.001 | Columba livia | yes |
| Columbidae | Columba livia | slow | A3 | W2 | 1 | 259919203 | 466672897 | CC BY | 633.766 | Zenaida macroura | no |
| Columbidae | Columba livia | slow | A3 | W2 | 2 | 264916366 | 475758272 | CC0 | 459.917 | Columba palumbus | no |
| Anatidae | Anas platyrhynchos | fast | A0 | W | 1 | 239451241 | 426465930 | CC BY | 0.032 | Anas platyrhynchos | yes |
| Anatidae | Anas platyrhynchos | fast | A0 | W2 | 2 | 259363032 | 465565798 | CC0 | 0.001 | Anas platyrhynchos | yes |
| Anatidae | Anas platyrhynchos | slow | A2 | W | 1 | 245328116 | 437754689 | CC0 | 42.701 | Anas platyrhynchos | yes |
| Anatidae | Anas platyrhynchos | slow | A2 | W2 | 2 | 259786975 | 466417560 | CC0 | 67.97 | Anas platyrhynchos | yes |
| Fabaceae | Trifolium pratense | fast | A0 | W | 1 | 259012646 | 464849500 | CC BY | 0.254 | Trifolium pratense | yes |
| Fabaceae | Trifolium pratense | fast | A0 | W | 2 | 229210727 | 406843155 | CC BY | 0.001 | Trifolium pratense | yes |
| Fabaceae | Trifolium pratense | slow | A2 | W | 1 | 228800349 | 406064248 | CC BY | 67.624 | Trifolium pratense | yes |
| Fabaceae | Trifolium pratense | slow | A2 | W | 2 | 230116577 | 408554544 | CC BY | 40.929 | Trifolium pratense | yes |
| Rosaceae | Geum urbanum | fast | A0 | W2 | 1 | 257702611 | 462335756 | CC BY | 0.135 | Geum urbanum | yes |
| Rosaceae | Geum urbanum | fast | A0 | W | 2 | 229762454 | 407878780 | CC BY | 0.404 | Geum urbanum | yes |
| Rosaceae | Geum urbanum | slow | A3 | W2 | 1 | 260270082 | 467373231 | CC BY | 366.146 | Geum urbanum | yes |
| Rosaceae | Geum urbanum | slow | A3 | W2 | 2 | 260271219 | 467375497 | CC BY | 366.139 | Geum urbanum | yes |

Replacements of drawn photographs that were not present: none.

Run time: 70 s.
