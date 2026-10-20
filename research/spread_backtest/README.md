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
