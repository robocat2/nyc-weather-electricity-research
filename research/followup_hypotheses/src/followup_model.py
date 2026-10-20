"""Fixed linear OLS additions; centering/scaling fitted on training rows only."""
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'spread_backtest/src'))
from model import calendar_features
FEATURES={'calendar':[], 'linear':['forecast_temperature_c'],
 'trajectory1':['forecast_temperature_c','change1_c'],
 'trajectory2':['forecast_temperature_c','change1_c','change2_c'],
 'revision':['forecast_temperature_c','revision_c']}
class FollowupModel:
 def __init__(self,name):self.name=name;self.features=FEATURES[name]
 def design(self,frame,fit=False):
  x,names=calendar_features(frame)
  if self.features:
   weather=frame[self.features].to_numpy(float)
   if fit:self.mean=weather.mean(0);self.scale=weather.std(0)
   if not np.isfinite(weather).all() or np.any(self.scale<=0):raise ValueError('Invalid covariates')
   x=np.column_stack([x,(weather-self.mean)/self.scale]);names+=self.features
  self.names=names
  return x
 def fit(self,frame):
  x=self.design(frame,True);self.coef,_,rank,s=np.linalg.lstsq(x,frame.rt_minus_da_mwh.to_numpy(),rcond=None)
  if rank!=x.shape[1]:raise ValueError('Rank deficient')
  self.rank=int(rank);self.condition=float(s[0]/s[-1]);return self
 def predict(self,frame):return self.design(frame)@self.coef
 def metadata(self):return {'features':self.names,'coef':self.coef.tolist(),'mean':self.mean.tolist() if self.features else [],'scale':self.scale.tolist() if self.features else [],'rank':self.rank,'condition_number':self.condition}
