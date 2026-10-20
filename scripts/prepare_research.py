"""Curate the original audited project; never modify original research files."""
from pathlib import Path
import shutil,hashlib,json,csv
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT.parent/'NYC_Weather_Electricity';DEST=ROOT/'research'
allowed={'.py','.md','.json','.csv','.ipynb','.png','.html'}
manifest=[]
for path in sorted(SOURCE.rglob('*')):
 if not path.is_file():continue
 rel=path.relative_to(SOURCE)
 if any(x in rel.parts for x in ['raw','.venv','__pycache__','portfolio','.git','.ipynb_checkpoints']):continue
 if path.suffix not in allowed and path.name!='requirements.txt':continue
 if 'Before_Trading' in path.name or path.name=='RELEASE_MANIFEST.json':continue
 target=DEST/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
 manifest.append({'file':str(rel),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
# One small GRIB fixture supports original price decoder tests; bulk raw caches omitted.
row=next(r for r in json.loads((SOURCE/'price_research/outputs/forecast_availability.json').read_text()) if r['available'])
for filename in [row['file'],row['file']+'.receipt.json']:
 rel=Path('price_research/raw')/filename;target=DEST/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SOURCE/rel,target)
 manifest.append({'file':str(rel),'sha256':hashlib.sha256((SOURCE/rel).read_bytes()).hexdigest()})
(ROOT/'docs/research_snapshot_manifest.json').write_text(json.dumps({'scope':'Curated copy; original audited file bytes preserved. Bulk raw caches and environments excluded; one GRIB test fixture included.','files':manifest},indent=2)+'\n')
print('Copied',len(manifest),'research evidence files')
