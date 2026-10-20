# NYC weather → electricity demand → price prediction → gross spread backtest

## What this combined walkthrough contains
This is the complete NYC research progression, combining the earlier electricity-demand study with the later finalized-price prediction study. It now includes three executed studies, all twelve charts, their calculations/tables, the reason for moving from demand to prices, the historical-data feasibility hurdle, the revised research question, source definitions and frozen methods. Baxter is a separate corporate-financial case study and is not part of this NYC analysis.

## The research story in plain English
We wanted a Python project that tests a weather-related economic hypothesis using enough consistent observations to evaluate a model on later dates. We began with NYC electricity demand because the load and temperature series could be aligned and checked across several years.

**Stage 1 — Understand demand.** Does temperature add information beyond the hour, weekday, season and holidays? Using 2021–2025 hourly NYC load and LaGuardia observed temperatures, we compared calendar-only, linear-temperature and nonlinear-temperature regressions. A modest temperature spline reduced 2025 mean absolute error by **39.2%, from 436.38 MW to 265.13 MW**, and improved every month. Linear temperature alone slightly worsened average error. This was retrospective modeling conditional on observed weather, not a day-ahead forecast.

**Why move to prices?** The demand result suggested that a nonlinear weather relationship could be worth testing in a market-relevant outcome. It did not prove that prices were predictable or that weather would add information beyond the market's existing expectations. We therefore asked a new question: can weather forecasts issued before a prediction cutoff improve estimates of a future electricity price?

**Stage 2 — Check historical timing.** We first considered a price-history/calendar baseline with archived weather forecasts. Genuine forecasts and price targets existed, but we could not establish complete historical versions of the lagged-price inputs. Current price archives can contain later corrections. We stopped that stricter extension before fitting. The initial proposed 08:00 cutoff was also too late for the documented 05:00 day-ahead market close, so the candidate cutoff became 04:00 New York time.

**Stage 3 — Ask the narrower, valid question.** The revised price experiment excluded historical prices, realized load, realized future temperature and demand-model outputs from inputs. It compared calendar-only against calendar plus a genuine archived temperature forecast. Corrected/finalized prices were allowed as the outcome being predicted. This removes the unresolved lagged-price vintage issue from the input set; it does not establish incremental value over a strong price-history baseline.

**Stage 4 — Test price prediction.** At 04:00 on the prior day, predict NYC's day-ahead electricity price for 18:00–19:00 the following day. We used the operational HRRR 06 UTC cycle's 40/41-hour temperature forecast at a grid point near LaGuardia. Every included forecast had matching embedded issue/valid times and archive-object timing before the cutoff buffer. Out of 1,826 daily dates, 1,809 passed the data gate; 17 were excluded without substituting later forecasts or actual weather. The selected spline reduced 2025 price MAE by **16.6%, from $35.16 to $29.33/MWh**, across 362 matched days, improving ten of twelve months.

**Stage 5 — Test a trading rule before costs.** We verified an NYC virtual electricity trade and fitted a new model for the **real-time minus day-ahead spread**, using the same available forecast/calendar inputs. At 04:00 on D−1, positive predicted spread means virtual load; negative means virtual supply. Gross payoff is side × (RT − DA), assuming one MWh clears. The weather model was selected using 2024 payoff, then evaluated on 362 eligible 2025 dates. Linear temperature was selected; the earlier price-level spline was not reused as a trading signal.

**Latest finding:** the selected rule earned **+$1,020.96 gross**, compared with **+$321.98 calendar-only** and **+$1,384.92 always virtual load / training-mean direction**. Its seven-day bootstrap interval for average daily payoff is **−$8.10 to +$18.29**; the increment over calendar is **−$0.72 to +$6.04/day**. Both cross zero, as do 14/28-day checks. The best day earned $1,768.53; all other dates together lost $747.57. Only three months were positive. **This test does not establish reliable gross alpha.** Costs were deliberately excluded, and clearing was assumed rather than demonstrated. The unselected spline is shown for transparency, not promoted after inspecting 2025.

## The connection between the studies
**The demand finding motivated the price experiment. The fitted demand model was NOT fed into the price model.** The demand and price studies are linked research questions, not one production pipeline that converts predicted demand into a trading order. Stage 1 uses realized temperature to study demand; The price experiment uses archived forecast temperature to predict finalized prices. Their percentages have different units, samples and baselines and must not be added or treated as returns.

## What the percentages actually mean
- **39.2%:** relative reduction in mean absolute demand-estimation error versus a calendar baseline, measured in MW.
- **16.6%:** relative reduction in mean absolute finalized-price prediction error versus a calendar baseline, measured in $/MWh.
- Neither percentage is an investment return, trading win rate, profit margin, or causal effect.

Mean absolute error (MAE) is the average magnitude of the estimate's miss, ignoring whether it is above or below the outcome. Lower is better. A spline is a regression that can bend at a few predefined temperature knots, allowing cold and hot conditions to have different associations. RMSE gives larger misses more weight.

## What makes the evidence useful—and what it cannot establish
All three studies used 2021–2023 for development fitting, 2024 for validation, and 2025 for evaluation after refitting on 2021–2024. Preprocessing and temperature knots used fitting data. There was no random hourly/day split. The price study disclosed that 2025 demand data and two source-feasibility price samples had already been inspected: its evaluation year was excluded from fitting and selection, but was not wholly unseen.

For demand, the seven-day paired block-bootstrap 95% interval for MAE improvement was 128.7–220.2 MW. For prices, it was $1.98–$9.82/MWh. Both price/demand improvements remained positive under 14/28-day block sensitivity checks. These are within-year dependent-error comparisons, not guarantees about future years or causal effects.

Important remaining errors are substantial. The demand spline underestimates load by 109 MW on average, and errors remain strongly serially dependent. The price spline underestimates finalized prices by $21.81/MWh on average, with $49.46/MWh RMSE. It worsens March and November and the spring aggregate. Hot-price performance covers only 16 days. A single NYC weather point cannot capture regional demand, fuel costs, outages, supply and congestion.

The price label is the corrected/latest historical archive snapshot retrieved for the study, called finalized here—not verified original auction publications or immutable settlements. Archive Last-Modified is historical object-availability evidence, not a complete first-NCEP-release or historical access-policy ledger. Retrospectively corrected fitting labels also mean this is not an exact simulation of the historical real-time training environment.

## Is this a signal or trading strategy?
Yes: Part III now tests a specific directional virtual-load/virtual-supply signal against calendar, constant-direction and flat benchmarks. This is a **hypothetical gross spread backtest conditional on clearing**, not an executable or net-profitability backtest. It uses finalized historical outcome prices, not verified original settlement vintages. Actual market access, bid acceptance, fees, uplift, financing and slippage have not been tested. The earlier 16.6% price-error improvement is not a return and did not translate into convincing incremental trading evidence. A strong price-history baseline remains untested.

Parts I and II retain their original conclusions from before the trading extension. Statements there about trading not yet being tested describe that earlier stage; Part III and this introduction provide the current status. 2025 had already been examined in the prior demand and price work, so the spread evaluation is excluded from fitting/selection but is not wholly unseen.

Delivery is normally 38 hours after the prediction cutoff (37/39 over DST), but the auction price is published the prior morning before delivery. The delivery horizon is not the same as time until price revelation.

## Instructions for another ChatGPT explaining this file
Use this file as the combined evidence for all three NYC stages. Explain the progression before discussing technical details. Distinguish observed-weather demand modeling from forecast-weather price prediction. State that demand estimates were not price-model inputs. Explain 39.2% and 16.6% as separate error reductions, not returns. Include failures and uncertainty, identify the calendar-only baseline, disclose prior 2025 exposure, and distinguish the conditional gross trading test from proven alpha or net profitability. Explain the unsuccessful benchmark comparison and concentration in one day. Use the embedded results and figures for interactive explanations; do not invent observations or scenario probabilities.

## Complete studies and methods follow
The full executed demand walkthrough comes first, followed by the full executed price walkthrough and gross spread backtest. Source notes, experiment specifications and the original feasibility decision are included at the end. No modeling or results were changed when combining these documents.


---

# Full demand findings and reproduction

# NYC weather and electricity demand

**A reproducible Python regression project with a completed chronological evaluation.** Does observed temperature improve NYC electricity-demand estimates beyond calendar effects?

On the reserved 2025 evaluation data, the piecewise-linear temperature spline cut mean absolute error by **39.2%**, from **436 MW to 265 MW**. A straight-line temperature term slightly worsened MAE. The spline improved MAE in every month and reduced hot-hour MAE by **55.0%** (1,136 → 511 MW).

| Model | 2025 MAE, MW | 2025 RMSE, MW |
|---|---:|---:|
| Calendar baseline | 436.4 | 602.3 |
| Calendar + linear temperature | 443.0 | 598.1 |
| Calendar + temperature spline | 265.1 | 359.7 |

**Read the executed notebook:** [NYC_Weather_Electricity.ipynb](NYC_Weather_Electricity.ipynb). The self-contained HTML export is [outputs/NYC_Weather_Electricity.html](outputs/NYC_Weather_Electricity.html). Both include the four charts, exact tables, methods, and limitations.

## What the result means
A modest nonlinear temperature response adds useful information beyond this calendar baseline on a later year. It demonstrates Python data acquisition, cleaning, DST/UTC handling, regression, chronological evaluation, and dependence-aware uncertainty. Temperature-sensitive electricity demand is an established modeling problem; no novelty claim is made.

This is conditional on **observed weather**. It is not a demonstrated operational day-ahead forecast, a causal estimate, a corporate-loss model, a long-term climate projection, or a trading strategy. No MW-to-profit conversion is attempted. Baxter remains the separate finished financial evidence project.

## Experiment
- Data: NYISO hourly integrated NYC/Zone J load, NOAA GHCNh LaGuardia temperature, 2021–2025.
- Development fit: 2021–2023; validation: 2024; final evaluation: 2025. All three final models refit on 2021–2024 after selection.
- Same calendar controls in every model: hour of week, three annual Fourier harmonics, hour-by-annual interactions, observed federal holidays.
- Ordinary least squares via NumPy SVD. Linear temperature is compared with a continuous piecewise-linear spline; 3 versus 5 knots chosen using validation MAE. Three knots selected.
- Hot: ≥28.3°C, the 2021–2023 temperature 95th percentile. 472 matched 2025 hot hours.
- 43,700 matched hours across five years; 124 excluded without imputation. 2025 has 8,654 matched of 8,760 expected hours (98.79%). NYISO load has complete hourly coverage.
- Paired daily circular moving-block bootstrap: 2,000 replicates. The seven-day 95% interval for baseline-minus-spline MAE is 128.7–220.2 MW; 14/28-day sensitivity intervals also remain positive. Linear temperature's interval crosses zero. These are approximate within-year error-comparison intervals, not promises for future years.

