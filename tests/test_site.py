"""Portable evidence, value and local-link checks for the presentation package."""
from pathlib import Path
import unittest,json,csv,hashlib
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
def rows(path):
 with path.open() as stream:return list(csv.DictReader(stream))
def snapshot():
 text=(ROOT/'site/assets/research-data.js').read_text();return json.loads(text.removeprefix('window.RESEARCH = ').removesuffix(';\n'))
class SiteTests(unittest.TestCase):
 def test_all_research_files_match_publication_manifest(self):
  m=json.loads((ROOT/'docs/research_snapshot_manifest.json').read_text())
  for item in m['files']:
   self.assertEqual(hashlib.sha256((ROOT/'research'/item['file']).read_bytes()).hexdigest(),item['sha256'],item['file'])
 def test_site_data_provenance(self):
  p=json.loads((ROOT/'site/evidence/provenance.json').read_text())
  for item in p['sources']:self.assertEqual(hashlib.sha256((ROOT/item['file']).read_bytes()).hexdigest(),item['sha256'])
 def test_error_reductions_from_original_metric_rows(self):
  data=snapshot()
  for kind,folder,column in [('demand',ROOT/'research','mae_mw'),('price',ROOT/'research/price_research','mae_mwh')]:
   m={r['model']:float(r[column]) for r in rows(folder/'outputs/test_metrics.csv') if r['group_type']=='overall'}
   for display in data[kind]:self.assertAlmostEqual(display['mae'],m[display['name']],places=10)
   self.assertAlmostEqual(data[kind+'Gain'],100*(1-m['spline']/m['calendar']),places=10)
 def test_daily_payoff_reconciles_every_cumulative_point(self):
  data=snapshot();daily=rows(ROOT/'research/spread_backtest/outputs/test_daily_signals.csv');self.assertEqual(len(daily),362)
  totals={k:0 for k in ['linear','always_load','calendar']}
  for raw,display in zip(daily,data['cumulative']):
   self.assertEqual(raw['delivery_date'],display['date'])
   for k in totals:
    totals[k]+=int(raw[k+'_side'])*(float(raw['rt_integrated_price_mwh'])-float(raw['finalized_price_mwh']))
    self.assertAlmostEqual(totals[k],display[k],places=7)
  for k in totals:self.assertAlmostEqual(totals[k],next(r['total'] for r in data['trading'] if r['name']==k),places=7)
 def test_followup_cohorts_and_primary_variants_preserved(self):
  data=snapshot()
  for f in ['trajectory','revision']:
   original=json.loads((ROOT/f'research/followup_hypotheses/outputs/{f}/summary.json').read_text())
   self.assertEqual(original,data['followups'][f]['summary'])
  self.assertEqual(data['followups']['trajectory']['summary']['test_days'],356);self.assertEqual(data['followups']['revision']['summary']['test_days'],362)
 def test_website_links_and_unique_ids(self):
  site=ROOT/'site'
  for file in site.rglob('*.html'):
   soup=BeautifulSoup(file.read_text(),'html.parser');ids=[t['id'] for t in soup.find_all(id=True)];self.assertEqual(len(ids),len(set(ids)),str(file))
   for a in soup.find_all('a',href=True):
    h=a['href']
    if h=='#':continue
    if h.startswith('#'):self.assertIn(h[1:],ids)
    elif not h.startswith(('http:','https:','mailto:','data:')):self.assertTrue((file.parent/h).exists(),f'{file}: {h}')
   for tag in soup.find_all(['script','link']):
    h=tag.get('src') if tag.name=='script' else tag.get('href')
    if h and not h.startswith(('http:','https:','data:')):self.assertTrue((file.parent/h).exists(),h)
 def test_caveats_are_visible_in_main_page(self):
  text=BeautifulSoup((ROOT/'site/index.html').read_text(),'html.parser').get_text(' ',strip=True).lower()
  for phrase in ['not establish reliable incremental alpha','clearing is assumed','observed weather','already been examined','cohort','not realized temperature lags']:
   self.assertIn(phrase,text)
 def test_vercel_build_is_static_and_no_fake_deployment_url(self):
  c=json.loads((ROOT/'vercel.json').read_text());self.assertEqual(c['outputDirectory'],'dist');self.assertNotIn('rewrites',c)
  self.assertNotIn('example.com',(ROOT/'site/index.html').read_text())
if __name__=='__main__':unittest.main()
