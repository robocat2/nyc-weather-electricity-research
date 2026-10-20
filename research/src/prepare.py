"""Schema-checked NYISO/NOAA ingestion, explicit DST offsets, no imputation."""
from pathlib import Path
import json, zipfile
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
def load_frame(frame):
    required={'Time Stamp','Time Zone','Name','PTID','Integrated Load'}
    if not required.issubset(frame): raise ValueError('NYISO schema changed')
    x=frame.loc[frame.PTID.eq(61761)].copy()
    if not x.Name.eq('N.Y.C.').all(): raise ValueError('Zone J identity mismatch')
    if not x['Time Zone'].isin(['EST','EDT']).all(): raise ValueError('Unknown timezone')
    naive=pd.to_datetime(x['Time Stamp'],format='%m/%d/%Y %H:%M:%S')
    x['utc']=pd.to_datetime(naive+pd.to_timedelta(x['Time Zone'].map({'EST':5,'EDT':4}),unit='h'),utc=True)
    local=x.utc.dt.tz_convert('America/New_York')
    if not np.array_equal(local.dt.tz_localize(None).values,naive.values): raise ValueError('DST label inconsistent')
    if not x.utc.dt.minute.eq(0).all(): raise ValueError('Nonhourly NYISO timestamp')
    x['load_mw']=pd.to_numeric(x['Integrated Load'],errors='raise')
    if not np.isfinite(x.load_mw).all() or not x.load_mw.gt(0).all(): raise ValueError('Invalid load')
    return x[['utc','load_mw']]
def weather_frame(x):
    if not x.STATION.eq('USW00014732').all(): raise ValueError('Wrong weather station')
    x=x.copy();x['utc']=pd.to_datetime(x.DATE,utc=True)
    # Six atmospheric variables have letter QC failure flags; retain only blank or legacy-good 1.
    quality=x.temperature_Quality_Code.fillna('').astype(str).str.strip()
    usable=x.temperature.notna() & x.temperature.between(-60,60) & (quality.isin(['','1']) | (quality.eq('5') & x.temperature_Source_Code.astype(str).eq('343'))) & x.temperature_Report_Type.isin(['FM15','FM12'])
    x=x.loc[usable].copy();x['hour']=x.utc.dt.floor('h')
    # Routine METAR first, SYNOP only when no routine METAR exists in that hour.
    x['priority']=x.temperature_Report_Type.map({'FM15':0,'FM12':1})
    x=x.sort_values(['hour','priority','utc']).drop_duplicates('hour',keep='first')
    return x.rename(columns={'hour':'hour_utc','temperature':'temperature_c'})[['hour_utc','temperature_c','utc','temperature_Report_Type']].rename(columns={'hour_utc':'utc','utc':'weather_report_utc'})
def prepare():
    loads=[];weather=[];weather_quality=[]
    for path in sorted((ROOT/'raw').glob('load_*.zip')):
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                if name.endswith('.csv'):loads.append(load_frame(pd.read_csv(z.open(name))))
    for path in sorted((ROOT/'raw').glob('weather_*.psv')):
        x=pd.read_csv(path,sep='|',usecols=['STATION','DATE','temperature','temperature_Quality_Code','temperature_Report_Type','temperature_Source_Code'],dtype={'temperature_Quality_Code':str,'temperature_Source_Code':str})
        weather_quality.append({'file':path.name,'reports':len(x),'quality_codes':x.temperature_Quality_Code.fillna('blank').value_counts().to_dict(),'report_types':x.temperature_Report_Type.value_counts().to_dict()})
        weather.append(weather_frame(x))
    l=pd.concat(loads).sort_values('utc');w=pd.concat(weather).sort_values('utc')
    if l.utc.duplicated().any() or w.utc.duplicated().any():raise ValueError('Duplicate UTC hour')
    # Keep only complete local calendar years 2021–2025; NOAA year files are UTC.
    grid=pd.DataFrame({'utc':pd.date_range('2021-01-01','2026-01-01',freq='h',tz='America/New_York',inclusive='left').tz_convert('UTC')})
    data=grid.merge(l,on='utc',how='left',validate='1:1').merge(w,on='utc',how='left',validate='1:1')
    local=data.utc.dt.tz_convert('America/New_York');data['local_time']=local.astype(str);data['year']=local.dt.year;data['month']=local.dt.month
    data['usable']=data[['load_mw','temperature_c']].notna().all(axis=1)
    summary=data.groupby(['year','month']).agg(expected_hours=('utc','size'),load_hours=('load_mw','count'),weather_hours=('temperature_c','count'),joined_hours=('usable','sum')).reset_index()
    summary['coverage']=summary.joined_hours/summary.expected_hours
    summary.to_csv(ROOT/'outputs/coverage.csv',index=False)
    (ROOT/'outputs/weather_quality.json').write_text(json.dumps(weather_quality,indent=2)+'\n')
    data.to_csv(ROOT/'outputs/hourly_data.csv',index=False)
    return data,summary
if __name__=='__main__':
    _,s=prepare();print(s.to_string(index=False))
