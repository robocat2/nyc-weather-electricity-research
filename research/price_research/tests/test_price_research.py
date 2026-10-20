"""Timing, forecast identity, feature isolation and finalized-score checks."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys, unittest
import eccodes
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from acquire import availability, dates_and_times
from prepare import decode_message
from model import calendar_features, PriceModel
from evaluate import block_interval

class PriceResearchTests(unittest.TestCase):
    def test_dst_cutoff_and_delivery_horizons(self):
        for date,horizon,lead in [('2024-03-10',37,40),('2024-11-03',39,41),('2025-07-15',38,40),('2025-01-15',38,41)]:
            target,cutoff,cycle,actual_lead = dates_and_times(date)
            self.assertEqual((target-cutoff).total_seconds()/3600,horizon)
            self.assertEqual(actual_lead,lead)
            self.assertLess(cycle,cutoff)
    def test_future_late_and_multipart_forecasts_rejected(self):
        cutoff = datetime(2025,7,14,8,tzinfo=timezone.utc)
        headers = {'Last-Modified':'Mon, 14 Jul 2025 07:37:57 GMT','ETag':'"abc123"'}
        availability(headers,cutoff)
        for updated in [{'Last-Modified':'Mon, 14 Jul 2025 07:56:00 GMT'},
                        {'Last-Modified':'Tue, 15 Jul 2025 07:37:57 GMT'},
                        {'ETag':'"abc123-2"'}]:
            with self.assertRaises(ValueError):
                availability({**headers,**updated},cutoff)
    def test_forecast_decoder_rejects_wrong_valid_date(self):
        rows = json.loads((ROOT/'outputs/forecast_availability.json').read_text())
        row = next(r for r in rows if r['available'])
        wrong = {**row,'target_utc':'2030-01-01T00:00:00+00:00'}
        with self.assertRaises(ValueError):
            decode_message((ROOT/'raw'/row['file']).read_bytes(),wrong,{})
    def test_decoded_point_matches_full_value_array(self):
        data = pd.read_csv(ROOT/'outputs/daily_data.csv')
        row = data.loc[data.usable].iloc[0]
        message = eccodes.codes_new_from_message((ROOT/'raw'/row['file']).read_bytes())
        try:
            values = eccodes.codes_get_values(message)
            self.assertAlmostEqual(values[int(row.grid_index)]-273.15,row.forecast_temperature_c,places=8)
            point = eccodes.codes_grib_find_nearest(message,40.7794,-73.8803,npoints=1)[0]
            self.assertEqual(int(point['index']),int(row.grid_index))
        finally:
            eccodes.codes_release(message)
    def test_features_ignore_prices_load_and_realized_weather(self):
        a = pd.DataFrame({'delivery_date':['2025-01-01','2025-07-04'],
                          'finalized_price_mwh':[1,2],'load_mw':[100,200],
                          'temperature_c':[-20,40],'forecast_temperature_c':[10,20]})
        b = a.copy()
        for column in ['finalized_price_mwh','load_mw','temperature_c','forecast_temperature_c']:
            b[column] = [-9999,9999]
        np.testing.assert_equal(calendar_features(a)[0],calendar_features(b)[0])
        names = calendar_features(a)[1]
        self.assertEqual(len(names),14)
        self.assertFalse(any('price' in name or 'load' in name for name in names))
    def test_weather_model_inputs_exclude_outcomes_and_unverified_covariates(self):
        frame = pd.read_csv(ROOT/'outputs/test_predictions.csv').iloc[:5].copy()
        models = json.loads((ROOT/'outputs/fitted_models.json').read_text())
        modified = frame.copy()
        modified['finalized_price_mwh'] = -99999
        modified['lagged_price'] = 99999
        modified['load_mw'] = 99999
        modified['temperature_c'] = 99999
        for name in ['calendar','linear','spline']:
            stored = models[name]
            model = PriceModel(name)
            model.coefficients = np.asarray(stored['coefficients'])
            if name != 'calendar':
                model.mean = stored['mean_forecast_c']
                model.scale = stored['scale_forecast_c']
                model.knots = stored['knots_forecast_c']
            np.testing.assert_equal(model.predict(frame),model.predict(modified))
    def test_actual_chronology_and_availability(self):
        data = pd.read_csv(ROOT/'outputs/daily_data.csv')
        self.assertEqual(len(data),1826)
        self.assertFalse(data.delivery_date.duplicated().any())
        usable = data.loc[data.usable]
        self.assertTrue((pd.to_datetime(usable.archive_available_utc,utc=True)<=pd.to_datetime(usable.cutoff_utc,utc=True)-pd.Timedelta(minutes=5)).all())
        self.assertTrue((pd.to_datetime(usable.decoder_valid_utc,utc=True)==pd.to_datetime(usable.target_utc,utc=True)).all())
        train,val,test = [usable.loc[mask] for mask in [usable.year.le(2023),usable.year.eq(2024),usable.year.eq(2025)]]
        self.assertLess(train.delivery_date.max(),val.delivery_date.min())
        self.assertLess(val.delivery_date.max(),test.delivery_date.min())
        predictions = pd.read_csv(ROOT/'outputs/test_predictions.csv')
        self.assertEqual(set(predictions.delivery_date),set(test.delivery_date))
    def test_fitted_transforms_and_selection_use_allowed_years(self):
        data = pd.read_csv(ROOT/'outputs/daily_data.csv')
        fitting = data.loc[data.usable & data.year.le(2024),'forecast_temperature_c']
        training = data.loc[data.usable & data.year.le(2023),'forecast_temperature_c']
        models = json.loads((ROOT/'outputs/fitted_models.json').read_text())
        config = json.loads((ROOT/'outputs/selected_configuration.json').read_text())
        for name in ['linear','spline']:
            self.assertAlmostEqual(models[name]['mean_forecast_c'],float(np.mean(fitting)),places=10)
            self.assertAlmostEqual(models[name]['scale_forecast_c'],float(np.std(fitting)),places=10)
        np.testing.assert_allclose(models['spline']['knots_forecast_c'],np.quantile(fitting,[.25,.5,.75]))
        self.assertAlmostEqual(config['hot_forecast_threshold_c_2021_2023'],float(np.quantile(training,.95)))
        val = pd.read_csv(ROOT/'outputs/validation_metrics.csv').set_index('model')
        expected = min(['linear','spline'],key=lambda name:(val.loc[name,'mae_mwh'],name!='linear'))
        self.assertEqual(expected,config['selected_weather_model'])
    def test_paired_block_bootstrap_handles_missing_dates(self):
        lower,upper = block_interval([10,0,10,10],[1,0,1,1],2,repeats=100)
        self.assertAlmostEqual(lower,10)
        self.assertAlmostEqual(upper,10)
    def test_prediction_scores_independently_recomputed(self):
        predictions = pd.read_csv(ROOT/'outputs/test_predictions.csv')
        scores = pd.read_csv(ROOT/'outputs/test_metrics.csv')
        for name in ['calendar','linear','spline']:
            errors = [float(row.finalized_price_mwh)-float(getattr(row,name)) for row in predictions.itertuples()]
            reported = scores.loc[scores.group_type.eq('overall') & scores.model.eq(name)].iloc[0]
            self.assertAlmostEqual(sum(abs(e) for e in errors)/len(errors),reported.mae_mwh,places=8)
            self.assertAlmostEqual((sum(e*e for e in errors)/len(errors))**.5,reported.rmse_mwh,places=8)
    def test_specification_code_and_data_hashes(self):
        config = json.loads((ROOT/'outputs/selected_configuration.json').read_text())
        for name,digest in config['code_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT/'src'/name).read_bytes()).hexdigest(),digest)
        for name,key in [('daily_data.csv','daily_data_sha256'),('forecast_availability.json','availability_sha256')]:
            self.assertEqual(hashlib.sha256((ROOT/'outputs'/name).read_bytes()).hexdigest(),config[key])
        self.assertEqual(hashlib.sha256((ROOT/'EXPERIMENT.md').read_bytes()).hexdigest(),config['specification_sha256'])

if __name__=='__main__':
    unittest.main()
