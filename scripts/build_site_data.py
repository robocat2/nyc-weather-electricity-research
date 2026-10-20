"""Build the website snapshot from saved, audited research outputs."""
from pathlib import Path
import csv,json,hashlib
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'research';SITE=ROOT/'site'
def rows(path):
 with path.open() as stream:return list(csv.DictReader(stream))
def obj(path):return json.loads(path.read_text())
def scores(folder,kind):
 return [{ 'name':r['model'],'mae':float(r['mae_'+kind]),'rmse':float(r['rmse_'+kind])} for r in rows(folder/'outputs/test_metrics.csv') if r['group_type']=='overall']
demand=scores(R,'mw');price=scores(R/'price_research','mwh')
trade=[{'name':r['strategy'],'total':float(r['total_gross_dollars']),'drawdown':float(r['max_drawdown_dollars']),'winRate':float(r['win_rate_active']) if r['win_rate_active'] else None} for r in rows(R/'spread_backtest/outputs/test_metrics.csv') if r['group_type']=='overall']
cumulative=rows(R/'spread_backtest/outputs/cumulative_payoff.csv')
data={'period':'2021–2025','repository':'https://github.com/robocat2/nyc-weather-electricity-research','demand':demand,'price':price,'trading':trade,
 'demandGain':100*(1-demand[2]['mae']/demand[0]['mae']),'priceGain':100*(1-price[2]['mae']/price[0]['mae']),
 'cumulative':[{'date':r['delivery_date'],'linear':float(r['linear_cumulative_dollars']),'calendar':float(r['calendar_cumulative_dollars']),'always_load':float(r['always_load_cumulative_dollars'])} for r in cumulative],
 'spreadIntervals':[{'benchmark':r['benchmark'],'mean':float(r['mean_incremental_daily_dollars']),'low':float(r['lower_95_dollars']),'high':float(r['upper_95_dollars'])} for r in rows(R/'spread_backtest/outputs/uncertainty.csv') if r['block_days']=='7'],
 'followups':{f:{'summary':obj(R/f'followup_hypotheses/outputs/{f}/summary.json'),'intervals':rows(R/f'followup_hypotheses/outputs/{f}/uncertainty.csv')} for f in ['trajectory','revision']}}
(SITE/'assets/research-data.js').write_text('window.RESEARCH = '+json.dumps(data,separators=(',',':'),allow_nan=False)+';\n')
(SITE/'evidence/results.json').write_text(json.dumps(data,indent=2)+'\n')
for source,name in [(R/'outputs/NYC_Combined_Research_Walkthrough.html','full-research.html'),(R/'followup_hypotheses/outputs/NYC_Weather_Followups.html','followups.html')]:
 soup=BeautifulSoup(source.read_text(),'html.parser')
 for a in soup.find_all('a',href=True):
  h=a['href']
  if not h.startswith(('https:','http:','#','mailto:','data:')):
   resolved=(source.parent/h).resolve()
   a['href']=data['repository']+'/blob/main/research/'+str(resolved.relative_to(R.resolve()))
 (SITE/'evidence'/name).write_text(str(soup))
for source,name in [(R/'spread_backtest/outputs/test_daily_signals.csv','daily-signals.csv'),(R/'spread_backtest/outputs/uncertainty.csv','spread-uncertainty.csv'),(R/'price_research/outputs/test_metrics.csv','price-metrics.csv'),(R/'outputs/test_metrics.csv','demand-metrics.csv')]:
 (SITE/'evidence'/name).write_bytes(source.read_bytes())
sources=[R/'outputs/test_metrics.csv',R/'price_research/outputs/test_metrics.csv',R/'spread_backtest/outputs/test_metrics.csv',R/'spread_backtest/outputs/cumulative_payoff.csv',R/'spread_backtest/outputs/uncertainty.csv']
for f in ['trajectory','revision']:sources.extend([R/f'followup_hypotheses/outputs/{f}/summary.json',R/f'followup_hypotheses/outputs/{f}/uncertainty.csv'])
(SITE/'evidence/provenance.json').write_text(json.dumps({'snapshot':'Completed research; 2021–2025 observations. No live data.','sources':[{'file':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources]},indent=2)+'\n')
print('Built data snapshot and local evidence pages')
