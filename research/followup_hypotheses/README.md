# NYC exploratory weather follow-ups

Two fixed follow-up experiments: **forecast temperature trajectory** and **six-hour forecast revisions**. The completed original portfolio release remains intact. No stock-price reaction is tested. These are retrospective, exploratory electricity-spread tests; 2024/2025 were already inspected in preceding research.

The trajectory experiment uses prior forecasts for successive evening delivery dates, not realized temperature lags. The revision experiment compares 00 UTC and 06 UTC forecasts for the same delivery hour/grid. Both use only retained pre-cutoff information and the original 04:00 ET D−1 decision rule. No future weather substitution, price-history inputs, fees or executable fills. One MWh is assumed cleared per signal.

Read [findings](outputs/FOLLOWUP_FINDINGS.md), [self-contained walkthrough](outputs/NYC_Weather_Followups.html), and [frozen experiment](EXPERIMENT.md). The findings include all variants, matched baselines, exclusions, concentration and uncertainty; gross totals across different family cohorts are not comparable rankings.

## Reproduce
Use Python 3.12 with the parent `price_research/.venv` or its pinned requirements plus beautifulsoup4/mistune from `../portfolio/requirements.txt`. From this folder:

```sh
../price_research/.venv/bin/python src/acquire_revisions.py          # six source samples, network
../price_research/.venv/bin/python src/acquire_revisions.py --full   # all older-cycle temperature fields, network
../price_research/.venv/bin/python src/run_followups.py --family trajectory
../price_research/.venv/bin/python src/run_followups.py --family revision
../price_research/.venv/bin/python -m unittest discover -s tests -v
../price_research/.venv/bin/python build_report.py
```

Original verified forecast/price files and raw RT source archives in adjacent folders are needed for source-hash checks. Cached bytes are reused. Only 2m temperature fields are downloaded using bounded HTTP ranges; full weather grids are not downloaded. NOAA source URL, HEAD/range receipts, ETags and hashes are retained in `raw/`; unavailable/multipart/late records are excluded and recorded.

The original freeze, selection records, source snapshots and release ZIP are not changed. This folder is deliberately outside that release. The two fixed follow-ups stop after reporting and auditing their results; there is no automated further model search. A positive retrospective result would still need a new prospective evaluation.
