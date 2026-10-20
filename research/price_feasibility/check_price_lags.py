"""Check original daily endpoints for proposed lagged-price inputs; no fitting."""
from datetime import datetime,timedelta,timezone
import concurrent.futures,json
from check_sources import ROOT,DATES,ZONE,request

def probe(item):
 delivery,lag=item
 day=datetime.fromisoformat(delivery).date()-timedelta(days=lag)
 cutoff=datetime.combine(datetime.fromisoformat(delivery).date()-timedelta(days=1),datetime.min.time(),ZONE).replace(hour=4).astimezone(timezone.utc)
 url=f'https://mis.nyiso.com/public/csv/damlbmp/{day:%Y%m%d}damlbmp_zone.csv'
 row={'delivery_date':delivery,'lag_days':lag,'lag_delivery_date':str(day),'cutoff_utc':cutoff.isoformat(),'url':url}
 try:
  _,receipt=request(url,method='HEAD');row['receipt']=receipt
 except Exception as e:row['error']=str(e)
 return row
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(probe,[(d,lag) for d in DATES for lag in [1,7]]))
 (ROOT/'outputs/price_lag_probes.json').write_text(json.dumps(rows,indent=2)+'\n')
 print(json.dumps(rows,indent=2))
