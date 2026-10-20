# Frozen exploratory weather follow-ups

Frozen after six older-cycle feasibility samples, before new-model fitting or payoff scores. Original release remains intact.

## Target and trading rule
NYISO NYC PTID61761, D18:00–19:00 local RT integrated minus DA price. Decide 04:00 ET D−1; +1 virtual load if predicted spread>0, −1 supply if<0, otherwise0. Assume one cleared MWh per active date. No fees, uplift, slippage, financing, access or fill testing. Corrected archive outcomes; no price/load inputs. This is not equity trading.

## Fixed feature comparisons
All regressions include the original 14 calendar columns, fit-only centering/scaling, OLS. Original linear baseline includes forecast temperature T(D) from D−1 06UTC (40/41h).

1. **Trajectory family:** baseline plus T(D)−T(D−1) (trajectory1); alternative adds both T(D)−T(D−1) and T(D)−T(D−2) (trajectory2). T(D−k) is the retained forecast for that calendar delivery date from its own D−k−1 06UTC cycle. All valid at 18:00 local and must have met their original cutoffs. This is forecast-level trajectory, not actual weather lags. D−1 evening is still future at current cutoff; no claim that it has occurred. Different issue times can mix forecast errors with weather changes. No row shift across missing dates; use exact date joins.
2. **Revision family:** baseline plus T06(D)−T00(D), same target hour/grid, six-hour issue-time change. The old 00UTC cycle D−1 has lead46/47h; must pass matching HEAD/range ETag, GRIB embedded operational forecast metadata, hash and original cutoff minus5min. No choice of revision window, threshold or interaction.

No combined trajectory/revision model, nonlinear search, filtering by weather regime or alternate hour is permitted. For trajectory, select trajectory1 or trajectory2 by maximum 2024 mean gross payoff (ties trajectory1). Revision has a single fixed variant. Both are evaluated and reported; no joint winning-hypothesis promotion based on 2025.

## Samples and chronology
For each family, retain a family-specific cohort requiring all features for all family variants, so every internal model/benchmark uses identical dates. Trajectory requires D−1 and D−2 original eligible records for both variants; first two 2021 dates may lack histories. Revision requires older and current forecast, same grid, and matching target. Minimum coverage >=90% each year and >=80% each month. Stop a family before fitting if its data gate fails; do not relax gates or impute. Exclusions retained, dates sorted.

Development fit2021–2023, validation2024. Record selection and source/spec/code hashes before final evaluation. Refit2021–2024, evaluate2025. All preprocessing fit on the corresponding training rows only. 2025 already examined extensively in prior studies and the hypotheses arose after those findings: explicitly exploratory, not independent/wholly unseen confirmation. Validation2024 was also examined in preceding studies. No new holdout claim.

## Baselines and reporting
Within each family refit calendar and original linear models on that same cohort. Also compare fixed always-load, always-supply, flat and training-mean direction (fit2021–2024). Show the trajectory alternatives transparently, but keep validation-selected variant primary. Report validation/final daily predictions, positions, gross totals/means, max drawdown including initial zero, win rate, month stability, top-day concentration and forecast MAE. Comparing gross totals across different family cohorts is not a fair ranking.

Paired circular daily block bootstrap, 5000 replicates, seed61761, full 2025 date grid, missing dates0total/0count, 7days primary14/28 sensitivity. For each primary variant compare against original linear, calendar, always-load and flat. All intervals descriptive and unadjusted for the two related hypotheses and past researcher exposure; no confirmatory significance or proven alpha claims. A promising outcome requires improvement over linear and constant direction, not merely positive gross dollars. Costs remain excluded as requested.

## Stop
Complete these fixed comparisons once, audit arithmetic/timing and publish a separate follow-up walkthrough. Do not tune using final-year results, alter the completed release, or launch further hypotheses automatically. A fresh prospective evaluation would be required before confidence in a discovered signal.