## Material limitations
The final spline underestimates load by **109 MW on average**. Residual lag-1 correlation is **0.952**, and lag-24 is **0.581**. Hot-hour MAE remains 511 MW. One final year, one zone, and one airport station limit generalization; humidity, thermal lags and other demand drivers are omitted. A 90-hour missing-weather gap crosses August/September 2025 and may create selective exclusions. Retrospective archives may include revisions and NOAA report sources change during 2025. The baseline is calendar-only; these results do not compare against commercial forecasts or load-lag forecasting baselines.

The final year was not used for model selection. It has now been examined, so future changes would require a fresh evaluation design. No further model search is included.

## Reproduce
Python 3.12 was used. From this folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/acquire.py --full  # unnecessary when the cached raw files are present
python src/run.py
python -m unittest discover -s tests -v
python execute_notebook.py  # executes notebook and writes HTML using this environment
```

Acquisition uses public sources, no API keys. Raw files are cached without overwriting existing downloads. [SOURCES.md](SOURCES.md) documents schemas, units, source quality flags, geographic assumptions and retired URLs. [EXPERIMENT.md](EXPERIMENT.md) is the pre-evaluation specification. Code lives in `src/`; outputs include predictions, coefficients, selection metadata, coverage, exclusions, monthly/season/hot scores, uncertainty and residual diagnostics.

## Stopping point
**Complete:** the bounded three-model comparison and review. There is no pending model expansion. This project supports an honest modeling portfolio; it does not need a trading signal or a more elaborate model to be useful.

## Verification
Ten tests pass; the seven notebook code cells execute end to end with four saved figures. Independent normal-equation calculations reproduce the SVD predictions within 0.000001 MW. All four chart PNGs were visually inspected. The HTML export has four embedded figures and valid local links; full browser rendering was not inspected. Details: `outputs/validation_status.json`.


---

# Full price findings and reproduction

# Weather forecasts and finalized NYC electricity prices

**Completed Python price-prediction research:** do archived operational weather forecasts improve finalized NYC day-ahead price predictions beyond a calendar-only baseline?

**Yes, in this chronological evaluation.** The forecast-temperature spline selected using 2024 validation reduced 2025 MAE by **16.6%**, from **$35.16 to $29.33/MWh**, over 362 matched daily predictions. A straight-line forecast-temperature term worsened 2025 MAE by 2.0%.

| Model | 2025 MAE, $/MWh | 2025 RMSE, $/MWh | MAE improvement vs calendar |
|---|---:|---:|---:|
| Calendar only | 35.16 | 62.30 | — |
| Calendar + linear forecast temperature | 35.86 | 61.59 | −2.0% |
| Calendar + forecast-temperature spline **(validation-selected)** | **29.33** | **49.46** | **16.6%** |

The paired seven-day block-bootstrap 95% interval for calendar-minus-spline MAE is **$1.98–$9.82/MWh**. Fourteen- and 28-day sensitivity intervals also remain positive. The spline improves ten of twelve months, but worsens March and November; the spring aggregate is also worse. Ten large baseline-error days contribute 26.7% of the total net improvement.

**This supports incremental predictive information from weather forecasts over this calendar baseline. It does not establish an advantage over price-history models or trading profitability.**

Start with the [executed notebook](NYC_Finalized_Price_Research.ipynb), or its [HTML export](outputs/NYC_Finalized_Price_Research.html). The figures and exact tables show results, coverage, uncertainty and limitations.

## Exact prediction task
At **04:00 New York time on the prior day**, predict NYC/Zone J's day-ahead LBMP for **18:00–19:00 the next day**, in $/MWh. Delivery is normally 38 hours ahead, with DST exceptions of 37/39 hours. The auction price is published on the prior day, before delivery; delivery horizon is not the same as time until price publication.

Inputs are calendar features and the operational HRRR **06 UTC cycle's 40/41-hour temperature forecast** at a grid point 1.46 km from LaGuardia. Every included message is verified as an NCEP operational forecast with the correct embedded issue time, target-valid time, field and 2m height. The archive object's timestamp must predate cutoff by at least five minutes, and receipt identity must match the checked object. Late/copied or multipart-timestamp files are excluded without replacing them with later forecasts or realized temperatures.

No historical price values, observed load, realized future weather or demand-model outputs enter features. Finalized/corrected historical prices are **outcomes only**, so the earlier inability to reconstruct lagged-price input vintages does not block this narrower task.

## Evaluation and source coverage
- 2021–2023 development fitting; 2024 validation selects linear versus a fixed three-hinge temperature spline; all three final models refit on 2021–2024; 2025 price evaluation excluded from fitting/selection.
- **2025 was not wholly unseen:** its demand data and two feasibility price samples were already inspected. No model choices were tuned to 2025 price scores.
- Same 14 calendar controls in each model: weekday, three annual Fourier harmonics, and a fixed observed federal-holiday proxy excluding Juneteenth. Temperature center/scale/spline knots use fitting rows only.
- One 18:00 target per date, not a shuffled hourly split. All 1,826 outcomes exist in the 60 NYISO archives. **1,809 forecasts pass** the timing/decoding gate. Seventeen exclusions: eleven late/replaced timestamps and six multipart timestamps whose completion time could not be verified.
- Coverage exceeds 98% in every year and 90% in every month. Evaluation covers **362 of 365 days in 2025**. Missing days are excluded equally from every model and retained in the calendar-day bootstrap grid as zero-count positions.
- Ordinary least squares; no price clipping, log transform or outlier deletion. Negative prices remain valid outcomes. Error metrics are daily target-hour MAE/RMSE in $/MWh.
- Paired daily circular moving-block bootstrap, 5,000 replicates, fixed seed; primary seven-day blocks plus 14/28-day sensitivity. Intervals describe this year's paired errors, not parameter-refitting uncertainty or all future years.

## Material limits
The selected model **underestimates prices by $21.81/MWh on average**, with $49.46/MWh RMSE. One-day residual correlation is 0.685. Hot-forecast performance covers only 16 evaluation days; hot-day MAE remains $84.91/MWh. These are substantial errors, not a production-quality forecasting claim.

The model omits lagged prices, gas/fuel costs, supply/outages, regional weather and congestion. Its calendar-only baseline is modest, and it has only one final evaluation year. Selective forecast exclusions may bias the evaluated date set. The fitted temperature curve is an adjusted association with a forecast, not a causal effect of realized temperature.

'Finalized prices' means the corrected/latest historical archive snapshot retrieved for this run, not verified original auction publications or guaranteed immutable settlements. Retrospectively corrected fitting labels do not reconstruct the label versions available for historical real-time model training. S3 Last-Modified supplies archive-object timing evidence, not an exact first-NCEP-dissemination or historical access-policy ledger. No executable orders, day-ahead/real-time spread strategy, market access, fees, slippage or P&L are tested.

## Reproduce
Python 3.12 was used. From this folder:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/acquire.py       # network; skip if cached raw files are already present
python src/prepare.py       # offline GRIB decoding, price parsing, coverage/timing gate
python src/run.py           # chronological selection, refit, evaluation
python -m unittest discover -s tests -v
python execute_notebook.py  # executes the notebook and exports HTML
```

The cached temperature messages total about **2.23 GB**; full weather grids were not downloaded. No API credentials are required. The notebook reproduces fitting/scoring from the verified daily table; preparation regenerates it from raw messages. Pinned direct dependencies are in `requirements.txt`; the resolved execution environment is in `outputs/environment.txt`.

[SOURCES.md](SOURCES.md) documents source URLs, units and timing interpretation. [EXPERIMENT.md](EXPERIMENT.md) is the pre-score specification, hashed in `outputs/specification_freeze.json`. The first pre-evaluation selection record is retained in `outputs/first_evaluation_configuration.json`; deterministic reruns also write `selected_configuration.json`. Raw per-file receipts preserve HTTP metadata and hashes. Outputs include forecasts, availability, exclusions, predictions, coefficients, validation/test scores, month/season/hot tables, uncertainty and residual diagnostics.

## Stopping point
**The predefined comparison is complete.** It answers the narrower weather-versus-calendar market question. A stronger price-history baseline and executable trading evaluation remain untested and are not pending work in this project. The original demand study and the earlier stricter feasibility assessment remain unchanged.

## Verification
Eleven tests pass. The seven notebook code cells execute, and all four saved chart PNGs were visually inspected. Independent normal-equation calculations reproduce SVD predictions within 0.000001 $/MWh. All raw source receipts were checked against cached-file SHA-256 hashes. HTML embedded figures and local links were checked; full browser layout was not inspected. The demand code/specification and prior feasibility raw evidence remain unchanged. Details: `outputs/validation_status.json`.


---

# Demand experiment specification

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


---

# Demand sources and transformations

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


---

# Initial stricter price feasibility decision (historical scope)

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


---

# Revised price experiment specification

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


---

# Price sources and timing evidence

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


---

# Trading feasibility and official settlement evidence

# NYC gross spread-trading feasibility

**Decision: feasible to test a hypothetical before-cost trading signal, conditional on a cleared virtual schedule.** The instrument/payoff exists and both outcome-price series are available for every 2021–2025 target day. A new spread target is required; the existing 16.6% price-error improvement is not a trading result.

This stage is complete. It fits **zero models**, computes **no trading performance**, places **no orders**, and leaves the completed demand/price research and combined walkthrough unchanged. Fees and slippage were deliberately excluded at the user's instruction; missing cost estimates do not block this gross test.

## 1. Instrument, decision time and payoff

Candidate instrument: **NYISO NYC / Zone J virtual energy transactions**, PTID 61761, for **hour beginning 18:00 (18:00–19:00 local time)**. These are financial day-ahead/real-time energy transactions rather than shares in an electricity company. NYISO describes them as transactions for qualified market participants; this feasibility check does not establish the user's market access or register an account.

Decision cutoff: **04:00 America/New_York on D−1**, before the documented **05:00 day-ahead market close** for next-day delivery. Retain the prior research's fixed HRRR 06 UTC forecast cycle, whose exact valid time and historical archive-availability evidence were checked. The elapsed time to delivery is normally 38 hours, or 37/39 across DST. Both auction clearing prices and next-day real-time prices are unknown at decision time; the subsequently published day-ahead price must not become an input to this pre-auction decision.

Let **DA** be that hour's NYC day-ahead zonal LBMP and **RT** the same hour's time-weighted/integrated real-time zonal LBMP, in $/MWh. For a cleared **1 MW schedule for one hour = 1 MWh**:

