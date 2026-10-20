"""Join original verified forecasts by exact dates; no outcome-driven inclusion."""
from pathlib import Path
import json,hashlib
import pandas as pd
import numpy as np
ROOT=Path(__file__).resolve().parents[1];P=ROOT.parent;O=ROOT/'outputs'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def prepare(family):
 daily=P/'price_research/outputs/daily_data.csv'
 cfg=json.loads((P/'price_research/outputs/selected_configuration.json').read_text())
 if digest(daily)!=cfg['daily_data_sha256']:raise ValueError('Original verified inputs changed')
 inventory=P/'trading_feasibility/outputs/spread_label_inventory.csv'
 original_snapshot=json.loads((P/'spread_backtest/outputs/source_snapshot.json').read_text())
 if digest(inventory)!=original_snapshot['spread_inventory_sha256']:raise ValueError('Original spread labels changed')
 for receipt in json.loads((P/'trading_feasibility/outputs/source_manifest.json').read_text()):
  if digest(P/'trading_feasibility/raw'/receipt['file'])!=receipt['sha256']:raise ValueError('RT archive changed')
 base=pd.read_csv(inventory)
 original=pd.read_csv(daily);verified=original[original.usable].copy()
 cols=['delivery_date','forecast_temperature_c','archive_available_utc','decoder_issue_utc','decoder_valid_utc','grid_md5','grid_index']
 data=base.merge(verified[cols],how='left',on='delivery_date',validate='one_to_one')
 data['reason']=np.where(data.forecast_temperature_c.isna(),'original forecast unavailable','')
 if family=='trajectory':
  for lag in [1,2]:
   date=pd.to_datetime(data.delivery_date)-pd.Timedelta(days=lag)
   lookup=verified.set_index('delivery_date')
   data[f'lag{lag}_date']=date.dt.strftime('%Y-%m-%d')
   data[f'lag{lag}_forecast_c']=data[f'lag{lag}_date'].map(lookup.forecast_temperature_c)
   data[f'lag{lag}_available_utc']=data[f'lag{lag}_date'].map(lookup.archive_available_utc)
   data[f'change{lag}_c']=data.forecast_temperature_c-data[f'lag{lag}_forecast_c']
  required=['forecast_temperature_c','change1_c','change2_c']
  data.loc[data[required].isna().any(axis=1)&data.reason.eq(''),'reason']='missing exact previous-date forecast'
 else:
  rawpath=O/'older_forecasts.json';rows=json.loads(rawpath.read_text())
  if len(rows)!=1826 or len({r['delivery_date'] for r in rows})!=1826:raise ValueError('Incomplete old forecast inventory')
  old=pd.DataFrame(rows);old=old[old.available].copy()
  for r in old.itertuples():
   if digest(ROOT/'raw'/r.file)!=r.sha256:raise ValueError('Older raw hash mismatch')
  ren={'forecast_temperature_c':'old_forecast_temperature_c','archive_available_utc':'old_available_utc','decoder_issue_utc':'old_issue_utc','decoder_valid_utc':'old_valid_utc','grid_md5':'old_grid_md5','grid_index':'old_grid_index'}
  data=data.merge(old[cols].rename(columns=ren),on='delivery_date',how='left',validate='one_to_one')
  data['revision_c']=data.forecast_temperature_c-data.old_forecast_temperature_c
  required=['forecast_temperature_c','revision_c']
  good=data[required].notna().all(axis=1)
  if not (data.loc[good,'grid_md5']==data.loc[good,'old_grid_md5']).all() or not (data.loc[good,'grid_index']==data.loc[good,'old_grid_index']).all():raise ValueError('Different forecast grids')
  if not (pd.to_datetime(data.loc[good,'old_valid_utc'],utc=True)==pd.to_datetime(data.loc[good,'target_utc'],utc=True)).all():raise ValueError('Different target times')
  if not (pd.to_datetime(data.loc[good,'decoder_issue_utc'],utc=True)-pd.to_datetime(data.loc[good,'old_issue_utc'],utc=True)==pd.Timedelta(hours=6)).all():raise ValueError('Wrong revision window')
  data.loc[~good&data.reason.eq(''),'reason']='older forecast unavailable/unverified'
 good=data[required].notna().all(axis=1)&data.usable_spread_research
 eligible=data[good].copy().sort_values('delivery_date');excluded=data[~good].copy()
 if family=='trajectory':timecols=['archive_available_utc','lag1_available_utc','lag2_available_utc']
 else:timecols=['archive_available_utc','old_available_utc']
 for col in timecols:
  if not (pd.to_datetime(eligible[col],utc=True)<=pd.to_datetime(eligible.cutoff_utc,utc=True)-pd.Timedelta(minutes=5)).all():raise ValueError('Late input')
 eligible['month']=pd.to_datetime(eligible.delivery_date).dt.month
 expected=data.groupby(['year',pd.to_datetime(data.delivery_date).dt.month]).size()
 counts=eligible.groupby(['year','month']).size().reindex(expected.index,fill_value=0)
 coverage=pd.DataFrame({'expected':expected,'eligible':counts});coverage['fraction']=coverage.eligible/coverage.expected
 annual=coverage.groupby(level=0)[['expected','eligible']].sum();annual['fraction']=annual.eligible/annual.expected
 folder=O/family;folder.mkdir(exist_ok=True)
 eligible.to_csv(folder/'eligible.csv',index=False);excluded.to_csv(folder/'excluded.csv',index=False);coverage.to_csv(folder/'monthly_coverage.csv');annual.to_csv(folder/'annual_coverage.csv')
 gate=bool(coverage.fraction.min()>=.8 and annual.fraction.min()>=.9)
 snapshot={'family':family,'passed':gate,'eligible':len(eligible),'excluded':len(excluded),'original_data_sha256':digest(daily),'spread_inventory_sha256':digest(P/'trading_feasibility/outputs/spread_label_inventory.csv'),'older_inventory_sha256':digest(O/'older_forecasts.json') if family=='revision' else None,'eligible_sha256':digest(folder/'eligible.csv')}
 (folder/'data_gate.json').write_text(json.dumps(snapshot,indent=2)+'\n')
 if not gate:raise ValueError(f'{family} coverage gate failed')
 return eligible
