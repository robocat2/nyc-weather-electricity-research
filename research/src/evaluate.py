"""Paired metrics and dependence-aware daily moving-block uncertainty."""
import numpy as np
import pandas as pd

def metrics(actual,predicted):
    error=np.asarray(actual)-np.asarray(predicted)
    return {'hours':len(error),'mae_mw':float(np.mean(np.abs(error))),'rmse_mw':float(np.sqrt(np.mean(error**2))),'mean_residual_mw':float(np.mean(error))}

def block_interval(daily_difference,daily_counts,block=7,repeats=2000):
    totals=np.asarray(daily_difference);counts=np.asarray(daily_counts)
    if len(totals)!=len(counts) or np.any(counts<0) or counts.sum()==0:raise ValueError('Invalid daily pairs')
    rng=np.random.default_rng(14732);n=len(totals);blocks=int(np.ceil(n/block))
    starts=rng.integers(0,n,size=(repeats,blocks));indices=(starts[:,:,None]+np.arange(block))%n
    indices=indices.reshape(repeats,-1)[:,:n]
    values=totals[indices].sum(axis=1)/counts[indices].sum(axis=1)
    return np.quantile(values,[.025,.975]).tolist()

def uncertainty(predictions):
    p=predictions.copy();p['date']=pd.to_datetime(p.utc,utc=True).dt.tz_convert('America/New_York').dt.strftime('%Y-%m-%d')
    dates=pd.date_range('2025-01-01','2025-12-31').strftime('%Y-%m-%d')
    rows=[]
    for alternative in ['linear','spline']:
        p['difference']=abs(p.load_mw-p.calendar)-abs(p.load_mw-p[alternative])
        d=p.groupby('date').agg(total=('difference','sum'),hours=('difference','count')).reindex(dates,fill_value=0)
        for block in [7,14,28]:
            lower,upper=block_interval(d.total,d.hours,block)
            rows.append({'comparison':f'calendar minus {alternative}','block_days':block,'mean_improvement_mw':float(d.total.sum()/d.hours.sum()),'lower_95_mw':lower,'upper_95_mw':upper,'calendar_days':len(d),'days_with_observations':int(d.hours.gt(0).sum())})
    return pd.DataFrame(rows)

def residual_diagnostics(p):
    x=p.set_index(pd.to_datetime(p.utc,utc=True)).reindex(pd.date_range(pd.to_datetime(p.utc,utc=True).min(),pd.to_datetime(p.utc,utc=True).max(),freq='h'))
    rows=[]
    for name in ['calendar','linear','spline']:
        r=x.load_mw-x[name]
        for lag in [1,24,168]:
            rows.append({'model':name,'lag_hours':lag,'correlation':float(r.corr(r.shift(lag))),'paired_hours':int((r.notna() & r.shift(lag).notna()).sum())})
    return pd.DataFrame(rows)
