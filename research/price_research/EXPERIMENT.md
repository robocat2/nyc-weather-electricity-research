# Revised NYC price research: frozen specification

Written before full-period price modeling or validation/test scores, 2026-10-16. This is a new, narrower experiment authorized after the price-history feasibility stop. The earlier stop remains the record of the stricter task; the demand study is unchanged.

## Question
Do historical operational weather forecasts add predictive value for corrected/finalized NYC electricity prices beyond calendar features? Do not claim that this beats a price-history model or demonstrates trading profitability.

## Prediction and label
At 04:00 America/New_York on D−1, predict the NYISO NYC/Zone J (N.Y.C., PTID 61761) day-ahead LBMP for hour beginning 18:00 on D, $/MWh. Delivery is normally 38 hours ahead, or 37/39 hours over DST. The auction-price label is published on D−1, before delivery; official guide says approximately 11 a.m., not an exact historical publication ledger. The cutoff precedes the documented 05:00 bidding deadline, but this is not an executable bidding backtest. Outcomes are the corrected/latest archived historical prices downloaded for this run, called finalized prices here; they are not verified original publications or immutable settlement records.

No past-price values, realized load, realized future weather, NYISO load forecasts without verified historical vintages, or demand-model outputs enter features. Corrected prices are outcomes only. Fitting with retrospectively corrected outcomes is chronological finalized-outcome research, not a reconstruction of the model/label versions that could have been trained in real time. 2025 demand data and eight sampled price records have already been examined. The 2025 price period is excluded from model fitting/selection but is not claimed to be wholly unseen.

## Forecast inputs and timing gate
One fixed NOAA operational HRRR 06 UTC cycle on D−1. Forecast valid at 18:00 local D, lead 40 or 41 hours. Extract 2m air temperature in Celsius at the nearest HRRR grid point to LaGuardia (40.7794, −73.8803). Retain actual grid coordinates and distance. No later cycle, interpolation across issues, forecast/analysis replacement, or realized observation substitution.

For each of 1,826 delivery days, 2021–2025: retrieve NOAA public-S3 whole-object HEAD metadata; require Last-Modified <= cutoff minus five minutes and no multipart ETag suffix (multipart initiation metadata is insufficient). Verify downloaded message has the same ETag/Last-Modified and embedded initialization/lead/temperature/height identity. Use If-Match on the byte-range request. Preserve URLs, UTC checks, HTTP receipts, hashes, range, issue/valid times, point coordinates and value. S3 timestamps are evidence for the retained archive object's availability, not a claim of exact first NCEP dissemination or a complete historical access-policy ledger. Files copied/replaced after cutoff, late files, missing files, decoder failures, and price-schema failures are excluded with reasons, identically across models. Never choose exclusions based on price magnitude or error. Retry transient retrieval failures at most twice with short backoff; cached success responses are reused.

Use raw GRIB temperature messages and the official ecCodes decoder. Decode before accessing labels for modeling. Price archives cover 60 months; select the unique 18:00 NYC record on each day. Repeated fall DST hours at 01:00 do not affect this target. No cap or log transformation of price; negative prices are valid outcomes. Coverage gate before fitting: >=90% of days per calendar year and >=80% in every month; all five years represented. If gate fails, report and stop rather than changing cutoff or replacing weather.

## Chronological experiment
Development fitting: delivery years 2021–2023. Validation: 2024. Final evaluation: 2025. The final evaluation is excluded from model development, subject to the exposure disclosure above. Same rows for all models. No shuffling, no price-dependent filtering.

Calendar features fixed for all models: intercept, six weekday indicators, three annual Fourier sine/cosine harmonics, and one observed-US-federal-holiday proxy excluding Juneteenth (introduced in 2021), to avoid assuming new legislation known at the earliest prediction cutoffs. These fixed holiday rules predate the sample; the proxy is not a complete energy-market holiday calendar. No year indicator, time trend or price/load lag.

Fit ordinary least squares by SVD:
1. Calendar-only baseline.
2. Calendar plus linear forecast temperature.
3. Calendar plus continuous piecewise-linear forecast-temperature spline with three hinges at fitting-data 25/50/75 percentiles.

Temperature centering, scale and spline knots use fitting rows only. Choose linear versus spline by validation MAE; exact tie chooses linear. No other hyperparameters. Record selected weather model and hashes before final evaluation; refit baseline and both predefined weather variants on 2021–2024. The primary comparison is calendar versus the validation-selected weather model. Report all variants transparently, without choosing the final-year winner after seeing scores.

## Evaluation and claims
Primary: daily target-hour MAE ($/MWh) on matched 2025 days. Secondary RMSE, mean residual (actual minus prediction), months, seasons and hot-forecast days. Hot threshold: fitting 2021–2023 forecast-temperature 95th percentile, unchanged after refit. Report counts and missing dates. No outlier deletion or final-period tuning.

Paired circular calendar-day moving-block bootstrap of absolute-error differences, with missing excluded days retained as zero-count positions: seed 61761, 5,000 replicates, 7-day primary, 14/28-day sensitivity. Positive difference means calendar MAE minus weather MAE, improvement. Report percentile 95% intervals; this is an approximate within-year paired error comparison, not causal inference, parameter-refitting uncertainty, or reliability across all future years. Diagnostics: exact-calendar-day residual correlations at lags 1 and 7, monthly stability, largest errors listed as diagnostics, and concentration of gains in the ten largest baseline-error days (without deleting them from primary scores).

Show an adjusted forecast-temperature response over fitting 1st–99th percentile support, calendar held fixed, relative to 18°C. It describes model association with forecast temperature, not realized-weather causal price sensitivity. Do not convert accuracy or predicted price into profit. A strong price-history/calendar baseline, regional weather/supply/fuel drivers, day-ahead versus real-time spread, executable instruments, fees/slippage and market access remain untested.

## Deliverables and stopping point
Dedicated price_research folder, cached sources/receipts, availability and exclusion tables, modular Python pipeline, meaningful timing/decoder/split/preprocessing/score tests, one executed notebook with four figures, short README with actual results and material limitations. Keep existing demand and strict feasibility artifacts unchanged. Stop after this predefined comparison and verification, regardless of whether weather helps. No trading backtest or additional model search is included.
