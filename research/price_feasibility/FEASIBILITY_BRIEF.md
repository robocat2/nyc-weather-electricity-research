# NYC electricity-price extension: feasibility decision

**Decision: STOP before fitting under the agreed strict historical-information rule.** Real forecast weather and NYC price targets exist, but this bounded check did not establish a complete way to recover the lagged-price versions available at each historical prediction cutoff. This is an unresolved data-provenance gap, not evidence that weather has no predictive value or that the demand study failed.

The existing demand project remains unchanged and finished. This extension contains source probes only: **zero price-model fits, zero reported predictive scores, zero trading-profit claims**. No realized future weather or demand estimates were substituted.

## Exact candidate task
At **04:00 America/New_York on day D−1**, predict **NYISO NYC / Zone J, PTID 61761, day-ahead zonal LBMP for hour beginning 18:00 on day D**, in **$/MWh**. The delivery interval is 18:00–19:00 local time.

The standard elapsed time to delivery is **38 hours**, or 37/39 across spring/fall DST. The auction price is normally published on D−1, so time to price revelation is much shorter than time to delivery: NYISO's Market Participants User's Guide describes approximately 11 a.m. publication (about seven hours after cutoff), while sampled archive member timestamps cluster around 09:31–09:34 (not an exact publication ledger). These are distinct horizons.

The provisional 08:00 cutoff was rejected before fitting because NYISO's training pricing rules show a **05:00 day-ahead market close**. Moving to 04:00 creates a candidate pre-bid-deadline task. Historical applicability of market rules and executable order handling still require verification before any trading backtest.

## What passed and what did not

| Requirement | Evidence obtained | Finding |
|---|---|---|
| Actual historical weather forecasts | Eight NOAA HRRR operational 06 UTC cycles, valid at target hour, 40/41-hour leads; downloaded temperature GRIB messages | Passed sample-level existence and forecast identity checks |
| Forecast availability before cutoff | S3 object Last-Modified precedes cutoff in all eight samples, by 10.6–82.2 minutes | Strong sample-level archive-timing evidence; not a complete historical first-publication ledger or full-period coverage audit |
| NYC price target | Eight NYISO monthly archives parsed; all have exactly one NYC target-hour record and numeric LBMP | Passed sample-level target availability |
| DST | Spring sample has 23 NYC hourly records; fall has 25, with a repeated naive timestamp; target hour 18 remains unique | Candidate target avoids ambiguous repeated hour; full-series processing must handle DST explicitly |
| Price publication/version evidence | Six price columns contain delivery timestamps, geography and prices, with no publication/revision/version field; ZIP member timestamps lack timezone | Insufficient to establish the exact lagged-price vintage known at cutoff |
| Original daily lag-price endpoints | Sixteen one-day/seven-day lag endpoints checked; all return HTTP 404. Current numerical history remains accessible in monthly ZIPs | Daily endpoint headers cannot supply historical version evidence for this sample |
| Correction records | P-29 explicitly stopped being populated in 2012. Checked its stated replacement authority, operational announcements, for January and July 2025 | Notices document validation/corrections, but inspected notices do not supply a full old/new numerical price-vintage ledger |

The daily 404s do **not** mean historical prices are absent: the monthly archives work. The gap is whether an input price was exactly that value at the historical cutoff. Likewise, absent explicit publication columns alone would not prove failure if a verified version archive existed; no such complete reconstruction path was established here.

## Forecast evidence
The fixed input candidate is the **06 UTC HRRR cycle on D−1**, with a 2m-temperature forecast valid at 18:00 local D. These are genuine forecasts, not analyses or realized observations. Each downloaded message starts with GRIB edition 2, contains the expected initialization date/time and lead, identifies temperature (category 0, parameter 0), and specifies height above ground at 2m. Complete messages and HTTP range receipts are retained; no 150–176 MB whole-grid files were needed.

