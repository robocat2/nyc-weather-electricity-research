from pathlib import Path
import unittest,json,hashlib,sys
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];P=ROOT.parent
sys.path.insert(0,str(ROOT/'src'))
from followup_model import FollowupModel,FEATURES
from pandas.tseries.holiday import USFederalHolidayCalendar

class FollowupTests(unittest.TestCase):
 def families(self):
  folders=[ROOT/'outputs'/f for f in ['trajectory','revision']]
  self.assertTrue(all((p/'summary.json').exists() for p in folders),'Both tests must complete before final verification')
  return folders
 def test_frozen_code_sources_and_release(self):
  for folder in self.families():
   cfg=json.loads((folder/'configuration.json').read_text());first=json.loads((folder/'first_evaluation_configuration.json').read_text())
   self.assertEqual(first['selected'],cfg['selected']);self.assertEqual(first['code_sha256'],cfg['code_sha256'])
   for file,h in cfg['code_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/'src'/file).read_bytes()).hexdigest(),h)
   for file,h in cfg['helpers_sha256'].items():self.assertEqual(hashlib.sha256((P/file).read_bytes()).hexdigest(),h)
   self.assertEqual(hashlib.sha256((ROOT/'EXPERIMENT.md').read_bytes()).hexdigest(),cfg['specification_sha256'])
  release=P/'portfolio/releases/NYC_Weather_Electricity_Portfolio.zip'
  self.assertEqual(hashlib.sha256(release.read_bytes()).hexdigest(),'fd040356edda1a9e7a1c702eaf06299c4aebe57d5d1442714425b0e7e255d659')
 def test_exact_date_trajectory(self):
  x=pd.read_csv(ROOT/'outputs/trajectory/eligible.csv');old=pd.read_csv(P/'price_research/outputs/daily_data.csv');lookup=old[old.usable].set_index('delivery_date')
  for lag in [1,2]:
   dates=(pd.to_datetime(x.delivery_date)-pd.Timedelta(days=lag)).dt.strftime('%Y-%m-%d')
   np.testing.assert_equal(dates.to_numpy(),x[f'lag{lag}_date'].to_numpy())
   np.testing.assert_allclose(x[f'lag{lag}_forecast_c'],dates.map(lookup.forecast_temperature_c))
   np.testing.assert_allclose(x[f'change{lag}_c'],x.forecast_temperature_c-x[f'lag{lag}_forecast_c'])
  excluded=pd.read_csv(ROOT/'outputs/trajectory/excluded.csv');self.assertTrue({'2021-01-01','2021-01-02'}.issubset(set(excluded.delivery_date)))
 def test_revisions_same_valid_time_grid_and_direction(self):
  x=pd.read_csv(ROOT/'outputs/revision/eligible.csv')
  np.testing.assert_allclose(x.revision_c,x.forecast_temperature_c-x.old_forecast_temperature_c)
  self.assertTrue(x.grid_md5.eq(x.old_grid_md5).all());self.assertTrue(x.grid_index.eq(x.old_grid_index).all())
  self.assertTrue((pd.to_datetime(x.decoder_valid_utc,utc=True)==pd.to_datetime(x.old_valid_utc,utc=True)).all())
  self.assertTrue((pd.to_datetime(x.decoder_issue_utc,utc=True)-pd.to_datetime(x.old_issue_utc,utc=True)==pd.Timedelta(hours=6)).all())
 def test_all_inputs_before_cutoff(self):
  for folder in self.families():
   x=pd.read_csv(folder/'eligible.csv');limit=pd.to_datetime(x.cutoff_utc,utc=True)-pd.Timedelta(minutes=5)
   cols=['archive_available_utc','old_available_utc'] if folder.name=='revision' else ['archive_available_utc','lag1_available_utc','lag2_available_utc']
   for col in cols:self.assertTrue((pd.to_datetime(x[col],utc=True)<=limit).all())
 def test_coverage_and_chronology(self):
  for folder in self.families():
   x=pd.read_csv(folder/'eligible.csv');self.assertFalse(x.delivery_date.duplicated().any());self.assertTrue(x.delivery_date.is_monotonic_increasing)
   self.assertTrue((pd.read_csv(folder/'monthly_coverage.csv').fraction>=.8).all());self.assertTrue((pd.read_csv(folder/'annual_coverage.csv').fraction>=.9).all())
   self.assertLess(x[x.year<=2023].delivery_date.max(),x[x.year==2024].delivery_date.min());self.assertLess(x[x.year==2024].delivery_date.max(),x[x.year==2025].delivery_date.min())
 def test_validation_selection_and_training_transforms(self):
  for folder in self.families():
   x=pd.read_csv(folder/'eligible.csv');fit=x[x.year<=2024];val=pd.read_csv(folder/'validation_metrics.csv').set_index('strategy');cfg=json.loads((folder/'configuration.json').read_text())
   candidates=['trajectory1','trajectory2'] if folder.name=='trajectory' else ['revision']
   self.assertEqual(cfg['selected'],min(candidates,key=lambda n:(-val.loc[n,'mean_daily_gross_dollars'],n)))
   for n,state in json.loads((folder/'fitted_models.json').read_text()).items():
    if FEATURES[n]:
     np.testing.assert_allclose(state['mean'],fit[FEATURES[n]].mean());np.testing.assert_allclose(state['scale'],fit[FEATURES[n]].std(ddof=0))
 def test_independent_all_payoffs_drawdowns_and_win_rates(self):
  for folder in self.families():
   x=pd.read_csv(folder/'daily_signals.csv');self.assertTrue(x.year.eq(2025).all());self.assertFalse(x.delivery_date.duplicated().any())
   for r in pd.read_csv(folder/'test_metrics.csv').itertuples():
    group=x if r.group_type=='overall' else x[x.month==int(r.group)]
    side=group[r.strategy+'_side'].to_numpy();self.assertTrue(np.isin(side,[-1,0,1]).all())
    pnl=side*(group.rt_integrated_price_mwh.to_numpy()-group.finalized_price_mwh.to_numpy())
    np.testing.assert_allclose(pnl,group[r.strategy+'_pnl']);self.assertAlmostEqual(float(pnl.sum()),r.total_gross_dollars,places=7)
    peak=equity=dd=0
    for v in pnl:equity+=v;peak=max(peak,equity);dd=max(dd,peak-equity)
    self.assertAlmostEqual(dd,r.max_drawdown_dollars,places=7)
    if (side!=0).any():self.assertAlmostEqual(float((pnl[side!=0]>0).mean()),r.win_rate_active)
 def test_independent_normal_equation_refits(self):
  holidays=USFederalHolidayCalendar();holidays.rules=[r for r in holidays.rules if 'Juneteenth' not in r.name];h=set(holidays.holidays('2020-01-01','2027-01-01').date)
  def design(frame,name,train):
   rows=[];features=FEATURES[name];means=train[features].mean().to_numpy();std=train[features].std(ddof=0).to_numpy()
   for _,r in frame.iterrows():
    d=pd.Timestamp(r.delivery_date);phase=2*np.pi*(d.dayofyear-1)/(366 if d.is_leap_year else 365)
    row=[1]+[float(d.dayofweek==day) for day in range(1,7)]
    for k in (1,2,3):row.extend([np.sin(k*phase),np.cos(k*phase)])
    row.append(float(d.date() in h));row.extend((r[features].to_numpy(float)-means)/std);rows.append(row)
   return np.asarray(rows)
  for folder in self.families():
   x=pd.read_csv(folder/'eligible.csv');signals=pd.read_csv(folder/'daily_signals.csv');validation=pd.read_csv(folder/'validation_metrics.csv').set_index('strategy')
   models=json.loads((folder/'fitted_models.json').read_text())
   for name in models:
    for end,year in [(2023,2024),(2024,2025)]:
     train=x[x.year<=end];test=x[x.year==year];a=design(train,name,train);b=design(test,name,train)
     coef=np.linalg.solve(a.T@a,a.T@train.rt_minus_da_mwh.to_numpy());pred=b@coef;pnl=np.sign(pred)*test.rt_minus_da_mwh.to_numpy()
     if year==2025:np.testing.assert_allclose(pred,signals[name+'_prediction'],atol=1e-8);np.testing.assert_equal(np.sign(pred),signals[name+'_side'])
     else:self.assertAlmostEqual(float(pnl.sum()),validation.loc[name,'total_gross_dollars'],places=7)
 def test_outcomes_cannot_change_predictions(self):
  for folder in self.families():
   x=pd.read_csv(folder/'eligible.csv');train=x[x.year<=2024];sample=x[x.year==2025].head().copy();changed=sample.copy()
   for col in ['rt_minus_da_mwh','rt_integrated_price_mwh','finalized_price_mwh','load_mw','realized_temperature']:changed[col]=1e9
   names=json.loads((folder/'fitted_models.json').read_text())
   for name in names:
    model=FollowupModel(name).fit(train);np.testing.assert_equal(model.predict(sample),model.predict(changed))
if __name__=='__main__':unittest.main()