| Direction | Financial transaction | Gross energy-settlement payoff |
|---|---|---|
| Virtual load | Buy day-ahead; settle offset in real time | **RT − DA dollars** |
| Virtual supply | Sell day-ahead; settle offset in real time | **DA − RT dollars** |

For quantity q MWh, multiply the spread by q. A flat position earns zero. These are the energy-settlement components before fees, uplift, financing or other charges. The published LBMP already contains energy/loss/congestion components; do not add those components a second time.

The accounting formula uses interval-duration weights for real-time settlement. Use **NYISO's official hourly integrated zonal price** rather than an unweighted mean of whatever five-minute reports happen to be present.

### Clearing is distinct from transaction costs
Virtual load uses a maximum purchase bid price; virtual supply uses a minimum sale offer price. A submitted bid can fail to clear or clear partially. The first gross screen can state the assumption: **one MWh is cleared in the signal direction**. That tests directional spread value conditional on clearing, not an executable bidding strategy. No historical bid-limit/fill simulation, partial-fill model, market impact or user eligibility is established here. Ignoring fees does not make future DA/RT prices known or guarantee a fill.

## 2. Required data: verified

Downloaded and parsed **60 monthly NYISO hourly integrated real-time zonal-price archives**, 2021–2025. Selected exactly one NYC PTID 61761 hour-18 outcome per date. Matched them one-to-one to the existing corrected day-ahead target prices and forecast-eligibility table. All price labels are finite; no negative-price restriction or outlier deletion was applied. DST's repeated 01:00 hour does not affect the unique 18:00 target.

| Delivery year | Expected days | DA and integrated RT outcomes present | Eligible forecasts and both prices |
|---|---:|---:|---:|
| 2021 | 365 | 365 | 360 |
| 2022 | 365 | 365 | 359 |
| 2023 | 365 | 365 | 364 |
| 2024 | 366 | 366 | 364 |
| 2025 | 365 | 365 | 362 |
| **Total** | **1,826** | **1,826** | **1,809** |

The 17 excluded forecast dates are the same timing exclusions as the existing price study. No replacement forecasts or actual future weather were introduced. The outcome inventory includes RT−DA labels for auditability but no fitted signal, sign-selection experiment, P&L summary, Sharpe ratio or hit rate was calculated.

Corrected/finalized price archives may be used as eventual outcome/settlement proxies. They must not enter pre-cutoff features. Exact original-publication price vintages remain unverified and are still excluded from inputs. The future study would be retrospective gross-settlement research using corrected outcomes, not a reconstruction of historical invoice vintages or actual trading records.

### Costs
Official NYISO training material identifies Schedule 1/FERC charges and uplift allocations, including charges relevant to virtual supply. **Per instruction, no historical cost series was collected or modeled.** Gross here means the DA/RT energy spread alone, excluding fees, uplift, slippage, collateral/financing and other charges. Results would be dollars per assumed MWh, not a percentage investment return without a separately defined capital base.

## 3. Does the existing forecast fit this trade?

**Its data/timing pipeline fits; its prediction target does not.** The current model estimates DA alone. A high or low predicted DA price does not determine whether RT will be higher or lower. The 16.6% lower DA-price MAE cannot be converted into a trading return or taken as evidence of spread-direction skill.

For this pre-auction candidate, predict **E[RT − DA | information available at 04:00]** directly. Reuse the verified calendar and archived forecast-temperature inputs, source dates, timing exclusions, location and delivery hour. Do not use the final 2021–2024 fitted DA model to generate historical 2021–2023 inputs: that would contaminate earlier fitting periods. No existing demand/price fitted output is needed for the minimum spread model.

A simple proposed rule for a later experiment is: positive expected RT−DA → virtual load; negative → virtual supply; exactly zero → flat; fixed one-MWh assumed cleared size. This is a proposed rule, **not a tested signal**. Its historical P&L would be direction × realized (RT−DA), before the excluded costs, conditional on clearing.

## Bounded next experiment, if requested

Freeze the spread question and rule before fitting/scoring. Compare a calendar-only spread model against the same model with forecast temperature; include always-virtual-load, always-virtual-supply and flat benchmarks so a persistent average spread is not mistaken for weather-specific alpha. Keep size fixed and do not search many thresholds. Use only earlier fitting rows for transforms, coefficients and any model selection. Report gross dollar P&L per MWh, mean trade P&L, volatility/tail losses, drawdown, trade counts, monthly/year stability and dependence-aware paired uncertainty. Separately assess whether weather improves the **trading payoff**, not only price MAE.

A chronological 2021–2023 fit / 2024 validation / 2025 evaluation remains possible as retrospective research, but **2025 has already been examined in the demand and DA-price projects**. It is not a new blind holdout. Retrospectively corrected fitting labels and current market documentation also do not establish exact historical as-of model training or exhaustive 2021–2025 rule-version reconstruction. A truly fresh prospective test would be a separate task.

**Stopping point reached:** instrument/payoff, timing, outcome-data availability and target suitability have been assessed. No signal model or gross backtest was run in this feasibility step.

## Sources and retained evidence

