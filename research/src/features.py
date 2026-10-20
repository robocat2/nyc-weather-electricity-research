"""Fixed calendar controls and fitting-sample-only temperature transforms."""
import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

def calendar_matrix(data):
    local=pd.to_datetime(data.utc,utc=True).dt.tz_convert('America/New_York')
    hour=local.dt.hour.to_numpy();how=(local.dt.dayofweek*24+local.dt.hour).to_numpy()
    columns=[np.ones(len(data))];names=['intercept']
    for k in range(1,168):columns.append((how==k).astype(float));names.append(f'hour_of_week_{k}')
    # Fraction of the local calendar year handles leap years without a seasonal jump.
    day=local.dt.dayofyear.to_numpy()-1+hour/24
    days=np.where(local.dt.is_leap_year,366,365);phase=2*np.pi*day/days
    for k in range(1,4):
        columns.extend([np.sin(k*phase),np.cos(k*phase)]);names.extend([f'annual_sin_{k}',f'annual_cos_{k}'])
    for h in range(1,24):
        columns.extend([(hour==h)*np.sin(phase),(hour==h)*np.cos(phase)])
        names.extend([f'hour_{h}_annual_sin',f'hour_{h}_annual_cos'])
    dates=local.dt.tz_localize(None).dt.normalize()
    holidays=USFederalHolidayCalendar().holidays(start='2020-01-01',end='2027-01-01')
    columns.append(dates.isin(holidays).to_numpy().astype(float));names.append('federal_observed_holiday')
    return np.column_stack(columns),names

class TemperatureTransform:
    def __init__(self,knots=0):self.n_knots=knots
    def fit(self,temperature):
        t=np.asarray(temperature,dtype=float)
        self.mean=float(t.mean());self.scale=float(t.std())
        if not self.scale>0:raise ValueError('Constant fitting temperature')
        self.knots_c=np.quantile(t,[.25,.5,.75] if self.n_knots==3 else [.1,.25,.5,.75,.9]).tolist() if self.n_knots else []
        return self
    def transform(self,temperature):
        t=np.asarray(temperature,dtype=float);z=(t-self.mean)/self.scale
        return np.column_stack([z]+[np.maximum((t-k)/self.scale,0) for k in self.knots_c])
    def metadata(self):return {'mean_c':self.mean,'scale_c':self.scale,'knots_c':self.knots_c}
