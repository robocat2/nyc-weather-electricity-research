"""Acquire an earlier issued forecast for exactly the existing delivery target."""
from pathlib import Path
from datetime import timedelta
import sys,json,concurrent.futures,argparse
ROOT=Path(__file__).resolve().parents[1];PARENT=ROOT.parent
sys.path.insert(0,str(PARENT/'price_research/src'))
from acquire import fetch,save_file,availability,dates_and_times,sha256
from prepare import decode_message

def one(date):
 target,cutoff,newcycle,_=dates_and_times(date);cycle=newcycle-timedelta(hours=6);lead=int((target-cycle).total_seconds()/3600)
 url=f'https://noaa-hrrr-bdp-pds.s3.amazonaws.com/hrrr.{cycle:%Y%m%d}/conus/hrrr.t00z.wrfsfcf{lead:02}.grib2'
 row={'delivery_date':date,'cycle_utc':cycle.isoformat(),'target_utc':target.isoformat(),'cutoff_utc':cutoff.isoformat(),'lead_hours':lead,'url':url,'available':False}
 base=ROOT/'raw'/f'old_{date}';headpath=base.with_suffix('.head.json');msg=base.with_suffix('.grib2');idx=base.with_suffix('.idx')
 try:
  if headpath.exists():head=json.loads(headpath.read_text())
  else:
   _,head=fetch(url,method='HEAD');headpath.write_text(json.dumps(head,indent=2)+'\n')
  modified,etag=availability(head['headers'],cutoff)
  if idx.exists():index=idx.read_bytes()
  else:
   index,receipt=fetch(url+'.idx');save_file(idx,index,receipt)
  lines=index.decode().splitlines();matches=[i for i,l in enumerate(lines) if ':TMP:2 m above ground:' in l]
  if len(matches)!=1:raise ValueError('Expected one 2m temperature field')
  pos=matches[0];start=int(lines[pos].split(':')[1]);end=int(lines[pos+1].split(':')[1])-1
  if not msg.exists():
   content,receipt=fetch(url,headers={'Range':f'bytes={start}-{end}','If-Match':etag});save_file(msg,content,receipt)
  content=msg.read_bytes();receipt=json.loads(msg.with_suffix('.grib2.receipt.json').read_text());headers={k.lower():v for k,v in receipt['headers'].items()}
  actualmodified,actualetag=availability(headers,cutoff)
  if actualetag!=etag or actualmodified!=modified or len(content)!=end-start+1 or receipt['sha256']!=sha256(content):raise ValueError('Receipt/range mismatch')
  if content[:4]!=b'GRIB' or content[-4:]!=b'7777':raise ValueError('Incomplete GRIB')
  decoded=decode_message(content,row,{})
  row.update(decoded,available=True,archive_available_utc=modified.isoformat(),etag=etag,file=msg.name,sha256=sha256(content),bytes=len(content),index_entry=lines[pos])
 except Exception as exc:row['reason']=str(exc)
 return row

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--full',action='store_true');args=parser.parse_args()
 import pandas as pd
 dates=pd.date_range('2021-01-01','2025-12-31').strftime('%Y-%m-%d').tolist() if args.full else ['2021-01-15','2022-07-15','2023-03-12','2024-11-03','2025-06-24','2025-12-31']
 output=ROOT/'outputs'/('older_forecasts.json' if args.full else 'feasibility_samples.json');rows=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
  for row in pool.map(one,dates):
   rows.append(row)
   if len(rows)%50==0 or len(rows)==len(dates):
    output.write_text(json.dumps(rows,indent=2)+'\n');print(f'{len(rows)}/{len(dates)}, available {sum(r["available"] for r in rows)}',flush=True)
 if not args.full:print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
