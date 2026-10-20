# Source definitions and historical timing

This extension uses corrected/finalized prices as outcomes. It deliberately excludes lagged prices, observed load, realized future temperature, and demand-model outputs from inputs. The earlier strict feasibility stop concerned a different baseline requiring price-history vintages; the user explicitly authorized this narrower calendar/weather experiment.

## Operational forecast source
- NOAA HRRR public archive: https://registry.opendata.aws/noaa-hrrr-pds/
- Bucket: `https://noaa-hrrr-bdp-pds.s3.amazonaws.com/`
- Fixed cycle/path: `hrrr.YYYYMMDD/conus/hrrr.t06z.wrfsfcf40.grib2` or `f41`, where YYYYMMDD is the calendar day before NYC delivery. Lead depends on delivery-hour UTC offset, not cutoff-day offset.
- HRRR product description: https://www.emc.ncep.noaa.gov/emc/pages/numerical_forecast_systems/hrrr.php
- Each downloaded `.idx` identifies the 2m TMP byte range. Only that complete GRIB2 message is downloaded, not the full grid/product file. Request uses If-Match against the whole-object ETag; response ETag and Last-Modified must match the checked object. Eight prior feasibility samples are reused with their original receipts, and the same identity/timing checks are applied.
- Initialization time alone is insufficient. Whole-object S3 Last-Modified must precede prediction cutoff by at least five minutes. Later/copied/late files are excluded. Multipart ETags are excluded because S3's multipart object timestamp can be initiation time rather than completed upload time. No fallback to another cycle or actual observation.
- AWS metadata definition: https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingMetadata.html . Last-Modified is creation/modification metadata, not an exact first-NCEP-release ledger. Retained past-dated objects in NOAA's publicly documented operational archive provide historical availability evidence. The pipeline does not reconstruct every historical bucket-access-policy change; this limit is disclosed rather than relabeling an archive timestamp as exact first dissemination.
- ecCodes is ECMWF's official GRIB decoder: https://github.com/ecmwf/eccodes-python . Decode and verify NCEP centre, operational production status, forecast type, initialization, step, valid time, temperature identity, units and 2m height. Initialization must equal the fixed 06 UTC cycle; valid time must equal next-day 18:00 local delivery.
- Nearest grid point to 40.7794 N, 73.8803 W; exact coordinates/index/distance retained in `outputs/grid_points.json` and each decoded row. A single near-airport point is a proxy, not population-weighted NYC/regional weather. Values are converted from Kelvin to Celsius once. No interpolation across issues or realized weather data.

Raw per-file HTTP receipts retain URL, retrieval UTC, relevant response headers, byte count and SHA-256. HEAD metadata is retained separately. `forecast_availability.json` includes every expected day and rejection reason; `forecast_point_data.csv` records decoder results.

## Finalized price outcome source
- NYISO day-ahead zonal LBMP archive: https://mis.nyiso.com/public/P-2Alist.htm
- Monthly pattern: `https://mis.nyiso.com/public/csv/damlbmp/YYYYMM01damlbmp_zone_csv.zip`
- Zone: N.Y.C., PTID 61761 (NYC / Zone J). Outcome column: `LBMP ($/MWHr)`; research units: $/MWh.
- Select hour beginning 18:00 on each local delivery date. No repeated fall-back 01:00 ambiguity affects this fixed-hour target. Each date must have exactly one target record, and the 60 archives must supply all 1,826 dates.
- Negative prices are allowed; no clipping, winsorization or logarithm. Price magnitude is never an eligibility rule.
- The archive explicitly flags corrected prices/updated historical LBMPs. 'Finalized' means the corrected/latest historical archive snapshot retrieved for this run, not guaranteed immutable settlement or first-publication prices. These values are outcomes only, not lagged covariates.
- The original publication-vintage history remains unverified. Retrospectively corrected fitting labels are used for this retrospective finalized-outcome study; it is not a full as-of simulation of historical model-training data. See the prior feasibility brief for the specific gap.
- Existing NYISO Market Participants User's Guide §5.4.1 describes approximately 11 a.m. day-ahead posting; §5.6.2 describes integrated load but load is not an input here. Cached in the parent demand project's raw evidence, original URL: https://www.nyiso.com/documents/20142/3625950/mpug.pdf . Price revelation is on D−1 and earlier than delivery; 38-hour delivery horizon must not be confused with 38 hours until price publication.
- NYISO pricing training document shows 05:00 DAM close: https://www.nyiso.com/documents/20142/25467833/Additional-Pricing-Rules.pdf . Cached in the prior feasibility raw evidence. We use 04:00 as a pre-close research cutoff, without claiming historical market-rule or executable-order validation.

## Evaluation boundaries
Calendar day, weekday, preexisting fixed holiday rules and annual cycle are known at cutoff. Juneteenth is excluded from the holiday proxy because its legislation occurred during the study. Forecast transforms and models use only fitting rows; final prices are outcome labels. The selected weather specification is chosen with 2024 validation, then final models refit on 2021–2024. The 2025 price evaluation is excluded from fitting/selection, but 2025 demand data and two of the eight feasibility price samples were already inspected. It is not wholly unseen.

Calendar-only is the sole baseline tested. The study cannot establish incremental value beyond lagged-price models, full energy-system forecasts, or trading strategies. No price/load history, weather revisions issued after cutoff, fees, orders, market-access or trading P&L is modeled.
