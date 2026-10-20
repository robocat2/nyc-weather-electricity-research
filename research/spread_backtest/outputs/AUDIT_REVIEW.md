# NYC research audit — October 16, 2026

**Share with caveats. Analytical checks complete within the scope below; rendered browser-layout review partial.** No numerical results, model choices, exclusions or frozen methods were changed. The combined introduction received minor wording corrections to consistently describe three stages.

The review focused on the new gross spread experiment, independently reconciled the two prior headline error reductions, and checked the combined document's claims and structure. It did not repeat the entire original hourly-demand ingestion audit. Scoped counts below describe components, not an accuracy percentage; zero observed defects does not mean every possible aspect was verified.

## Report usefulness and presentation

| Category | Observed defects | Assessment |
|---|---|---|
| Usefulness/completeness | 0 / 3 | Demand, finalized DA-price prediction and gross spread trading stages are included, with distinct questions and outcomes. |
| Analytical clarity | 0 / 3 | Error reductions are distinguished from trading returns; model selection and prior 2025 exposure are disclosed. Wording now consistently refers to three stages. |
| Visual/interaction consistency | 0 / 12 | Twelve embedded charts and all anchors/local links verified structurally. Four spread-chart PNGs visually inspected in the preceding build; full browser layout and eight earlier chart renderings were not rechecked in this audit. No interactive model controls exist. |

## Analytical correctness and robustness

| Category | Observed defects | Assessment |
|---|---|---|
| Source authority/confidence | 0 / 3 | Official NYISO DA/RT archives, NOAA forecast records, and retained NYISO market/settlement documents inspected. Retained documents do not establish every historical rule, publication or invoice vintage. |
| Value accuracy | 0 / 121 | Independently recomputed 119 spread strategy/period totals and drawdowns, plus the two original headline MAE reductions. Six independent OLS fits reproduced validation/final model payoffs. |
| Within-chart agreement | 0 / 4 | Spread chart calculations and labels agree with the verified strategy, monthly and uncertainty outputs. |
| Complete source details | 0 / 3 | Outcome archives, forecast receipts and market-payoff evidence remain inspectable. All eligible forecast hashes/header times checked; embedded GRIB metadata and nearest-point values independently checked on 12 stratified dates, not all 1,809. |
| Cross-artifact consistency | 0 / 3 | Demand, price and spread headline results agree with the combined walkthrough; historical no-trading statements are identified as preceding Part III. |
| Data-quality controls | 0 / 3 | Raw DA/RT labels checked across all 1,826 dates; all 1,809 eligible forecast timing records checked; chronological train/validation/evaluation and identical benchmark dates verified. |
| Conclusion support | 0 / 3 | 39.2% demand-error reduction and 16.6% DA-price-error reduction confirmed. Gross signal's lack of convincing incremental alpha is supported by baseline comparisons, concentration and 15 independently recomputed intervals. |

## Prioritized problems and proposed fixes

1. **Trading interpretation:** The selected linear weather rule earns $1,020.96 gross versus $1,384.92 always virtual load. The best day contributes $1,768.53 and the remaining days lose $747.57. Every reported paired confidence interval crosses zero. **Status:** no mathematical repair needed; retain the conclusion that reliable gross alpha was not established. Do not promote the unselected spline after observing 2025.
2. **Historical/execution scope:** Clearing one MWh is assumed. Fees, uplift, financing, partial fills and executable bids are not modeled. 2025 had been inspected in preceding studies; historical corrected labels are not exact real-time training or immutable settlement vintages. **Status:** keep these caveats beside the findings; they prevent live-profitability or wholly-unseen-test claims.
3. **Verification limits:** Full browser layout was unavailable for inspection. Forecast decoder checks were sampled on 12 dates, although hashes and header timing were checked for every eligible forecast. Original demand/price fitting pipelines were not independently reimplemented in full during this audit. **Status:** no blanket certification of every aspect; these limits are explicit.

A provenance wording ambiguity was resolved without changing frozen metadata: feasibility inspected eight price samples in total, of which two were in 2025. The README's two-2025-samples statement is correct; the price configuration's unqualified “eight source-feasibility price samples” describes the total sample set.

## Reproducible evidence

From the Backtest Factory directory:

```sh
NYC_Weather_Electricity/price_research/.venv/bin/python NYC_Weather_Electricity/spread_backtest/audit_independent.py
NYC_Weather_Electricity/price_research/.venv/bin/python NYC_Weather_Electricity/spread_backtest/audit_supplemental.py
NYC_Weather_Electricity/price_research/.venv/bin/python -m unittest discover -s NYC_Weather_Electricity/spread_backtest/tests -v
```

Machine-readable results: `independent_audit.json`, `supplemental_audit.json`, `validation_status.json`. Nine tests passed. Independent normal-equation refits differed from saved predictions by at most 8.4e-12 $/MWh, with identical positions. All 15 uncertainty intervals reproduced, including 7/14/28-day blocks and all five paired benchmarks. Core spread and price code/specification hashes remain unchanged.
