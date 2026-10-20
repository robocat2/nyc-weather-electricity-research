"""Independent forecast metadata/point spot checks and paired-interval replay."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd,eccodes
ROOT=Path(__file__).resolve().parent;O=ROOT/'outputs'
rows=json.loads((O/'older_forecasts.json').read_text());available=[r for r in rows if r['available']]
for r in available:assert hashlib.sha256((ROOT/'raw'/r['file']).read_bytes()).hexdigest()==r['sha256']
# Sample all years plus the large-price date and DST boundaries; failures are not substituted.
sample_dates=['2021-01-15','2021-07-15','2022-01-15','2022-07-15','2023-03-12','2023-07-15','2024-01-15','2024-11-03','2025-03-09','2025-06-24','2025-11-02','2025-12-31']
lookup={r['delivery_date']:r for r in available};checked=[];not_eligible=[]
for date in sample_dates:
 if date not in lookup:not_eligible.append(date);continue
 r=lookup[date];g=eccodes.codes_new_from_message((ROOT/'raw'/r['file']).read_bytes())
 try:
  get=lambda k:eccodes.codes_get(g,k)
  assert get('shortName')=='2t' and get('typeOfLevel')=='heightAboveGround' and get('level')==2 and get('units')=='K'
  assert get('dataType')=='fc' and get('productionStatusOfProcessedData')==0 and get('centre')=='kwbc'
  issue=pd.to_datetime(str(get('dataDate'))+f'{get("dataTime"):04}',format='%Y%m%d%H%M',utc=True)
  valid=pd.to_datetime(str(get('validityDate'))+f'{get("validityTime"):04}',format='%Y%m%d%H%M',utc=True)
  assert issue==pd.Timestamp(r['cycle_utc']) and valid==pd.Timestamp(r['target_utc']) and int(get('step'))==r['lead_hours']
  nearest=eccodes.codes_grib_find_nearest(g,40.7794,-73.8803,npoints=1)[0]
  assert nearest['distance']<5 and nearest['index']==r['grid_index']
  assert abs(nearest['value']-273.15-r['forecast_temperature_c'])<1e-9
  checked.append(date)
 finally:eccodes.codes_release(g)
interval_count=0
for family in ['trajectory','revision']:
 folder=O/family;x=pd.read_csv(folder/'daily_signals.csv');s=json.loads((folder/'summary.json').read_text());intervals=pd.read_csv(folder/'uncertainty.csv')
 for block in [7,14,28]:
  rng=np.random.default_rng(61761);starts=rng.integers(0,365,size=(5000,int(np.ceil(365/block))))
  indices=np.concatenate([(starts[:,i,None]+np.arange(block))%365 for i in range(starts.shape[1])],axis=1)[:,:365]
  for bench in ['linear','calendar','always_load','flat']:
   v=pd.Series(x[s['selected']+'_pnl'].to_numpy()-x[bench+'_pnl'].to_numpy(),index=x.delivery_date).reindex(pd.date_range('2025-01-01','2025-12-31').strftime('%Y-%m-%d'))
   count=v.notna().to_numpy(int);total=v.fillna(0).to_numpy();ci=np.percentile(total[indices].sum(1)/count[indices].sum(1),[2.5,97.5])
   row=intervals[(intervals.block_days==block)&(intervals.benchmark==bench)].iloc[0]
   np.testing.assert_allclose(ci,[row.lower_95,row.upper_95],atol=1e-10);interval_count+=1
result={'older_inventory_dates':len(rows),'older_available_raw_hashes_verified':len(available),'older_GRIB_samples_independently_verified':checked,'sample_dates_excluded_not_substituted':not_eligible,'paired_intervals_independently_replayed':interval_count,'full_browser_layout':'not inspected'}
(O/'independent_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
