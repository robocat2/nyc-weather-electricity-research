# Price-prediction feasibility task (no model fitting authorized in this stage)

Scope fixed 2026-10-16. Stay with NYC. Verify inputs and historical timing, then report before fitting. Existing demand study is unchanged.

## One prediction task
At **04:00 America/New_York on the calendar day before delivery**, predict the **NYISO NYC / Zone J (PTID 61761) day-ahead zonal LBMP for delivery 18:00–19:00 local time the next day**, in **$/MWh**. This is an auction-price target, not an executable quote observed at prediction time. Standard elapsed horizon is 38 hours; a daylight-saving transition can make it 37 or 39 hours. Record both cutoff and delivery timestamp in UTC.

The provisional 08:00 cutoff was rejected before fitting because NYISO documents a 05:00 day-ahead bidding deadline. A 04:00 cutoff leaves an hour before that deadline, but does not establish executable orders, market access, or profitability. Verify the historical applicability of the bidding schedule before an actual trading backtest.

## Candidate inputs and timing requirements
- Fixed HRRR operational 06 UTC cycle on the cutoff date, 2m temperature forecast valid at target hour. Required lead is 40 hours in EDT delivery hours or 41 in EST delivery hours. Model initialization is not publication time. Inspect actual forecast GRIB reference time, forecast lead, temperature identity, and historical object timestamp. A forecast must be available before cutoff. Never substitute analysis/f00 or realized temperature. Current S3 Last-Modified may show a later archive copy rather than original dissemination; do not infer unavailable-in-2021 from a 2023 copy or infer available from the cycle name alone.
- Price-history/calendar baseline: prior delivery-date day-ahead prices already published before cutoff, including prior day's 18:00 price and seven-day lag. Those delivery hours may still be future at cutoff, but their day-ahead auction prices were normally published earlier; actual publication/version evidence must verify that. Require the price version known at cutoff, not a later correction silently inserted into a lag.
- Do not use realized future load or weather. No observed load inputs or demand-model inputs are necessary for this minimum extension. If later included, verify their publication/revision timing and generate demand estimates from fitting data strictly preceding the prediction period. Do not reuse the final demand fit to generate earlier historical inputs.

## Bounded evidence sample
Eight delivery dates selected for winter, summer, chronological span and DST: 2021-01-15, 2021-07-15, 2023-01-15, 2023-07-15, 2024-03-10, 2024-11-03, 2025-01-15, 2025-07-15. Check forecast-object metadata, forecast index and actual 2m-temperature GRIB message; parse NYC archived price samples, exact columns and timestamp availability. Review official scheduling and correction documentation plus operational announcements (the stated authority replacing obsolete correction logs). These are sample probes, not five-year completeness verification. No provider hopping or model fitting.

## Gate
Pass requires a credible point-in-time path for both historical forecast input and price-history input, not just numerical files. If original publication times/vintages cannot be established within this focused check, **STOP**, report the gap and preserve the existing demand study. A fresh forward data collection could remedy a gap; it is not part of this task. Calendar-only retrospective prediction is a different, weaker baseline and must not silently replace the requested price-history comparison.

If this gate were to pass, freeze feature/model/metric choices before scoring: training 2021–2023, chronological validation 2024, evaluation 2025. Disclose that 2025 demand relationships have already been examined; it is not wholly unseen. Maintain a separate price-research specification, fit preprocessing only on fitting rows, and evaluate baseline versus baseline plus forecast weather. Never infer profitability from price MAE or directional accuracy; order timing, executable products and costs require separate testing.