| Delivery date | Forecast lead, hours | Actual elapsed delivery horizon, hours | Archive object timestamp before cutoff, minutes |
|---|---:|---:|---:|
| 2021-01-15 | 41 | 38 | 74.8 |
| 2021-07-15 | 40 | 38 | 23.3 |
| 2023-01-15 | 41 | 38 | 75.0 |
| 2023-07-15 | 40 | 38 | 10.6 |
| 2024-03-10 | 40 | 37 | 74.9 |
| 2024-11-03 | 41 | 39 | 18.9 |
| 2025-01-15 | 41 | 38 | 82.2 |
| 2025-07-15 | 40 | 38 | 22.1 |

[NOAA's archive listing](https://registry.opendata.aws/noaa-hrrr-pds/) identifies the publicly available archive. [AWS documents Last-Modified](https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingMetadata.html) as creation/modification metadata, not a forecast's initialization or necessarily its first dissemination. Copies can have later timestamps, and multipart initiation dates need care. The sampled whole-object ETags do not carry a multipart suffix. We use these timestamps as archive-availability evidence and retain the caveat about historical access policy; we do not relabel them as exact NCEP publication times. No all-days completeness, point-extraction decoder, or full model-input pipeline has been validated.

## Why price revisions remain the blocking requirement
[NYISO's day-ahead archive](https://mis.nyiso.com/public/P-2Alist.htm) explicitly flags corrected dates and updated historical LBMPs. Archived current values are suitable potential labels; using a later corrected value as a historical **input** needs a separate justification.

[NYISO's old correction-log page](https://mis.nyiso.com/public/P-29list.htm) stopped updating on October 15, 2012 and identifies [Operational Announcements](https://mis.nyiso.com/public/P-25list.htm) as the controlling source. We checked two 2025 monthly announcement archives rather than treating the retired log as the end of the search. The files contain dated validation statements about day-ahead prices and explicit real-time correction notices; their nonstandard multiline quoting required timestamp-anchored parsing.

Examples include a January 9 notice correcting January 4 real-time prices and a July 7 notice correcting July 1 real-time prices. **These examples concern real-time prices, not evidence that our sampled day-ahead target values were corrected.** No specific wrong day-ahead sample or numerical leakage was established. However, inspected messages do not pair every historical day-ahead price observation with the original and each revised numeric value/publication time needed to reconstruct a five-year price-history baseline.

ZIP member timestamps provide partial corroboration of file creation times, but carry no timezone and are not an immutable archive of every published numerical vintage. An end-of-month ZIP's HTTP date is also not the availability time of each embedded observation. Neither should be silently promoted to full point-in-time proof.

## What would resolve the gap
A provider/source with original publication times and numerical price versions, or an auditable reconstruction of official original and revised price values, could allow the strict historical extension. A fresh forward collection of timestamped forecast and price snapshots could support a new prospective test, but collecting that is a separate task and has not been started.

A calendar-only retrospective price study would avoid lagged-price inputs, but it would weaken the agreed price-history baseline comparison. It is not a substitute performed under this task. No additional provider search, model fitting, or trading backtest is pending.

If the source gap is later resolved, freeze a separate price-research specification before scoring. Train 2021–2023, validate 2024, and reserve 2025 for price evaluation while disclosing that 2025 demand data have already been examined. Fit preprocessing only on fitting rows. If demand estimates are added, generate them using only earlier fitting periods and genuinely available forecast inputs. Predictive accuracy alone never establishes trading profitability; executable products, order deadlines, settlement rules and costs need separate evaluation.

## Reproduce and inspect
- `TASK_DEFINITION.md`: fixed question, sample dates and stop gate.
- `check_sources.py`: bounded network samples, HTTP receipts, GRIB identity checks, price schemas.
- `check_price_lags.py`: sixteen lagged-price endpoint probes.
- `inspect_cached.py`: offline metadata recheck and robust operational-announcement parsing.
- `Feasibility_Checks.ipynb`: executed companion displaying cached evidence; no model fitting.
- `raw/`: exact source bytes plus retrieval URLs, HTTP headers and hashes in receipts.
- `outputs/`: source-level sample records, lag checks and extracted notices.

Run from this folder with the project's Python environment: `python inspect_cached.py`. Network reproduction: `python check_sources.py`, `python check_price_lags.py`, then `python inspect_cached.py`. The evidence snapshot was collected on 2026-10-16; rechecking live sources may give different access/metadata results.