- [NYISO Market Participants User's Guide](https://www.nyiso.com/documents/20142/3625950/mpug.pdf), §§7.7.1–7.7.4: qualification, financial virtual-load/supply transactions, price-dependent bidding and 05:00 close. §5.4.3: official time-weighted/integrated real-time prices. Previously cached in `../raw/nyiso_market_guide.pdf` and searchable extraction.
- [NYISO Accounting and Billing Manual](https://www.nyiso.com/documents/20142/2923231/acctbillmnl.pdf), §§4.4.1–4.4.2 and 6.3.1–6.3.2: DA/RT cash flows for virtual supply/load; Appendix B.9: RTD interval-duration weighting. Cached PDF and text in this folder's `raw/`.
- [NYISO Virtual Trading Market Settlements workshop, December 2024](https://www.nyiso.com/documents/20142/3035389/Virtual-Trading-Settlements.pdf/2e4e8a27-b4b1-a0e1-b376-0cab32b93180), slides 9/18/27/36/39: energy-settlement formulas and direction; later slides describe fees/uplift. Cached PDF and text. This is supporting training material, not a substitute for participant-specific invoices or a historical tariff audit.
- [NYISO P-4A integrated real-time zonal price index](https://mis.nyiso.com/public/P-4Alist.htm). Monthly pattern: `https://mis.nyiso.com/public/csv/rtlbmp/YYYYMM01rtlbmp_zone_csv.zip`. All 60 archived ZIPs cached with URL, retrieval UTC, response headers, bytes and SHA-256 receipts.
- [NYISO P-2A day-ahead zonal prices](https://mis.nyiso.com/public/P-2Alist.htm): previously cached in `../price_research/raw/`; original labels and receipt hashes preserved.

`check_feasibility.py` reproduces the downloads and outcome join. `outputs/annual_coverage.csv`, `spread_label_inventory.csv` and `data_feasibility.json` preserve the data checks. This assessment uses official market mechanics plus complete target-hour outcome coverage; it does not prove executable fills, full settlement amounts or profitable alpha.


---

# Frozen gross spread experiment

# Frozen gross spread-signal experiment

Written before spread-model fitting or trading-performance scoring on October 16, 2026. This is a retrospective hypothetical energy-settlement backtest conditional on a cleared one-MWh virtual schedule. No live orders or actual account/market access. Fees, uplift, financing, collateral, slippage, market impact and bid-limit/partial-fill simulation are intentionally excluded at the user's instruction.

## Task and information
At 04:00 America/New_York on D−1, choose the side of a NYC/Zone J virtual energy schedule for hour beginning 18:00 on D. Documented DAM close is 05:00. Retain the prior forecast-availability gate, fixed HRRR 06 UTC cycle, 40/41-hour horizon, verified point and exact eligibility dates. No new weather acquisition or substitutions. Outcomes: corrected archived NYC hourly integrated RT LBMP minus corrected DA LBMP, $/MWh. Both are unknown at the decision cutoff. No observed price/load or demand/DA fitted-model outputs enter features. Prices are outcome labels only; corrected training labels do not reconstruct historical as-of training vintages.

Use all 1,809 eligible dates in 2021–2025; 17 timing exclusions shared across all strategies. Check all source hashes, one-to-one join, timing, issue/valid metadata, RT-minus-DA arithmetic and no duplicate target dates. Existing projects remain preserved. 2025 demand and DA-price research and a few source samples have already been examined; no wholly unseen/forward-tested claim. This spread target has not previously been fitted or trading-scored.

## Fixed models, selection and position
Train 2021–2023, validate 2024, evaluate 2025 after refitting 2021–2024. Features identical to the prior price study: 14 calendar columns (intercept, weekdays, three annual Fourier harmonics and preexisting observed federal holidays excluding Juneteenth), then optional linear forecast temperature or a continuous piecewise-linear temperature spline at fitting 25/50/75 percentiles. OLS/SVD predicts RT-minus-DA directly. Center, scale and knots use fitting rows only. Do not import prior demand/DA-price coefficients or predictions.

Compare calendar-only, calendar+linear forecast temperature and calendar+spline forecast temperature. Select the weather variant with larger 2024 mean gross daily payoff under the fixed sign rule; exact tie favors linear. This trading objective differs from the preceding price study's validation MAE. No other variants, thresholds or position sizes searched. Record selection and hashes before scoring 2025. Refit all three on 2021–2024 and report all; primary strategy is the validation-selected weather variant, not the final-year winner.

Position s = +1 for predicted RT−DA > 0 (virtual load), −1 for predicted RT−DA < 0 (virtual supply), zero for exact zero. Cleared quantity is assumed 1 MWh on each active target date. Gross energy-settlement payoff = s × (RT−DA) dollars. This is conditional directional spread research, not a validated executable bidding strategy. No actual DA price used to decide side or guaranteed fill inferred from the assumption.

Benchmarks on identical dates: calendar-model sign rule; always virtual load; always virtual supply; flat; and training-mean-spread sign (computed from the fitting sample only). Calendar vs weather is the primary incremental comparison. Always-side benchmarks reveal persistent spread premia. Do not report weather as alpha merely because raw gross payoff is positive.

## Reporting
2025 primary: mean gross payoff per eligible decision date ($ for assumed 1 MWh), and incremental mean payoff vs calendar. Report total gross dollars, mean active-trade payoff, positions/trade count, positive-payoff win rate, zero-payoff trades, sample daily standard deviation, best/worst trade, fifth-percentile daily payoff, worst-5%-day average, and maximum drawdown of cumulative dollar payoff including initial equity zero. No percentage return, capital-based return or annualized Sharpe ratio because capital/collateral is undefined and dependence matters. Forecast MAE/RMSE are secondary, not substitutes for trading metrics.

Paired circular calendar-day moving-block bootstrap: seed 61761, 5,000 replicates; primary 7-day blocks, 14/28-day sensitivity. Reindex all 365 evaluation dates; excluded dates have zero count and zero payoff. Compare selected strategy against flat, calendar, always-load, always-supply, and training-mean. Percentile 95% intervals concern mean paired payoff differences for this year; no parameter-refitting uncertainty or across-all-future-years guarantee. Report monthly and meteorological-season stability, residual lag-1/7 exact-day correlations, exposure directions and disagreement with calendar. Ten best and ten worst selected payoffs are diagnostics, retained in the primary result, with top-ten contribution disclosed. No outlier deletion or final-year tuning.

## Delivery and stop
Runnable modular code, hashes/split/selection metadata, daily predictions/positions/payoffs, metrics/uncertainty/exclusions, meaningful arithmetic/timing/input-isolation/preprocessing/selection tests, one executed notebook with four figures and concise findings. Add a clearly separated Part III to the combined NYC walkthrough after verification; retain earlier studies and the original combined package as a snapshot. Stop after this fixed gross comparison regardless of results. No execution or cost extension is included.


---

# Gross spread findings and reproduction

# NYC gross spread-signal backtest

**Completed: a directional trading rule was tested, but convincing gross alpha was not established.** Costs are deliberately excluded.

At 04:00 New York time on the prior day, forecast **real-time minus day-ahead electricity price** for NYC's 18:00–19:00 delivery hour. Positive forecast means virtual load; negative means virtual supply; exactly zero means flat. Assume **one MWh clears** for each active signal. Gross energy payoff is side × realized spread. Bid acceptance, partial fills and actual execution are not established.

## Result: 2025 retrospective evaluation

| Strategy | Gross total, $ | Mean per decision day, $ | Maximum dollar drawdown |
|---|---:|---:|---:|
| **Linear-weather signal, selected on 2024** | **1,020.96** | **2.82** | **983.09** |
| Calendar-only signal | 321.98 | 0.89 | 1,660.66 |
| Always virtual load | 1,384.92 | 3.83 | 1,096.67 |
| Training-mean signal (chooses virtual load) | 1,384.92 | 3.83 | 1,096.67 |
| Always virtual supply | −1,384.92 | −3.83 | 2,684.56 |
| Flat | 0.00 | 0.00 | 0.00 |
| Spline-weather signal **(unselected alternative)** | 2,524.12 | 6.97 | 1,300.91 |

Same 362 eligible dates, one assumed cleared MWh per active date. These are hypothetical gross dollars—not percentage returns, a live account, or net profit. The selected signal buys the DA/RT spread on 195 days and sells it on 167; win rate is 44.5%.

**Why this does not establish alpha:**
- The selected signal underperforms the simple always-load / training-mean benchmark.
- Its seven-day block-bootstrap 95% interval for mean gross payoff is **−$8.10 to +$18.29/day**. Increment versus calendar: **−$0.72 to +$6.04/day**. Both cross zero, as do 14/28-day sensitivity intervals.
- Only **three months** have positive payoff. The best day contributes **+$1,768.53**, more than the entire +$1,020.96 net total. All other days together contribute **−$747.57**.
- The ten best days sum to $4,288.91 (420.1% of net gain), illustrating how other days offset the winners.
- The spline's better 2025 result was not the validation-selected strategy. Selecting it after seeing the final year would be an outcome-informed change, not the original test.

The June 24 outlier was reconciled to raw NYISO archives: NYC DA **$365.00/MWh**, hourly integrated RT **$2,133.53/MWh**, spread **+$1,768.53/MWh**. It is retained, not removed. Calendar, linear weather and always-load all chose virtual load that day, so its profit is not unique weather timing.

Read the [executed notebook](NYC_Gross_Spread_Backtest.ipynb) or [HTML walkthrough](outputs/NYC_Gross_Spread_Backtest.html).

## How the experiment was frozen
Development fitting 2021–2023; validation 2024; final refit 2021–2024; evaluation 2025. All three OLS models predict the spread directly, using the same 14 calendar features and optional linear / fixed three-hinge forecast-temperature terms. Fitting rows alone determine centering/scaling/knots. Weather variant selection maximizes **2024 mean gross payoff** under the fixed sign rule; linear wins $4.53/day versus spline $0.89/day. No threshold search, leverage or sizing optimization.

The prior 16.6% DA-price MAE improvement used a different target and validation objective. Its fitted model and demand estimates are not inputs here. The new spread models were fitted independently. Price outcomes do not enter prediction-time features.

1,826 target-day DA/RT outcomes exist. The original 17 forecast timing exclusions are retained, giving 1,809 eligible days. Forecast objects must predate cutoff by five minutes and have the correct issue/valid metadata. No realized future weather, late forecast, price history or observed load is substituted. Official integrated RT prices preserve duration weighting and include loss/congestion components; these are not added again.

## Limits and interpretation
This is conditional on cleared one-MWh schedules. Fees, uplift, slippage, financing/collateral, bid limits, market access and partial fills are intentionally omitted. A percentage return cannot be calculated without a defined capital base. Both DA and RT clearing prices are unknown at the decision cutoff; neither is an input.

2025 demand and DA-price data were examined before this experiment. It is a retrospective chronological evaluation, not a new blind or prospective holdout. Corrected outcome labels and archive timestamp evidence do not reconstruct every historical training/invoice vintage. Only one evaluation year, heavy tails, selective timing exclusions and omitted market drivers limit inference. Bootstrap intervals describe this year's paired payoffs, not model-refitting uncertainty or all future years.

**The honest conclusion is that this specific gross signal did not demonstrate reliable incremental alpha.** The earlier 39.2% demand and 16.6% DA-price prediction-error reductions remain separate valid findings, not trading returns.

## Reproduce
This folder uses raw data retained in adjacent `price_research/` and `trading_feasibility/` folders. Use `../price_research/.venv/bin/python` or a Python 3.12 environment with `requirements.txt` installed. From this folder:

```sh
python src/run.py
python -m unittest discover -s tests -v
python execute_notebook.py
```

[EXPERIMENT.md](EXPERIMENT.md) is the frozen pre-score specification. Source receipts, the market-payoff evidence and all outcome data are in [trading_feasibility](../trading_feasibility/FEASIBILITY_BRIEF.md). Outputs preserve source hashes, exclusions, model/selection records, daily predictions/positions/payoffs, benchmarks, monthly/season metrics, uncertainty, risk and large-day diagnostics. The first selection record is retained separately from deterministic reruns.

## Stopping point
The fixed gross trading experiment is complete. No final-year tuning, cost/execution extension or extra model search is pending.


## Demand exact model scores

```csv
group_type,group,model,hours,mae_mw,rmse_mw,mean_residual_mw,mae_improvement_pct
overall,all,calendar,8654,436.37865472479353,602.3483601645777,125.75739675980869,0.0
overall,all,linear,8654,442.98880319997204,598.0812921037207,145.7415828716658,-1.5147735581492316
overall,all,spline,8654,265.1337867602567,359.6811562038539,109.4226530975946,39.24226497112561
temperature,hot,calendar,472,1136.3795812205906,1377.115749285471,1036.674197384142,0.0
temperature,hot,linear,472,1056.9652094164082,1284.0716347530301,947.7666123398342,6.988366661682093
temperature,hot,spline,472,511.2979207781684,648.7829654266264,161.1433616615198,55.00641429785451
temperature,not_hot,calendar,8182,395.9972764180206,523.7866308361021,73.20878640846607,0.0
temperature,not_hot,linear,8182,407.56997360645477,532.1827959738722,99.47467821400565,-2.922418379518819
temperature,not_hot,spline,8182,250.93316695379693,335.4873789402325,106.43900919119363,36.63260282403858
month,1,calendar,744,471.1977480752552,567.9677268771688,430.961831548193,0.0
month,1,linear,744,546.4018839299033,669.6274142554189,489.56628785886153,-15.9602069750633
month,1,spline,744,295.43246451392605,332.7705430282478,272.2927377072708,37.30180890704461
month,2,calendar,672,376.9031527350545,439.00137546814915,292.9448855769593,0.0
month,2,linear,672,458.686369376916,535.4787272820679,333.71150952097724,-21.698735085761225
month,2,spline,672,218.3558274901066,253.923824461151,204.861906852912,42.06579968737999
month,3,calendar,742,154.01168777204177,203.1101011827319,-10.019912153529413,0.0
month,3,linear,742,212.61936574909478,277.27427665824456,-33.9794590916293,-38.05404565385995
month,3,spline,742,130.93155049573167,178.41805721298365,56.18746216131062,14.985964773317619
month,4,calendar,720,203.40977063219972,251.45381341420912,142.19592263473615,0.0
month,4,linear,720,220.78071304740783,290.28574122760057,123.83532839570022,-8.539876113727985
month,4,spline,720,184.64574124526018,266.46221310157074,52.03847144454702,9.224743397832238
month,5,calendar,744,335.4516128587796,412.759771963287,-43.73499251096366,0.0
month,5,linear,744,275.9869922796088,345.02898720304995,-32.333149456158175,17.72673563033503
month,5,spline,744,230.75797418745842,296.252282398433,53.38086088331601,31.209758623338537
month,6,calendar,720,839.188895928298,1112.3981906043784,246.53538124919723,0.0
month,6,linear,720,757.9039280453665,1025.2747475312954,241.07069783734426,9.686134823437504
month,6,spline,720,426.9675592310994,576.3824726178975,153.47706023191722,49.12140028273439
month,7,calendar,743,669.198644161227,824.1407167208919,448.96825919567743,0.0
month,7,linear,743,636.3527426788963,779.5039000643675,433.21928479445705,4.9082438777950115
month,7,spline,743,426.73795244907643,535.7592618529428,299.0515164265787,36.231497751471174
month,8,calendar,691,839.3496182254954,945.161882604698,-631.3878461437508,0.0
month,8,linear,691,783.4452662261745,878.6151402142465,-584.9626001072195,6.660436936578434
month,8,spline,691,444.5350434991173,532.0723951492737,-284.90049500140447,47.038155037357654
month,9,calendar,672,499.3355546174247,579.0086010733239,39.45682090259782,0.0
month,9,linear,672,444.84647612957235,519.6716005648904,36.21796722982169,10.912316974824709
month,9,spline,672,260.9184522481845,337.05976589947494,84.68329297663935,47.74687084958489
month,10,calendar,742,232.79790188135752,322.89527518320716,10.52263792642535,0.0
month,10,linear,742,209.96241268948128,283.7771856571311,32.93574882396395,9.809147336522841
month,10,spline,742,144.50186714824056,210.4495495693026,56.937691691019324,37.92819180050682
month,11,calendar,720,171.23913692386412,220.51214479017986,96.96339235991424,0.0
month,11,linear,720,218.35617707458024,280.21606991697064,129.57971802845063,-27.51534549701986
month,11,spline,720,151.61340032703723,188.781508547088,103.10080662263483,11.461011162157888
month,12,calendar,744,469.4357920368329,539.9573859258736,442.8308842006825,0.0
month,12,linear,744,571.2336980614186,659.3467684909089,537.0235484480994,-21.685160729414193
month,12,spline,744,272.54698124660376,308.6158323434248,240.04898639377802,41.9415847981998
season,DJF,calendar,2160,441.2547557784029,521.0523822424672,392.1114553818889,0.0
season,DJF,linear,2160,527.665793158718,627.2157095954692,457.42452435670174,-19.583026867977935
season,DJF,spline,2160,263.5702887588823,301.67575670101877,240.20807598904506,40.26800044479369
season,JJA,calendar,2154,780.6040779359255,966.6905043614775,34.726039645533184,0.0
season,JJA,linear,2154,724.1697283961794,899.2283546461763,42.360108807372725,7.229574010037188
season,JJA,spline,2154,432.523981603503,548.5221564079441,63.06059332681425,44.59111938702862
season,MAM,calendar,2206,231.32715645918893,303.26935539218493,28.28987082997926,0.0
season,MAM,linear,2206,236.65458070534493,305.7966617965792,18.08377815210043,-2.3029826362370347
season,MAM,spline,2206,182.13058792379388,251.95435274981355,53.8867438172953,21.267096041996425
season,SON,calendar,2134,295.9614407141794,397.7802806665321,48.798698916162905,0.0
season,SON,linear,2134,286.7597889729923,373.54365510083426,66.57647450154916,3.109071140815763
season,SON,spline,2134,183.5610279148272,251.39496230253553,81.25000978600518,37.978059752689646
```


## Demand validation scores

```csv
model,hours,mae_mw,rmse_mw,mean_residual_mw
calendar,8778,351.81185632630223,513.0798056798285,68.65283953357866
linear,8778,364.07517821717414,506.8997229579998,66.96957315108283
spline_3,8778,226.81170376865515,331.48352004680993,82.79877715309185
spline_5,8778,226.92853646576972,331.2572601755779,83.0725078257313
```


## Demand block uncertainty

```csv
comparison,block_days,mean_improvement_mw,lower_95_mw,upper_95_mw,calendar_days,days_with_observations
calendar minus linear,7,-6.610148475178449,-24.890974165026304,12.05319568526153,365,362
calendar minus linear,14,-6.610148475178449,-30.95198940344407,17.59626543335394,365,362
calendar minus linear,28,-6.610148475178449,-40.17264319823039,28.18103401325487,365,362
calendar minus spline,7,171.2448679645368,128.70404739965318,220.1923785899817,365,362
calendar minus spline,14,171.2448679645368,116.03203165141808,229.95953286164502,365,362
calendar minus spline,28,171.2448679645368,106.1630712748894,239.43472327576416,365,362
```


## Price exact model scores

```csv
group_type,group,model,days,mae_mwh,rmse_mwh,mean_residual_mwh,improvement_pct
overall,all,calendar,362,35.15811028663848,62.3019590739985,27.419049280036777,0.0
overall,all,linear,362,35.85742178913522,61.58693783288309,26.40749435686642,-1.9890474681243258
overall,all,spline,362,29.332627300982686,49.45781347346849,21.806438975920223,16.569385948680292
forecast_temperature,hot,calendar,16,106.09783759361925,152.40219361003025,106.09783759361925,0.0
forecast_temperature,hot,linear,16,115.75001562289147,160.43722515997038,115.75001562289147,-9.097431435164996
forecast_temperature,hot,spline,16,84.90866463476678,122.80070965592704,69.70812636298312,19.97135232860466
forecast_temperature,not_hot,calendar,346,31.877660468974636,54.65320217970395,23.78072380888846,0.0
forecast_temperature,not_hot,linear,346,32.162966582949956,52.70724518694505,22.27604828676121,-0.895003302557282
forecast_temperature,not_hot,spline,346,26.762637135258572,43.14912422646145,19.591332044726563,16.04579275412739
month,1,calendar,31,86.0144090876166,113.87056946673805,81.51848044597611,0.0
month,1,linear,31,81.5643636035624,107.33869230580112,77.03137058610744,5.173604668400691
month,1,spline,31,56.86214769769479,75.47001474903934,51.904090335843485,33.89229978924406
month,2,calendar,28,66.14089611137047,83.70884543296067,64.91038588087167,0.0
month,2,linear,28,63.97580002001161,79.5715971946476,63.22314056537157,3.273460474005654
month,2,spline,28,58.682750068387634,67.22092545811769,56.84834936295469,11.276149071860974
month,3,calendar,31,15.795484715138663,24.382774273315444,15.341687100438172,0.0
month,3,linear,31,18.41851784348873,24.679913093366068,18.41851784348873,-16.60622118063972
month,3,spline,31,24.03511367739025,28.249579334389175,22.840597019874878,-52.16445782353602
month,4,calendar,30,14.504110933811319,18.539521076117964,14.003738399017925,0.0
month,4,linear,30,15.245511853501169,18.253872796299294,14.734240773584325,-5.111660570394083
month,4,spline,30,13.657445075963377,17.911155625157743,10.429825318129542,5.837419899169642
month,5,calendar,31,9.338562365230477,11.003533016992337,-0.9162396605993761,0.0
month,5,linear,31,13.707790232032702,16.56692501358855,-2.669404377158065,-46.786943170929845
month,5,spline,31,5.444640659079589,6.648410941940151,0.49151511436187884,41.69722869388136
month,6,calendar,29,37.99923727856269,78.98723911228969,17.50417986965765,0.0
month,6,linear,29,43.94458675332906,84.73831178751392,18.73913930929783,-15.645970552468034
month,6,spline,29,29.360347296943893,63.193516662324505,13.367631456598929,22.73437731996909
month,7,calendar,31,62.835442112447645,106.84457560779043,60.54899410926494,0.0
month,7,linear,31,65.50900340353397,109.75310232827884,62.47526921469456,-4.254861907873315
month,7,spline,31,57.261832743272656,95.28193392599546,52.009439793016156,8.870168143642076
month,8,calendar,31,26.01925368064536,41.97884811418173,3.000871136462168,0.0
month,8,linear,31,28.53639362373297,43.348245081337176,0.520549776670683,-9.674143516883445
month,8,spline,31,22.52207885335988,39.29670029852106,9.879315268118207,13.440719208202667
month,9,calendar,30,11.720799970224952,13.844091993276345,-7.908883174595616,0.0
month,9,linear,30,14.833040316574234,17.264666814006006,-7.096021163351653,-26.553139327140567
month,9,spline,30,7.558013259869445,9.499823803828358,-3.741303785572572,35.51623371212275
month,10,calendar,29,20.23690968764499,25.179901417627267,19.2691643437361,0.0
month,10,linear,29,20.167897428648807,26.37679935381237,18.642315650573124,0.34102172743457443
month,10,spline,29,18.83623574586503,24.030624906864034,17.84021519226798,6.921382579648994
month,11,calendar,30,16.624049114558552,19.19048278021707,16.20320666329058,0.0
month,11,linear,30,14.601891419636111,16.21720887268974,13.299387926681735,12.164050292365484
month,11,spline,30,19.680168542298546,21.93089920402407,14.864753129901016,-18.383724727230195
month,12,calendar,31,54.86696965398223,69.52024318508876,46.08156802617087,0.0
month,12,linear,31,49.98615510454987,63.31996687749673,40.25836151785946,8.895724659504882
month,12,spline,31,38.73626270647638,46.71618208750775,16.118633901995405,29.399668050256697
season,DJF,calendar,90,69.10297591231041,91.16453241884065,64.14547008112183,0.0
season,DJF,linear,90,65.2154275612423,85.55357642065856,60.06921812281533,5.625732176862109
season,DJF,spline,90,51.185196938268454,64.18239180397777,41.11620259484152,25.92909890997904
season,JJA,calendar,91,42.37882912817804,80.48261925087179,27.227110316896834,0.0
season,JJA,linear,91,46.04176179881117,83.85663403645327,27.431927787933628,-8.64330786382585
season,JJA,spline,91,36.53572891326353,69.93862309937452,25.34299691358829,13.787781151861463
season,MAM,calendar,92,13.198682472888946,18.79377072898583,9.427185028321093,0.0
season,MAM,linear,92,15.796531586371731,20.158747890093803,10.111410224606306,-19.682639678763064
season,MAM,spline,92,14.386910181624637,19.708122358386184,11.262937344622022,-9.002623641991525
season,SON,calendar,89,16.148492735788874,19.88302901220728,9.074555849766245,0.0
season,SON,linear,89,16.493449185585682,20.391760920197964,8.165484907489025,-2.136152614617107
season,SON,spline,89,15.319059446012647,19.511732809970326,9.562581133771063,5.136289208825091
```


## Price validation scores

```csv
model,days,mae_mwh,rmse_mwh,mean_residual_mwh
calendar,364,28.808347146989785,35.76410855102028,-16.598073708402442
linear,364,28.39483152346955,34.97918670580673,-16.721870112980348
spline,364,20.322908307280183,25.968090975339592,-14.29196747707433
```


## Price block uncertainty

```csv
weather_model,block_days,improvement_mwh,lower_95_mwh,upper_95_mwh,expected_calendar_days,paired_days
linear,7,-0.6993115024967332,-1.8992457790041581,0.5190372025062564,365,362
linear,14,-0.6993115024967332,-2.190502822368572,0.7541628051799013,365,362
linear,28,-0.6993115024967332,-2.4940460933963555,1.187102931328029,365,362
spline,7,5.825482985655798,1.981990758646593,9.815705556231423,365,362
spline,14,5.825482985655798,1.648893785908006,10.388190809700493,365,362
spline,28,5.825482985655798,1.4974863335309179,10.648416480057685,365,362
```


## Gross trading metrics

```csv
group_type,group,strategy,days,active_trades,virtual_load_days,virtual_supply_days,flat_days,total_gross_dollars,mean_daily_gross_dollars,mean_active_trade_dollars,win_rate_active,zero_payoff_active_trades,daily_std_dollars,best_day_dollars,worst_day_dollars,fifth_percentile_dollars,worst_five_percent_mean_dollars,max_drawdown_dollars,spread_mae_mwh,spread_rmse_mwh
overall,all,calendar,362,362,191,171,0,321.9800000000005,0.889447513812156,0.889447513812156,0.4281767955801105,0,113.66568351091794,1768.5300000000002,-302.82,-100.9645,-149.92526315789473,1660.6599999999994,37.62546358590256,112.93515840377592
overall,all,linear,362,362,195,167,0,1020.9600000000005,2.8203314917127087,2.8203314917127087,0.4447513812154696,0,113.63408209085948,1768.5300000000002,-233.7,-92.28549999999998,-138.89578947368423,983.0900000000003,37.43419435616741,112.63945963672772
overall,all,spline,362,362,184,178,0,2524.12,6.972707182320442,6.972707182320442,0.5082872928176796,0,113.45451772937419,1768.5300000000002,-302.82,-67.46800000000002,-134.8242105263158,1300.9099999999976,37.80916978028991,110.08145413265643
overall,all,always_load,362,362,362,0,0,1384.9200000000003,3.825745856353592,3.825745856353592,0.3314917127071823,0,113.60459515852303,1768.5300000000002,-233.7,-54.554,-112.09052631578949,1096.6700000000008,,
overall,all,always_supply,362,362,0,362,0,-1384.9200000000003,-3.825745856353592,-3.825745856353592,0.6685082872928176,0,113.60459515852303,233.7,-1768.5300000000002,-100.68299999999999,-287.3736842105263,2684.56,,
overall,all,flat,362,0,0,0,362,0.0,0.0,,,0,0.0,0.0,-0.0,0.0,0.0,0.0,,
overall,all,training_mean,362,362,362,0,0,1384.9200000000003,3.825745856353592,3.825745856353592,0.3314917127071823,0,113.60459515852303,1768.5300000000002,-233.7,-54.554,-112.09052631578949,1096.6700000000008,,
month,1,calendar,31,31,5,26,0,-315.19999999999993,-10.16774193548387,-10.16774193548387,0.3870967741935484,0,61.44176677742253,110.41000000000004,-124.07,-117.64500000000001,-123.01,609.69,48.015746218153765,62.67692282146826
month,1,linear,31,31,4,27,0,-322.9399999999999,-10.417419354838707,-10.417419354838707,0.3548387096774194,0,61.39853201110169,110.41000000000004,-124.07,-117.64500000000001,-123.01,569.95,47.98594133155499,62.899933784887715
month,1,spline,31,31,19,12,0,-60.94000000000001,-1.9658064516129037,-1.9658064516129037,0.45161290322580644,0,62.27300034387261,124.07,-113.34,-110.38000000000002,-111.87500000000003,497.7800000000001,49.59449090715296,63.18404019065923
month,1,always_load,31,31,31,0,0,126.3,4.074193548387097,4.074193548387097,0.5161290322580645,0,62.16725364017049,124.07,-110.41000000000004,-100.25,-110.38000000000002,384.6099999999999,,
month,1,always_supply,31,31,0,31,0,-126.3,-4.074193548387097,-4.074193548387097,0.4838709677419355,0,62.16725364017049,110.41000000000004,-124.07,-117.64500000000001,-123.01,450.05,,
month,1,flat,31,0,0,0,31,0.0,0.0,,,0,0.0,0.0,-0.0,0.0,0.0,0.0,,
month,1,training_mean,31,31,31,0,0,126.3,4.074193548387097,4.074193548387097,0.5161290322580645,0,62.16725364017049,124.07,-110.41000000000004,-100.25,-110.38000000000002,384.6099999999999,,
month,2,calendar,28,28,5,23,0,-290.92999999999995,-10.390357142857141,-10.390357142857141,0.5714285714285714,0,52.4718655113204,55.349999999999994,-147.75,-114.136,-131.265,453.68,36.04715021012272,53.39493828775647
month,2,linear,28,28,5,23,0,-354.92999999999995,-12.676071428571428,-12.676071428571428,0.5714285714285714,0,51.94825012839332,55.349999999999994,-147.75,-114.136,-131.265,525.38,36.61967273036115,54.191719492295306
month,2,spline,28,28,13,15,0,636.39,22.728214285714284,22.728214285714284,0.7142857142857143,0,48.2654191101487,147.75,-101.37,-23.271000000000015,-63.11500000000001,101.37,33.237508788105046,49.78916961097396
month,2,always_load,28,28,28,0,0,428.51,15.303928571428571,15.303928571428571,0.4642857142857143,0,51.20908132275598,147.75,-43.84,-40.68699999999999,-43.275,145.87000000000006,,
month,2,always_supply,28,28,0,28,0,-428.51,-15.303928571428571,-15.303928571428571,0.5357142857142857,0,51.20908132275598,43.84,-147.75,-114.136,-131.265,484.0299999999999,,
month,2,flat,28,0,0,0,28,0.0,0.0,,,0,0.0,0.0,-0.0,0.0,0.0,0.0,,
month,2,training_mean,28,28,28,0,0,428.51,15.303928571428571,15.303928571428571,0.4642857142857143,0,51.20908132275598,147.75,-43.84,-40.68699999999999,-43.275,145.87000000000006,,
month,3,calendar,31,31,9,22,0,-72.28,-2.3316129032258064,-2.3316129032258064,0.4838709677419355,0,18.228605010948076,31.580000000000005,-46.44999999999999,-33.445,-45.154999999999994,175.1,14.329171718227338,18.817597918986063
month,3,linear,31,31,13,18,0,-11.059999999999995,-0.35677419354838696,-0.35677419354838696,0.5483870967741935,0,18.378469538583595,31.580000000000005,-46.44999999999999,-33.445,-45.154999999999994,175.1,14.426633450976283,18.77032384456211
month,3,spline,31,31,10,21,0,-66.88000000000005,-2.1574193548387113,-2.1574193548387113,0.5161290322580645,0,18.250755229623046,31.580000000000005,-46.44999999999999,-33.445,-45.154999999999994,138.23,14.412024402507425,20.300476082097195
month,3,always_load,31,31,31,0,0,-160.78000000000003,-5.186451612903227,-5.186451612903227,0.3548387096774194,0,17.609762926359362,43.86,-46.44999999999999,-27.295000000000005,-39.015,160.78000000000006,,
month,3,always_supply,31,31,0,31,0,160.78000000000003,5.186451612903227,5.186451612903227,0.6451612903225806,0,17.609762926359362,46.44999999999999,-43.86,-19.625,-33.445,90.24,,
month,3,flat,31,0,0,0,31,0.0,0.0,,,0,0.0,0.0,-0.0,-0.0,0.0,0.0,,
month,3,training_mean,31,31,31,0,0,-160.78000000000003,-5.186451612903227,-5.186451612903227,0.3548387096774194,0,17.609762926359362,43.86,-46.44999999999999,-27.295000000000005,-39.015,160.78000000000006,,
month,4,calendar,30,30,9,21,0,34.33999999999999,1.1446666666666663,1.1446666666666663,0.6,0,13.442703374804806,21.43,-41.120000000000005,-21.842499999999994,-34.035,41.120000000000005,9.815001780153638,13.034269825030128
month,4,linear,30,30,10,20,0,81.50000000000001,2.7166666666666672,2.7166666666666672,0.6333333333333333,0,13.20707943212415,26.949999999999996,-41.120000000000005,-13.3005,-28.360000000000003,41.120000000000005,9.71788056291538,12.833353725625964
month,4,spline,30,30,8,22,0,16.18000000000001,0.5393333333333337,0.5393333333333337,0.6333333333333333,0,13.481869545310904,20.89,-41.120000000000005,-24.465999999999998,-34.035,55.03999999999999,10.983749903061819,14.600830711585814
month,4,always_load,30,30,30,0,0,-176.46,-5.882000000000001,-5.882000000000001,0.3,0,12.09424496937739,21.43,-41.120000000000005,-24.222999999999995,-34.035,205.52999999999997,,
month,4,always_supply,30,30,0,30,0,176.46,5.882000000000001,5.882000000000001,0.7,0,12.09424496937739,41.120000000000005,-21.43,-9.779499999999995,-16.48,29.069999999999993,,
month,4,flat,30,0,0,0,30,0.0,0.0,,,0,0.0,0.0,-0.0,0.0,0.0,0.0,,
month,4,training_mean,30,30,30,0,0,-176.46,-5.882000000000001,-5.882000000000001,0.3,0,12.09424496937739,21.43,-41.120000000000005,-24.222999999999995,-34.035,205.52999999999997,,
month,5,calendar,31,31,17,14,0,-76.05999999999997,-2.4535483870967734,-2.4535483870967734,0.41935483870967744,0,11.882644079605376,20.04,-27.14,-19.880000000000003,-24.005000000000003,87.71999999999997,11.46647940083879,13.58980504532767
month,5,linear,31,31,18,13,0,-34.31999999999998,-1.1070967741935478,-1.1070967741935478,0.45161290322580644,0,12.08930414141591,20.870000000000005,-27.14,-18.89,-23.015,66.85,11.198227631778138,13.207034097534917
month,5,spline,31,31,12,19,0,22.840000000000018,0.7367741935483877,0.7367741935483877,0.5161290322580645,0,12.118451327650954,20.04,-27.14,-19.880000000000003,-24.005000000000003,35.35999999999999,10.613589681974531,13.308648499307402
month,5,always_load,31,31,31,0,0,-168.19999999999996,-5.425806451612902,-5.425806451612902,0.2903225806451613,0,10.816520011597554,20.870000000000005,-27.14,-19.465,-23.59,199.42999999999998,,
month,5,always_supply,31,31,0,31,0,168.19999999999996,5.425806451612902,5.425806451612902,0.7096774193548387,0,10.816520011597554,27.14,-20.870000000000005,-10.005000000000003,-15.940000000000005,31.88000000000001,,
month,5,flat,31,0,0,0,31,0.0,0.0,,,0,0.0,0.0,-0.0,0.0,0.0,0.0,,
month,5,training_mean,31,31,31,0,0,-168.19999999999996,-5.425806451612902,-5.425806451612902,0.2903225806451613,0,10.816520011597554,20.870000000000005,-27.14,-19.465,-23.59,199.42999999999998,,
month,6,calendar,29,29,28,1,0,2313.1099999999997,79.76241379310343,79.76241379310343,0.4482758620689655,0,342.02548117955837,1768.5300000000002,-49.36000000000001,-32.02,-40.940000000000005,228.92000000000004,101.1186678822597,341.87510709250813
month,6,linear,29,29,29,0,0,2289.69,78.9548275862069,78.9548275862069,0.41379310344827586,0,342.219498876929,1768.5300000000002,-49.36000000000001,-32.02,-40.940000000000005,252.34000000000006,100.54741060510611,340.8057323697557
month,6,spline,29,29,23,6,0,2427.0700000000006,83.69206896551727,83.69206896551727,0.4827586206896552,0,341.0515650620604,1768.5300000000002,-49.36000000000001,-29.818000000000005,-40.31500000000001,159.60000000000002,99.2882836531458,329.9596899239397
month,6,always_load,29,29,29,0,0,2289.69,78.9548275862069,78.9548275862069,0.41379310344827586,0,342.219498876929,1768.5300000000002,-49.36000000000001,-32.02,-40.940000000000005,252.34000000000006,,
month,6,always_supply,29,29,0,29,0,-2289.69,-78.9548275862069,-78.9548275862069,0.5862068965517241,0,342.219498876929,49.36000000000001,-1768.5300000000002,-395.306,-1152.8700000000001,2542.03,,
month,6,flat,29,0,0,0,29,0.0,0.0,,,0,0.0,0.0,-0.0,0.0,0.0,0.0,,
month,6,training_mean,29,29,29,0,0,2289.69,78.9548275862069,78.9548275862069,0.41379310344827586,0,342.219498876929,1768.5300000000002,-49.36000000000001,-32.02,-40.940000000000005,252.34000000000006,,
month,7,calendar,31,31,31,0,0,-382.94000000000005,-12.352903225806454,-12.352903225806454,0.3548387096774194,0,116.30615077439795,340.48,-233.7,-210.115,-229.94,943.2,78.06381059556139,115.12045060195975
month,7,linear,31,31,31,0,0,-382.94000000000005,-12.352903225806454,-12.352903225806454,0.3548387096774194,0,116.30615077439795,340.48,-233.7,-210.115,-229.94,943.2,77.99694624783771,114.79703622261958
month,7,spline,31,31,27,4,0,210.90000000000003,6.803225806451614,6.803225806451614,0.4838709677419355,0,116.77745810977666,340.48,-233.7,-174.55,-213.875,619.88,77.69552216491755,112.81579680407783
month,7,always_load,31,31,31,0,0,-382.94000000000005,-12.352903225806454,-12.352903225806454,0.3548387096774194,0,116.30615077439795,340.48,-233.7,-210.115,-229.94,943.2,,
month,7,always_supply,31,31,0,31,0,382.94000000000005,12.352903225806454,12.352903225806454,0.6451612903225806,0,116.30615077439795,233.7,-340.48,-198.21999999999997,-297.195,600.75,,
month,7,flat,31,0,0,0,31,0.0,0.0,,,0,0.0,0.0,-0.0,-0.0,0.0,0.0,,
month,7,training_mean,31,31,31,0,0,-382.94000000000005,-12.352903225806454,-12.352903225806454,0.3548387096774194,0,116.30615077439795,340.48,-233.7,-210.115,-229.94,943.2,,
month,8,calendar,31,31,27,4,0,-145.65999999999994,-4.698709677419353,-4.698709677419353,0.25806451612903225,0,105.57610675848763,528.8100000000001,-131.81,-109.65,-121.515,590.59,48.956407742153594,104.51829103737036
month,8,linear,31,31,25,6,0,-55.639999999999894,-1.7948387096774159,-1.7948387096774159,0.3225806451612903,0,105.66834574494446,528.8100000000001,-131.81,-109.65,-121.515,500.57,48.43278335819545,104.50535378739643
month,8,spline,31,31,12,19,0,247.86000000000004,7.995483870967743,7.995483870967743,0.6129032258064516,0,105.37110340248917,528.8100000000001,-131.81,-109.65,-121.515,400.43999999999994,46.65320834077703,105.83290561373892
month,8,always_load,31,31,31,0,0,-248.77999999999994,-8.025161290322579,-8.025161290322579,0.12903225806451613,0,105.36877209341067,528.8100000000001,-131.81,-109.65,-121.515,673.61,,
month,8,always_supply,31,31,0,31,0,248.77999999999994,8.025161290322579,8.025161290322579,0.8709677419354839,0,105.36877209341067,131.81,-528.8100000000001,-17.284999999999997,-273.39000000000004,556.3800000000001,,
month,8,flat,31,0,0,0,31,0.0,0.0,,,0,0.0,0.0,-0.0,0.0,0.0,0.0,,
month,8,training_mean,31,31,31,0,0,-248.77999999999994,-8.025161290322579,-8.025161290322579,0.12903225806451613,0,105.36877209341067,528.8100000000001,-131.81,-109.65,-121.515,673.61,,
month,9,calendar,30,30,13,17,0,-156.64,-5.221333333333333,-5.221333333333333,0.43333333333333335,0,17.08359199355624,23.090000000000003,-70.29,-24.2805,-47.98500000000001,163.88,12.437474028880404,19.11547056863277
month,9,linear,30,30,13,17,0,-116.95999999999997,-3.8986666666666654,-3.8986666666666654,0.43333333333333335,0,17.444993300783118,25.680000000000007,-70.29,-21.998499999999996,-46.43,158.17,12.416978744240641,18.7063904461849
month,9,spline,30,30,3,27,0,117.16000000000001,3.9053333333333335,3.9053333333333335,0.6333333333333333,0,17.443450649877526,70.29,-25.680000000000007,-22.2845,-24.385000000000005,28.840000000000003,14.123529927723308,19.270625538788465
month,9,always_load,30,30,30,0,0,42.340000000000025,1.4113333333333342,1.4113333333333342,0.4666666666666667,0,17.83230132581638,70.29,-22.569999999999993,-19.3855,-21.609999999999996,46.48,,
month,9,always_supply,30,30,0,30,0,-42.340000000000025,-1.4113333333333342,-1.4113333333333342,0.5333333333333333,0,17.83230132581638,22.569999999999993,-70.29,-24.514500000000005,-47.98500000000001,97.48,,
month,9,flat,30,0,0,0,30,0.0,0.0,,,0,0.0,0.0,-0.0,0.0,0.0,0.0,,
month,9,training_mean,30,30,30,0,0,42.340000000000025,1.4113333333333342,1.4113333333333342,0.4666666666666667,0,17.83230132581638,70.29,-22.569999999999993,-19.3855,-21.609999999999996,46.48,,
month,10,calendar,29,29,10,19,0,-653.1899999999999,-22.523793103448273,-22.523793103448273,0.4482758620689655,0,75.56211822135826,121.76,-302.82,-156.80400000000003,-257.49,681.7900000000001,43.94219504423197,78.9016943818194
month,10,linear,29,29,13,16,0,-69.05000000000007,-2.381034482758623,-2.381034482758623,0.4827586206896552,0,78.925292403858,302.82,-212.16000000000005,-71.306,-142.96500000000003,484.81000000000006,43.80329793583438,78.67357721683666
month,10,spline,29,29,17,12,0,-623.85,-21.51206896551724,-21.51206896551724,0.3448275862068966,0,75.86683730530329,121.76,-302.82,-154.34000000000003,-257.49,652.45,45.7572441349198,79.3903851527355
month,10,always_load,29,29,29,0,0,370.21000000000004,12.765862068965518,12.765862068965518,0.27586206896551724,0,77.8863665182095,302.82,-73.77,-44.046,-59.879999999999995,181.5,,
month,10,always_supply,29,29,0,29,0,-370.21000000000004,-12.765862068965518,-12.765862068965518,0.7241379310344828,0,77.8863665182095,73.77,-302.82,-176.00000000000003,-257.49,553.2300000000001,,
month,10,flat,29,0,0,0,29,0.0,0.0,,,0,0.0,0.0,-0.0,0.0,0.0,0.0,,
month,10,training_mean,29,29,29,0,0,370.21000000000004,12.765862068965518,12.765862068965518,0.27586206896551724,0,77.8863665182095,302.82,-73.77,-44.046,-59.879999999999995,181.5,,
month,11,calendar,30,30,19,11,0,-109.55000000000004,-3.651666666666668,-3.651666666666668,0.3333333333333333,0,29.959275931968318,37.73,-126.84,-26.008499999999994,-79.095,277.55,22.100465278120407,30.816507077842772
month,11,linear,30,30,20,10,0,-177.55000000000004,-5.918333333333335,-5.918333333333335,0.3,0,29.582397035531386,37.73,-126.84,-33.374,-80.935,293.31,21.8407697058527,30.83445690111887
month,11,spline,30,30,18,12,0,-194.79,-6.492999999999999,-6.492999999999999,0.3,0,29.457425051922907,35.03000000000001,-126.84,-34.858999999999995,-82.285,277.2,22.745475714954086,32.083498468553444
month,11,always_load,30,30,30,0,0,-167.25000000000003,-5.575000000000001,-5.575000000000001,0.23333333333333334,0,29.65131243824368,126.84,-37.73,-33.374,-36.38,230.02999999999997,,
month,11,always_supply,30,30,0,30,0,167.25000000000003,5.575000000000001,5.575000000000001,0.7666666666666667,0,29.65131243824368,37.73,-126.84,-31.574999999999992,-80.03999999999999,138.49,,
month,11,flat,30,0,0,0,30,0.0,0.0,,,0,0.0,0.0,-0.0,0.0,0.0,0.0,,
month,11,training_mean,30,30,30,0,0,-167.25000000000003,-5.575000000000001,-5.575000000000001,0.23333333333333334,0,29.65131243824368,126.84,-37.73,-33.374,-36.38,230.02999999999997,,
month,12,calendar,31,31,18,13,0,176.98000000000002,5.709032258064517,5.709032258064517,0.41935483870967744,0,33.56918401896186,88.97000000000001,-38.25999999999999,-34.345,-36.614999999999995,78.30000000000004,27.35368609056184,33.46474591798848
month,12,linear,31,31,14,17,0,175.16000000000003,5.650322580645162,5.650322580645162,0.4838709677419355,0,33.579446837201964,88.97000000000001,-52.209999999999994,-36.614999999999995,-45.23499999999999,117.55000000000001,26.42360031530112,32.559873621537776
month,12,spline,31,31,22,9,0,-207.82000000000005,-6.7038709677419375,-6.7038709677419375,0.41935483870967744,0,33.378580724512474,52.92,-88.97000000000001,-59.57,-76.73500000000001,356.65999999999997,30.526849734022985,38.08216033666227
month,12,always_load,31,31,31,0,0,-567.7199999999999,-18.31354838709677,-18.31354838709677,0.1935483870967742,0,28.5307555161545,52.209999999999994,-88.97000000000001,-59.57,-76.73500000000001,567.7200000000001,,
month,12,always_supply,31,31,0,31,0,567.7199999999999,18.31354838709677,18.31354838709677,0.8064516129032258,0,28.5307555161545,88.97000000000001,-52.209999999999994,-22.415000000000006,-40.275,85.69,,
month,12,flat,31,0,0,0,31,0.0,0.0,,,0,0.0,0.0,-0.0,-0.0,0.0,0.0,,
month,12,training_mean,31,31,31,0,0,-567.7199999999999,-18.31354838709677,-18.31354838709677,0.1935483870967742,0,28.5307555161545,52.209999999999994,-88.97000000000001,-59.57,-76.73500000000001,567.7200000000001,,
season,DJF,calendar,90,90,28,62,0,-429.15000000000003,-4.7683333333333335,-4.7683333333333335,0.45555555555555555,0,50.457483253647666,110.41000000000004,-147.75,-113.16,-124.378,661.6500000000001,37.17525119392912,51.242929730032166
season,DJF,linear,90,90,23,67,0,-502.71,-5.585666666666667,-5.585666666666667,0.4666666666666667,0,50.37261022407432,110.41000000000004,-147.75,-113.16,-124.378,733.3900000000001,37.022740305585025,51.39625442201149
season,DJF,spline,90,90,54,36,0,367.63,4.084777777777778,4.084777777777778,0.5222222222222223,0,50.51808789934792,147.75,-113.34,-96.32099999999998,-108.37400000000002,497.7800000000001,37.93790895492662,51.43794637854585
season,DJF,always_load,90,90,90,0,0,-12.909999999999954,-0.14344444444444393,-0.14344444444444393,0.3888888888888889,0,50.68460598158099,147.75,-110.41000000000004,-61.984500000000004,-92.876,623.24,,
season,DJF,always_supply,90,90,0,90,0,12.909999999999954,0.14344444444444393,0.14344444444444393,0.6111111111111112,0,50.68460598158099,110.41000000000004,-147.75,-113.16,-124.378,610.3300000000002,,
season,DJF,flat,90,0,0,0,90,0.0,0.0,,,0,0.0,0.0,-0.0,0.0,0.0,0.0,,
season,DJF,training_mean,90,90,90,0,0,-12.909999999999954,-0.14344444444444393,-0.14344444444444393,0.3888888888888889,0,50.68460598158099,147.75,-110.41000000000004,-61.984500000000004,-92.876,623.24,,
season,JJA,calendar,91,91,86,5,0,1784.5100000000004,19.610000000000007,19.610000000000007,0.3516483516483517,0,215.26735096412347,1768.5300000000002,-233.7,-121.515,-188.158,943.2000000000007,75.4952542533483,213.26760796350362
season,JJA,linear,91,91,85,6,0,1851.1100000000004,20.341868131868136,20.341868131868136,0.3626373626373626,0,215.19867101981262,1768.5300000000002,-233.7,-121.515,-188.158,943.2000000000007,75.11204972895722,212.6597512675231
season,JJA,spline,91,91,62,29,0,2885.8300000000004,31.712417582417586,31.712417582417586,0.5274725274725275,0,213.80366149728567,1768.5300000000002,-233.7,-109.65,-165.166,619.8800000000003,74.00187771008527,206.99569347755545
season,JJA,always_load,91,91,91,0,0,1657.9700000000003,18.219450549450553,18.219450549450553,0.2967032967032967,0,215.39085542005643,1768.5300000000002,-233.7,-121.515,-188.158,943.2000000000007,,
season,JJA,always_supply,91,91,0,91,0,-1657.9700000000003,-18.219450549450553,-18.219450549450553,0.7032967032967034,0,215.39085542005643,233.7,-1768.5300000000002,-218.18,-685.788,2684.5600000000004,,
season,JJA,flat,91,0,0,0,91,0.0,0.0,,,0,0.0,0.0,-0.0,-0.0,0.0,0.0,,
season,JJA,training_mean,91,91,91,0,0,1657.9700000000003,18.219450549450553,18.219450549450553,0.2967032967032967,0,215.39085542005643,1768.5300000000002,-233.7,-121.515,-188.158,943.2000000000007,,
season,MAM,calendar,92,92,35,57,0,-113.99999999999996,-1.2391304347826082,-1.2391304347826082,0.5,0,14.71265170235019,31.580000000000005,-46.44999999999999,-24.794,-37.104,175.1,11.892556935822382,15.393072364414252
season,MAM,linear,92,92,41,51,0,36.12000000000005,0.39260869565217443,0.39260869565217443,0.5434782608695652,0,14.760033940039989,31.580000000000005,-46.44999999999999,-23.019000000000002,-36.32,175.1,11.803338157096178,15.20516361405971
season,MAM,spline,92,92,30,62,0,-27.86000000000001,-0.30282608695652186,-0.30282608695652186,0.5543478260869565,0,14.762172129852704,31.580000000000005,-46.44999999999999,-24.794,-37.104,153.5,12.01420145337821,16.37257808150802
season,MAM,always_load,92,92,92,0,0,-505.44000000000005,-5.493913043478261,-5.493913043478261,0.31521739130434784,0,13.693052056781138,43.86,-46.44999999999999,-24.783,-34.648,505.44,,
season,MAM,always_supply,92,92,0,92,0,505.44000000000005,5.493913043478261,5.493913043478261,0.6847826086956522,0,13.693052056781138,46.44999999999999,-43.86,-14.344500000000002,-25.082,90.24,,
season,MAM,flat,92,0,0,0,92,0.0,0.0,,,0,0.0,0.0,-0.0,-0.0,0.0,0.0,,
season,MAM,training_mean,92,92,92,0,0,-505.44000000000005,-5.493913043478261,-5.493913043478261,0.31521739130434784,0,13.693052056781138,43.86,-46.44999999999999,-24.783,-34.648,505.44,,
season,SON,calendar,89,89,42,47,0,-919.3800000000001,-10.330112359550563,-10.330112359550563,0.4044943820224719,0,47.767843393722856,121.76,-302.82,-69.218,-157.176,991.5300000000001,25.960245342615185,49.71724472143555
season,SON,linear,89,89,46,43,0,-363.56000000000006,-4.08494382022472,-4.08494382022472,0.4044943820224719,0,48.71154198963704,302.82,-212.16000000000005,-60.31400000000001,-110.13400000000001,670.4000000000001,25.820540377999965,49.550474106063604
season,SON,spline,89,89,38,51,0,-701.48,-7.881797752808989,-7.881797752808989,0.42696629213483145,0,48.237558347906905,121.76,-302.82,-44.046,-151.084,839.7899999999997,27.337418530258386,50.2581427094188
season,SON,always_load,89,89,89,0,0,245.30000000000004,2.7561797752808994,2.7561797752808994,0.3258426966292135,0,48.805817893362274,302.82,-73.77,-36.614000000000004,-47.257999999999996,348.7500000000002,,
season,SON,always_supply,89,89,0,89,0,-245.30000000000004,-2.7561797752808994,-2.7561797752808994,0.6741573033707865,0,48.805817893362274,73.77,-302.82,-69.218,-166.774,631.8600000000001,,
season,SON,flat,89,0,0,0,89,0.0,0.0,,,0,0.0,0.0,-0.0,0.0,0.0,0.0,,
season,SON,training_mean,89,89,89,0,0,245.30000000000004,2.7561797752808994,2.7561797752808994,0.3258426966292135,0,48.805817893362274,302.82,-73.77,-36.614000000000004,-47.257999999999996,348.7500000000002,,
```


## Gross trading validation selection

```csv
strategy,days,active_trades,virtual_load_days,virtual_supply_days,flat_days,total_gross_dollars,mean_daily_gross_dollars,mean_active_trade_dollars,win_rate_active,zero_payoff_active_trades,daily_std_dollars,best_day_dollars,worst_day_dollars,fifth_percentile_dollars,worst_five_percent_mean_dollars,max_drawdown_dollars,spread_mae_mwh,spread_rmse_mwh
calendar,364,364,201,163,0,1728.4199999999996,4.748406593406592,4.748406593406592,0.49725274725274726,0,63.23519753128357,828.7299999999999,-132.61,-41.885499999999986,-71.12631578947368,630.5900000000015,22.040904121381274,63.07541412522596
linear,364,364,202,162,0,1647.2199999999998,4.52532967032967,4.52532967032967,0.489010989010989,0,63.25159810175118,828.7299999999999,-132.61,-41.885499999999986,-70.69,635.6100000000006,22.003707329358978,63.010168901096435
spline,364,364,154,210,0,323.41999999999996,0.8885164835164834,0.8885164835164834,0.5274725274725275,0,63.40747629092132,828.7299999999999,-161.1,-57.236499999999985,-88.97263157894736,738.9799999999999,25.26727122605972,64.73359031358221
always_load,364,364,364,0,0,540.38,1.4845604395604395,1.4845604395604395,0.35714285714285715,0,63.39629086033012,828.7299999999999,-130.73000000000002,-44.910999999999994,-66.07105263157894,952.76,,
always_supply,364,364,0,364,0,-540.38,-1.4845604395604395,-1.4845604395604395,0.6428571428571429,0,63.39629086033012,130.73000000000002,-828.7299999999999,-49.039999999999985,-167.3736842105263,1799.44,,
flat,364,0,0,0,364,0.0,0.0,,,0,0.0,0.0,-0.0,0.0,0.0,0.0,,
training_mean,364,364,364,0,0,540.38,1.4845604395604395,1.4845604395604395,0.35714285714285715,0,63.39629086033012,828.7299999999999,-130.73000000000002,-44.910999999999994,-66.07105263157894,952.76,,
```


## Gross trading uncertainty

```csv
selected_weather,benchmark,block_days,mean_incremental_daily_dollars,lower_95_dollars,upper_95_dollars,paired_days
linear,flat,7,2.8203314917127087,-8.099593663911845,18.291685273830975,362
linear,flat,14,2.8203314917127087,-8.10402982305936,19.300474422781306,362
linear,flat,28,2.8203314917127087,-6.883781556778229,18.011651924083164,362
linear,calendar,7,1.9308839779005529,-0.724517693905817,6.03939554317548,362
linear,calendar,14,1.9308839779005529,-0.6303658553152945,5.7909298080728115,362
linear,calendar,28,1.9308839779005529,-0.5132085635359115,5.7667106943335975,362
linear,always_load,7,-1.0054143646408835,-8.073449283137757,5.862510896680485,362
linear,always_load,14,-1.0054143646408835,-8.088486426592798,5.548059682699572,362
linear,always_load,28,-1.0054143646408835,-7.6003330702446705,5.4550570992166625,362
linear,always_supply,7,6.646077348066301,-12.926212042124543,36.626184714177796,362
linear,always_supply,14,6.646077348066301,-13.207842032967035,39.09835781132827,362
linear,always_supply,28,6.646077348066301,-11.448389807162531,36.16894874301673,362
linear,training_mean,7,-1.0054143646408835,-8.073449283137757,5.862510896680485,362
linear,training_mean,14,-1.0054143646408835,-8.088486426592798,5.548059682699572,362
linear,training_mean,28,-1.0054143646408835,-7.6003330702446705,5.4550570992166625,362
```
