"""Render the fixed follow-up results without refitting or changing selections."""
from pathlib import Path
import base64,json,html
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np,pandas as pd,mistune
ROOT=Path(__file__).resolve().parent;O=ROOT/'outputs'
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.grid':True,'grid.alpha':.18,'savefig.dpi':150})
labels={'linear':'Original linear','calendar':'Calendar','trajectory1':'1-day trajectory','trajectory2':'1+2-day trajectory','revision':'6-hour revision','always_load':'Always virtual load','always_supply':'Always virtual supply','flat':'Flat','training_mean':'Training-mean side'}
families=['trajectory','revision'];results={f:json.loads((O/f/'summary.json').read_text()) for f in families}
metrics={f:pd.read_csv(O/f/'test_metrics.csv') for f in families};frames={f:pd.read_csv(O/f/'daily_signals.csv') for f in families}
charts=[]
def save(fig,name):
 fig.tight_layout();fig.savefig(O/name,bbox_inches='tight',facecolor='white');plt.close(fig);charts.append(name)
fig,axes=plt.subplots(2,1,figsize=(11,9))
for ax,f in zip(axes,families):
 s=results[f];selected=s['selected'];names=['calendar','linear',selected,'always_load','flat'];m=metrics[f];m=m[m.group_type=='overall'].set_index('strategy')
 vals=m.loc[names,'total_gross_dollars'];bars=ax.barh([labels[n]+(' · selected' if n==selected else '') for n in names],vals,color=['#2166ac' if n==selected else '#84929c' for n in names])
 scale=max(abs(vals).max(),1)
 for bar,v in zip(bars,vals):ax.text(v+scale*.025,bar.get_y()+bar.get_height()/2,(f'−${abs(v):,.2f}' if v<0 else f'${v:,.2f}'),va='center',ha='left')
 ax.axvline(0,color='#263238',lw=1);ax.set_xlim(min(vals.min()*1.3,-scale*.1),scale*1.28);ax.set_title(f'{f.title()} · {s["test_days"]} matched 2025 dates');ax.set_xlabel('Hypothetical gross payoff ($), one MWh assumed cleared')
save(fig,'01_matched_benchmarks.png')
fig,axes=plt.subplots(2,1,figsize=(11,8))
for ax,f in zip(axes,families):
 x=frames[f];s=results[f]
 for n,c in [(s['selected'],'#2166ac'),('linear','#84929c'),('always_load','#c18b25')]:ax.plot(pd.to_datetime(x.delivery_date),x[n+'_pnl'].cumsum(),label=labels[n],color=c)
 ax.axhline(0,color='#263238',lw=.8);ax.set(title=f'{f.title()} · cumulative gross payoff',ylabel='Dollars');ax.legend(loc='upper left')
save(fig,'02_cumulative_payoffs.png')
fig,axes=plt.subplots(2,1,figsize=(11,8))
for ax,f in zip(axes,families):
 u=pd.read_csv(O/f/'uncertainty.csv');u=u[u.block_days==7];y=np.arange(len(u));ax.hlines(y,u.lower_95,u.upper_95,color='#2166ac',lw=3);ax.scatter(u.mean_increment,y,color='#2166ac');ax.axvline(0,color='#263238',lw=1)
 ax.set_yticks(y,[f'vs {labels[b]}' for b in u.benchmark]);ax.set(title=f'{f.title()} · 7-day block bootstrap, unadjusted 95% intervals',xlabel='Mean incremental gross dollars per matched decision date')
save(fig,'03_incremental_uncertainty.png')
fig,axes=plt.subplots(2,1,figsize=(11,8))
for ax,f in zip(axes,families):
 x=frames[f];selected=results[f]['selected'];v=x.groupby('month')[selected+'_pnl'].sum();ax.bar(v.index,v.values,color='#2166ac');ax.set_xticks(range(1,13));ax.axhline(0,color='#263238',lw=.8);ax.set(title=f'{f.title()} · selected variant monthly gross payoff',xlabel='Month of 2025',ylabel='Dollars')
