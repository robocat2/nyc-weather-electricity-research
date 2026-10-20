"""Decode forecast-only covariates before joining corrected-price outcomes."""
from pathlib import Path
from datetime import datetime, timezone
import csv, io, json, zipfile
import eccodes
import numpy as np
import pandas as pd
from acquire import ROOT, sha256, availability, dates_and_times

POINT_LATITUDE = 40.7794
POINT_LONGITUDE = -73.8803

def decode_message(content, row, grid_cache):
    """Validate issue/valid times and extract a fixed-location forecast in Celsius."""
    message = eccodes.codes_new_from_message(content)
    try:
        get = lambda key: eccodes.codes_get(message, key)
        issue = datetime.strptime(f'{get("dataDate"):08}{get("dataTime"):04}', '%Y%m%d%H%M').replace(tzinfo=timezone.utc)
        valid = datetime.strptime(f'{get("validityDate"):08}{get("validityTime"):04}', '%Y%m%d%H%M').replace(tzinfo=timezone.utc)
        if issue.isoformat() != row['cycle_utc'] or valid.isoformat() != row['target_utc']:
            raise ValueError('Forecast embedded issue or valid time mismatch')
        if int(get('step')) != row['lead_hours'] or get('stepType') != 'instant':
            raise ValueError('Not the specified instantaneous forecast horizon')
        if get('shortName') != '2t' or get('typeOfLevel') != 'heightAboveGround' or get('level') != 2 or get('units') != 'K':
            raise ValueError('Not 2m air temperature in Kelvin')
        if get('dataType') != 'fc' or get('productionStatusOfProcessedData') != 0 or get('centre') != 'kwbc':
            raise ValueError('Not an NCEP operational forecast')
        grid = get('md5GridSection')
        if grid not in grid_cache:
            point = dict(eccodes.codes_grib_find_nearest(message, POINT_LATITUDE, POINT_LONGITUDE, npoints=1)[0])
            if point['distance'] > 5:
                raise ValueError('Nearest forecast grid point too far from requested NYC point')
            grid_cache[grid] = point
        point = grid_cache[grid]
        value = float(eccodes.codes_get_double_element(message, 'values', point['index'])) - 273.15
        if not np.isfinite(value) or not -60 <= value <= 60:
            raise ValueError('Missing or implausible forecast temperature')
        return {'forecast_temperature_c': value, 'grid_md5': grid,
                'grid_index': int(point['index']), 'grid_latitude': point['lat'],
                'grid_longitude': (point['lon']+180) % 360-180,
                'grid_distance_km': point['distance'], 'decoder_issue_utc': issue.isoformat(),
                'decoder_valid_utc': valid.isoformat()}
    finally:
        eccodes.codes_release(message)

def decode_forecasts():
    rows = json.loads((ROOT/'outputs/forecast_availability.json').read_text())
    if len(rows) != 1826 or len({r['delivery_date'] for r in rows}) != 1826:
        raise ValueError('Incomplete daily availability inventory')
    grid_cache = {}
    completed = []
    for index, row in enumerate(rows):
        row = row.copy()
        if row['available']:
            try:
                content = (ROOT/'raw'/row['file']).read_bytes()
                if sha256(content) != row['sha256']:
                    raise ValueError('Forecast cached hash mismatch')
                head = json.loads((ROOT/'raw'/f"forecast_{row['delivery_date']}_head.json").read_text())
                availability(head['headers'], datetime.fromisoformat(row['cutoff_utc']))
                row.update(decode_message(content, row, grid_cache))
            except Exception as error:
                row['available'] = False
                row['reason'] = 'decode/verification: '+str(error)
        completed.append(row)
        if (index+1) % 200 == 0:
            print('Decoded forecast records:', index+1, flush=True)
    frame = pd.DataFrame(completed)
    frame.to_csv(ROOT/'outputs/forecast_point_data.csv', index=False)
    (ROOT/'outputs/grid_points.json').write_text(json.dumps(grid_cache, indent=2)+'\n')
    return frame

def price_outcomes():
    records = []
    manifest = json.loads((ROOT/'outputs/price_source_manifest.json').read_text())
    if len(manifest) != 60:
        raise ValueError('Incomplete monthly outcome archives')
    for source in manifest:
        path = ROOT/'raw'/source['file']
        if sha256(path.read_bytes()) != source['sha256']:
            raise ValueError('Outcome archive hash mismatch')
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if not name.endswith('.csv'):
                    continue
                rows = csv.DictReader(io.StringIO(archive.read(name).decode('utf-8-sig')))
                for row in rows:
                    if row.get('Name') != 'N.Y.C.' or row.get('PTID') != '61761':
                        continue
                    timestamp = datetime.strptime(row['Time Stamp'], '%m/%d/%Y %H:%M')
                    if timestamp.hour != 18:
                        continue
                    if timestamp.minute != 0:
                        raise ValueError('Nonhourly price target')
                    price = float(row['LBMP ($/MWHr)'])
                    if not np.isfinite(price):
                        raise ValueError('Invalid price outcome')
                    records.append({'delivery_date': timestamp.date().isoformat(),
                                    'finalized_price_mwh': price,
                                    'outcome_archive': path.name, 'outcome_member': name})
    frame = pd.DataFrame(records)
    if len(frame) != 1826 or frame.delivery_date.duplicated().any():
        raise ValueError('Missing/duplicate NYC target-hour prices')
    return frame

def main():
    forecasts = decode_forecasts()
    data = forecasts.merge(price_outcomes(), on='delivery_date', how='left', validate='one_to_one')
    data['usable'] = data.available & data.forecast_temperature_c.notna() & data.finalized_price_mwh.notna()
    dates = pd.to_datetime(data.delivery_date)
    data['year'] = dates.dt.year
    data['month'] = dates.dt.month
    data.to_csv(ROOT/'outputs/daily_data.csv', index=False)
    monthly = data.groupby(['year','month']).agg(expected_days=('delivery_date','size'), usable_days=('usable','sum')).reset_index()
    monthly['coverage'] = monthly.usable_days/monthly.expected_days
    annual = monthly.groupby('year')[['expected_days','usable_days']].sum().reset_index()
    annual['coverage'] = annual.usable_days/annual.expected_days
    monthly.to_csv(ROOT/'outputs/monthly_coverage.csv', index=False)
    annual.to_csv(ROOT/'outputs/annual_coverage.csv', index=False)
    data.loc[~data.usable].to_csv(ROOT/'outputs/excluded_days.csv', index=False)
    gate = bool(len(annual)==5 and annual.coverage.min()>=.90 and monthly.coverage.min()>=.80)
    status = {'passed':gate, 'expected_days':len(data), 'usable_days':int(data.usable.sum()),
              'excluded_days':int((~data.usable).sum()), 'minimum_month_coverage':float(monthly.coverage.min()),
              'minimum_year_coverage':float(annual.coverage.min()), 'raw_forecast_bytes':int(forecasts.loc[forecasts.available,'bytes'].sum())}
    (ROOT/'outputs/data_gate.json').write_text(json.dumps(status, indent=2)+'\n')
    print(json.dumps(status, indent=2), flush=True)
    if not gate:
        raise ValueError('Frozen data-coverage gate failed; no fitting permitted')
    return data

if __name__ == '__main__':
    main()
