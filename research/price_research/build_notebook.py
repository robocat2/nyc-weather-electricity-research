"""Build a result-backed notebook after the frozen price experiment has run."""
from pathlib import Path
import json
import pandas as pd
import nbformat as nb

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'outputs'
summary = json.loads((OUT/'summary.json').read_text())
configuration = json.loads((OUT/'selected_configuration.json').read_text())
gate = json.loads((OUT/'data_gate.json').read_text())
selected = summary['selected_weather_model']
scores = pd.read_csv(OUT/'test_metrics.csv')
overall = scores.loc[scores.group_type.eq('overall')].set_index('model')
intervals = pd.read_csv(OUT/'uncertainty.csv')
primary = intervals.loc[intervals.weather_model.eq(selected) & intervals.block_days.eq(7)].iloc[0]
verb = 'reduced' if summary['selected_improvement_pct']>0 else 'increased'
uncertainty_text = ('The primary paired block interval remains above zero.' if primary.lower_95_mwh>0 else
                    'The primary paired block interval crosses zero; a reliably positive gain is not established.' if primary.upper_95_mwh>=0 else
                    'The primary paired block interval is below zero, indicating worse error on this evaluation year.')
n = nb.v4.new_notebook()
cells = []
def md(text): cells.append(nb.v4.new_markdown_cell(text))
def code(text): cells.append(nb.v4.new_code_cell(text))

