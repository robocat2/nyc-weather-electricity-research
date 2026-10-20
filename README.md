# Weather forecasts, electricity prices & the search for a trading edge

**A completed Python research case study · NYC / NYISO Zone J · 2021–2025**

Can weather information improve electricity-market predictions—and does better prediction translate into trading value?

I built a pipeline from observed-weather demand modeling to archived-forecast price prediction, then tested a fixed day-ahead/real-time spread signal. Weather improved demand and price estimates against calendar baselines. The trading experiments did **not establish reliable incremental alpha**.

## Start here

- **Visual case study:** [Read the live research overview](https://nyc-weather-electricity-research.vercel.app/).
- **Full research:** [combined executed walkthrough](research/outputs/NYC_Combined_Research_Walkthrough.html) · [portable text](research/outputs/NYC_Combined_Research_Context.md).
- **Code:** [demand](research/src) · [DA prices](research/price_research/src) · [spread backtest](research/spread_backtest/src) · [follow-ups](research/followup_hypotheses/src).

This repository contains the Python research, notebooks, tests and source for the visual overview. The website explains the findings; the research folders provide the supporting code and evidence.

[Website preview](docs/preview/desktop.png) · [Verification record](docs/VERIFICATION.md)

## The research in three phases

```mermaid
flowchart LR
  A[Understand electricity demand] --> B[Predict day-ahead prices]
  B --> C[Test RT-minus-DA trading value]
  C --> D[Bounded exploratory follow-ups]
```

| Phase | Comparison | Evaluation result |
|---|---|---|
| Retrospective demand modeling | Calendar versus calendar + observed-temperature spline | MAE **436.38 → 265.13 MW**, a **39.2% reduction**, on 8,654 matched 2025 hours. |
| Day-ahead price prediction | Calendar versus calendar + genuine archived forecast-temperature spline | MAE **$35.16 → $29.33/MWh**, a **16.6% reduction**, on 362 matched 2025 dates. |
| Gross spread-signal backtest | Validation-selected linear-weather rule versus simple benchmarks | **+$1,020.96**, versus **+$1,384.92 always virtual load**; reliable incremental alpha not established. |

The demand finding motivated price research; fitted demand estimates were **not** price-model inputs. Prediction-error reductions are **not investment returns**. Observed-weather demand modeling is not a demonstrated operational demand forecast.

## What was built

- Public-data acquisition and caching, source receipts and hashes, UTC/DST alignment and coverage gates.
- Operational HRRR GRIB forecast decoding, matching issue/valid times, and availability evidence before a fixed decision cutoff. Seventeen current-forecast dates excluded; no realized future temperature substitution.
- Modular NumPy/pandas OLS regressions with calendar controls, linear temperature and piecewise-linear splines.
- Chronological model fitting/selection, fit-only preprocessing, matched benchmarks, daily signals, drawdowns, concentration and block-bootstrap uncertainty.
- A responsive, dependency-free visual case study with a research map, evidence links, expandable methods and an interactive cumulative-payoff comparison.

## Why the trading result matters

At 04:00 ET on D−1, predict NYC's D18:00–19:00 **RT minus DA** spread. Positive means virtual load, negative virtual supply, zero flat. Assume one MWh clears per active date; gross payoff = direction × (RT − DA).

The selected rule's best day earned **$1,768.53**, more than its full-year gross total. The remaining 361 dates lost **$747.57** combined. Its seven-day 95% interval for mean daily gross payoff was **−$8.10 to +$18.29**. The increment versus calendar also crossed zero; 14/28-day checks did too. The unselected spline is retained transparently and was not promoted after inspecting 2025.

Two completed exploratory follow-ups asked whether forecast temperature trajectories or six-hour same-target forecast revisions helped. The trajectory rule's increment versus matched linear remained uncertain; revisions slightly worsened gross payoff. Their cohorts differ, so raw totals should not be ranked across families. [Full follow-up findings](research/followup_hypotheses/outputs/FOLLOWUP_FINDINGS.md).

## Evaluation and important limits

Development fit: **2021–2023**. Validation: **2024**. Final refit: **2021–2024**. Evaluation: **2025**. Later stages had prior exposure to the evaluation year; the follow-ups are explicitly exploratory, not new blind tests.

One zone, one weather location and one final evaluation year limit generalization. Baselines do not include strong price-history or commercial forecasts. Corrected/latest archive labels are not verified original auction or invoice vintages. Timestamp evidence is not a complete historical dissemination ledger. Trading assumes clearing and excludes fees, uplift, slippage, financing and market access. No production deployment or live trading is claimed.

## Run and inspect

### Website

No frontend packages or external services are required. Node.js and Python 3:

```sh
npm run check
npm run build        # creates dist/ from site/
npm run dev          # local source preview on 127.0.0.1:4173
```

### Research and portable tests

Python 3.12:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-review.txt
python -m unittest discover -s research/price_research/tests -v
python -m unittest discover -s research/spread_backtest/tests -v
python -m unittest discover -s tests -v
```

The one retained GRIB fixture supports the original price decoder tests. Bulk raw downloads are omitted; this is a curated review repository, not a complete offline raw-data archive. Exact raw-source audits and the full demand/follow-up suites require their original caches. Reacquiring current archives can change historical source hashes. See [reproduction scope](docs/REPRODUCIBILITY.md).

The daily price model can be refitted from bundled derived inputs with `cd research/price_research && python src/run.py`. Run this in a scratch copy: it writes outputs. The spread runner also verifies omitted raw sources and needs those caches; its saved-output tests run without them.

## Evidence and sources

- [Demand methods and sources](research/DEMAND_STUDY.md) · [price methods](research/price_research/EXPERIMENT.md) · [source/timing definitions](research/price_research/SOURCES.md).
- [Virtual-trade feasibility and NYISO settlement evidence](research/trading_feasibility/FEASIBILITY_BRIEF.md).
- [Independent audit](research/spread_backtest/outputs/AUDIT_REVIEW.md) · [follow-up audit results](research/followup_hypotheses/outputs/independent_audit.json).
- [Original-file snapshot manifest](docs/research_snapshot_manifest.json) · [website-data provenance](site/evidence/provenance.json).

Analytical code, specifications and data are preserved from the audited original. Presentation exports omit internal explanation instructions; the snapshot manifest records those text-only edits. The original completed portfolio ZIP remains untouched. Follow-ups are included as an explicitly separate extension. Raw-source acquisition URLs remain in the original code and documentation.
