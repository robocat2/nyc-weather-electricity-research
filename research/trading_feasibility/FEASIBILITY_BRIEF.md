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
