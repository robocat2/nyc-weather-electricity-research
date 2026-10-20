# Frozen experiment: NYC weather and electricity demand

Specification written on 2026-10-16 before any model scores or test-period relationships were examined. This is retrospective chronological evaluation using currently archived, possibly revised observations, not an as-issued forecast or a prospective experiment.

## Question and scope
Does observed hourly temperature improve conditional NYC Zone J load estimates beyond calendar effects, and does a modest nonlinear temperature response improve further? One zone, one station, 2021–2025. No trading, causal, corporate-loss, or long-term climate projection claims.

## Data gate and processing
NYISO palIntegrated monthly archives: N.Y.C., PTID 61761, hourly time-weighted load in MW. Interpret timestamps as hour beginning; map explicit EST/EDT to UTC and verify against America/New_York. NOAA GHCNh USW00014732 LaGuardia Airport (40.7794,-73.8803) is a single-station proxy for NYC weather, not a citywide spatial average. NOAA documents GHCNh as the successor to ISD; old CSV links returned HTML. Preserve that access finding.

Weather dates are UTC, temperature is directly in degrees Celsius. Keep routine METAR FM15 preferentially, then SYNOP FM12 within the same UTC hour; choose the earliest report of the preferred type. Exclude SPECI FM16 to avoid overweighting event-driven reports. No rounding to adjacent hours. Accept unflagged observations or quality 1 (good); source 343 quality 5 means passed all checks and is also accepted. Reject other codes, missing and implausible temperatures. Reports within the load hour serve as representative observed temperature, not an exact hourly temperature integral. No interpolation or forward fill. Exclude unmatched hours from every model equally.

Gate: all five local calendar years accessible, unique hourly UTC load records; >=98% matched coverage each year and >=90% each month. These are usability thresholds, not statistical power calculations. Document every excluded hour and flag any long gap. Download 2026 weather only if needed to cover the final five UTC hours of local 2025 (boundary data only).

## Splits and models
Development training 2021–2023, validation 2024, final evaluation 2025, by local calendar year. Inspect final schema/coverage only before freeze. No shuffled split. Fit preprocessing only on fitting rows.

All models use exactly the same calendar features: intercept; hour-of-week categorical effects (167 indicators); three annual Fourier harmonics; first annual sine/cosine interactions with hour of day (23 indicators each); federal observed holiday indicator. Holidays are a reproducible calendar proxy, not a complete NYC business closure calendar. No target lags, year effects, or time trend. Pandas USFederalHolidayCalendar defines dates, including actual/observed dates as returned by the library.

1. Calendar baseline: ordinary least squares on calendar features.
2. Linear temperature: same plus temperature, standardized using fitting data mean/standard deviation.
3. Piecewise-linear temperature spline: same plus standardized temperature and positive-part hinge functions at fitting temperature quantiles. Choose between 3 knots (25/50/75%) and 5 knots (10/25/50/75/90%) using validation MAE, exact tie favors 3. This is one nonlinear model with two predetermined complexity candidates, not a model search. No interactions with temperature.

Select spline complexity on 2024, then refit all three models on 2021–2024, recomputing preprocessing/knots on that fitting sample. Write selected configuration and source/spec hashes before calculating final scores. The 2021–2023 95th percentile defines hot conditions for all evaluation tables, unchanged after refit.

## Evaluation
Primary: hourly MAE (MW) for all matched 2025 hours. Secondary: RMSE, improvement versus baseline, months, meteorological seasons, and training-defined hot hours. Report coverage with every subgroup. Do not remove errors/outliers after evaluation. Retain validation results separately.

For uncertainty, aggregate paired absolute-error differences and counts by local date; use paired circular moving-block bootstrap of daily totals, weighted by their hour counts. Fixed random seed 14732, 2,000 replicates, primary block 7 calendar days; 14/28-day sensitivity. Show percentile 95% intervals in MW for baseline MAE minus alternative MAE (positive is improvement). Report residual mean and lag-1/24/168-hour correlations with exact UTC lag pairs, not across missing-row compression. No independent-hour significance tests. These intervals describe one observed year's dependent errors, not generalization to every future year or uncertainty from refitting.

## Deliverables and stopping point
Modular acquisition, cleaning, features, models, evaluation; raw URLs/times/hashes; coverage/exclusion tables; meaningful data/leakage tests; saved model metadata; one executed notebook with four charts (representative two-week observed period fixed to July 1–14, response within fitting 1st–99th percentiles, MAE comparison, hot-hour performance); monthly/residual diagnostics in tables. Response is an adjusted association with calendar held fixed, not a causal effect. No MW-to-profit conversion. Stop after this comparison and verification; do not expand the model family in response to final scores.