md(f'''# Weather forecasts and finalized NYC electricity prices
## tl;dr
**The validation-selected {selected} temperature model {verb} 2025 MAE by {abs(summary['selected_improvement_pct']):.1f}% versus calendar alone**: ${summary['baseline_mae_mwh']:.2f}/MWh to ${summary['selected_mae_mwh']:.2f}/MWh across {summary['matched_2025_days']} matched target days. It improved MAE in {summary['months_with_selected_improvement']} of 12 months.

The seven-day paired block-bootstrap 95% interval for calendar-minus-selected-weather MAE is **${primary.lower_95_mwh:.2f} to ${primary.upper_95_mwh:.2f}/MWh**. {uncertainty_text}

This is retrospective **prediction research for finalized day-ahead prices using dated operational forecasts**. A price-history baseline and trading profitability remain untested. The 2025 demand period and two feasibility price samples had already been inspected; 2025 price outcomes were excluded from model fitting and selection but are not described as wholly unseen.''')
md('''## Context & Methods
At **04:00 New York time on D−1**, predict the NYC/Zone J day-ahead LBMP for **18:00–19:00 on D**, in $/MWh. Delivery is normally 38 hours ahead, or 37/39 at DST. The auction price is usually published on D−1, before physical delivery; this is a different horizon from time until price revelation.

The question is narrowly whether forecast temperature adds information beyond the specified calendar baseline. No historical-price or load inputs are included, so unavailable corrections cannot leak through those covariates. Outcomes are corrected/latest archived prices, called finalized prices in this study; they are not verified original auction publications or immutable settlement records.

### Key Assumptions
- The retained NOAA HRRR operational 06 UTC forecast object's Last-Modified predates cutoff by at least five minutes. It is archive-availability evidence, not an exact first-NCEP-publication ledger. Multipart objects and late/replaced files are excluded.
- The forecast is genuinely a 40/41-hour forecast valid at the target time, not an analysis or realized future observation. Embedded issue/valid times, field identity, operational status and byte receipts are checked.
- A grid point near LaGuardia proxies city weather; regional weather, fuel prices, supply outages, congestion and other price drivers are omitted.
- Corrected historical prices are outcome labels only. Retrospectively corrected fitting labels mean this is not a complete as-of simulation of historical model training.
- Missing/late-forecast dates are excluded equally across models, potentially selecting easier or harder dates. No late issue or realized weather is substituted.

Fit 2021–2023; choose the weather specification on 2024 MAE; refit on 2021–2024; evaluate 2025. All models have the same 14 calendar columns: weekday, three annual Fourier harmonics and a fixed federal-holiday proxy excluding Juneteenth. Ordinary least squares compares calendar-only, linear forecast temperature, and a three-hinge piecewise-linear forecast-temperature spline. Center/scale/knots use fitting data only. See [EXPERIMENT.md](EXPERIMENT.md) for the frozen choices.''')
md('### 1. Reproduce the frozen calculation')
code('''from pathlib import Path
import sys, json, io, contextlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from IPython.display import display
ROOT = Path.cwd()
assert (ROOT / 'EXPERIMENT.md').exists(), 'Execute from price_research.'
sys.path.insert(0, str(ROOT / 'src'))
from run import main
with contextlib.redirect_stdout(io.StringIO()):
    main()  # Refit and evaluate the same frozen choices from source-verified daily data.
OUT = ROOT / 'outputs'
summary = json.loads((OUT / 'summary.json').read_text())
configuration = json.loads((OUT / 'selected_configuration.json').read_text())
selected = summary['selected_weather_model']
plt.rcParams.update({'figure.figsize': (10, 5), 'font.size': 11,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.alpha': .18, 'axes.axisbelow': True,
                     'savefig.dpi': 150})
COLORS = {'calendar': '#52616b', 'linear': '#b5791b', 'spline': '#2166ac'}
LABELS = {'calendar': 'Calendar only', 'linear': '+ Linear forecast temperature',
          'spline': '+ Forecast-temperature spline'}
def save_figure(fig, filename):
    fig.tight_layout()
    fig.savefig(OUT / filename, bbox_inches='tight')
    plt.show()
print('Frozen price comparison reproduced; no realized weather, price history, load or demand-model inputs.')''')
md('''## Data
[NOAA's operational HRRR archive](https://registry.opendata.aws/noaa-hrrr-pds/) supplies the fixed 06 UTC cycle and target-valid 2m temperature forecast. Only the relevant GRIB message is downloaded using byte ranges. ecCodes extracts the nearest point to LaGuardia and verifies forecast metadata. [NYISO's historical day-ahead archive](https://mis.nyiso.com/public/P-2Alist.htm) supplies corrected outcome prices. [SOURCES.md](SOURCES.md) documents the timing evidence and its limits.''')
code('''data = pd.read_csv(OUT / 'daily_data.csv')
coverage = pd.read_csv(OUT / 'annual_coverage.csv')
exclusions = pd.read_csv(OUT / 'excluded_days.csv')
display(coverage.assign(coverage_pct=coverage.coverage * 100).drop(columns='coverage').round(2))
print(f"Matched {data.usable.sum():,} of {len(data):,} target days; {len(exclusions)} excluded.")
display(exclusions.reason.value_counts().rename('Excluded days').to_frame())
points = json.loads((OUT / 'grid_points.json').read_text())
print('Nearest grid metadata:', {grid: {k:v for k,v in point.items() if k != 'value'} for grid, point in points.items()})
assert (pd.to_datetime(data.loc[data.usable, 'archive_available_utc'], utc=True)
        <= pd.to_datetime(data.loc[data.usable, 'cutoff_utc'], utc=True) - pd.Timedelta(minutes=5)).all()
print('Every included forecast has a retained archive-availability witness before the cutoff buffer.')''')
md('''The coverage table's denominator is all expected delivery dates, not only dates with successful downloads. Each exclusion is retained. Eight feasibility source samples were reused with original receipts; all dates pass the same gate. The study uses one daily target hour, not thousands of independent hourly experiments.''')
md('''## Results
### 2. Validation selection and final error comparison''')
code('''display(pd.read_csv(OUT / 'validation_metrics.csv').round(3))
print('Weather model selected using 2024 MAE:', selected)
scores = pd.read_csv(OUT / 'test_metrics.csv')
overall = scores.loc[scores.group_type.eq('overall')].set_index('model').loc[list(LABELS)]
display(overall[['days', 'mae_mwh', 'rmse_mwh', 'mean_residual_mwh', 'improvement_pct']].round(3))
fig, ax = plt.subplots(figsize=(11, 5))
bars = ax.bar([LABELS[name] for name in LABELS], overall.mae_mwh,
              color=[COLORS[name] for name in LABELS], hatch=['', '//', '..'],
              edgecolor='#263238', linewidth=.6)
ax.bar_label(bars, fmt='$%.2f', padding=5)
ax.set(ylabel='Mean absolute error ($/MWh)',
       title=f"2025 finalized NYC prices · {summary['matched_2025_days']} matched days · selected weather model: {selected}",
       ylim=(0, overall.mae_mwh.max() * 1.23))
save_figure(fig, '01_model_error_comparison.png')''')
md(f'''The primary weather comparison is **{selected}**, chosen before scoring 2025. Both predefined weather variants are shown for transparency; we do not change the primary model to whichever wins in 2025. A calendar baseline is deliberately limited: this test does not establish incremental value over price-history/calendar or commercial energy forecasts. The selected model still underestimates finalized prices by **$21.81/MWh on average**, with **$49.46/MWh RMSE**; these are substantial remaining errors.''')
md('### 3. Finalized outcomes and estimates over the evaluation year')
code('''predictions = pd.read_csv(OUT / 'test_predictions.csv', parse_dates=['delivery_date'])
# Reindex to all calendar dates so missing forecasts leave gaps in the plotted lines.
plot = predictions.set_index('delivery_date').reindex(pd.date_range('2025-01-01', '2025-12-31'))
fig, ax = plt.subplots(figsize=(11, 5.5))
ax.plot(plot.index, plot.finalized_price_mwh, color='#263238', linewidth=1.1, label='Finalized outcome')
ax.plot(plot.index, plot.calendar, color=COLORS['calendar'], linestyle='--', linewidth=1.1, label='Calendar estimate')
ax.plot(plot.index, plot[selected], color=COLORS[selected], linewidth=1.2, label=f'Selected weather estimate ({selected})')
ax.set(ylabel='18:00–19:00 day-ahead price ($/MWh)', xlabel='2025 delivery date',
       title='Finalized prices and frozen-model predictions · no price clipping')
ax.set_xticks(pd.to_datetime(['2025-01-01','2025-03-01','2025-05-01','2025-07-01','2025-09-01','2025-12-31']))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax.set_xlim(pd.Timestamp('2025-01-01'), pd.Timestamp('2025-12-31'))
ax.legend(frameon=False, loc='upper right')
save_figure(fig, '02_evaluation_year.png')''')
md('''All matched outcomes remain in the evaluation, including negative values and price spikes. Missing-forecast dates are gaps, not zeros. A forecast of the finalized price level is not a trading return or an executable entry/exit price.''')
md('### 4. Monthly stability and dependence-aware uncertainty')
code('''monthly = scores.loc[scores.group_type.eq('month')].pivot(index='group', columns='model', values='mae_mwh')
monthly.index = monthly.index.astype(int)
monthly = monthly.sort_index()
monthly['selected_improvement_mwh'] = monthly.calendar - monthly[selected]
monthly['selected_improvement_pct'] = 100 * monthly.selected_improvement_mwh / monthly.calendar
display(monthly.round(3))
fig, ax = plt.subplots()
labels = [pd.Timestamp(2025, month, 1).strftime('%b') for month in monthly.index]
values = monthly.selected_improvement_mwh
bars = ax.bar(labels, values, color=COLORS[selected], edgecolor='#263238', linewidth=.6)
ax.axhline(0, color='#263238', linewidth=1)
ax.set(ylabel='Calendar MAE minus weather MAE ($/MWh)', xlabel='2025 delivery month',
       title=f'Monthly incremental value · validation-selected {selected} model')
save_figure(fig, '03_monthly_improvement.png')
display(pd.read_csv(OUT / 'uncertainty.csv').round(3))
display(pd.read_csv(OUT / 'residual_diagnostics.csv').round(3))''')
md(f'''Positive monthly bars mean lower weather-model error; negative bars mean deterioration. **{summary['months_with_selected_improvement']} of twelve months improve.** The seven-day paired block interval for the selected comparison is ${primary.lower_95_mwh:.2f}–${primary.upper_95_mwh:.2f}/MWh. {uncertainty_text} Fourteen- and 28-day sensitivity intervals are reported without selecting the most favorable one. These intervals describe this one year's paired errors, not all future years or causal effects.''')
md('### 5. Adjusted association with forecast temperature')
code('''curve = pd.read_csv(OUT / 'forecast_temperature_response.csv')
fig, ax = plt.subplots()
for name, style in [('linear', '--'), ('spline', '-')]:
    ax.plot(curve.forecast_temperature_c, curve[name + '_relative_mwh'],
            label=LABELS[name] + (' · selected' if name == selected else ''),
            color=COLORS[name], linestyle=style, linewidth=2)
ax.axhline(0, color='#263238', linewidth=.8)
ax.axvline(18, color='#888888', linewidth=.8, linestyle=':')
ax.set(xlabel='Forecast temperature at the NYC grid point (°C)',
       ylabel='Estimated price relative to 18°C ($/MWh)',
       title='Fitted forecast-temperature association · calendar held fixed')
ax.legend(frameon=False)
save_figure(fig, '04_forecast_temperature_response.png')
print(f"Curve restricted to fitting-sample 1st–99th percentiles: {curve.forecast_temperature_c.min():.1f}–{curve.forecast_temperature_c.max():.1f}°C.")''')
md('''This curve is a model association with **forecast**, not realized, temperature. It is not a causal temperature-to-price estimate or a climate scenario. Calendar is held fixed, and the model assumes an additive temperature response; other weather and market drivers are omitted.''')
md('### 6. Hot forecasts, large errors and gain concentration')
code('''display(scores.loc[scores.group_type.eq('forecast_temperature') & scores.group.eq('hot'),
                   ['model', 'days', 'mae_mwh', 'rmse_mwh', 'mean_residual_mwh', 'improvement_pct']].round(3))
print(f"Hot cutoff fixed from 2021–2023 forecast temperatures: {configuration['hot_forecast_threshold_c_2021_2023']:.2f}°C.")
concentration = json.loads((OUT / 'gain_concentration.json').read_text())
print('Gain concentration diagnostic:', concentration)
display(pd.read_csv(OUT / 'ten_largest_baseline_errors.csv')[
    ['delivery_date', 'finalized_price_mwh', 'baseline_absolute_error', 'selected_absolute_error', 'selected_error_improvement']].round(3))''')
