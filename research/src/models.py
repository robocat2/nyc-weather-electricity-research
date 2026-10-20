"""Ordinary least squares using NumPy SVD; no preprocessing on evaluation rows."""
import numpy as np
from features import calendar_matrix, TemperatureTransform
class DemandModel:
    def __init__(self,kind,knots=0):self.kind=kind;self.knots=knots
    def matrix(self,data,fit=False):
        x,names=calendar_matrix(data)
        if self.kind!='calendar':
            if fit:self.temperature=TemperatureTransform(self.knots).fit(data.temperature_c)
            x=np.column_stack([x,self.temperature.transform(data.temperature_c)])
            names+=['temperature_z']+[f'temperature_hinge_{i}' for i in range(self.knots)]
        return x,names
    def fit(self,data):
        x,self.names=self.matrix(data,fit=True)
        self.coefficients,_,rank,singular=np.linalg.lstsq(x,data.load_mw.to_numpy(),rcond=None)
        self.rank=int(rank);self.condition_number=float(singular[0]/singular[-1])
        if rank!=x.shape[1]:raise ValueError('Rank deficient model')
        return self
    def predict(self,data):return self.matrix(data)[0]@self.coefficients
    def metadata(self):
        return {'kind':self.kind,'knot_count':self.knots,'features':self.names,'coefficients':self.coefficients.tolist(),'rank':self.rank,'condition_number':self.condition_number,'temperature_transform':self.temperature.metadata() if self.kind!='calendar' else None}
