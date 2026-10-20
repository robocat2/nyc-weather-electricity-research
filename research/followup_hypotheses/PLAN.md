# Bounded follow-up: weather trajectory and forecast revisions

The completed portfolio release is preserved. This folder holds separate exploratory follow-ups. No stock-price hypothesis is tested: the instrument remains NYC virtual electricity and the target is next-day hour-18 RT minus DA.

## Data feasibility before fitting
1. Forecast revision: compare the prior-day 00 UTC and 06 UTC operational HRRR forecasts for the SAME delivery date/hour, grid and 2m temperature. Old lead 46/47 hours, new lead 40/41. Both must meet the existing 04:00 ET cutoff with a five-minute buffer, matching receipts and embedded issue/valid metadata.
2. Temperature trajectory: use the already retained forecasts for delivery days D, D−1 and D−2. Compare forecast temperatures at the same local evening hour. This tests changes in previously forecast temperature levels, NOT realized past temperature or delayed stock-price incorporation. Earlier forecasts have different issue times, so trajectory features can mix weather evolution and forecast errors; this is explicitly a proxy question. Do not fill gaps or substitute actual temperatures. Day joins use calendar dates rather than row shifts.

Probe six stratified older-cycle forecasts first (cold/hot years and DST boundaries). Stop the revision extension if they do not represent pre-cutoff operational forecasts. If samples pass, obtain the full dated temperature-field archive using bounded HTTP ranges. No full weather-grid downloads. Failures and excluded dates retained. A model-specific full coverage gate requires >=90% per year and >=80% per month for 2021–2025 after all input checks. No fitting until a frozen experiment specification is written.

## Evaluation constraints
Use original train 2021–2023 / validate 2024 / refit 2021–2024 / evaluate 2025 chronology. 2025 already examined: all follow-up evidence is exploratory and cannot restore an unseen holdout. No tuning on 2025 or promotion of an alternative based on final-year payoff. Compare every candidate with calendar, the original linear temperature model and constant/flat benchmarks on the SAME eligible dates. Fixed one-MWh sign rule, no costs and assumed clearing as before. Weather trajectory and revision tests will be separate additions to the original linear weather baseline; a combined interaction/search is out of scope. Same dependence-aware uncertainty and no percentage capital returns. Freeze the exact variants and selection rule before fitting.

Stop after the fixed comparison and report positive or negative findings. Do not alter the original studies, source files, frozen release ZIP or published conclusions.
