# Source and transformation notes

Downloaded on 2026-10-16 UTC. Per-file URLs, retrieval times, byte sizes and SHA-256 hashes are in `raw/manifest.json`. Cached files are authoritative inputs for this run; online sources may later revise their archives. No credentials, private data, synthetic observations, or third-party data mirrors are used.

## Electricity
- Index: https://mis.nyiso.com/public/P-58Clist.htm
- Monthly pattern: `https://mis.nyiso.com/public/csv/palIntegrated/YYYYMM01palIntegrated_csv.zip`
- 60 monthly ZIPs, 2021–2025, containing daily CSV files. Exact fields: Time Stamp, Time Zone, Name, PTID, Integrated Load.
- NYC selection: Name `N.Y.C.`, PTID `61761` (NYISO Zone J). All expected 43,824 local calendar hours are present, with unique UTC keys.
- NYISO Market Participants User's Guide §5.6.2: integrated actual load is the time-weighted hourly zonal load, posted after each hour. Cached `raw/nyiso_market_guide.pdf`.
- Units supported by NYISO's Operations Performance Metrics, April 2025, p.7, which explicitly labels average hourly integrated load in MW and hour beginning: https://www.nyiso.com/documents/20142/51357934/03a_202504_OpsReport_NewFormat_V1.pdf/f9e2bf17-9e5c-d25a-30c1-ae92f0a4deac . Reviewed through web text, not part of numeric inputs.
- Additional corroboration of the palIntegrated interval convention: GridStatus's own open-source NYISO implementation maps this dataset to interval start with duration 60 minutes: https://opensource.gridstatus.io/en/latest/_modules/gridstatus/nyiso.html . This supports the timestamp interpretation; no GridStatus data or library is used.
- Explicit EST is UTC−5 and EDT UTC−4. We verify labels against America/New_York; repeated fall-back local hours remain distinct UTC hours. Spring-forward hours are absent as expected. Integrated load is a power average; it is not summed and called MW, nor converted into financial value.

## Weather
- Product: https://www.ncei.noaa.gov/products/global-historical-climatology-network-hourly
- Documentation: https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/doc/ghcnh_DOCUMENTATION.pdf (cached).
- Station list: https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/doc/ghcnh-station-list.txt (cached).
- Pattern: `https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/access/by-year/YYYY/psv/GHCNh_USW00014732_YYYY.psv`.
- NOAA identifies GHCNh as the replacement for ISD. The old global-hourly 2021/2023/2025 CSV URLs returned HTML S3 Explorer pages, and old ISD metadata stopped at August 27, 2025. Those responses are retained as `weather_YYYY.redirect.html`, explicitly excluded from data input. GHCNh provides all twelve 2025 months.
- Station USW00014732 LAGUARDIA AP, latitude 40.7794, longitude −73.8803, elevation 3m. An NYC airport station is geographically relevant but cannot represent every neighborhood or urban microclimate.
- `DATE` is UTC; `temperature` is directly in °C with tenths precision, not integer tenths requiring division by ten. The docs describe measurement, source, report and quality columns separately.
- Prefer routine METAR FM15 to SYNOP FM12 inside the same UTC hour; choose the earliest preferred report. Exclude SPECI FM16 reports, so storms do not receive more weight simply because extra reports were issued. This uses an observed in-hour temperature proxy, not a time-weighted temperature integral.
- Quality 1 is good for source 223; quality 5 means passed all checks for source 343. Blank codes are unflagged; other numeric/letter codes are conservatively rejected. The code retains source identifiers during cleaning so numeric 5 is never interpreted universally as good. Actual weather distributions are in `outputs/weather_quality.json`; report sources change during 2025, another limitation of retrospective harmonized observations.
- No imputation. The full grid includes all hours, retaining missing temperature as missing. `excluded_hours.csv`, `missing_runs.csv`, and monthly/annual coverage tables disclose omissions. The longest gap is 90 hours from 2025-08-29 23:00 UTC through 2025-09-02 16:00 UTC. We do not infer its cause.
- The 2026 station file supplies only UTC January 1 00:00–04:59 observations for local December 31, 2025. Every later observation is discarded by the fixed local-year grid. No 2026 relationships or model scores are examined.

## Calendar and reproducibility
Pandas `USFederalHolidayCalendar` is a reproducible proxy for observed US federal holidays, not a comprehensive utility/customer operating calendar. It returns the dates used directly. See `src/features.py` for the exact design matrix. Package versions are pinned in `requirements.txt` and the fully resolved execution environment is in `outputs/environment.txt`.

The specification was saved before performance was calculated. `outputs/specification_freeze.json` hashes it. `outputs/selected_configuration.json` records the validation choice, hot threshold, and fitting/source/spec code hashes before each deterministic final evaluation. The test year has now been examined; rerunning the same pipeline is reproduction, not a new unseen test. No post-result model-family or feature changes were made.
