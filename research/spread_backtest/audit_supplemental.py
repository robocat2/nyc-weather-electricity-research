from pathlib import Path
import json,hashlib,sys
import numpy as np,pandas as pd,eccodes
P=Path('NYC_Weather_Electricity');O=P/'spread_backtest/outputs';result={}
a=json.loads((P/'price_research/outputs/forecast_availability.json').read_text());eligible={r['delivery_date']:r for r in a if r['available']}
points=pd.read_csv(P/'price_research/outputs/daily_data.csv').set_index('delivery_date')
for date,r in eligible.items():
 p=P/'price_research/raw'/r['file']; assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
 h=json.loads((P/'price_research/raw'/f'forecast_{date}_head.json').read_text())['headers'];h={k.lower():v for k,v in h.items()}
 assert h['etag']==r['etag'] and '-' not in h['etag']
 assert pd.Timestamp(h['last-modified'])==pd.Timestamp(r['archive_available_utc'])
 assert pd.Timestamp(r['archive_available_utc'])<=pd.Timestamp(r['cutoff_utc'])-pd.Timedelta(minutes=5)
result['forecast_raw_hashes_and_header_timing']=len(eligible)
# Stratified raw GRIB sample: all years, both DST transitions, heat-spike date.
dates=['2021-01-01','2021-07-15','2022-01-15','2022-07-15','2023-01-15','2023-07-15','2024-01-15','2024-07-15','2025-03-09','2025-06-24','2025-11-02','2025-12-31']
for date in dates:
 r=eligible[date];g=eccodes.codes_new_from_message((P/'price_research/raw'/r['file']).read_bytes())
 try:
  get=lambda k:eccodes.codes_get(g,k)
  assert get('shortName')=='2t' and get('level')==2 and get('units')=='K' and get('dataType')=='fc'
  valid=pd.to_datetime(str(get('validityDate'))+f'{get("validityTime"):04}',format='%Y%m%d%H%M',utc=True)
  issue=pd.to_datetime(str(get('dataDate'))+f'{get("dataTime"):04}',format='%Y%m%d%H%M',utc=True)
  assert valid==pd.Timestamp(r['target_utc']) and issue==pd.Timestamp(r['cycle_utc'])
  nearest=eccodes.codes_grib_find_nearest(g,40.7794,-73.8803,npoints=1)[0]
  assert nearest['distance']<5
  value=nearest['value']-273.15
  assert abs(value-points.loc[date,'forecast_temperature_c'])<1e-9
 finally:eccodes.codes_release(g)
result['independent_raw_GRIB_point_and_metadata_samples']=dates
# Independently recompute original headline MAE reductions.
for name,folder,target in [('demand',P,'load_mw'),('price',P/'price_research','finalized_price_mwh')]:
 x=pd.read_csv(folder/'outputs/test_predictions.csv');mae={k:float(np.mean(abs(x[target]-x[k]))) for k in ['calendar','linear','spline']}
 gain=100*(1-mae['spline']/mae['calendar']);result[name+'_MAE']=mae;result[name+'_improvement_percent']=gain
 assert abs(gain-({'demand':39.242265,'price':16.569386}[name]))<.00001
x=pd.read_csv(O/'test_daily_signals.csv');u=pd.read_csv(O/'uncertainty.csv')
for block in [7,14,28]:
 rng=np.random.default_rng(61761);starts=rng.integers(0,365,size=(5000,int(np.ceil(365/block))))
 idx=np.concatenate([(starts[:,i,None]+np.arange(block))%365 for i in range(starts.shape[1])],axis=1)[:,:365]
 for bench in ['flat','calendar','always_load','always_supply','training_mean']:
  values=pd.Series(x.linear_pnl.to_numpy()-x[bench+'_pnl'].to_numpy(),index=x.delivery_date).reindex(pd.date_range('2025-01-01','2025-12-31').strftime('%Y-%m-%d'))
  counts=values.notna().to_numpy().astype(int);totals=values.fillna(0).to_numpy()
  means=np.take(totals,idx).sum(1)/np.take(counts,idx).sum(1)
  ci=np.percentile(means,[2.5,97.5]);row=u[(u.block_days==block)&(u.benchmark==bench)].iloc[0]
  np.testing.assert_allclose(ci,[row.lower_95_dollars,row.upper_95_dollars],atol=1e-10)
result['independently_recomputed_bootstrap_intervals']=15
probes=json.loads((P/'price_feasibility/outputs/price_probes.json').read_text())
result['prior_price_feasibility_samples_total']=len(probes);result['prior_2025_samples']=sum(r['delivery_date'].startswith('2025') for r in probes)
(O/'supplemental_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
