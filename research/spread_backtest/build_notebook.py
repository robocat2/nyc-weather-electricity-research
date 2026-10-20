"""Build the evidence-backed gross spread-signal notebook, including negative findings."""
from pathlib import Path
import json
import pandas as pd
import nbformat as nb
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'outputs'
s=json.loads((OUT/'summary.json').read_text());selected=s['selected_weather_strategy']
n=nb.v4.new_notebook();cells=[]
def md(text):cells.append(nb.v4.new_markdown_cell(text))
def code(text):cells.append(nb.v4.new_code_cell(text))
md('''# NYC weather-based spread signal: gross backtest
## tl;dr
**We tested an actual directional trading rule—but did not establish convincing gross alpha.** The validation-selected **linear forecast-temperature spread rule** earned a hypothetical **+$1,020.96** in 2025, versus **+$321.98** for calendar-only and **+$1,384.92** for always virtual load / the training-mean benchmark. Each active day assumes one MWh clears; no costs or executable fills are modeled.

The selected rule's seven-day block-bootstrap interval for mean daily gross payoff spans **−$8.10 to +$18.29**. Its incremental interval versus calendar spans **−$0.72 to +$6.04/day**. Neither establishes a reliably positive effect in this year. The best day earned **$1,768.53**, exceeding the entire net profit; the other 361 days together lost **$747.57**.

A spline did better in 2025, but performed much worse in validation and was **not selected**. Promoting it after seeing the final year would be a different, outcome-informed experiment. The prior **16.6% day-ahead price MAE improvement remains valid for that separate question**; it was never a trading return.''')
md('''## Context & Methods
At 04:00 New York time on D−1, predict the NYC hour-18 **real-time minus day-ahead spread** for D. Positive predicted spread → virtual load (+1); negative → virtual supply (−1); exactly zero → flat. For a one-MWh cleared schedule, gross energy payoff is **side × (RT − DA)** dollars.

This is the first trading-rule experiment following the demand and DA-price studies. **Neither previous fitted model is an input.** We refit spread models directly using the same verified calendar and archived forecast-temperature covariates. Train 2021–2023, select linear vs three-hinge spline on **2024 gross mean daily payoff**, refit 2021–2024, evaluate 2025. All models share fourteen calendar controls. No threshold/size search, price-history features or realized future weather.

### Key Assumptions
- One MWh is assumed cleared per active signal. Actual bid acceptance, limits, partial fills and access are not established.
- Fees, uplift, slippage, collateral/financing and other charges are intentionally excluded. This is hypothetical gross energy settlement, not net trading profitability or a capital-based percentage return.
- Both DA and RT prices are unknown at cutoff and are outcomes only. Corrected historical labels and archive timestamp evidence do not reconstruct exact historical training/invoice vintages.
- 2025 was already examined in prior demand/DA-price research; this is retrospective chronological evaluation, not a blind or prospective test.
- Selectively excluded forecast dates are shared by every strategy. One final year and heavy tails limit inference.

The frozen choices are in [EXPERIMENT.md](EXPERIMENT.md). Market mechanics and source evidence are in the [feasibility brief](../trading_feasibility/FEASIBILITY_BRIEF.md).''')
md('### 1. Reproduce the fixed experiment')
code('''from pathlib import Path
import sys,json,io,contextlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from IPython.display import display
ROOT=Path.cwd()
assert (ROOT/'EXPERIMENT.md').exists(), 'Execute from spread_backtest.'
sys.path.insert(0,str(ROOT/'src'))
from run import main
with contextlib.redirect_stdout(io.StringIO()):
    main()  # Source verification, chronological selection, refit, gross payoff arithmetic.
OUT=ROOT/'outputs'
summary=json.loads((OUT/'summary.json').read_text())
selected=summary['selected_weather_strategy']
LABELS={'calendar':'Calendar rule','linear':'Linear-weather rule','spline':'Spline-weather rule',
        'always_load':'Always virtual load','always_supply':'Always virtual supply','flat':'Flat',
        'training_mean':'Training-mean rule'}
plt.rcParams.update({'figure.figsize':(10,5),'font.size':11,'axes.spines.top':False,
                     'axes.spines.right':False,'axes.grid':True,'grid.alpha':.18,
                     'axes.axisbelow':True,'savefig.dpi':150})
def save(fig,name):
    fig.tight_layout();fig.savefig(OUT/name,bbox_inches='tight');plt.show()
print('Same frozen gross experiment reproduced. Selected:',selected)''')
md('''## Data
NYISO NYC / Zone J PTID 61761, delivery 18:00–19:00. [Day-ahead zonal prices](https://mis.nyiso.com/public/P-2Alist.htm) and [official integrated real-time zonal prices](https://mis.nyiso.com/public/P-4Alist.htm) exist for all 1,826 dates in 2021–2025. The official RT series preserves interval-duration weighting; no unweighted five-minute average is substituted. Both outcome prices already include their loss/congestion components.

The prior HRRR forecast gate leaves 1,809 eligible dates: 360/359/364/364/362 by year. Seventeen late or insufficiently timestamped files remain excluded. Forecast inputs were retained before cutoff with a five-minute buffer; issue/valid metadata were verified. No price values enter features.''')
code('''eligible=pd.read_csv(OUT/'eligible_data.csv')
display(eligible.groupby('year').size().rename('Eligible target days').to_frame())
assert (pd.to_datetime(eligible.archive_available_utc,utc=True)
        <= pd.to_datetime(eligible.cutoff_utc,utc=True)-pd.Timedelta(minutes=5)).all()
print('Every included forecast precedes the frozen cutoff buffer.')
validation=pd.read_csv(OUT/'validation_metrics.csv')
display(validation[['strategy','active_trades','total_gross_dollars','mean_daily_gross_dollars']].round(3))''')
md('''The linear weather rule earned $4.53/day in 2024 versus $0.89/day for the spline; it was selected under the prespecified trading objective. Calendar-only earned $4.75/day in validation. The trading objective deliberately differs from the prior DA-price study's MAE objective.''')
md('''## Results
### 2. Gross payoff and risk versus benchmarks''')
code('''metrics=pd.read_csv(OUT/'test_metrics.csv')
overall=metrics.loc[metrics.group_type.eq('overall')].set_index('strategy')
display(overall[['active_trades','virtual_load_days','virtual_supply_days','total_gross_dollars',
                 'mean_daily_gross_dollars','win_rate_active','daily_std_dollars',
                 'max_drawdown_dollars','worst_day_dollars']].round(3))
fig,ax=plt.subplots(figsize=(10,5.7))
order=['flat','always_supply','calendar','linear','always_load','spline']
values=overall.loc[order,'total_gross_dollars']
colors=['#2166ac' if name==selected else '#84929c' for name in order]
bars=ax.barh([LABELS[name]+(' · selected' if name==selected else ' · unselected' if name=='spline' else '') for name in order],values,color=colors,
             edgecolor='#263238',linewidth=.6)
ax.axvline(0,color='#263238',linewidth=1)
for rect,value in zip(bars,values):
    label=f'−${abs(value):,.2f}' if value<0 else f'${value:,.2f}'
    ax.text(value+60,rect.get_y()+rect.get_height()/2,label,ha='left',va='center',color='#1c2630')
ax.set(xlabel='Total hypothetical gross energy payoff ($)',title='2025 · 362 dates · assumed 1 MWh cleared per active signal')
ax.set_xlim(values.min()*1.30,values.max()*1.20)
save(fig,'01_gross_benchmark_comparison.png')''')
md('''**The selected weather rule loses the benchmark comparison to always virtual load / training mean.** Its +$698.98 increment over calendar is positive in the sample, but statistically uncertain. The always-supply strategy wins more often (66.9%) yet loses $1,384.92 because a few large adverse spreads outweigh its frequent small wins. Win rate is not profitability.

The spline's +$2,524.12 is an explicitly reported unselected alternative. It cannot replace the primary linear rule after seeing 2025. No strategy has been retuned.''')
md('### 3. Cumulative dollar payoff and drawdown')
code('''signals=pd.read_csv(OUT/'test_daily_signals.csv',parse_dates=['delivery_date'])
full=signals.set_index('delivery_date').reindex(pd.date_range('2025-01-01','2025-12-31'))
fig,ax=plt.subplots(figsize=(11,5.5))
for name,color,style in [(selected,'#2166ac','-'),('calendar','#52616b','--'),
                         ('always_load','#b5791b','-.'),('always_supply','#697b32',':')]:
    equity=full[name+'_pnl'].fillna(0).cumsum()
    ax.plot(equity.index,equity,label=LABELS[name],color=color,linestyle=style,linewidth=1.6)
ax.axhline(0,color='#263238',linewidth=.8,label='Flat benchmark')
ax.set(xlabel='2025 delivery date',ylabel='Cumulative gross energy payoff ($)',
       title='Hypothetical gross payoff · excluded dates contribute no trades')
ax.set_xticks(pd.to_datetime(['2025-01-01','2025-03-01','2025-05-01','2025-07-01','2025-09-01','2025-12-31']))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax.set_xlim(pd.Timestamp('2025-01-01'),pd.Timestamp('2025-12-31'))
ax.legend(frameon=False)
save(fig,'02_cumulative_gross_payoff.png')''')
md('''The selected rule's maximum drawdown is **$983.09**, against $1,020.96 net gross gain. It takes virtual load on 195 days and virtual supply on 167, differing from calendar on 32 days. The training-mean rule chooses virtual load using fitting data and therefore duplicates that constant-direction benchmark in this evaluation.''')
md('### 4. Monthly stability')
code('''monthly=metrics.loc[metrics.group_type.eq('month') & metrics.strategy.eq(selected)].copy()
monthly['month']=monthly['group'].astype(int);monthly=monthly.sort_values('month')
display(monthly[['month','days','total_gross_dollars','mean_daily_gross_dollars']].round(3))
fig,ax=plt.subplots()
ax.bar([pd.Timestamp(2025,m,1).strftime('%b') for m in monthly.month],monthly.total_gross_dollars,
       color='#2166ac',edgecolor='#263238',linewidth=.6)
ax.axhline(0,color='#263238',linewidth=1)
ax.set(xlabel='2025 delivery month',ylabel='Selected-rule gross payoff ($)',
       title='Monthly gross payoff · validation-selected linear weather rule')
save(fig,'03_monthly_gross_payoff.png')''')
md('''Only **three months** have positive net payoff; June contributes $2,289.69. A positive full-year total masks weak consistency. No months are removed or used to redesign the rule.''')
md('### 5. Paired uncertainty in the gross edge')
code('''intervals=pd.read_csv(OUT/'uncertainty.csv')
display(intervals.round(3))
primary=intervals.loc[intervals.block_days.eq(7)].copy()
fig,ax=plt.subplots(figsize=(10,5))
y=np.arange(len(primary))
ax.errorbar(primary.mean_incremental_daily_dollars,y,
            xerr=[primary.mean_incremental_daily_dollars-primary.lower_95_dollars,
                  primary.upper_95_dollars-primary.mean_incremental_daily_dollars],
            fmt='o',color='#2166ac',ecolor='#52616b',capsize=5,linewidth=1.5)
ax.axvline(0,color='#263238',linewidth=1)
ax.set_yticks(y,[LABELS[name] for name in primary.benchmark])
ax.invert_yaxis()
ax.set(xlabel='Selected rule minus benchmark mean payoff ($ per decision day)',
       title='Paired seven-day block-bootstrap 95% intervals · 2025')
save(fig,'04_paired_gross_uncertainty.png')''')
md('''The intervals cross zero for raw payoff versus flat and for every incremental comparison, including calendar and always-load. The 14/28-day sensitivity intervals also cross zero. **Reliable positive gross alpha is not established**, even before costs. Bootstrap intervals cover this year's dependent payoffs, not refitting uncertainty or every future year.''')
md('### 6. Large-spread reconciliation and concentration')
code('''best=pd.read_csv(OUT/'ten_best_days.csv');worst=pd.read_csv(OUT/'ten_worst_days.csv')
columns=['delivery_date','finalized_price_mwh','rt_integrated_price_mwh','rt_minus_da_mwh',selected+'_side',selected+'_pnl']
display(best[columns].round(3));display(worst[columns].round(3))
print('Ten best days together:',round(best[selected+'_pnl'].sum(),2),'dollars.')
display(pd.read_csv(OUT/'residual_diagnostics.csv').round(3))''')
md('''The largest gain is **June 24, 2025**: official archived NYC DA price **$365.00/MWh**, integrated RT price **$2,133.53/MWh**, and spread **+$1,768.53/MWh**. These exact values were reconciled to the two raw ZIP members; the large observation is retained. The selected rule, calendar and always-load all took virtual load that day, so it is not evidence of unique weather timing.

The best day exceeds the selected rule's entire net total: the remaining 361 dates sum to **−$747.57**. The ten best days sum to $4,288.91, or 420.1% of net gain; percentages above 100% mean other days offset the winners. This is a concentration diagnostic, not an alternative backtest with outliers removed.''')
md('''## Takeaways
**We have now tested a genuine directional spread signal in a hypothetical gross backtest. We have not demonstrated convincing alpha.** Positive sample P&L is outweighed by weak benchmark performance, broad uncertainty, concentration in a few large events and only one exposed evaluation year. Costs were not needed to reach this limited conclusion.

The earlier 39.2% demand and 16.6% DA-price error reductions remain findings about their own questions. They do not imply tradable spread skill. The primary linear-weather signal was selected using validation trading payoff; switching to the final-year-winning spline now would be a new, outcome-informed choice requiring fresh evaluation.

Stop this fixed experiment here. No threshold search, sizing optimization, execution extension or cost model has been started. Keep the negative/uncertain trading result alongside the useful earlier research rather than presenting the price-error result as a profitable strategy.

Reproduce from this folder: use the parent `price_research/.venv` environment or install this folder's `requirements.txt`, then `python src/run.py`, `python -m unittest discover -s tests -v`, and `python execute_notebook.py`. Earlier raw inputs and their receipts remain required in adjacent project folders. This notebook reruns source verification, fitting, selection and the same frozen evaluation.''')
n.cells=cells;n.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'}}
nb.validate(n);nb.write(n,ROOT/'NYC_Gross_Spread_Backtest.ipynb');print('Built',len(cells),'cells')
