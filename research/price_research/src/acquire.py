"""Cache dated operational forecast messages and corrected-price outcome archives.

Only 2m-temperature GRIB messages are retrieved, using HTTP ranges. Each forecast
has a cutoff, an archive-availability witness and an If-Match byte receipt.
"""
from pathlib import Path
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from email.utils import parsedate_to_datetime
from urllib.error import HTTPError
import argparse, concurrent.futures, hashlib, json, re, shutil, time, urllib.request

ROOT = Path(__file__).resolve().parents[1]
ZONE = ZoneInfo('America/New_York')
PREVIOUS = ROOT.parent / 'price_feasibility' / 'raw'

def sha256(content):
    return hashlib.sha256(content).hexdigest()

def fetch(url, method='GET', headers=None):
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, method=method, headers={
                'User-Agent': 'NYCForecastPriceResearch/1.0', **(headers or {})})
            with urllib.request.urlopen(request, timeout=45) as response:
                receipt = {'url': url, 'http_status': response.status,
                           'headers': dict(response.headers.items()),
                           'checked_utc': datetime.now(timezone.utc).isoformat()}
                if method == 'HEAD':
                    return b'', receipt
                if headers and 'Range' in headers:
                    if response.status != 206:
                        raise ValueError('Range ignored; full-grid download refused')
                    content = response.read(3_000_001)
                    if len(content) > 3_000_000:
                        raise ValueError('Temperature message exceeds bounded range')
                else:
                    content = response.read()
                return content, receipt
        except HTTPError as error:
            if error.code not in [429, 500, 502, 503, 504] or attempt == 2:
                raise
        except (TimeoutError, OSError):
            if attempt == 2:
                raise
        time.sleep(attempt + 1)

def save_file(path, content, receipt):
    path.write_bytes(content)
    receipt = {**receipt, 'file': path.name, 'bytes': len(content), 'sha256': sha256(content)}
    path.with_suffix(path.suffix + '.receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')

def dates_and_times(delivery):
    date = datetime.fromisoformat(delivery).date()
    previous = date - timedelta(days=1)
    target = datetime.combine(date, datetime.min.time(), ZONE).replace(hour=18).astimezone(timezone.utc)
    cutoff = datetime.combine(previous, datetime.min.time(), ZONE).replace(hour=4).astimezone(timezone.utc)
    cycle = datetime.combine(previous, datetime.min.time(), timezone.utc).replace(hour=6)
    return target, cutoff, cycle, int((target - cycle).total_seconds() / 3600)

def availability(headers, cutoff):
    headers = {key.lower(): value for key, value in headers.items()}
    modified = parsedate_to_datetime(headers['last-modified'])
    etag = headers['etag']
    if re.search(r'-\d+"?$', etag):
        raise ValueError('Multipart timestamp does not prove completed availability')
    if modified > cutoff - timedelta(minutes=5):
        raise ValueError('Archive object unavailable at cutoff minus five minutes')
    return modified, etag

