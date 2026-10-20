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
