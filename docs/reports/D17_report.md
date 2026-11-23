# D17 - Membership of the analysed photographs in the training data of BioCLIP 2.5 Huge (post hoc)

Decision D17 in docs/PLAN.md (post hoc, written after the confirmatory results were seen; commit 7eb275e, before anything was downloaded for it). Scripts: scripts/d17_fetch_provenance.py, scripts/d17_membership.py, scripts/d17_report.py; outputs in outputs/D17/ (not tracked). No decision rule; the results are described.

## Source file

dataset/metadata/provenance.parquet of imageomics/TreeOfLife-200M at commit 97e2340877d3a2ccad78078431fa68f404ed4870, downloaded with range requests to outputs/tmp/tol200m_97e2340/ (git-ignored; kept until this report has been checked).

| check | value | result |
|---|---|---|
| bytes on disk against the repository listing (10,286,368,327) | 10,286,368,327 | PASS |
| SHA-256 of the downloaded file | 7a4b02601f7352be68024d3b8012534949561430760875ff66b17efd0f3eb3a5 | recorded |
| SHA-256 against the LFS identifier sent by the server (x-linked-etag) | 7a4b02601f7352be68024d3b8012534949561430760875ff66b17efd0f3eb3a5 | PASS |
| rows read against the file footer (233,055,986) | 233,055,986 | PASS |

Footer: 233,055,986 rows in 78 row groups; written by parquet-mr version 1.13.1 (build db4183109d5b734ec5930d870cdae161e408ddba). Columns (name, type): uuid (string); source_id (string); data_source (string); source_url (string); license_name (string); copyright_owner (string); license_link (string); title (string); bibliographicCitation (string).

## Reading and parsing rule

The file was read row group by row group and, within a row group, column by column (4 row groups in parallel, each with its own file handle). Columns searched: every string column (uuid, source_id, data_source, source_url, license_name, copyright_owner, license_link, title, bibliographicCitation). Values of the columns are not stored or reported; only counts and photo identifiers.

- Rule E, the rule of the earlier gates for source_url: host = lower-case text between the first "://" and the next "/", ":", "?" or "#"; the host must equal inaturalist-open-data.s3.amazonaws.com; the identifier is the first match of "/photos/(digits)/"; more than 18 digits counts as not matching.
- Rule X, every string column including source_url: the value contains "inaturalist" (case-insensitive); the identifier is the first match, in the lower-cased value, of "://<host containing inaturalist>[:port]/photos/(digits)" (any iNaturalist host; a trailing "/" is not required); more than 18 digits counts as not matching.
- A record's iNaturalist photo identifier is that of rule E if there is one, otherwise the first rule-X identifier over the columns in file order. A record refers to iNaturalist if any string column contains "inaturalist" (case-insensitive).
- Source: the value of data_source (gbif = GBIF, eol = EOL, bioscan = BIOSCAN-5M, fathomnet = FathomNet, any other value listed as other). Publisher column: none in this file, so no per-publisher count is possible from it.

## Records per source

| source | records | with an iNaturalist photo id | of which rule E | of which rule X only | largest id | above 367,752,438 | records referring to iNaturalist |
|---|---|---|---|---|---|---|---|
| GBIF | 222,660,750 | 134,879,030 | 134,866,701 | 12,329 | 367,752,438 | 0 | 134,879,156 |
| EOL | 5,206,441 | 26 | 0 | 26 | 221,678,433 | 0 | 2,701 |
| BIOSCAN-5M | 5,150,850 | 0 | 0 | 0 | - | 0 | 0 |
| FathomNet | 37,945 | 0 | 0 | 0 | - | 0 | 0 |

Records referring to iNaturalist, per source and column:

| source | uuid | source_id | data_source | source_url | license_name | copyright_owner | license_link | title | bibliographicCitation |
|---|---|---|---|---|---|---|---|---|---|
| GBIF | 0 | 0 | 0 | 134,879,156 | 0 | 30,902 | 0 | 0 | 196 |
| EOL | 0 | 0 | 0 | 0 | 0 | 2,701 | 0 | 0 | 0 |
| BIOSCAN-5M | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| FathomNet | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

EOL records: 5,206,441; with any reference to iNaturalist in their columns: 2,701; with an iNaturalist photo identifier: 26.

