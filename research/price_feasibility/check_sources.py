"""Bounded source/timing probes only. No fitting, forecasts, or realized-weather inputs."""
from pathlib import Path
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
from email.utils import parsedate_to_datetime
import concurrent.futures,csv,hashlib,io,json,struct,urllib.request,zipfile
ROOT=Path(__file__).resolve().parent
DATES=['2021-01-15','2021-07-15','2023-01-15','2023-07-15','2024-03-10','2024-11-03','2025-01-15','2025-07-15']
ZONE=ZoneInfo('America/New_York')
def request(url,method='GET',headers=None):
 req=urllib.request.Request(url,method=method,headers={'User-Agent':'NYCPriceFeasibility/1.0',**(headers or {})})
 with urllib.request.urlopen(req,timeout=60) as response:
  meta={'url':url,'http_status':response.status,'headers':dict(response.headers.items()),'checked_utc':datetime.now(timezone.utc).isoformat()}
  if method=='HEAD':return b'',meta
  if headers and 'Range' in headers and response.status!=206:raise ValueError('Server ignored byte range; full download avoided')
  data=response.read(3_000_001) if headers and 'Range' in headers else response.read()
  if headers and 'Range' in headers and len(data)>3_000_000:raise ValueError('Unexpectedly large GRIB temperature message')
  return data,meta

def retain(name,data,meta):
 (ROOT/'raw'/name).write_bytes(data);meta['file']=name;meta['sha256']=hashlib.sha256(data).hexdigest();meta['bytes']=len(data)
 (ROOT/'raw'/(name+'.receipt.json')).write_text(json.dumps(meta,indent=2)+'\n')

def grib_metadata(data):
 if data[:4]!=b'GRIB' or data[7]!=2 or data[-4:]!=b'7777':raise ValueError('Not complete GRIB2 message')
 offset=16;result={'grib_edition':2}
 while offset<len(data)-4:
  length=int.from_bytes(data[offset:offset+4],'big');s=data[offset:offset+length]
  if length<5:raise ValueError('Invalid GRIB section')
  if s[4]==1:
   result['initialization_utc']=datetime(int.from_bytes(s[12:14],'big'),s[14],s[15],s[16],s[17],s[18],tzinfo=timezone.utc).isoformat()
  if s[4]==4:
   result.update(product_template=int.from_bytes(s[7:9],'big'),parameter_category=s[9],parameter_number=s[10],forecast_time_unit=s[17],forecast_lead=int.from_bytes(s[18:22],'big'),first_surface_type=s[22],first_surface_scale=s[23],first_surface_value=int.from_bytes(s[24:28],'big'))
  offset+=length
 return result

def weather_probe(delivery):
 target=datetime.fromisoformat(delivery).replace(hour=18,tzinfo=ZONE)
 previous=target.date()-timedelta(days=1)
 cutoff=datetime.combine(previous,datetime.min.time(),ZONE).replace(hour=4).astimezone(timezone.utc)
 cycle=datetime.combine(previous,datetime.min.time(),timezone.utc).replace(hour=6)
 lead=int((target.astimezone(timezone.utc)-cycle).total_seconds()/3600)
 key=f'hrrr.{previous:%Y%m%d}/conus/hrrr.t06z.wrfsfcf{lead:02}.grib2'
 url='https://noaa-hrrr-bdp-pds.s3.amazonaws.com/'+key
 row={'delivery_date':delivery,'cutoff_utc':cutoff.isoformat(),'target_start_utc':target.astimezone(timezone.utc).isoformat(),'elapsed_prediction_horizon_hours':(target.astimezone(timezone.utc)-cutoff).total_seconds()/3600,'cycle_utc':cycle.isoformat(),'lead_hours':lead,'grib_url':url}
 try:
  _,head=request(url,method='HEAD');(ROOT/'raw'/f'weather_{delivery}_head.json').write_text(json.dumps(head,indent=2)+'\n')
  headers={k.lower():v for k,v in head['headers'].items()};modified=parsedate_to_datetime(headers['last-modified'])
  row.update(object_last_modified_utc=modified.isoformat(),object_before_cutoff=modified<=cutoff,object_bytes=int(headers['content-length']),minutes_before_cutoff=(cutoff-modified).total_seconds()/60)
  idx,meta=request(url+'.idx');retain(f'weather_{delivery}.idx',idx,meta)
  lines=idx.decode().splitlines();position=next(i for i,line in enumerate(lines) if ':TMP:2 m above ground:' in line)
  entry=lines[position].split(':');start=int(entry[1]);end=int(lines[position+1].split(':')[1])-1
  row['temperature_index_entry']=lines[position]
  data,meta=request(url,headers={'Range':f'bytes={start}-{end}'})
  retain(f'weather_{delivery}_temperature.grib2',data,meta)
  details=grib_metadata(data);row.update(details)
  row['forecast_metadata_matches']=details['initialization_utc']==cycle.isoformat() and details['forecast_lead']==lead and details['forecast_time_unit']==1 and details['parameter_category']==0 and details['parameter_number']==0 and details['first_surface_type']==103 and details['first_surface_scale']==0 and details['first_surface_value']==2
 except Exception as e:row['error']=str(e)
 return row

