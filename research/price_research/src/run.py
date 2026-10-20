"""Fit fixed alternatives, select on 2024, then evaluate finalized 2025 prices."""
import hashlib, json
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from acquire import ROOT
from model import PriceModel
from evaluate import metrics, comparisons, residual_diagnostics, MODELS

OUT = ROOT/'outputs'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def main():
    frozen = json.loads((OUT/'specification_freeze.json').read_text())
    if frozen['sha256']!=digest(ROOT/'EXPERIMENT.md'):
        raise ValueError('Specification changed since freeze')
    if not json.loads((OUT/'data_gate.json').read_text())['passed']:
        raise ValueError('Data gate not passed')
    data = pd.read_csv(OUT/'daily_data.csv')
    data = data.loc[data.usable].copy()
    train, validation = data.loc[data.year.le(2023)], data.loc[data.year.eq(2024)]
    validation_scores = []
    for name in MODELS:
        model = PriceModel(name).fit(train)
        validation_scores.append({'model':name,**metrics(validation.finalized_price_mwh,model.predict(validation))})
    scores = pd.DataFrame(validation_scores)
    scores.to_csv(OUT/'validation_metrics.csv',index=False)
    selected = min(['linear','spline'],key=lambda name:(float(scores.loc[scores.model.eq(name),'mae_mwh'].iloc[0]),name!='linear'))
    hot_threshold = float(train.forecast_temperature_c.quantile(.95))
    # Written before scoring the final-price year; weather model chosen on validation only.
    configuration = {'recorded_utc':datetime.now(timezone.utc).isoformat(),
                     'selected_weather_model':selected,'selection_metric':'2024 MAE $/MWh',
                     'fitting_years':[2021,2022,2023],'validation_year':2024,
                     'final_refit_years':[2021,2022,2023,2024],'evaluation_year':2025,
                     'prior_exposure':'2025 demand data and eight source-feasibility price samples examined; not wholly unseen',
                     'hot_forecast_threshold_c_2021_2023':hot_threshold,
                     'specification_sha256':digest(ROOT/'EXPERIMENT.md'),
                     'daily_data_sha256':digest(OUT/'daily_data.csv'),
                     'availability_sha256':digest(OUT/'forecast_availability.json'),
                     'price_manifest_sha256':digest(OUT/'price_source_manifest.json'),
                     'code_sha256':{path.name:digest(path) for path in sorted((ROOT/'src').glob('*.py'))}}
    write_json(OUT/'selected_configuration.json',configuration)
    if not (OUT/'first_evaluation_configuration.json').exists():
        write_json(OUT/'first_evaluation_configuration.json',configuration)
    fitting, test = data.loc[data.year.le(2024)], data.loc[data.year.eq(2025)]
    predictions = test[['delivery_date','year','month','forecast_temperature_c','finalized_price_mwh']].copy()
    fitted = {}
    for name in MODELS:
        fitted[name] = PriceModel(name).fit(fitting)
        predictions[name] = fitted[name].predict(test)
    predictions['hot_forecast'] = predictions.forecast_temperature_c.ge(hot_threshold)
    predictions['season'] = predictions.month.map({12:'DJF',1:'DJF',2:'DJF',3:'MAM',4:'MAM',5:'MAM',6:'JJA',7:'JJA',8:'JJA',9:'SON',10:'SON',11:'SON'})
    predictions.to_csv(OUT/'test_predictions.csv',index=False)
    write_json(OUT/'fitted_models.json',{name:model.metadata() for name,model in fitted.items()})
    groups = [('overall','all',predictions),('forecast_temperature','hot',predictions.loc[predictions.hot_forecast]),
              ('forecast_temperature','not_hot',predictions.loc[~predictions.hot_forecast])]
    groups += [('month',str(month),group) for month,group in predictions.groupby('month')]
    groups += [('season',season,group) for season,group in predictions.groupby('season')]
    results = []
    for group_type, label, group in groups:
        baseline = metrics(group.finalized_price_mwh,group.calendar)['mae_mwh']
        for name in MODELS:
            score = metrics(group.finalized_price_mwh,group[name])
            results.append({'group_type':group_type,'group':label,'model':name,**score,
                            'improvement_pct':100*(baseline-score['mae_mwh'])/baseline})
    results = pd.DataFrame(results)
    results.to_csv(OUT/'test_metrics.csv',index=False)
    comparisons(predictions).to_csv(OUT/'uncertainty.csv',index=False)
    residual_diagnostics(predictions).to_csv(OUT/'residual_diagnostics.csv',index=False)
    diagnostics = predictions.copy()
    diagnostics['baseline_absolute_error'] = abs(diagnostics.finalized_price_mwh-diagnostics.calendar)
    diagnostics['selected_absolute_error'] = abs(diagnostics.finalized_price_mwh-diagnostics[selected])
    diagnostics['selected_error_improvement'] = diagnostics.baseline_absolute_error-diagnostics.selected_absolute_error
    top = diagnostics.nlargest(10,'baseline_absolute_error')
    top.to_csv(OUT/'ten_largest_baseline_errors.csv',index=False)
    total = float(diagnostics.selected_error_improvement.sum())
    concentration = {'total_absolute_error_improvement':total,'ten_largest_baseline_error_days_improvement':float(top.selected_error_improvement.sum()),
                     'ten_day_share_of_total_improvement':float(top.selected_error_improvement.sum()/total) if abs(total)>1e-12 else None,
                     'diagnostic_only':'Primary evaluation includes every matched day; no outlier deletion or model changes.'}
    write_json(OUT/'gain_concentration.json',concentration)
    temperatures = np.linspace(fitting.forecast_temperature_c.quantile(.01),fitting.forecast_temperature_c.quantile(.99),160)
    curve = pd.DataFrame({'delivery_date':['2024-07-01']*len(temperatures),'forecast_temperature_c':temperatures})
    reference = curve.iloc[[0]].copy()
    reference['forecast_temperature_c'] = 18.0
    for name in ['linear','spline']:
        curve[name+'_relative_mwh'] = fitted[name].predict(curve)-fitted[name].predict(reference)[0]
    curve.to_csv(OUT/'forecast_temperature_response.csv',index=False)
    summary = {'selected_weather_model':selected,'hot_forecast_threshold_c':hot_threshold,
               'matched_2025_days':len(test), 'matched_fitting_days':len(fitting),
               'baseline_mae_mwh':float(results.loc[results.group_type.eq('overall') & results.model.eq('calendar'),'mae_mwh'].iloc[0]),
               'selected_mae_mwh':float(results.loc[results.group_type.eq('overall') & results.model.eq(selected),'mae_mwh'].iloc[0]),
               'selected_improvement_pct':float(results.loc[results.group_type.eq('overall') & results.model.eq(selected),'improvement_pct'].iloc[0]),
               'months_with_selected_improvement':int((results.loc[results.group_type.eq('month') & results.model.eq(selected),'improvement_pct']>0).sum()),
               'price_history_or_trading_tested':False}
    write_json(OUT/'summary.json',summary)
    print('VALIDATION\n',scores.to_string(index=False))
    print('FINAL\n',results.loc[results.group_type.eq('overall')].to_string(index=False))
    print('SUMMARY\n',json.dumps(summary,indent=2))

if __name__=='__main__':
    main()