save(fig,'04_monthly_payoffs.png')
text='''# Weather trajectory and forecast revisions: exploratory follow-ups

The completed portfolio release is preserved. These are two additional, bounded experiments in the same NYC electricity project, not stock trading. Both predict hour-18 real-time minus day-ahead prices at 04:00 ET on the prior day. Positive forecast means virtual load; negative means virtual supply. All dollars assume one MWh clears per signal, before fees, uplift, slippage and financing.

**Both 2024 and 2025 were examined in earlier work. These are exploratory results, not fresh confirmation of alpha.** The two related hypothesis comparisons are not corrected for multiple testing. No variant was promoted based on its 2025 score.

## What changed

**Trajectory:** add the difference between forecast evening temperatures for D and D−1, optionally also D−2, to the existing linear-weather/calendar model. These are forecasts issued on different dates. They are not realized temperature lags or evidence that stock prices react slowly. At the decision cutoff, D−1 evening has not yet occurred. The proxy can mix weather evolution with forecast errors.

**Revisions:** add the six-hour change between 00 UTC and 06 UTC forecasts for the SAME next-day evening temperature at the SAME grid point. Both must be archived before the cutoff buffer. Leads are 46/47 versus 40/41 hours. Thus this compares changes in forecast expectations rather than changes in the weather target date.

Development fit 2021–2023, selection 2024, refit 2021–2024, evaluate 2025. Trajectory variant selection uses validation gross payoff; revision has one fixed variant. Calendar/linear baselines are refitted on each family's exact eligible cohort. Cross-family dollar totals are not a fair ranking because cohorts differ.
'''
for f in families:
 s=results[f];u=pd.read_csv(O/f/'uncertainty.csv');primary=u[u.block_days==7].set_index('benchmark');m=metrics[f];overall=m[m.group_type=='overall'];val=pd.read_csv(O/f/'validation_metrics.csv')
 linear=primary.loc['linear'];load=primary.loc['always_load'];flat=primary.loc['flat']
 supported=all(primary.loc[b,'lower_95']>0 for b in ['linear','always_load','flat'])
 text+=f'''\n## {f.title()} result

Selected variant: **{labels[s['selected']]}**. Eligible evaluation dates: **{s['test_days']}**.

- Selected gross payoff: **${s['gross_total']:,.2f}**.
- Same-cohort original linear: **${s['linear_total']:,.2f}**; always virtual load: **${s['always_load_total']:,.2f}**.
- Increment over linear: **${linear.mean_increment:,.2f}/decision**, seven-day 95% interval **[${linear.lower_95:,.2f}, ${linear.upper_95:,.2f}]**.
- Increment over always-load: **${load.mean_increment:,.2f}/decision**, interval **[${load.lower_95:,.2f}, ${load.upper_95:,.2f}]**.
- Raw gross mean versus flat interval: **[${flat.lower_95:,.2f}, ${flat.upper_95:,.2f}]**.
- Best day **{s['best_date']}**, payoff **${s['best_payoff']:,.2f}**; remaining dates **${s['rest_payoff']:,.2f}**. Positive months: **{s['positive_months']} of 12**.

**Interpretation:** {'The primary intervals favor this variant in this retrospective sample, but prior exposure, related testing and execution assumptions prevent a confirmed-alpha claim.' if supported else 'This comparison does not establish reliable incremental gross alpha over the original linear model and constant-direction benchmark.'}

### Validation selection and all alternatives

'''
 text+='\n```csv\n'+val.to_csv(index=False)+'```\n'
 text+='\n### Final strategy metrics (including unselected alternatives)\n\n```csv\n'+overall.to_csv(index=False)+'```\n'
 text+='\n### All block-length sensitivity intervals\n\n```csv\n'+u.to_csv(index=False)+'```\n'
 gate=json.loads((O/f/'data_gate.json').read_text());text+=f"\nData gate: {gate['eligible']} eligible of 1,826 dates, {gate['excluded']} exclusions. No imputations or actual-future-weather substitution.\n"
text+='''
## Limits and stopping point

Same-cohort benchmarks are essential: excluding dates and refitting can change the original linear strategy's payoff. Do not compare these selected totals directly with the original 362-date $1,020.96 result. Gross dollars are not percentage returns. Operational forecast archive timestamps provide availability evidence, not a complete first-dissemination ledger. Corrected outcome prices do not recreate historical training-label or invoice vintages. One evaluation year, one grid point, heavy tails and omissions of price history/outages/fuel costs limit interpretation. Bootstrap intervals do not cover researcher choices or future-year performance.

Both fixed tests are complete. No interaction search, tuning to 2025 or automatic next hypothesis follows. A new prospective evaluation would be needed before increasing confidence in any signal.

## Reproduction and source evidence

`src/acquire_revisions.py` retrieves bounded temperature-message ranges from the public NOAA HRRR S3 archive. Prior forecast gates, NYISO price archives and market documentation are retained in the adjacent original studies. Run the family preparation/model scripts and tests described in the folder README. The frozen `EXPERIMENT.md` defines features, cohorts, selection and stopping rules. Raw receipts, availability metadata, family exclusions, daily signals and source/code hashes are retained. Chart PNGs are inspected separately; full browser layout is not certified.
'''
(O/'FOLLOWUP_FINDINGS.md').write_text(text)
overview='''## Main finding
Neither follow-up establishes reliable incremental gross alpha. The selected forecast trajectory earned $1,121.88 versus $776.12 for its matched linear baseline; its increment remains uncertain. Forecast revisions earned $982.62 versus $1,020.96 for the matched linear baseline. Both remain dominated by the June 24 extreme-price day. Trajectory uses 356 dates; revision uses 362. Do not rank their raw totals across cohorts.

'''
text=text.replace('## What changed',overview+'## What changed',1)
(O/'FOLLOWUP_FINDINGS.md').write_text(text)
body=mistune.html(text)
figures=''.join(f'<figure><img alt="{html.escape(n)}" src="data:image/png;base64,{base64.b64encode((O/n).read_bytes()).decode()}"/><figcaption>{html.escape(n)}</figcaption></figure>' for n in charts)
page='<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NYC exploratory weather follow-ups</title><style>body{font-family:system-ui,sans-serif;max-width:1050px;margin:auto;padding:24px;color:#1c2630;line-height:1.6}img{width:100%;height:auto}pre{overflow:auto;font-size:12px;background:#f4f6f8;padding:12px}h1,h2{color:#174b7b}figure{margin:30px 0}figcaption{font-size:12px;color:#536270}</style></head><body>'+body+'<h2>Figures: matched comparisons</h2>'+figures+'<details><summary>Frozen experiment</summary><pre>'+html.escape((ROOT/'EXPERIMENT.md').read_text())+'</pre></details></body></html>'
(O/'NYC_Weather_Followups.html').write_text(page)
print('Created follow-up findings and self-contained HTML with',len(charts),'figures')
if __name__=='__main__':pass
