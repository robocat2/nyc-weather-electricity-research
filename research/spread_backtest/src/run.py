"""Run the fixed gross spread-signal experiment; no orders, costs or sizing search."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
import pandas as pd
from model import SpreadModel
from evaluate import positions,payoff,trading_metrics,forecast_metrics,uncertainty

ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT.parent
OUT=ROOT/'outputs'
MODELS=['calendar','linear','spline']
STRATEGIES=MODELS+['always_load','always_supply','flat','training_mean']

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write_json(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def prepare():
    source=PARENT/'price_research/outputs/daily_data.csv'
    old=json.loads((PARENT/'price_research/outputs/selected_configuration.json').read_text())
    if digest(source)!=old['daily_data_sha256']:raise ValueError('Verified forecast data changed')
    inventory=PARENT/'trading_feasibility/outputs/spread_label_inventory.csv'
    forecasts=pd.read_csv(source)
    labels=pd.read_csv(inventory)
    for item in json.loads((PARENT/'trading_feasibility/outputs/source_manifest.json').read_text()):
        if digest(PARENT/'trading_feasibility/raw'/item['file'])!=item['sha256']:raise ValueError('RT raw source changed')
    # Carry only the forecast covariate and availability metadata; prices are labels.
    covariates=forecasts[['delivery_date','forecast_temperature_c','archive_available_utc','decoder_issue_utc','decoder_valid_utc']]
    data=labels.merge(covariates,on='delivery_date',how='left',validate='one_to_one')
    if len(data)!=1826 or data.delivery_date.duplicated().any():raise ValueError('Daily grid mismatch')
    if not np.allclose(data.rt_minus_da_mwh,data.rt_integrated_price_mwh-data.finalized_price_mwh):raise ValueError('Spread sign mismatch')
    eligible=data.loc[data.usable_spread_research].copy()
    if len(eligible)!=1809 or not eligible.forecast_temperature_c.notna().all():raise ValueError('Eligible cohort changed')
    if not (pd.to_datetime(eligible.archive_available_utc,utc=True)<=pd.to_datetime(eligible.cutoff_utc,utc=True)-pd.Timedelta(minutes=5)).all():raise ValueError('Late forecast input')
    if not (pd.to_datetime(eligible.decoder_valid_utc,utc=True)==pd.to_datetime(eligible.target_utc,utc=True)).all():raise ValueError('Wrong forecast target')
    eligible['month']=pd.to_datetime(eligible.delivery_date).dt.month
    eligible['season']=eligible.month.map({12:'DJF',1:'DJF',2:'DJF',3:'MAM',4:'MAM',5:'MAM',6:'JJA',7:'JJA',8:'JJA',9:'SON',10:'SON',11:'SON'})
    data.loc[~data.usable_spread_research].to_csv(OUT/'excluded_days.csv',index=False)
    eligible.to_csv(OUT/'eligible_data.csv',index=False)
    write_json(OUT/'source_snapshot.json',{'forecast_data_sha256':digest(source),'spread_inventory_sha256':digest(inventory),
               'rt_source_manifest_sha256':digest(PARENT/'trading_feasibility/outputs/source_manifest.json'),
               'eligible_days':len(eligible),'outcome_days':len(data),'raw_rt_receipts_verified':63})
    return eligible

def strategy_table(data,models,mean_spread):
    result=data[['delivery_date','year','month','season','forecast_temperature_c','rt_minus_da_mwh','finalized_price_mwh','rt_integrated_price_mwh']].copy()
    for name,model in models.items():
        result[name+'_prediction']=model.predict(data)
        result[name+'_side']=positions(result[name+'_prediction'])
    result['always_load_side']=1
    result['always_supply_side']=-1
    result['flat_side']=0
    result['training_mean_side']=int(np.sign(mean_spread))
    for name in STRATEGIES:result[name+'_pnl']=payoff(result[name+'_side'],result.rt_minus_da_mwh)
    return result

def main():
    if digest(ROOT/'EXPERIMENT.md')!=json.loads((OUT/'specification_freeze.json').read_text())['sha256']:raise ValueError('Frozen specification changed')
    data=prepare()
    train=data.loc[data.year.le(2023)];validation=data.loc[data.year.eq(2024)]
    development={name:SpreadModel(name).fit(train) for name in MODELS}
    val=strategy_table(validation,development,float(train.rt_minus_da_mwh.mean()))
    validation_scores=[]
    for name in STRATEGIES:
        row={'strategy':name,**trading_metrics(val[name+'_pnl'],val[name+'_side'])}
        if name in MODELS:row.update(forecast_metrics(val.rt_minus_da_mwh,val[name+'_prediction']))
        validation_scores.append(row)
    validation_scores=pd.DataFrame(validation_scores)
    validation_scores.to_csv(OUT/'validation_metrics.csv',index=False)
    selected=min(['linear','spline'],key=lambda name:(-float(validation_scores.loc[validation_scores.strategy.eq(name),'mean_daily_gross_dollars'].iloc[0]),name!='linear'))
    config={'selected_weather_strategy':selected,'selection':'maximum 2024 mean gross payoff under fixed sign rule; tie linear',
            'recorded_utc':datetime.now(timezone.utc).isoformat(),'training_years':[2021,2022,2023],'validation_year':2024,
            'refit_years':[2021,2022,2023,2024],'evaluation_year':2025,'position_mwh':1,'threshold':0,
            'specification_sha256':digest(ROOT/'EXPERIMENT.md'),'eligible_data_sha256':digest(OUT/'eligible_data.csv'),
            'source_snapshot_sha256':digest(OUT/'source_snapshot.json'),
            'code_sha256':{p.name:digest(p) for p in sorted((ROOT/'src').glob('*.py'))},
            'exposure_disclosure':'2025 examined in earlier demand and day-ahead-price studies; retrospective evaluation, not blind or prospective',
            'fees_uplift_slippage_included':False,'clearing':'assumed one MWh cleared per active signal'}
    write_json(OUT/'selected_configuration.json',config)
    if not (OUT/'first_evaluation_configuration.json').exists():write_json(OUT/'first_evaluation_configuration.json',config)
    fitting=data.loc[data.year.le(2024)];test=data.loc[data.year.eq(2025)]
    fitted={name:SpreadModel(name).fit(fitting) for name in MODELS}
    mean_spread=float(fitting.rt_minus_da_mwh.mean())
    write_json(OUT/'fitted_models.json',{name:model.metadata() for name,model in fitted.items()})
    frame=strategy_table(test,fitted,mean_spread)
    frame.to_csv(OUT/'test_daily_signals.csv',index=False)
    results=[]
    groups=[('overall','all',frame)]+[('month',str(k),g) for k,g in frame.groupby('month')]+[('season',str(k),g) for k,g in frame.groupby('season')]
    for kind,label,group in groups:
        for name in STRATEGIES:
            row={'group_type':kind,'group':label,'strategy':name,**trading_metrics(group[name+'_pnl'],group[name+'_side'])}
            if name in MODELS:row.update(forecast_metrics(group.rt_minus_da_mwh,group[name+'_prediction']))
            results.append(row)
    metrics=pd.DataFrame(results);metrics.to_csv(OUT/'test_metrics.csv',index=False)
    uncertainty(frame,selected).to_csv(OUT/'uncertainty.csv',index=False)
    frame.nlargest(10,selected+'_pnl').to_csv(OUT/'ten_best_days.csv',index=False)
    frame.nsmallest(10,selected+'_pnl').to_csv(OUT/'ten_worst_days.csv',index=False)
    cumulative=frame[['delivery_date']].copy()
    for name in STRATEGIES:cumulative[name+'_cumulative_dollars']=frame[name+'_pnl'].cumsum()
    cumulative.to_csv(OUT/'cumulative_payoff.csv',index=False)
    residual_rows=[]
    regular=frame.set_index('delivery_date').reindex(pd.date_range('2025-01-01','2025-12-31').strftime('%Y-%m-%d'))
    for name in MODELS:
        residual=regular.rt_minus_da_mwh-regular[name+'_prediction']
        for lag in [1,7]:residual_rows.append({'model':name,'lag_days':lag,'correlation':float(residual.corr(residual.shift(lag))),
                                             'pairs':int((residual.notna()&residual.shift(lag).notna()).sum())})
    pd.DataFrame(residual_rows).to_csv(OUT/'residual_diagnostics.csv',index=False)
    overall=metrics.loc[metrics.group_type.eq('overall')].set_index('strategy')
    pnl=float(overall.loc[selected,'total_gross_dollars'])
    primary={'selected_weather_strategy':selected,'evaluation_days':len(frame),'gross_total_dollars':pnl,
             'gross_mean_daily_dollars':float(overall.loc[selected,'mean_daily_gross_dollars']),
             'calendar_gross_total_dollars':float(overall.loc['calendar','total_gross_dollars']),
             'incremental_mean_vs_calendar':float((frame[selected+'_pnl']-frame.calendar_pnl).mean()),
             'training_mean_spread_mwh':mean_spread,'training_mean_side':int(np.sign(mean_spread)),
             'disagreement_days_vs_calendar':int((frame[selected+'_side']!=frame.calendar_side).sum()),
             'top_ten_payoff_dollars':float(frame.nlargest(10,selected+'_pnl')[selected+'_pnl'].sum()),
             'top_ten_share_of_net_total':float(frame.nlargest(10,selected+'_pnl')[selected+'_pnl'].sum()/pnl) if abs(pnl)>1e-12 else None,
             'costs_or_execution_validated':False,'retrospective_exposed_2025':True}
    write_json(OUT/'summary.json',primary)
    print('VALIDATION\n',validation_scores[['strategy','mean_daily_gross_dollars','total_gross_dollars']].to_string(index=False))
    print('FINAL\n',overall[['days','virtual_load_days','virtual_supply_days','total_gross_dollars','mean_daily_gross_dollars','max_drawdown_dollars']].to_string())
    print(json.dumps(primary,indent=2))

if __name__=='__main__':main()
