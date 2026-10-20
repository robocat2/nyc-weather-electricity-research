"""Download immutable public-source files with a SHA-256 manifest."""
from pathlib import Path
import argparse, concurrent.futures, hashlib, json, urllib.request
from datetime import datetime, timezone
ROOT = Path(__file__).resolve().parents[1]
def fetch(item):
    name,url = item
    path=ROOT/'raw'/name
    if not path.exists():
        req=urllib.request.Request(url,headers={'User-Agent':'NYCWeatherDemandResearch/1.0'})
        with urllib.request.urlopen(req,timeout=60) as response:
            content=response.read()
        if name.endswith('.html'):
            path.write_bytes(content)
            return {'file':name,'url':url,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest(),'retrieved_utc':datetime.now(timezone.utc).isoformat()}
        if not content or b'<!doctype html' in content[:1000].lower() or b'<html' in content[:1000].lower(): raise ValueError(f'Not data: {url}')
        path.write_bytes(content)
    content=path.read_bytes()
    return {'file':name,'url':url,'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest(),'retrieved_utc':datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat()}
def main():
    p=argparse.ArgumentParser();p.add_argument('--full',action='store_true');args=p.parse_args()
    items=[('ghcnh_documentation.pdf','https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/doc/ghcnh_DOCUMENTATION.pdf'),('ghcnh_stations.txt','https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/doc/ghcnh-station-list.txt'),('noaa_explorer.html','https://www.ncei.noaa.gov/oa/global-historical-climatology-network/index.html'),('isd-history.csv','https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv'),('isd-format-document.pdf','https://www.ncei.noaa.gov/pub/data/noaa/isd-format-document.pdf'),('nyiso_market_guide.pdf','https://www.nyiso.com/documents/20142/3625950/mpug.pdf')]
    years=range(2021,2026) if args.full else [2021,2023,2025]
    months=range(1,13) if args.full else [1,7]
    for y in years:
        items.append((f'weather_{y}.psv',f'https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/access/by-year/{y}/psv/GHCNh_USW00014732_{y}.psv'))
        for m in months:
            items.append((f'load_{y}{m:02}.zip',f'https://mis.nyiso.com/public/csv/palIntegrated/{y}{m:02}01palIntegrated_csv.zip'))
    if args.full: items.append(('weather_2026.psv','https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/access/by-year/2026/psv/GHCNh_USW00014732_2026.psv'))
    old={x['file']:x for x in json.loads((ROOT/'raw/manifest.json').read_text())} if (ROOT/'raw/manifest.json').exists() else {}
    failures=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(fetch,item):item for item in items}
        for f in concurrent.futures.as_completed(futures):
            try:
                row=f.result();old[row['file']]=row;print(row['file'],row['bytes'],flush=True)
            except Exception as e:
                failures.append({'file':futures[f][0],'error':str(e)});print('FAILED',futures[f],str(e),flush=True)
    (ROOT/'raw/manifest.json').write_text(json.dumps(list(old.values()),indent=2)+'\n')
    (ROOT/'outputs/download_failures.json').write_text(json.dumps(failures,indent=2)+'\n')
    if failures: raise SystemExit(1)
if __name__=='__main__': main()