md('''The selected model worsens MAE in **March and November**, and in the spring aggregate. Its one-day residual correlation remains **0.685**. The ten largest baseline-error days account for **26.7% of the net absolute-error improvement**; they contribute materially but do not account for the whole gain. Hot-forecast results cover only **16 evaluation days**, so they provide limited evidence about extreme conditions.

Hot conditions and largest-error tables are descriptive diagnostics. No hot-day cutoff or outlier rule was chosen using 2025 errors. The ten large-error days remain in the primary result. A gain dominated by a handful of events would limit the generalization even if overall MAE improves.''')
md('''## Takeaways
The evaluated claim is strictly **incremental predictive value of dated forecast temperature over this calendar-only baseline for finalized NYC day-ahead prices**. Report the observed improvement or deterioration, its monthly stability and uncertainty without expanding the claim.

A strong price-history baseline remains untested. Weather may already be incorporated into auction participants' expectations; predictable price levels do not automatically identify mispricing. Supply, gas costs, regional weather, congestion and other drivers are omitted. One final year and selectively missing forecast dates limit generalization. Corrected historical outcome labels and archive timestamp evidence do not constitute a full historical execution simulation.

**No trading profitability, executable strategy, or causal price-impact claim is made.** No further model search or trading backtest is pending. The original demand study and the earlier stricter feasibility assessment remain separate records.

Reproduction from this folder: install `requirements.txt`; `python src/acquire.py` (network, cached files reused); `python src/prepare.py` (offline decoder and source gate); `python src/run.py`; `python -m unittest discover -s tests -v`; `python execute_notebook.py`. The executed notebook reruns fitting and scoring from the verified daily table; run preparation to regenerate that table from raw source messages.''')
n.cells = cells
n.metadata = {'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'}}
nb.validate(n)
nb.write(n,ROOT/'NYC_Finalized_Price_Research.ipynb')
print('Notebook built:',len(cells),'cells')
