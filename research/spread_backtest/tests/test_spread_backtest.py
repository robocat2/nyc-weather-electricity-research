"""Verify payoff signs, timing, isolation, risk arithmetic and chronological selection."""
from pathlib import Path
import sys,json,hashlib,unittest
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from evaluate import positions,payoff,trading_metrics,block_interval
from model import SpreadModel

class SpreadTests(unittest.TestCase):
    def test_virtual_payoff_and_position_signs(self):
        np.testing.assert_equal(positions([5,-2,0]),[1,-1,0])
        np.testing.assert_allclose(payoff([1,-1,0],[20,20,20]),[20,-20,0])
        np.testing.assert_allclose(payoff([1,-1],[-30,-30]),[-30,30])
        with self.assertRaises(ValueError):payoff([2],[10])
    def test_drawdown_includes_initial_zero(self):
        result=trading_metrics([-5,2,-4,10],[1,1,-1,1])
        self.assertEqual(result['max_drawdown_dollars'],7)
        self.assertEqual(result['total_gross_dollars'],3)
        self.assertEqual(result['win_rate_active'],.5)
        flat=trading_metrics([0,0],[0,0])
        self.assertIsNone(flat['mean_active_trade_dollars'])
        self.assertEqual(flat['max_drawdown_dollars'],0)
    def test_block_uncertainty_preserves_constant_difference(self):
        lower,upper=block_interval([4,0,4,4],[1,0,1,1],2,repeats=100)
        self.assertEqual(lower,4);self.assertEqual(upper,4)
    def test_no_future_or_unverified_covariate_inputs(self):
        frame=pd.read_csv(ROOT/'outputs/test_daily_signals.csv').iloc[:10].copy()
        other=frame.copy()
        for column in ['rt_minus_da_mwh','finalized_price_mwh','rt_integrated_price_mwh','lagged_price','load_mw','temperature_c']:
            other[column]=99999
        stored=json.loads((ROOT/'outputs/fitted_models.json').read_text())
        for name in ['calendar','linear','spline']:
            model=SpreadModel(name);state=stored[name];model.coefficients=np.asarray(state['coefficients'])
            if name!='calendar':model.mean=state['mean_forecast_c'];model.scale=state['scale_forecast_c'];model.knots=state['knots_forecast_c']
            np.testing.assert_equal(model.predict(frame),model.predict(other))
    def test_same_dates_and_exact_pnl(self):
        x=pd.read_csv(ROOT/'outputs/test_daily_signals.csv')
        self.assertEqual(len(x),362);self.assertFalse(x.delivery_date.duplicated().any())
        self.assertTrue(x.year.eq(2025).all())
        np.testing.assert_allclose(x.rt_minus_da_mwh,x.rt_integrated_price_mwh-x.finalized_price_mwh)
        for name in ['calendar','linear','spline','always_load','always_supply','flat','training_mean']:
            np.testing.assert_allclose(x[name+'_pnl'],x[name+'_side']*x.rt_minus_da_mwh)
        np.testing.assert_allclose(x.always_supply_pnl,-x.always_load_pnl)
    def test_scores_independent_recalculation(self):
        x=pd.read_csv(ROOT/'outputs/test_daily_signals.csv');scores=pd.read_csv(ROOT/'outputs/test_metrics.csv')
        for name in scores.strategy.unique():
            row=scores.loc[scores.group_type.eq('overall')&scores.strategy.eq(name)].iloc[0]
            pnl=[getattr(r,name+'_side')*(r.rt_integrated_price_mwh-r.finalized_price_mwh) for r in x.itertuples()]
            self.assertAlmostEqual(sum(pnl),row.total_gross_dollars,places=8)
            self.assertAlmostEqual(sum(pnl)/len(pnl),row.mean_daily_gross_dollars,places=8)
            equity=peak=drawdown=0
            for value in pnl:equity+=value;peak=max(peak,equity);drawdown=max(drawdown,peak-equity)
            self.assertAlmostEqual(drawdown,row.max_drawdown_dollars,places=8)
    def test_selection_fitting_and_preprocessing_windows(self):
        data=pd.read_csv(ROOT/'outputs/eligible_data.csv');config=json.loads((ROOT/'outputs/selected_configuration.json').read_text())
        train=data.loc[data.year.le(2023)];validation=data.loc[data.year.eq(2024)];test=data.loc[data.year.eq(2025)]
        self.assertLess(train.delivery_date.max(),validation.delivery_date.min());self.assertLess(validation.delivery_date.max(),test.delivery_date.min())
        val=pd.read_csv(ROOT/'outputs/validation_metrics.csv').set_index('strategy')
        expected=min(['linear','spline'],key=lambda name:(-val.loc[name,'mean_daily_gross_dollars'],name!='linear'))
        self.assertEqual(expected,config['selected_weather_strategy'])
        fitting=data.loc[data.year.le(2024),'forecast_temperature_c']
        models=json.loads((ROOT/'outputs/fitted_models.json').read_text())
        for name in ['linear','spline']:
            self.assertAlmostEqual(models[name]['mean_forecast_c'],float(fitting.mean()),places=10)
            self.assertAlmostEqual(models[name]['scale_forecast_c'],float(fitting.std(ddof=0)),places=10)
        np.testing.assert_allclose(models['spline']['knots_forecast_c'],np.quantile(fitting,[.25,.5,.75]))
        summary=json.loads((ROOT/'outputs/summary.json').read_text())
        self.assertAlmostEqual(summary['training_mean_spread_mwh'],float(data.loc[data.year.le(2024),'rt_minus_da_mwh'].mean()))
    def test_every_input_precedes_cutoff(self):
        data=pd.read_csv(ROOT/'outputs/eligible_data.csv')
        self.assertEqual(len(data),1809)
        self.assertTrue((pd.to_datetime(data.archive_available_utc,utc=True)<=pd.to_datetime(data.cutoff_utc,utc=True)-pd.Timedelta(minutes=5)).all())
        self.assertTrue((pd.to_datetime(data.decoder_valid_utc,utc=True)==pd.to_datetime(data.target_utc,utc=True)).all())
    def test_frozen_code_and_specification(self):
        config=json.loads((ROOT/'outputs/selected_configuration.json').read_text())
        for file,digest in config['code_sha256'].items():self.assertEqual(hashlib.sha256((ROOT/'src'/file).read_bytes()).hexdigest(),digest)
        self.assertEqual(hashlib.sha256((ROOT/'EXPERIMENT.md').read_bytes()).hexdigest(),config['specification_sha256'])
        first=json.loads((ROOT/'outputs/first_evaluation_configuration.json').read_text())
        self.assertEqual(first['selected_weather_strategy'],config['selected_weather_strategy'])
        self.assertEqual(first['code_sha256'],config['code_sha256'])

if __name__=='__main__':unittest.main()
