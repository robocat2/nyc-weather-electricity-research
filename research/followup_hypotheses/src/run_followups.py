"""Fixed exploratory comparisons; preserve each family's matched benchmarks."""
from pathlib import Path
import argparse,sys,json,hashlib
from datetime import datetime,timezone
import numpy as np
import pandas as pd
from prepare_followups import prepare,ROOT,O,digest
from followup_model import FollowupModel
from evaluate import trading_metrics,forecast_metrics,block_interval
VARIANTS={'trajectory':['trajectory1','trajectory2'],'revision':['revision']}
def save(path,obj):path.write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def table(data,models,mean):
 frame=data.copy()
 for name,model in models.items():frame[name+'_prediction']=model.predict(data);frame[name+'_side']=np.sign(frame[name+'_prediction']).astype(int)
 for name,side in [('always_load',1),('always_supply',-1),('flat',0),('training_mean',int(np.sign(mean)))]:frame[name+'_side']=side
 for name in list(models)+['always_load','always_supply','flat','training_mean']:frame[name+'_pnl']=frame[name+'_side']*frame.rt_minus_da_mwh
 return frame
def main(family):
 if digest(ROOT/'EXPERIMENT.md')!=json.loads((O/'specification_freeze.json').read_text())['sha256']:raise ValueError('Specification changed')
 data=prepare(family);out=O/family;names=['calendar','linear']+VARIANTS[family]
 train=data[data.year<=2023];validation=data[data.year==2024]
 development={n:FollowupModel(n).fit(train) for n in names};val=table(validation,development,train.rt_minus_da_mwh.mean())
 strategies=names+['always_load','always_supply','flat','training_mean']
 v=pd.DataFrame([{'strategy':n,**trading_metrics(val[n+'_pnl'],val[n+'_side'])} for n in strategies]);v.to_csv(out/'validation_metrics.csv',index=False)
 selected=min(VARIANTS[family],key=lambda n:(-float(v.set_index('strategy').loc[n,'mean_daily_gross_dollars']),n))
 cfg={'family':family,'selected':selected,'recorded_utc':datetime.now(timezone.utc).isoformat(),'specification_sha256':digest(ROOT/'EXPERIMENT.md'),'source_gate_sha256':digest(out/'data_gate.json'),'code_sha256':{p.name:digest(p) for p in sorted((ROOT/'src').glob('*.py'))},'evaluation_exposure':'2025 and 2024 examined previously; exploratory follow-up','helpers_sha256':{str(p.relative_to(ROOT.parent)):digest(p) for p in [ROOT.parent/'spread_backtest/src/model.py',ROOT.parent/'spread_backtest/src/evaluate.py',ROOT.parent/'price_research/src/prepare.py',ROOT.parent/'price_research/src/acquire.py']}}
 save(out/'configuration.json',cfg)
 if not (out/'first_evaluation_configuration.json').exists():save(out/'first_evaluation_configuration.json',cfg)
 fitting=data[data.year<=2024];test=data[data.year==2025];models={n:FollowupModel(n).fit(fitting) for n in names}
 save(out/'fitted_models.json',{n:m.metadata() for n,m in models.items()})
 frame=table(test,models,fitting.rt_minus_da_mwh.mean());frame.to_csv(out/'daily_signals.csv',index=False)
 rows=[]
 for group,label,subset in [('overall','all',frame)]+[('month',str(k),g) for k,g in frame.groupby('month')]:
  for n in strategies:
   r={'group_type':group,'group':label,'strategy':n,**trading_metrics(subset[n+'_pnl'],subset[n+'_side'])}
   if n in names:r.update(forecast_metrics(subset.rt_minus_da_mwh,subset[n+'_prediction']))
   rows.append(r)
 metrics=pd.DataFrame(rows);metrics.to_csv(out/'test_metrics.csv',index=False)
 intervals=[]
 for bench in ['linear','calendar','always_load','flat']:
  daily=pd.DataFrame({'date':frame.delivery_date,'difference':frame[selected+'_pnl']-frame[bench+'_pnl'],'count':1}).set_index('date').reindex(pd.date_range('2025-01-01','2025-12-31').strftime('%Y-%m-%d'),fill_value=0)
  for block in [7,14,28]:
   low,high=block_interval(daily.difference,daily['count'],block)
   intervals.append({'selected':selected,'benchmark':bench,'block_days':block,'mean_increment':float(daily.difference.sum()/daily['count'].sum()),'lower_95':low,'upper_95':high})
 pd.DataFrame(intervals).to_csv(out/'uncertainty.csv',index=False)
 overall=metrics[metrics.group_type=='overall'].set_index('strategy');best=frame.loc[frame[selected+'_pnl'].idxmax()]
 summary={'family':family,'selected':selected,'test_days':len(frame),'gross_total':float(frame[selected+'_pnl'].sum()),'linear_total':float(frame.linear_pnl.sum()),'always_load_total':float(frame.always_load_pnl.sum()),'best_date':best.delivery_date,'best_payoff':float(best[selected+'_pnl']),'rest_payoff':float(frame[selected+'_pnl'].sum()-best[selected+'_pnl']),'positive_months':int((frame.groupby('month')[selected+'_pnl'].sum()>0).sum()),'exploratory':True,'costs_or_fills_tested':False}
 save(out/'summary.json',summary);print(json.dumps(summary,indent=2));print(overall[['total_gross_dollars','max_drawdown_dollars']].to_string())
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--family',choices=list(VARIANTS),required=True);main(parser.parse_args().family)
