"""Gross hypothetical energy-spread payoffs, risk and paired block uncertainty."""
import numpy as np
import pandas as pd

def positions(prediction):
    return np.sign(np.asarray(prediction,dtype=float)).astype(int)

def payoff(side, spread):
    side,spread=np.asarray(side),np.asarray(spread,dtype=float)
    if not np.isin(side,[-1,0,1]).all() or not np.isfinite(spread).all():
        raise ValueError('Invalid fixed one-MWh side or spread')
    return side*spread

def trading_metrics(pnl,side):
    pnl,side=np.asarray(pnl,dtype=float),np.asarray(side)
    active=side!=0
    equity=np.r_[0,np.cumsum(pnl)]
    drawdown=np.maximum.accumulate(equity)-equity
    tail_count=max(1,int(np.ceil(.05*len(pnl))))
    return {'days':len(pnl),'active_trades':int(active.sum()),'virtual_load_days':int((side==1).sum()),
            'virtual_supply_days':int((side==-1).sum()),'flat_days':int((side==0).sum()),
            'total_gross_dollars':float(pnl.sum()),'mean_daily_gross_dollars':float(pnl.mean()),
            'mean_active_trade_dollars':float(pnl[active].mean()) if active.any() else None,
            'win_rate_active':float((pnl[active]>0).mean()) if active.any() else None,
            'zero_payoff_active_trades':int(((pnl==0)&active).sum()),
            'daily_std_dollars':float(pnl.std(ddof=1)), 'best_day_dollars':float(pnl.max()),
            'worst_day_dollars':float(pnl.min()),'fifth_percentile_dollars':float(np.quantile(pnl,.05)),
            'worst_five_percent_mean_dollars':float(np.sort(pnl)[:tail_count].mean()),
            'max_drawdown_dollars':float(drawdown.max())}

def forecast_metrics(actual,prediction):
    error=np.asarray(actual)-np.asarray(prediction)
    return {'spread_mae_mwh':float(np.abs(error).mean()),'spread_rmse_mwh':float(np.sqrt(np.mean(error**2)))}

def block_interval(totals,counts,block,repeats=5000):
    totals,counts=np.asarray(totals),np.asarray(counts)
    if len(totals)!=len(counts) or counts.sum()==0 or np.any(counts<0):raise ValueError('Invalid daily pairs')
    rng=np.random.default_rng(61761);size=len(totals)
    starts=rng.integers(0,size,size=(repeats,int(np.ceil(size/block))))
    indices=((starts[:,:,None]+np.arange(block))%size).reshape(repeats,-1)[:,:size]
    means=totals[indices].sum(axis=1)/counts[indices].sum(axis=1)
    return np.quantile(means,[.025,.975]).tolist()

def uncertainty(frame,selected):
    days=pd.date_range('2025-01-01','2025-12-31').strftime('%Y-%m-%d')
    rows=[]
    for benchmark in ['flat','calendar','always_load','always_supply','training_mean']:
        difference=frame[selected+'_pnl']-frame[benchmark+'_pnl']
        daily=pd.DataFrame({'date':frame.delivery_date,'difference':difference,'count':1}).set_index('date').reindex(days,fill_value=0)
        for block in [7,14,28]:
            lower,upper=block_interval(daily.difference,daily['count'],block)
            rows.append({'selected_weather':selected,'benchmark':benchmark,'block_days':block,
                         'mean_incremental_daily_dollars':float(daily.difference.sum()/daily['count'].sum()),
                         'lower_95_dollars':lower,'upper_95_dollars':upper,'paired_days':int(daily['count'].sum())})
    return pd.DataFrame(rows)
