# D16 - Exposure test of BioCLIP 2.5 Huge (post hoc): stopped before the predictions

Decision D16 in docs/PLAN.md (post hoc, written after the confirmatory results were seen; registered in commit 0a5843e
before any part of D16 was run). Development half only. Script: scripts/d16_run.py; outputs in outputs/D16/ (row tables,
raw responses and photographs not tracked).

## Status

D16 stopped at the photograph download of set B, because the download limit of task N21 (1.5 GB) was reached. No
prediction and no estimate of D16 was computed; the reading fixed in D16 has no result.

## What was done

- Frame of set B (frozen frame code, development half, eight families, observed 2026-08-28 to 2026-10-20, photo ids
  above max_M1, licence and size filters, label-space species): snapshot manifest checks of observations.csv.gz,
  photos.csv.gz and taxa.csv.gz PASS; 673,473 development-half rows of the eight families in the window before the
  photograph and label filters; 514,283 frame rows (both grades); 5.6 minutes.
- Sample (research-grade frame, up to 1,500 per family, seed 20261124): 1,500 in every family; research-grade frame
  rows: Fabaceae 27,732; Asteraceae 78,235; Columbidae 17,287; Lamiaceae 14,050; Nymphalidae 60,053; Anatidae 35,899;
  Rosaceae 17,590; Sciuridae 16,592.
- Histories (public API v1, 60 requests of up to 200 observations, at most one per second, 539 seconds): 11,993 of
  12,000 returned; failed batches 0; hidden identifications 0; identification time reconstructed for 11,989; T < 1 day
  for 9,305.
- Photographs (medium size) of the 9,305 rows with T < 1 day, in sample order: 8,797 obtained (2 failed after 3
  retries) when the download budget of 1,500,000,000 bytes was reached; bytes downloaded 1,505,970,832 (the budget is
  checked before each batch of 400 photographs, so the last batch passed the limit by 5,970,832 bytes).

| family | rows with T < 1 day | photographs obtained |
|---|---|---|
| Fabaceae | 990 | 990 |
| Asteraceae | 993 | 993 |
| Columbidae | 1,348 | 1,347 |
| Lamiaceae | 960 | 960 |
| Nymphalidae | 1,342 | 1,341 |
| Anatidae | 1,359 | 1,359 |
| Rosaceae | 1,040 | 1,040 |
| Sciuridae | 1,273 | 768 |

The mean size of a medium photograph in set B was about 171 KB, against about 127 KB in the confirmatory sets on which
the budget had been projected.

## What remains

Completing D16 as registered needs the 505 remaining Sciuridae photographs (about 0.09 GB), then the predictions of the
three models and the estimate. The run resumes from its saved outputs (frame, sample, histories and the downloaded
photographs are kept); it needs a download allowance above the limit of task N21. Set A (D4 rows of the development half
with T < 1 day) was not read for outcomes in this task.
