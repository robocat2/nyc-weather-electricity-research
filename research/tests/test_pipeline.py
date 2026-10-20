"""Boundary and leakage tests for consequential pipeline behavior."""
import hashlib,json,sys,unittest
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from prepare import load_frame,weather_frame
from features import TemperatureTransform,calendar_matrix
from evaluate import block_interval

class PipelineTests(unittest.TestCase):
    def test_fall_dst_two_distinct_hours(self):
        x=pd.DataFrame({'Time Stamp':['11/03/2024 01:00:00']*2,'Time Zone':['EDT','EST'],'Name':['N.Y.C.']*2,'PTID':[61761]*2,'Integrated Load':[4000,4100]})
        result=load_frame(x)
        self.assertEqual(result.utc.diff().iloc[1],pd.Timedelta(hours=1))
        self.assertEqual(result.utc.dt.hour.tolist(),[5,6])
    def test_spring_dst_and_reject_wrong_offset(self):
        x=pd.DataFrame({'Time Stamp':['03/10/2024 01:00:00','03/10/2024 03:00:00'],'Time Zone':['EST','EDT'],'Name':['N.Y.C.']*2,'PTID':[61761]*2,'Integrated Load':[4000,4100]})
        self.assertEqual(load_frame(x).utc.diff().iloc[1],pd.Timedelta(hours=1))
        x.loc[1,'Time Zone']='EST'
        with self.assertRaises(ValueError):load_frame(x)
    def test_quality_priority_and_no_imputation(self):
        x=pd.DataFrame({'STATION':['USW00014732']*5,'DATE':['2021-01-01T00:00:00','2021-01-01T00:51:00','2021-01-01T00:30:00','2021-01-01T01:51:00','2021-01-01T03:51:00'],'temperature':[5,6,12,7,8],'temperature_Quality_Code':['1','5','5','6','1'],'temperature_Source_Code':['223','343','343','343','223'],'temperature_Report_Type':['FM12','FM15','FM16','FM15','FM15']})
        result=weather_frame(x)
        self.assertEqual(result.temperature_c.tolist(),[6,8])
        self.assertEqual(result.utc.dt.hour.tolist(),[0,3])
        self.assertEqual(result.weather_report_utc.dt.minute.tolist(),[51,51])
    def test_preprocessing_uses_only_fitting_sample(self):
        transform=TemperatureTransform(3).fit([0,10,20,30])
        before=json.dumps(transform.metadata(),sort_keys=True)
        transform.transform([-1000,1000])
        self.assertEqual(before,json.dumps(transform.metadata(),sort_keys=True))
        self.assertEqual(transform.knots_c,[7.5,15,22.5])
    def test_calendar_independent_of_outcome_and_temperature(self):
        a=pd.DataFrame({'utc':pd.date_range('2024-01-01',periods=24,freq='h',tz='UTC'),'temperature_c':0,'load_mw':100})
        b=a.copy();b['temperature_c']=999;b['load_mw']=-999
        np.testing.assert_equal(calendar_matrix(a)[0],calendar_matrix(b)[0])
    def test_raw_hashes_and_frozen_specification(self):
        for row in json.loads((ROOT/'raw/manifest.json').read_text()):
            self.assertEqual(row['sha256'],hashlib.sha256((ROOT/'raw'/row['file']).read_bytes()).hexdigest(),row['file'])
        spec=json.loads((ROOT/'outputs/specification_freeze.json').read_text())
        self.assertEqual(spec['sha256'],hashlib.sha256((ROOT/'EXPERIMENT.md').read_bytes()).hexdigest())
    def test_actual_split_and_join_integrity(self):
        x=pd.read_csv(ROOT/'outputs/hourly_data.csv',parse_dates=['utc'])
        self.assertEqual(len(x),43824);self.assertFalse(x.utc.duplicated().any())
        self.assertTrue(x.utc.diff().dropna().eq(pd.Timedelta(hours=1)).all())
        train=x.loc[x.year.le(2023)];validation=x.loc[x.year.eq(2024)];test=x.loc[x.year.eq(2025)]
        self.assertLess(train.utc.max(),validation.utc.min());self.assertLess(validation.utc.max(),test.utc.min())
        self.assertTrue(x.loc[x.usable,['load_mw','temperature_c']].notna().all().all())
        self.assertTrue(x.loc[~x.usable,'temperature_c'].isna().all())
        p=pd.read_csv(ROOT/'outputs/test_predictions.csv');self.assertEqual(len(p),int(test.usable.sum()))
        self.assertTrue(p.year.eq(2025).all());self.assertTrue(np.isfinite(p[['calendar','linear','spline']]).all().all())
    def test_fitted_preprocessing_and_hot_threshold_exclude_final_year(self):
        x=pd.read_csv(ROOT/'outputs/hourly_data.csv')
        fitting=x.loc[x.usable & x.year.le(2024),'temperature_c'].to_numpy()
        train=x.loc[x.usable & x.year.le(2023),'temperature_c'].to_numpy()
        models=json.loads((ROOT/'outputs/fitted_models.json').read_text())
        for name in ['linear','spline']:
            transform=models[name]['temperature_transform']
            self.assertAlmostEqual(transform['mean_c'],float(np.mean(fitting)),places=10)
            self.assertAlmostEqual(transform['scale_c'],float(np.std(fitting)),places=10)
        np.testing.assert_allclose(models['spline']['temperature_transform']['knots_c'],np.quantile(fitting,[.25,.5,.75]))
        selected=json.loads((ROOT/'outputs/selected_configuration.json').read_text())
        self.assertAlmostEqual(selected['hot_threshold_c_from_2021_2023'],float(np.quantile(train,.95)))
        for name,expected in selected['code_sha256'].items():
            self.assertEqual(expected,hashlib.sha256((ROOT/'src'/name).read_bytes()).hexdigest())
    def test_paired_block_interval_constant_effect_and_counts(self):
        lo,hi=block_interval(np.array([20.,30.,40.]),np.array([2.,3.,4.]),block=2,repeats=100)
        self.assertAlmostEqual(lo,10);self.assertAlmostEqual(hi,10)
    def test_scores_recomputed_from_predictions(self):
        p=pd.read_csv(ROOT/'outputs/test_predictions.csv');s=pd.read_csv(ROOT/'outputs/test_metrics.csv')
        for name in ['calendar','linear','spline']:
            row=s.loc[s.group_type.eq('overall') & s.model.eq(name)].iloc[0]
            error=p.load_mw.to_numpy()-p[name].to_numpy()
            self.assertAlmostEqual(row.mae_mw,sum(abs(v) for v in error)/len(error),places=8)
            self.assertAlmostEqual(row.rmse_mw,(sum(v*v for v in error)/len(error))**.5,places=8)
if __name__=='__main__':unittest.main()
