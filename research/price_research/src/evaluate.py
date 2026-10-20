"""Paired daily error comparison for the predefined finalized-price task."""
import numpy as np
import pandas as pd

MODELS = ['calendar','linear','spline']

def metrics(actual, prediction):
    error = np.asarray(actual)-np.asarray(prediction)
    return {'days':len(error), 'mae_mwh':float(np.mean(np.abs(error))),
            'rmse_mwh':float(np.sqrt(np.mean(error**2))), 'mean_residual_mwh':float(error.mean())}

def block_interval(differences, counts, block_days, repeats=5000):
    differences, counts = np.asarray(differences), np.asarray(counts)
    if len(counts)!=len(differences) or counts.sum()==0 or np.any(counts<0):
        raise ValueError('Invalid paired daily totals/counts')
    rng = np.random.default_rng(61761)
    size = len(differences)
    starts = rng.integers(0,size,size=(repeats,int(np.ceil(size/block_days))))
    indices = ((starts[:,:,None]+np.arange(block_days)) % size).reshape(repeats,-1)[:,:size]
    sampled = differences[indices].sum(axis=1)/counts[indices].sum(axis=1)
    return np.quantile(sampled,[.025,.975]).tolist()

def comparisons(predictions):
    dates = pd.date_range('2025-01-01','2025-12-31').strftime('%Y-%m-%d')
    rows = []
    for name in ['linear','spline']:
        difference = np.abs(predictions.finalized_price_mwh-predictions.calendar)-np.abs(predictions.finalized_price_mwh-predictions[name])
        pairs = pd.DataFrame({'date':predictions.delivery_date, 'difference':difference, 'count':1}).set_index('date').reindex(dates,fill_value=0)
        for block in [7,14,28]:
            lower, upper = block_interval(pairs.difference,pairs['count'],block)
            rows.append({'weather_model':name, 'block_days':block,
                         'improvement_mwh':float(pairs.difference.sum()/pairs['count'].sum()),
                         'lower_95_mwh':lower, 'upper_95_mwh':upper,
                         'expected_calendar_days':len(pairs), 'paired_days':int(pairs['count'].sum())})
    return pd.DataFrame(rows)

def residual_diagnostics(predictions):
    days = pd.date_range('2025-01-01','2025-12-31').strftime('%Y-%m-%d')
    frame = predictions.set_index('delivery_date').reindex(days)
    rows = []
    for name in MODELS:
        residual = frame.finalized_price_mwh-frame[name]
        for lag in [1,7]:
            rows.append({'model':name,'lag_days':lag,'correlation':float(residual.corr(residual.shift(lag))),
                         'paired_days':int((residual.notna() & residual.shift(lag).notna()).sum())})
    return pd.DataFrame(rows)