Whole file: 134,879,056 records with an iNaturalist photo identifier; 79,691,610 distinct identifiers; largest 367,752,438; distinct identifiers above 367,752,438: 0. Comparison with M1 of the earlier gates (revision a8f38b4, 79,680,896 distinct identifiers by rule E): 79,665,648 of them are also identifiers of this file; 25,962 identifiers of this file are not in M1.

## Analysed photographs

Every photo identifier (all positions) of every observation of the analysed sets, from photos.csv.gz of the snapshot of 2026-10-27 (manifest check: PASS; 511,879,544 snapshot rows read). Only photo identifiers were read for this check: no photograph, identification history or model output. Sets: the phase-2 samples (selected rows) of the four confirmatory sets; the D14 additions (observations whose first photograph is in the D14 photograph manifest, found in the D14 raw responses: 220 of 220 first photographs); the D4 sample (all rows); set B of D16 (all sampled rows).

Observations: 191,352 distinct; with photographs in the snapshot: 191,352; without: 0. Stored first photograph found among the snapshot photographs of its observation: 167,603 of 167,603. Distinct photographs: 326,994; identifiers from 401,310,004 to 756,229,386; at or below 367,752,438: 0.

## Intersections

Analysed photographs whose identifier is an iNaturalist photo identifier of the provenance file at 97e2340877d3: 0. Analysed photographs in M1 (revision a8f38b4, available in the inputs): 0.

