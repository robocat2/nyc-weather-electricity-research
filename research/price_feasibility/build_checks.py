"""Create a small source-feasibility companion; no prediction models or tuning."""
from pathlib import Path
import json,hashlib
import nbformat as nb
ROOT=Path(__file__).resolve().parent
n=nb.v4.new_notebook();n.cells=[
 nb.v4.new_markdown_cell('''# NYC electricity-price extension: source feasibility
## tl;dr
**Stop before fitting under the strict historical-information rule.** Eight genuine forecast messages and eight price-target samples were verified, but a complete numerical price-vintage reconstruction for the lagged-price baseline was not established. No predictive or trading results were produced. The demand project is unchanged. Read [FEASIBILITY_BRIEF.md](FEASIBILITY_BRIEF.md) for the decision and limitations.'''),
 nb.v4.new_markdown_cell('''## Context & Methods
Candidate: predict next-day 18:00–19:00 NYC day-ahead LBMP ($/MWh) at 04:00 New York time the previous day. Normal delivery horizon is 38 hours, or 37/39 at DST. The auction price is normally published the morning of the cutoff day, before its delivery day. The 04:00 cutoff precedes the documented 05:00 auction deadline; historical trading-rule applicability remains to be verified.

Eight winter/summer/DST dates were fixed before source probing. Check real forecast metadata and archive timestamps, price schemas, sixteen prior-price endpoints and two announcement months. These are bounded samples, not full-year coverage validation. No realized weather, demand fit, price model or profit calculation is used.'''),
 nb.v4.new_code_cell('''from pathlib import Path
import sys, json, hashlib, io, contextlib
import pandas as pd
from IPython.display import display
ROOT = Path.cwd()
assert (ROOT / 'TASK_DEFINITION.md').exists(), 'Execute from price_feasibility.'
sys.path.insert(0, str(ROOT))
from inspect_cached import main
with contextlib.redirect_stdout(io.StringIO()):
    main()  # Offline recheck of exact cached forecast bytes and price schemas.
weather = pd.read_json(ROOT / 'outputs/weather_probes.json')
prices = pd.read_json(ROOT / 'outputs/price_probes.json')
lags = pd.read_json(ROOT / 'outputs/price_lag_probes.json')
assert len(weather) == len(prices) == 8 and len(lags) == 16
assert weather.forecast_metadata_matches.all() and weather.object_before_cutoff.all()
assert prices.hour_18_rows.eq(1).all() and not prices.publication_timestamp_column.any()
print('Cached evidence checks passed; no model fitting performed.')'''),
 nb.v4.new_markdown_cell('''## Data
Sources: [NOAA HRRR public archive](https://registry.opendata.aws/noaa-hrrr-pds/), [NYISO day-ahead prices](https://mis.nyiso.com/public/P-2Alist.htm), [NYISO correction-log notice](https://mis.nyiso.com/public/P-29list.htm), and its designated authority [Operational Announcements](https://mis.nyiso.com/public/P-25list.htm). Raw responses, range receipts and headers are retained in `raw/`. S3 Last-Modified is archive object metadata, not an exact NCEP first-publication timestamp; it nevertheless predates cutoff in every sampled object. ETags have no multipart suffix. ZIP-member times are naive and not a numerical vintage ledger.'''),
 nb.v4.new_code_cell('''display(weather[['delivery_date', 'lead_hours', 'elapsed_prediction_horizon_hours',
                 'object_last_modified_utc', 'minutes_before_cutoff', 'forecast_metadata_matches']].round(2))
display(prices[['delivery_date', 'nyc_hourly_rows', 'hour_18_rows',
                'publication_timestamp_column', 'target_zip_member_naive_timestamp']])
print('Lagged daily price endpoint checks:', len(lags))
print(lags.error.value_counts().to_string())'''),
 nb.v4.new_markdown_cell('''## Results
Weather samples are actual 40/41-hour 2m-temperature forecasts: GRIB reference time, lead and height identity match. All eight archive object timestamps precede cutoff by 10.6–82.2 minutes. Price target records exist, including the expected 23/25-hour DST days. The target 18:00 hour is unique.

The archived price schema has no publication/version fields. Original daily endpoints for all sixteen lagged-price samples return 404; numerical values remain available inside monthly ZIPs. The old correction log stopped in 2012. Its successor announcements supply dated validation and correction notices, but inspected messages do not reconstruct every original/revised numerical day-ahead input. **This is an unresolved provenance gap, not a detected error in our sampled day-ahead prices.**'''),
 nb.v4.new_code_cell('''notices = []
for name in ['announcements_202501_selected.json', 'announcements_202507_selected.json']:
    notices.extend(json.loads((ROOT / 'outputs' / name).read_text()))
examples = [r for r in notices if 'has corrected prices' in r['message']]
display(pd.DataFrame(examples)[['insert_time_local_string', 'message']])
print('The displayed corrections concern real-time prices, not the sampled day-ahead target.')
checked = 0
for receipt_path in (ROOT / 'raw').glob('*.receipt.json'):
    receipt = json.loads(receipt_path.read_text())
    content = (ROOT / 'raw' / receipt['file']).read_bytes()
    assert receipt['sha256'] == hashlib.sha256(content).hexdigest()
    checked += 1
print(f'{checked} cached-source receipts verified against SHA-256 hashes.')'''),
 nb.v4.new_markdown_cell('''## Takeaways
**Stop this strict historical price extension before fitting.** The weather hurdle has a promising, directly sampled path; the lagged-price vintage requirement is unverified. A versioned historical price source or a separately authorized forward snapshot collection could resolve it. Neither is established or started here. No claim is made that a solution does not exist elsewhere.

2025 has already been examined in the demand project and is not wholly unseen. If a future price study becomes feasible, freeze its separate experiment, use chronological fitting/validation, and disclose that exposure. Any demand-derived input must be produced using only earlier fitting data and genuinely available forecasts. Price accuracy does not establish executable trading profitability.''')]
n.metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'}}
nb.validate(n);nb.write(n,ROOT/'Feasibility_Checks.ipynb')
manifest=[]
for path in sorted((ROOT/'raw').iterdir()):
 if path.is_file():manifest.append({'file':path.name,'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(ROOT/'outputs/evidence_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Built',len(n.cells),'cells; hashed',len(manifest),'raw evidence artifacts.')