def price_probe(delivery):
 y,m=delivery[:4],delivery[5:7]
 url=f'https://mis.nyiso.com/public/csv/damlbmp/{y}{m}01damlbmp_zone_csv.zip'
 row={'delivery_date':delivery,'url':url}
 try:
  data,meta=request(url);retain(f'prices_{y}{m}.zip',data,meta)
  with zipfile.ZipFile(io.BytesIO(data)) as z:
   name=delivery.replace('-','')+'damlbmp_zone.csv';content=z.read(name);retain(f'price_{delivery}.csv',content,{'url':url+'#'+name,'checked_utc':datetime.now(timezone.utc).isoformat()})
   allrows=list(csv.DictReader(io.StringIO(content.decode('utf-8-sig'))));nyc=[r for r in allrows if r.get('Name')=='N.Y.C.' and r.get('PTID')=='61761']
  row.update(columns=list(allrows[0]),nyc_hourly_rows=len(nyc),hour_18_rows=sum(datetime.strptime(r['Time Stamp'],'%m/%d/%Y %H:%M').hour==18 for r in nyc),nyc_timestamp_unique=len({r['Time Stamp'] for r in nyc})==len(nyc),numeric_prices=all(isinstance(float(r['LBMP ($/MWHr)']),float) for r in nyc),publication_timestamp_column=any(any(w in k.lower() for w in ['publish','issued','version','revision']) for k in allrows[0]))
  _,head=request(f'https://mis.nyiso.com/public/csv/damlbmp/{delivery.replace("-","")}damlbmp_zone.csv',method='HEAD')
  (ROOT/'raw'/f'price_{delivery}_head.json').write_text(json.dumps(head,indent=2)+'\n')
  row['daily_last_modified']=next((v for k,v in head['headers'].items() if k.lower()=='last-modified'),None)
 except Exception as e:row['error']=str(e)
 return row

def main():
 # This sample is frozen in the source code; no date selection based on price values.
 for kind,function in [('weather',weather_probe),('price',price_probe)]:
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(function,DATES))
  (ROOT/'outputs'/f'{kind}_probes.json').write_text(json.dumps(rows,indent=2)+'\n')
  print(kind,json.dumps(rows,indent=2),flush=True)
 # Authoritative public pages, including the replacement for the retired correction logs.
 for name,url in [('price_index.html','https://mis.nyiso.com/public/P-2Alist.htm'),('correction_index.html','https://mis.nyiso.com/public/P-29list.htm'),('announcements_index.html','https://mis.nyiso.com/public/P-25list.htm'),('dayahead_manual.pdf','https://www.nyiso.com/documents/20142/2923301/dayahd_schd_mnl.pdf'),('additional_pricing_rules.pdf','https://www.nyiso.com/documents/20142/25467833/Additional-Pricing-Rules.pdf'),('announcements_202501.zip','https://mis.nyiso.com/public/csv/OperMessages/20250101OperMessages_csv.zip'),('announcements_202507.zip','https://mis.nyiso.com/public/csv/OperMessages/20250701OperMessages_csv.zip')]:
  try:data,meta=request(url);retain(name,data,meta);print(name,len(data),flush=True)
  except Exception as e:print(name,str(e),flush=True)
if __name__=='__main__':main()