| set | family | stratum | observations | photographs | in the file at 97e2340877d3 | of which first photographs | observations with a photograph in it | in M1 |
|---|---|---|---|---|---|---|---|---|
| D14 additions | Ardeidae | D14 addition | 220 | 331 | 0 | 0 | 0 | 0 |
| D16 set B | Anatidae | sample | 1,500 | 2,377 | 0 | 0 | 0 | 0 |
| D16 set B | Asteraceae | sample | 1,500 | 2,572 | 0 | 0 | 0 | 0 |
| D16 set B | Columbidae | sample | 1,500 | 2,358 | 0 | 0 | 0 | 0 |
| D16 set B | Fabaceae | sample | 1,500 | 2,524 | 0 | 0 | 0 | 0 |
| D16 set B | Lamiaceae | sample | 1,500 | 2,360 | 0 | 0 | 0 | 0 |
| D16 set B | Nymphalidae | sample | 1,500 | 2,512 | 0 | 0 | 0 | 0 |
| D16 set B | Rosaceae | sample | 1,500 | 2,480 | 0 | 0 | 0 | 0 |
| D16 set B | Sciuridae | sample | 1,500 | 2,530 | 0 | 0 | 0 | 0 |
| D4 sample | Anatidae | A0 | 2,156 | 3,465 | 0 | 0 | 0 | 0 |
| D4 sample | Anatidae | A1 | 243 | 382 | 0 | 0 | 0 | 0 |
| D4 sample | Anatidae | A2 | 84 | 115 | 0 | 0 | 0 | 0 |
| D4 sample | Anatidae | A3 | 15 | 23 | 0 | 0 | 0 | 0 |
| D4 sample | Anatidae | B1 | 345 | 599 | 0 | 0 | 0 | 0 |
| D4 sample | Anatidae | B2 | 155 | 286 | 0 | 0 | 0 | 0 |
| D4 sample | Anatidae | none (no stratum in the D4 table) | 2 | 7 | 0 | 0 | 0 | 0 |
| D4 sample | Asteraceae | A0 | 1,158 | 2,110 | 0 | 0 | 0 | 0 |
| D4 sample | Asteraceae | A1 | 604 | 1,133 | 0 | 0 | 0 | 0 |
| D4 sample | Asteraceae | A2 | 520 | 923 | 0 | 0 | 0 | 0 |
| D4 sample | Asteraceae | A3 | 215 | 357 | 0 | 0 | 0 | 0 |
| D4 sample | Asteraceae | B1 | 438 | 908 | 0 | 0 | 0 | 0 |
| D4 sample | Asteraceae | B2 | 62 | 118 | 0 | 0 | 0 | 0 |
| D4 sample | Asteraceae | none (no stratum in the D4 table) | 3 | 6 | 0 | 0 | 0 | 0 |
| D4 sample | Columbidae | A0 | 2,211 | 3,502 | 0 | 0 | 0 | 0 |
| D4 sample | Columbidae | A1 | 201 | 294 | 0 | 0 | 0 | 0 |
| D4 sample | Columbidae | A2 | 67 | 118 | 0 | 0 | 0 | 0 |
| D4 sample | Columbidae | A3 | 21 | 27 | 0 | 0 | 0 | 0 |
| D4 sample | Columbidae | B1 | 168 | 248 | 0 | 0 | 0 | 0 |
| D4 sample | Columbidae | B2 | 86 | 125 | 0 | 0 | 0 | 0 |
| D4 sample | Fabaceae | A0 | 1,350 | 2,389 | 0 | 0 | 0 | 0 |
| D4 sample | Fabaceae | A1 | 565 | 945 | 0 | 0 | 0 | 0 |
| D4 sample | Fabaceae | A2 | 494 | 776 | 0 | 0 | 0 | 0 |
| D4 sample | Fabaceae | A3 | 91 | 168 | 0 | 0 | 0 | 0 |
| D4 sample | Fabaceae | B1 | 414 | 829 | 0 | 0 | 0 | 0 |
| D4 sample | Fabaceae | B2 | 85 | 166 | 0 | 0 | 0 | 0 |
| D4 sample | Lamiaceae | A0 | 1,338 | 2,195 | 0 | 0 | 0 | 0 |
| D4 sample | Lamiaceae | A1 | 621 | 1,031 | 0 | 0 | 0 | 0 |
| D4 sample | Lamiaceae | A2 | 425 | 763 | 0 | 0 | 0 | 0 |
| D4 sample | Lamiaceae | A3 | 113 | 192 | 0 | 0 | 0 | 0 |
| D4 sample | Lamiaceae | B1 | 439 | 765 | 0 | 0 | 0 | 0 |
| D4 sample | Lamiaceae | B2 | 61 | 108 | 0 | 0 | 0 | 0 |
| D4 sample | Lamiaceae | none (no stratum in the D4 table) | 2 | 5 | 0 | 0 | 0 | 0 |
| D4 sample | Nymphalidae | A0 | 2,114 | 3,404 | 0 | 0 | 0 | 0 |
| D4 sample | Nymphalidae | A1 | 235 | 389 | 0 | 0 | 0 | 0 |
| D4 sample | Nymphalidae | A2 | 116 | 190 | 0 | 0 | 0 | 0 |
| D4 sample | Nymphalidae | A3 | 33 | 55 | 0 | 0 | 0 | 0 |
| D4 sample | Nymphalidae | B1 | 368 | 597 | 0 | 0 | 0 | 0 |
| D4 sample | Nymphalidae | B2 | 131 | 230 | 0 | 0 | 0 | 0 |
| D4 sample | Nymphalidae | none (no stratum in the D4 table) | 2 | 3 | 0 | 0 | 0 | 0 |
| D4 sample | Rosaceae | A0 | 1,227 | 2,045 | 0 | 0 | 0 | 0 |
| D4 sample | Rosaceae | A1 | 586 | 985 | 0 | 0 | 0 | 0 |
| D4 sample | Rosaceae | A2 | 520 | 851 | 0 | 0 | 0 | 0 |
| D4 sample | Rosaceae | A3 | 166 | 253 | 0 | 0 | 0 | 0 |
| D4 sample | Rosaceae | B1 | 430 | 775 | 0 | 0 | 0 | 0 |
| D4 sample | Rosaceae | B2 | 70 | 141 | 0 | 0 | 0 | 0 |
| D4 sample | Sciuridae | A0 | 1,875 | 3,181 | 0 | 0 | 0 | 0 |
| D4 sample | Sciuridae | A1 | 423 | 708 | 0 | 0 | 0 | 0 |
| D4 sample | Sciuridae | A2 | 154 | 248 | 0 | 0 | 0 | 0 |
| D4 sample | Sciuridae | A3 | 44 | 88 | 0 | 0 | 0 | 0 |
| D4 sample | Sciuridae | B1 | 362 | 660 | 0 | 0 | 0 | 0 |
| D4 sample | Sciuridae | B2 | 138 | 285 | 0 | 0 | 0 | 0 |
| D4 sample | Sciuridae | none (no stratum in the D4 table) | 3 | 4 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Anatidae | A0 | 5,166 | 8,352 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Anatidae | A1 | 986 | 1,634 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Anatidae | A2 | 316 | 514 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Anatidae | A3 | 107 | 173 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Anatidae | B1 | 87 | 140 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Anatidae | B2 | 71 | 109 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Asteraceae | A0 | 1,613 | 2,755 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Asteraceae | A1 | 1,494 | 2,658 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Asteraceae | A2 | 1,481 | 2,568 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Asteraceae | A3 | 572 | 1,017 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Asteraceae | B1 | 2,258 | 4,171 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Asteraceae | B2 | 706 | 1,312 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Columbidae | A0 | 5,272 | 7,910 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Columbidae | A1 | 852 | 1,406 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Columbidae | A2 | 330 | 546 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Columbidae | A3 | 121 | 212 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Columbidae | B1 | 44 | 76 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Columbidae | B2 | 55 | 90 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Fabaceae | A0 | 2,162 | 3,637 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Fabaceae | A1 | 2,041 | 3,459 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Fabaceae | A2 | 1,773 | 2,910 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Fabaceae | A3 | 352 | 617 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Fabaceae | B1 | 1,474 | 2,824 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Fabaceae | B2 | 553 | 1,064 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Lamiaceae | A0 | 2,263 | 3,661 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Lamiaceae | A1 | 2,138 | 3,565 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Lamiaceae | A2 | 1,421 | 2,355 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Lamiaceae | A3 | 441 | 743 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Lamiaceae | B1 | 1,542 | 2,853 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Lamiaceae | B2 | 383 | 738 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Nymphalidae | A0 | 4,524 | 7,402 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Nymphalidae | A1 | 1,008 | 1,673 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Nymphalidae | A2 | 483 | 830 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Nymphalidae | A3 | 130 | 216 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Nymphalidae | B1 | 501 | 798 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Nymphalidae | B2 | 326 | 532 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Rosaceae | A0 | 1,568 | 2,451 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Rosaceae | A1 | 1,522 | 2,533 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Rosaceae | A2 | 1,385 | 2,279 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Rosaceae | A3 | 471 | 763 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Rosaceae | B1 | 2,388 | 4,268 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Rosaceae | B2 | 700 | 1,271 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Sciuridae | A0 | 4,330 | 7,328 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Sciuridae | A1 | 1,789 | 2,975 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Sciuridae | A2 | 594 | 1,024 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Sciuridae | A3 | 158 | 276 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Sciuridae | B1 | 288 | 600 | 0 | 0 | 0 | 0 |
| eight_W phase 2 | Sciuridae | B2 | 213 | 361 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Anatidae | A0 | 2,197 | 3,446 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Anatidae | A1 | 389 | 611 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Anatidae | A2 | 108 | 173 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Anatidae | A3 | 13 | 16 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Anatidae | B1 | 31 | 45 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Anatidae | B2 | 59 | 104 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Asteraceae | A0 | 819 | 1,391 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Asteraceae | A1 | 965 | 1,644 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Asteraceae | A2 | 530 | 826 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Asteraceae | A3 | 129 | 222 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Asteraceae | B1 | 975 | 1,713 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Asteraceae | B2 | 393 | 703 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Columbidae | A0 | 2,187 | 3,284 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Columbidae | A1 | 488 | 746 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Columbidae | A2 | 105 | 153 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Columbidae | A3 | 25 | 48 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Columbidae | B1 | 18 | 21 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Columbidae | B2 | 28 | 36 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Fabaceae | A0 | 776 | 1,396 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Fabaceae | A1 | 943 | 1,765 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Fabaceae | A2 | 672 | 1,215 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Fabaceae | A3 | 197 | 344 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Fabaceae | B1 | 933 | 1,762 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Fabaceae | B2 | 493 | 951 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Lamiaceae | A0 | 1,278 | 2,032 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Lamiaceae | A1 | 1,258 | 1,974 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Lamiaceae | A2 | 591 | 941 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Lamiaceae | A3 | 111 | 208 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Lamiaceae | B1 | 469 | 806 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Lamiaceae | B2 | 207 | 398 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Nymphalidae | A0 | 1,755 | 2,757 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Nymphalidae | A1 | 538 | 876 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Nymphalidae | A2 | 248 | 418 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Nymphalidae | A3 | 112 | 191 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Nymphalidae | B1 | 280 | 403 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Nymphalidae | B2 | 311 | 505 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Rosaceae | A0 | 666 | 1,183 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Rosaceae | A1 | 795 | 1,468 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Rosaceae | A2 | 535 | 995 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Rosaceae | A3 | 151 | 265 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Rosaceae | B1 | 1,154 | 2,030 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Rosaceae | B2 | 451 | 883 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Sciuridae | A0 | 1,954 | 3,236 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Sciuridae | A1 | 700 | 1,211 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Sciuridae | A2 | 296 | 548 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Sciuridae | A3 | 63 | 88 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Sciuridae | B1 | 105 | 176 | 0 | 0 | 0 | 0 |
| eight_W2 phase 2 | Sciuridae | B2 | 69 | 131 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Araneidae | A0 | 2,631 | 4,608 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Araneidae | A1 | 1,417 | 2,511 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Araneidae | A2 | 643 | 1,171 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Araneidae | A3 | 122 | 244 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Araneidae | B1 | 473 | 855 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Araneidae | B2 | 971 | 1,803 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Colubridae | A0 | 3,938 | 7,570 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Colubridae | A1 | 990 | 1,786 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Colubridae | A2 | 324 | 585 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Colubridae | A3 | 570 | 1,051 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Colubridae | B1 | 24 | 33 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Colubridae | B2 | 147 | 281 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Pinaceae | A0 | 1,378 | 2,477 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Pinaceae | A1 | 1,657 | 2,769 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Pinaceae | A2 | 1,195 | 2,088 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Pinaceae | A3 | 459 | 701 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Pinaceae | B1 | 1,052 | 1,820 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Pinaceae | B2 | 421 | 762 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Poaceae | A0 | 1,297 | 2,423 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Poaceae | A1 | 1,537 | 2,831 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Poaceae | A2 | 991 | 1,775 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Poaceae | A3 | 305 | 602 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Poaceae | B1 | 1,252 | 2,624 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Poaceae | B2 | 393 | 858 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Polyporaceae | A0 | 818 | 1,796 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Polyporaceae | A1 | 1,022 | 2,223 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Polyporaceae | A2 | 1,010 | 2,137 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Polyporaceae | A3 | 295 | 681 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Polyporaceae | B1 | 1,563 | 3,154 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Polyporaceae | B2 | 819 | 1,865 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Ranidae | A0 | 3,028 | 4,636 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Ranidae | A1 | 1,929 | 2,809 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Ranidae | A2 | 725 | 1,107 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Ranidae | A3 | 135 | 224 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Ranidae | B1 | 164 | 241 | 0 | 0 | 0 | 0 |
| new_W phase 2 | Ranidae | B2 | 598 | 924 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Acrididae | A0 | 306 | 530 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Acrididae | A1 | 416 | 688 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Acrididae | A2 | 400 | 712 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Acrididae | A3 | 71 | 124 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Apiaceae | A0 | 392 | 681 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Apiaceae | A1 | 371 | 657 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Apiaceae | A2 | 273 | 459 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Apiaceae | A3 | 70 | 123 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Apocynaceae | A0 | 516 | 796 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Apocynaceae | A1 | 270 | 433 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Apocynaceae | A2 | 146 | 236 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Apocynaceae | A3 | 52 | 77 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Ardeidae | A0 | 473 | 861 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Ardeidae | A1 | 90 | 139 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Ardeidae | A2 | 50 | 89 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Ardeidae | A3 | 14 | 25 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Asparagaceae | A0 | 390 | 596 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Asparagaceae | A1 | 342 | 534 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Asparagaceae | A2 | 319 | 509 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Asparagaceae | A3 | 57 | 97 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Caprifoliaceae | A0 | 380 | 631 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Caprifoliaceae | A1 | 383 | 632 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Caprifoliaceae | A2 | 250 | 402 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Caprifoliaceae | A3 | 107 | 180 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Caryophyllaceae | A0 | 389 | 673 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Caryophyllaceae | A1 | 315 | 513 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Caryophyllaceae | A2 | 346 | 609 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Caryophyllaceae | A3 | 59 | 103 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Chrysomelidae | A0 | 470 | 768 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Chrysomelidae | A1 | 324 | 555 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Chrysomelidae | A2 | 171 | 298 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Chrysomelidae | A3 | 63 | 104 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Coccinellidae | A0 | 562 | 893 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Coccinellidae | A1 | 284 | 469 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Coccinellidae | A2 | 69 | 118 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Coccinellidae | A3 | 21 | 39 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Cyperaceae | A0 | 322 | 627 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Cyperaceae | A1 | 363 | 709 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Cyperaceae | A2 | 375 | 707 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Cyperaceae | A3 | 117 | 232 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Erebidae | A0 | 522 | 767 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Erebidae | A1 | 211 | 349 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Erebidae | A2 | 190 | 305 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Erebidae | A3 | 54 | 82 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Ericaceae | A0 | 460 | 766 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Ericaceae | A1 | 351 | 539 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Ericaceae | A2 | 187 | 304 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Ericaceae | A3 | 42 | 65 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Fagaceae | A0 | 362 | 683 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Fagaceae | A1 | 374 | 704 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Fagaceae | A2 | 301 | 556 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Fagaceae | A3 | 101 | 182 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Formicidae | A0 | 472 | 1,178 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Formicidae | A1 | 308 | 587 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Formicidae | A2 | 200 | 385 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Formicidae | A3 | 45 | 83 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Geometridae | A0 | 560 | 669 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Geometridae | A1 | 226 | 313 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Geometridae | A2 | 128 | 191 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Geometridae | A3 | 26 | 40 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Hesperiidae | A0 | 469 | 741 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Hesperiidae | A1 | 318 | 513 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Hesperiidae | A2 | 192 | 335 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Hesperiidae | A3 | 50 | 79 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Laridae | A0 | 524 | 889 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Laridae | A1 | 244 | 395 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Laridae | A2 | 177 | 295 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Laridae | A3 | 27 | 56 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Libellulidae | A0 | 588 | 934 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Libellulidae | A1 | 192 | 306 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Libellulidae | A2 | 79 | 112 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Libellulidae | A3 | 52 | 109 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Lycaenidae | A0 | 487 | 779 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Lycaenidae | A1 | 190 | 328 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Lycaenidae | A2 | 113 | 199 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Lycaenidae | A3 | 220 | 387 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Malvaceae | A0 | 340 | 617 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Malvaceae | A1 | 358 | 595 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Malvaceae | A2 | 326 | 552 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Malvaceae | A3 | 137 | 237 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Noctuidae | A0 | 450 | 616 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Noctuidae | A1 | 294 | 438 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Noctuidae | A2 | 161 | 237 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Noctuidae | A3 | 141 | 196 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Onagraceae | A0 | 420 | 686 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Onagraceae | A1 | 411 | 702 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Onagraceae | A2 | 182 | 337 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Onagraceae | A3 | 64 | 123 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Pentatomidae | A0 | 574 | 926 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Pentatomidae | A1 | 204 | 343 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Pentatomidae | A2 | 85 | 146 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Pentatomidae | A3 | 62 | 112 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Pieridae | A0 | 424 | 654 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Pieridae | A1 | 321 | 467 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Pieridae | A2 | 248 | 387 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Pieridae | A3 | 79 | 150 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Plantaginaceae | A0 | 382 | 616 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Plantaginaceae | A1 | 346 | 567 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Plantaginaceae | A2 | 317 | 508 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Plantaginaceae | A3 | 71 | 103 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Polygonaceae | A0 | 316 | 606 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Polygonaceae | A1 | 328 | 637 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Polygonaceae | A2 | 334 | 593 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Polygonaceae | A3 | 203 | 417 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Ranunculaceae | A0 | 337 | 543 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Ranunculaceae | A1 | 363 | 629 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Ranunculaceae | A2 | 378 | 637 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Ranunculaceae | A3 | 83 | 140 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Syrphidae | A0 | 556 | 965 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Syrphidae | A1 | 202 | 396 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Syrphidae | A2 | 151 | 283 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Syrphidae | A3 | 34 | 59 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Tettigoniidae | A0 | 439 | 779 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Tettigoniidae | A1 | 296 | 528 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Tettigoniidae | A2 | 249 | 437 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Tettigoniidae | A3 | 76 | 124 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Vespidae | A0 | 603 | 1,290 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Vespidae | A1 | 156 | 313 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Vespidae | A2 | 67 | 148 | 0 | 0 | 0 | 0 |
| replication_W phase 2 | Vespidae | A3 | 70 | 115 | 0 | 0 | 0 | 0 |

## Matching photographs

None.

Run time of the provenance pass: 2.5 minutes; of the snapshot pass: 2.4 minutes.