def acquire_forecast(delivery):
    target, cutoff, cycle, lead = dates_and_times(delivery)
    url = (f'https://noaa-hrrr-bdp-pds.s3.amazonaws.com/hrrr.{cycle:%Y%m%d}/conus/'
           f'hrrr.t06z.wrfsfcf{lead:02}.grib2')
    row = {'delivery_date': delivery, 'target_utc': target.isoformat(),
           'cutoff_utc': cutoff.isoformat(), 'cycle_utc': cycle.isoformat(),
           'lead_hours': lead, 'delivery_horizon_hours': (target-cutoff).total_seconds()/3600,
           'url': url, 'available': False}
    base = ROOT / 'raw' / f'forecast_{delivery}'
    head_path = Path(str(base) + '_head.json')
    message_path = base.with_suffix('.grib2')
    index_path = base.with_suffix('.idx')
    try:
        # Reuse exact feasibility bytes and receipts where the same forecast was sampled.
        prior_head = PREVIOUS / f'weather_{delivery}_head.json'
        prior_message = PREVIOUS / f'weather_{delivery}_temperature.grib2'
        prior_index = PREVIOUS / f'weather_{delivery}.idx'
        if prior_head.exists() and prior_message.exists() and not head_path.exists():
            shutil.copyfile(prior_head, head_path)
            for source, destination in [(prior_message, message_path), (prior_index, index_path)]:
                content = source.read_bytes()
                receipt = json.loads(source.with_suffix(source.suffix+'.receipt.json').read_text())
                save_file(destination, content, receipt)
        if head_path.exists():
            head = json.loads(head_path.read_text())
        else:
            _, head = fetch(url, method='HEAD')
            head_path.write_text(json.dumps(head, indent=2)+'\n')
        modified, etag = availability(head['headers'], cutoff)
        row.update(archive_available_utc=modified.isoformat(), etag=etag,
                   margin_minutes=(cutoff-modified).total_seconds()/60)
        if index_path.exists():
            index = index_path.read_bytes()
        else:
            index, receipt = fetch(url+'.idx')
            save_file(index_path, index, receipt)
        lines = index.decode().splitlines()
        matches = [i for i, line in enumerate(lines) if ':TMP:2 m above ground:' in line]
        if len(matches) != 1:
            raise ValueError('Expected exactly one 2m-temperature field')
        position = matches[0]
        start = int(lines[position].split(':')[1])
        end = int(lines[position+1].split(':')[1])-1
        row['index_entry'] = lines[position]
        if not message_path.exists():
            content, receipt = fetch(url, headers={'Range': f'bytes={start}-{end}', 'If-Match': etag})
            save_file(message_path, content, receipt)
        content = message_path.read_bytes()
        receipt = json.loads(message_path.with_suffix('.grib2.receipt.json').read_text())
        received = {k.lower(): v for k, v in receipt['headers'].items()}
        if received['etag'] != etag or parsedate_to_datetime(received['last-modified']) != modified:
            raise ValueError('Forecast changed between metadata and byte retrieval')
        if receipt['sha256'] != sha256(content) or len(content) != end-start+1:
            raise ValueError('Cached forecast byte/range hash mismatch')
        if content[:4] != b'GRIB' or content[7] != 2 or content[-4:] != b'7777':
            raise ValueError('Incomplete GRIB2 temperature message')
        row.update(available=True, file=message_path.name, sha256=sha256(content),
                   bytes=len(content), byte_range=f'{start}-{end}')
    except Exception as error:
        row['reason'] = str(error)
    return row

def acquire_prices(year_month):
    year, month = year_month
    name = f'prices_{year}{month:02}.zip'
    url = f'https://mis.nyiso.com/public/csv/damlbmp/{year}{month:02}01damlbmp_zone_csv.zip'
    path = ROOT/'raw'/name
    if not path.exists():
        prior = PREVIOUS/name
        if prior.exists():
            save_file(path, prior.read_bytes(), json.loads(prior.with_suffix('.zip.receipt.json').read_text()))
        else:
            content, receipt = fetch(url)
            if content[:2] != b'PK':
                raise ValueError('NYISO outcome archive is not ZIP')
            save_file(path, content, receipt)
    receipt = json.loads(path.with_suffix('.zip.receipt.json').read_text())
    if sha256(path.read_bytes()) != receipt['sha256']:
        raise ValueError('Cached price hash mismatch')
    return receipt

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=8)
    args = parser.parse_args()
    dates = [(datetime(2021,1,1)+timedelta(days=i)).date().isoformat() for i in range(1826)]
    completed = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(acquire_forecast, date) for date in dates]
        for future in concurrent.futures.as_completed(futures):
            completed.append(future.result())
            if len(completed) % 50 == 0 or len(completed) == len(dates):
                rows = sorted(completed, key=lambda row: row['delivery_date'])
                (ROOT/'outputs/forecast_availability.json').write_text(json.dumps(rows, indent=2)+'\n')
                print('forecast checks', len(rows), '/', len(dates), 'available',
                      sum(row['available'] for row in rows), flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        receipts = list(pool.map(acquire_prices, [(year,month) for year in range(2021,2026) for month in range(1,13)]))
    (ROOT/'outputs/price_source_manifest.json').write_text(json.dumps(receipts,indent=2)+'\n')
    print('Outcome archives cached:', len(receipts), flush=True)

if __name__ == '__main__':
    main()
