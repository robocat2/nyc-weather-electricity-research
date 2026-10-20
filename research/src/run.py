"""Run the frozen experiment in order; cache sources first with acquire.py --full."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
import pandas as pd
from prepare import prepare,ROOT
from models import DemandModel
from evaluate import metrics,uncertainty,residual_diagnostics
OUT=ROOT/'outputs'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write_json(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def main():
    frozen=json.loads((OUT/'specification_freeze.json').read_text())
    if frozen['sha256']!=digest(ROOT/'EXPERIMENT.md'):raise ValueError('Specification changed after freeze')
    data,coverage=prepare()
    annual=coverage.groupby('year')[['expected_hours','load_hours','weather_hours','joined_hours']].sum().reset_index()
    annual['coverage']=annual.joined_hours/annual.expected_hours
    annual.to_csv(OUT/'annual_coverage.csv',index=False)
    usable=data.loc[data.usable].copy()
    if len(annual)!=5 or annual.coverage.min()<.98 or coverage.coverage.min()<.90:raise ValueError('Feasibility gate failed')
    if not (coverage.load_hours==coverage.expected_hours).all():raise ValueError('Missing load hours')
    data.loc[~data.usable].to_csv(OUT/'excluded_hours.csv',index=False)
    missing=data.loc[~data.usable,['utc']].copy()
    missing['run']=(missing.utc.diff()!=pd.Timedelta(hours=1)).cumsum()
    runs=missing.groupby('run').agg(start_utc=('utc','min'),end_utc=('utc','max'),hours=('utc','size')).sort_values('hours',ascending=False)
    runs.to_csv(OUT/'missing_runs.csv',index=False)
    write_json(OUT/'feasibility.json',{'passed':True,'matched_hours':len(usable),'expected_hours':len(data),'excluded_hours':int((~data.usable).sum()),'minimum_annual_coverage':float(annual.coverage.min()),'minimum_monthly_coverage':float(coverage.coverage.min()),'longest_missing_run_hours':int(runs.hours.max()),'load_duplicate_utc_hours':0,'weather_duplicate_utc_hours':0})
    train=usable.loc[usable.year.le(2023)];val=usable.loc[usable.year.eq(2024)]
    hot=float(train.temperature_c.quantile(.95));validation=[];candidates={}
    for name,kind,knots in [('calendar','calendar',0),('linear','linear',0),('spline_3','spline',3),('spline_5','spline',5)]:
        model=DemandModel(kind,knots).fit(train);score=metrics(val.load_mw,model.predict(val))
        validation.append({'model':name,**score});candidates[name]=score['mae_mw']
    pd.DataFrame(validation).to_csv(OUT/'validation_metrics.csv',index=False)
    chosen=min([3,5],key=lambda k:(candidates[f'spline_{k}'],k))
    # This artifact is written before accessing final outcomes for model evaluation.
    write_json(OUT/'selected_configuration.json',{'written_utc':datetime.now(timezone.utc).isoformat(),'training_years':[2021,2022,2023],'validation_year':2024,'final_evaluation_year':2025,'selected_spline_knots':chosen,'hot_threshold_c_from_2021_2023':hot,'refit_years':[2021,2022,2023,2024],'selection_metric':'2024 MAE MW','specification_sha256':digest(ROOT/'EXPERIMENT.md'),'source_manifest_sha256':digest(ROOT/'raw/manifest.json'),'code_sha256':{p.name:digest(p) for p in sorted((ROOT/'src').glob('*.py'))}})
    fitting=usable.loc[usable.year.le(2024)];test=usable.loc[usable.year.eq(2025)]
    predictions=test[['utc','load_mw','temperature_c','year','month']].copy()
    finalmodels={}
    for name,kind,knots in [('calendar','calendar',0),('linear','linear',0),('spline','spline',chosen)]:
        model=DemandModel(kind,knots).fit(fitting);predictions[name]=model.predict(test);finalmodels[name]=model
    write_json(OUT/'fitted_models.json',{k:v.metadata() for k,v in finalmodels.items()})
    predictions['hot']=predictions.temperature_c.ge(hot)
    predictions['season']=predictions.month.map({12:'DJF',1:'DJF',2:'DJF',3:'MAM',4:'MAM',5:'MAM',6:'JJA',7:'JJA',8:'JJA',9:'SON',10:'SON',11:'SON'})
    predictions.to_csv(OUT/'test_predictions.csv',index=False)
    rows=[]
    groups=[('overall','all',predictions),('temperature','hot',predictions.loc[predictions.hot]),('temperature','not_hot',predictions.loc[~predictions.hot])]
    groups += [('month',str(k),g) for k,g in predictions.groupby('month')]+[('season',str(k),g) for k,g in predictions.groupby('season')]
    for kind,label,g in groups:
        base=metrics(g.load_mw,g.calendar)['mae_mw']
        for name in finalmodels:
            score=metrics(g.load_mw,g[name]);rows.append({'group_type':kind,'group':label,'model':name,**score,'mae_improvement_pct':100*(base-score['mae_mw'])/base})
    scores=pd.DataFrame(rows);scores.to_csv(OUT/'test_metrics.csv',index=False)
    uncertainty(predictions).to_csv(OUT/'uncertainty.csv',index=False)
    residual_diagnostics(predictions).to_csv(OUT/'residual_diagnostics.csv',index=False)
    # Hold a common fixed calendar row and express temperature effect relative to 18 C.
    temperatures=np.linspace(fitting.temperature_c.quantile(.01),fitting.temperature_c.quantile(.99),160)
    curve=pd.DataFrame({'utc':pd.to_datetime(['2024-07-01T16:00:00Z']*len(temperatures),utc=True),'temperature_c':temperatures})
    reference=curve.iloc[[0]].copy();reference['temperature_c']=18.0
    for name in ['linear','spline']:curve[name+'_relative_mw']=finalmodels[name].predict(curve)-finalmodels[name].predict(reference)[0]
    curve.to_csv(OUT/'temperature_response.csv',index=False)
    print('FEASIBILITY',json.loads((OUT/'feasibility.json').read_text()))
    print('VALIDATION\n',pd.DataFrame(validation).to_string(index=False))
    print('FINAL\n',scores.loc[scores.group_type.eq('overall')].to_string(index=False))
    print('UNCERTAINTY\n',pd.read_csv(OUT/'uncertainty.csv').to_string(index=False))
if __name__=='__main__':main()
