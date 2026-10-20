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
