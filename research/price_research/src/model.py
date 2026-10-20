"""Small calendar baseline and two fixed forecast-temperature alternatives."""
import numpy as np
import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

HOLIDAY_CALENDAR = USFederalHolidayCalendar()
HOLIDAY_CALENDAR.rules = [rule for rule in HOLIDAY_CALENDAR.rules if 'Juneteenth' not in rule.name]

def calendar_features(frame):
    dates = pd.to_datetime(frame.delivery_date)
    weekday = dates.dt.dayofweek.to_numpy()
    phase = 2*np.pi*(dates.dt.dayofyear.to_numpy()-1)/np.where(dates.dt.is_leap_year,366,365)
    columns = [np.ones(len(frame))]
    names = ['intercept']
    for day in range(1,7):
        columns.append((weekday==day).astype(float))
        names.append(f'weekday_{day}')
    for harmonic in range(1,4):
        columns.extend([np.sin(harmonic*phase),np.cos(harmonic*phase)])
        names.extend([f'annual_sin_{harmonic}',f'annual_cos_{harmonic}'])
    holidays = HOLIDAY_CALENDAR.holidays(start='2020-01-01',end='2027-01-01')
    columns.append(dates.isin(holidays).to_numpy().astype(float))
    names.append('fixed_observed_federal_holiday')
    return np.column_stack(columns), names

class PriceModel:
    def __init__(self, kind):
        if kind not in ['calendar','linear','spline']:
            raise ValueError('Unknown predefined model')
        self.kind = kind

    def design(self, frame, fitting=False):
        matrix, names = calendar_features(frame)
        if self.kind != 'calendar':
            temperature = frame.forecast_temperature_c.to_numpy(dtype=float)
            if fitting:
                self.mean = float(temperature.mean())
                self.scale = float(temperature.std())
                if self.scale <= 0:
                    raise ValueError('No temperature variation in fitting rows')
                self.knots = np.quantile(temperature,[.25,.5,.75]).tolist() if self.kind=='spline' else []
            weather = [(temperature-self.mean)/self.scale]
            weather += [np.maximum((temperature-knot)/self.scale,0) for knot in self.knots]
            matrix = np.column_stack([matrix]+weather)
            names += ['forecast_temperature_z'] + [f'forecast_hinge_{i}' for i in range(len(self.knots))]
        return matrix, names

    def fit(self, frame):
        matrix, self.names = self.design(frame, fitting=True)
        self.coefficients, _, rank, singular = np.linalg.lstsq(matrix,frame.finalized_price_mwh.to_numpy(),rcond=None)
        self.rank = int(rank)
        if rank != matrix.shape[1]:
            raise ValueError('Rank-deficient fitting design')
        self.condition_number = float(singular[0]/singular[-1])
        return self

    def predict(self, frame):
        return self.design(frame)[0]@self.coefficients

    def metadata(self):
        return {'kind':self.kind, 'features':self.names, 'coefficients':self.coefficients.tolist(),
                'rank':self.rank, 'condition_number':self.condition_number,
                'mean_forecast_c':self.mean if self.kind!='calendar' else None,
                'scale_forecast_c':self.scale if self.kind!='calendar' else None,
                'knots_forecast_c':self.knots if self.kind!='calendar' else []}
