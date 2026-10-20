# Weather Forecasts, Electricity Prices & Trading-Signal Evaluation

**Completed Python portfolio project · NYC / NYISO Zone J · 2021–2025**

Investigated weather information from economic modeling through market prediction and a hypothetical gross trading test. The result is a reproducible research pipeline with both useful predictive findings and an unsuccessful trading hypothesis.

| Experiment | Evaluation finding | Interpretation |
|---|---|---|
| Observed-weather demand regression | MAE 436.38 → 265.13 MW (**39.2% reduction**) | Retrospective demand modeling, not operational forecasting. |
| Archived-forecast DA-price regression | MAE $35.16 → $29.33/MWh (**16.6% reduction**) | Improvement against calendar-only; not a trading return. |
| Forecast-weather RT−DA spread signal | **+$1,020.96 gross**, versus **+$1,384.92 always virtual load** | Reliable incremental alpha not established. |

Development fitting: 2021–2023. Validation: 2024. Final refit: 2021–2024. Evaluation: 2025. The later stages disclose prior examination of 2025; chronological separation does not make it a wholly unseen test. Demand estimates are not price-model inputs.

## Start here
- [Complete walkthrough: all three studies and twelve figures](outputs/NYC_Combined_Research_Walkthrough.html)
- [Portable text context](outputs/NYC_Combined_Research_Context.md)
- [Résumé bullets and interview explanation](portfolio/RESUME_AND_INTERVIEW.md)
- [Closeout and release scope](portfolio/PROJECT_CLOSEOUT.md)
- [Independent audit and coverage limits](spread_backtest/outputs/AUDIT_REVIEW.md)

## Code and evidence
- Demand: [executed notebook](NYC_Weather_Electricity.ipynb), [stage documentation](DEMAND_STUDY.md), `src/`, `tests/`.
- DA-price research: [documentation](price_research/README.md), [executed notebook](price_research/NYC_Finalized_Price_Research.ipynb), `price_research/src/`.
- Spread backtest: [documentation](spread_backtest/README.md), [executed notebook](spread_backtest/NYC_Gross_Spread_Backtest.ipynb), `spread_backtest/src/`.
- Feasibility decisions: [price-input timing](price_feasibility/FEASIBILITY_BRIEF.md), [virtual-trade payoff and data](trading_feasibility/FEASIBILITY_BRIEF.md).

Python, NumPy, pandas, matplotlib and ecCodes support acquisition, UTC/DST alignment, forecast decoding, OLS/splines, chronological evaluation, block bootstrapping and signal/risk diagnostics. Stage specifications and code hashes preserve the audited methods.

## Reproduce from derived data
Use Python 3.12 and install `portfolio/requirements.txt` in an isolated environment. From project root, run each stage in its own directory:

```sh
(cd price_research && python src/run.py)
python build_combined_walkthrough.py
```

These commands recompute the daily price experiment from bundled derived inputs and rebuild the combined document from saved HTML exports. The spread runner (`cd spread_backtest && python src/run.py`) additionally checks raw-source hashes, so its full run requires the original raw cache or reacquisition; without that cache, inspect saved outputs and run the spread tests instead:

```sh
python -m unittest discover -s spread_backtest/tests -v
```

For original raw-data acquisition, hourly-demand replay, notebook execution and stage-specific checks, follow each stage's documentation. The compact review ZIP omits bulk raw downloads and environments; the full original raw cache remains in the local project. Exact raw-snapshot verification requires that cache. No API credentials are needed for the documented public sources.

## What this project demonstrates
Careful data preparation, availability-aware features, baseline comparisons, separate model selection/evaluation, and honest interpretation when prediction improvements do not translate into convincing trading evidence.

The gross test assumes one MWh clears per signal. It excludes fees, uplift, slippage and financing. Its best day exceeds its full-year profit, and all paired bootstrap intervals cross zero. Corrected labels and archive timing do not reconstruct every historical training or settlement vintage. Full browser layout was not verified; chart PNGs were inspected separately.

**Release status: complete.** No follow-up model search is included or pending. This is research evidence, not a live strategy or a claim of trading profitability.
