"""Read-only independent raw-price, OLS, payoff and artifact audit."""
from pathlib import Path
import csv,io,zipfile,json,hashlib
import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent; P=ROOT.parent; O=ROOT/'outputs'
checks={}
raw={}
for label,folder,pattern in [('da',P/'price_research/raw','prices_*.zip'),('rt',P/'trading_feasibility/raw','rt_*.zip')]:
 records={}
 for path in sorted(folder.glob(pattern)):
  with zipfile.ZipFile(path) as z:
   for member in z.namelist():
    if not member.endswith('.csv'):continue
    for r in csv.DictReader(io.StringIO(z.read(member).decode('utf-8-sig'))):
     if r['PTID']=='61761' and r['Name']=='N.Y.C.':
      stamp=pd.Timestamp(r['Time Stamp'])
      if stamp.hour==18:
       assert stamp.minute==0
       date=str(stamp.date());assert date not in records,(label,date)
       records[date]=float(r['LBMP ($/MWHr)'])
 assert len(records)==1826
 raw[label]=records
 checks[label+'_raw_days']=len(records)
x=pd.read_csv(O/'eligible_data.csv'); test=pd.read_csv(O/'test_daily_signals.csv')
for r in x.itertuples():
 assert abs(raw['da'][r.delivery_date]-r.finalized_price_mwh)<1e-9
 assert abs(raw['rt'][r.delivery_date]-r.rt_integrated_price_mwh)<1e-9
 assert abs(raw['rt'][r.delivery_date]-raw['da'][r.delivery_date]-r.rt_minus_da_mwh)<1e-9
 cutoff=pd.Timestamp(r.cutoff_utc); target=pd.Timestamp(r.target_utc)
 assert cutoff.tz_convert('America/New_York').hour==4
 assert target.tz_convert('America/New_York').hour==18
 assert cutoff.tz_convert('America/New_York').date()==(pd.Timestamp(r.delivery_date)-pd.Timedelta(days=1)).date()
 assert pd.Timestamp(r.archive_available_utc)<=cutoff-pd.Timedelta(minutes=5)
 assert pd.Timestamp(r.decoder_issue_utc)<cutoff
 assert pd.Timestamp(r.decoder_valid_utc)==target
checks['eligible_raw_label_and_timing_matches']=len(x)
calendar=USFederalHolidayCalendar();calendar.rules=[r for r in calendar.rules if 'Juneteenth' not in r.name]
holidays=set(calendar.holidays('2020-01-01','2027-01-01').date)
def matrix(frame,kind,train):
 rows=[];temp=train.forecast_temperature_c.to_numpy();mean=temp.mean();scale=temp.std()
 knots=np.quantile(temp,[.25,.5,.75]) if kind=='spline' else []
 for r in frame.itertuples():
  d=pd.Timestamp(r.delivery_date);phase=2*np.pi*(d.dayofyear-1)/(366 if d.is_leap_year else 365)
  row=[1]+[float(d.dayofweek==i) for i in range(1,7)]
  for h in (1,2,3):row.extend([np.sin(h*phase),np.cos(h*phase)])
  row.append(float(d.date() in holidays))
  if kind!='calendar':row.extend([(r.forecast_temperature_c-mean)/scale]+[max(r.forecast_temperature_c-k,0)/scale for k in knots])
  rows.append(row)
 return np.asarray(rows)
validation=pd.read_csv(O/'validation_metrics.csv').set_index('strategy')
scores=pd.read_csv(O/'test_metrics.csv');maxdiff=0
for cutoff,year in [(2023,2024),(2024,2025)]:
 train=x[x.year<=cutoff];eval=x[x.year==year]
 for kind in ['calendar','linear','spline']:
  a=matrix(train,kind,train);b=matrix(eval,kind,train)
  # Solve the normal equations independently of production's lstsq.
  coef=np.linalg.solve(a.T@a,a.T@train.rt_minus_da_mwh.to_numpy())
  pred=b@coef;side=np.sign(pred);pnl=side*np.array([raw['rt'][d]-raw['da'][d] for d in eval.delivery_date])
  expected=validation.loc[kind,'total_gross_dollars'] if year==2024 else scores[(scores.strategy==kind)&(scores.group_type=='overall')].iloc[0].total_gross_dollars
  assert abs(pnl.sum()-expected)<1e-7
  if year==2025:
   maxdiff=max(maxdiff,float(np.max(np.abs(pred-test[kind+'_prediction']))))
   np.testing.assert_allclose(pred,test[kind+'_prediction'],atol=1e-8)
   np.testing.assert_equal(side,test[kind+'_side'])
checks['independent_OLS_fits']=6;checks['maximum_prediction_difference']=maxdiff
for r in scores.itertuples():
 subset=test if r.group_type=='overall' else test[test.month==int(r.group)] if r.group_type=='month' else test[test.season==r.group]
 pnl=[getattr(t,r.strategy+'_side')*(raw['rt'][t.delivery_date]-raw['da'][t.delivery_date]) for t in subset.itertuples()]
 assert abs(sum(pnl)-r.total_gross_dollars)<1e-7
 equity=peak=dd=0
 for v in pnl:equity+=v;peak=max(peak,equity);dd=max(dd,peak-equity)
 assert abs(dd-r.max_drawdown_dollars)<1e-7
checks['all_strategy_period_totals_and_drawdowns']=len(scores)
intervals=pd.read_csv(O/'uncertainty.csv');assert ((intervals.lower_95_dollars<0)&(intervals.upper_95_dollars>0)).all()
for cfgpath in [O/'selected_configuration.json',P/'price_research/outputs/selected_configuration.json']:
 cfg=json.loads(cfgpath.read_text());base=cfgpath.parents[1]
 for file,digest in cfg['code_sha256'].items():assert hashlib.sha256((base/'src'/file).read_bytes()).hexdigest()==digest
 assert hashlib.sha256((base/'EXPERIMENT.md').read_bytes()).hexdigest()==cfg['specification_sha256']
checks['spread_and_price_frozen_code_and_protocol']='unchanged'
for file,count in [(O/'NYC_Gross_Spread_Backtest.html',4),(P/'outputs/NYC_Combined_Research_Walkthrough.html',12)]:
 soup=BeautifulSoup(file.read_text(),'html.parser');ids=[e['id'] for e in soup.find_all(id=True)]
 assert len(ids)==len(set(ids));assert len(soup.find_all('img'))==count
 for a in soup.find_all('a',href=True):
  h=a['href']
  if h.startswith('#'):assert h[1:] in ids
  elif not h.startswith(('https:','http:','mailto:')):assert (file.parent/h).exists()
checks['html_links_anchors_and_figures']='passed'
checks['browser_layout']='not verified; chart PNGs reviewed separately'
(O/'independent_audit.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
