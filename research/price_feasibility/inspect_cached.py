"""Recompute data-format and forecast checks from cached source bytes."""
from pathlib import Path
from datetime import datetime
import csv,io,json,re,zipfile
from check_sources import ROOT,DATES,grib_metadata

def main():
 weather=json.loads((ROOT/'outputs/weather_probes.json').read_text());prices=json.loads((ROOT/'outputs/price_probes.json').read_text())
 for row in weather:
  details=grib_metadata((ROOT/'raw'/f"weather_{row['delivery_date']}_temperature.grib2").read_bytes());row.update(details)
  assert details['initialization_utc']==row['cycle_utc'] and details['forecast_lead']==row['lead_hours']
  assert (details['parameter_category'],details['parameter_number'],details['first_surface_type'],details['first_surface_scale'],details['first_surface_value'])==(0,0,103,0,2)
  row['forecast_metadata_matches']=True
 for row in prices:
  date=row['delivery_date'];content=(ROOT/'raw'/f'price_{date}.csv').read_text();rows=list(csv.DictReader(io.StringIO(content)))
  nyc=[r for r in rows if r['Name']=='N.Y.C.' and r['PTID']=='61761']
  row['hour_18_rows']=sum(datetime.strptime(r['Time Stamp'],'%m/%d/%Y %H:%M').hour==18 for r in nyc)
  assert row['hour_18_rows']==1
  if 'error' in row:row['historical_daily_head_error']=row.pop('error')
  with zipfile.ZipFile(ROOT/'raw'/f'prices_{date[:4]}{date[5:7]}.zip') as z:
   member=z.getinfo(date.replace('-','')+'damlbmp_zone.csv');row['target_zip_member_naive_timestamp']=datetime(*member.date_time).isoformat()
   # ZIP timestamps have no timezone; neither these nor archive HTTP dates establish first publication.
  row['zip_member_timestamp_has_timezone']=False
 (ROOT/'outputs/weather_probes.json').write_text(json.dumps(weather,indent=2)+'\n');(ROOT/'outputs/price_probes.json').write_text(json.dumps(prices,indent=2)+'\n')
 for p in sorted((ROOT/'raw').glob('announcements_*.zip')):
  selected=[];allmessages=[]
  with zipfile.ZipFile(p) as z:
   for name in z.namelist():
    if not name.endswith('.csv'):continue
    text=z.read(name).decode('utf-8-sig')
    # These official files contain nonstandard doubled opening/closing quotes and multiline messages.
    # Split only at a timestamp-anchored record start; preserve commas and embedded newlines.
    matches=list(re.finditer(r'(?m)^"(\d{2}-[A-Za-z]{3}-\d{4} \d{2}:\d{2})","',text))
    for i,m in enumerate(matches):
     end=matches[i+1].start() if i+1<len(matches) else len(text)
     message=text[m.end():end].strip().strip('"').strip()
     row={'file':name,'insert_time_local_string':m.group(1),'message':message};allmessages.append(row)
     if any(w in message.lower() for w in ['correct','day-ahead','day ahead']):selected.append(row)
  (ROOT/'outputs'/f'{p.stem}_selected.json').write_text(json.dumps(selected,indent=2)+'\n')
  print(p.name,'records',len(allmessages),'correction/DA notices',len(selected))
  actual=[r for r in selected if re.search(r'corrected|correction|repost|review',r['message'],re.I)]
  print(json.dumps(actual[:5],indent=2))
 print('weather full GRIB metadata verified',len(weather));print('price hourly target records verified',len(prices));print('price schemas lack publication/version fields',sum(not p['publication_timestamp_column'] for p in prices))
if __name__=='__main__':main()
