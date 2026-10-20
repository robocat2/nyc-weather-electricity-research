"""Bounded spread-data and market-document inventory. No fitting or P&L scoring."""
from pathlib import Path
from datetime import datetime,timezone
import concurrent.futures,csv,hashlib,io,json,urllib.request,zipfile
ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent

def fetch(item):
 name,url=item;path=ROOT/'raw'/name
 if not path.exists():
  req=urllib.request.Request(url,headers={'User-Agent':'NYCSpreadFeasibility/1.0'})
  with urllib.request.urlopen(req,timeout=45) as response:
   data=response.read();meta={'url':url,'http_status':response.status,'headers':dict(response.headers.items()),'retrieved_utc':datetime.now(timezone.utc).isoformat()}
  if name.endswith('.zip') and data[:2]!=b'PK':raise ValueError('Expected ZIP')
  if name.endswith('.pdf') and data[:4]!=b'%PDF':raise ValueError('Expected PDF')
  path.write_bytes(data);meta.update(file=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest());path.with_suffix(path.suffix+'.receipt.json').write_text(json.dumps(meta,indent=2)+'\n')
 return json.loads(path.with_suffix(path.suffix+'.receipt.json').read_text())

def main():
 items=[(f'rt_{y}{m:02}.zip',f'https://mis.nyiso.com/public/csv/rtlbmp/{y}{m:02}01rtlbmp_zone_csv.zip') for y in range(2021,2026) for m in range(1,13)]
 items += [('accounting_billing.pdf','https://www.nyiso.com/documents/20142/2923231/acctbillmnl.pdf'),('virtual_settlements.pdf','https://www.nyiso.com/documents/20142/3035389/Virtual-Trading-Settlements.pdf/2e4e8a27-b4b1-a0e1-b376-0cab32b93180'),('rt_index.html','https://mis.nyiso.com/public/P-4Alist.htm')]
 sources=[];failures=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
  jobs={pool.submit(fetch,item):item for item in items}
  for future in concurrent.futures.as_completed(jobs):
   try:sources.append(future.result())
   except Exception as error:failures.append({'file':jobs[future][0],'url':jobs[future][1],'error':str(error)})
 (ROOT/'outputs/source_manifest.json').write_text(json.dumps(sources,indent=2)+'\n');(ROOT/'outputs/retrieval_failures.json').write_text(json.dumps(failures,indent=2)+'\n')
 rows=[]
 for path in sorted((ROOT/'raw').glob('rt_*.zip')):
  with zipfile.ZipFile(path) as archive:
   for member in archive.namelist():
    if not member.endswith('.csv'):continue
    reader=csv.DictReader(io.StringIO(archive.read(member).decode('utf-8-sig')))
    for row in reader:
     if row.get('Name')!='N.Y.C.' or row.get('PTID')!='61761':continue
     stamp=datetime.strptime(row['Time Stamp'],'%m/%d/%Y %H:%M')
     if stamp.hour==18:
      rows.append({'delivery_date':stamp.date().isoformat(),'rt_integrated_price_mwh':float(row['LBMP ($/MWHr)']),'archive':path.name,'member':member})
 import pandas as pd
 frame=pd.DataFrame(rows)
 if frame.empty or frame.delivery_date.duplicated().any():raise ValueError('Missing/duplicate NYC hour-18 RT targets')
 prior=pd.read_csv(PROJECT/'price_research/outputs/daily_data.csv')
 joined=prior[['delivery_date','year','usable','finalized_price_mwh','cutoff_utc','target_utc']].merge(frame,on='delivery_date',how='left',validate='one_to_one')
 joined['rt_target_present']=joined.rt_integrated_price_mwh.notna()
 joined['usable_spread_research']=joined.usable & joined.rt_target_present
 # Labels only. No historical RT/DA values become prediction-time inputs.
 joined['rt_minus_da_mwh']=joined.rt_integrated_price_mwh-joined.finalized_price_mwh
 joined.to_csv(ROOT/'outputs/spread_label_inventory.csv',index=False)
 coverage=joined.groupby('year').agg(expected_days=('delivery_date','size'),rt_target_days=('rt_target_present','sum'),usable_forecast_and_spread_days=('usable_spread_research','sum')).reset_index()
 coverage.to_csv(ROOT/'outputs/annual_coverage.csv',index=False)
 result={'rt_monthly_archives':len(list((ROOT/'raw').glob('rt_*.zip'))),'rt_target_days':len(frame),'existing_da_target_days':len(prior),'joined_days':len(joined),'matched_spread_outcomes':int(joined.rt_target_present.sum()),'timing_eligible_forecast_and_spread_days':int(joined.usable_spread_research.sum()),'models_fitted':0,'pnl_calculated':False,'fees_slippage_modeled':False,'failures':failures}
 (ROOT/'outputs/data_feasibility.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2));print(coverage.to_string(index=False))
if __name__=='__main__':main()
