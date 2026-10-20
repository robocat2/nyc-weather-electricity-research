"""Package the three completed NYC studies and their research progression into one file."""
from pathlib import Path
from html import escape
import hashlib,json,os
from datetime import datetime
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs'
demand_path=OUT/'NYC_Weather_Electricity.html'
price_path=ROOT/'price_research/outputs/NYC_Finalized_Price_Research.html'
spread_path=ROOT/'spread_backtest/outputs/NYC_Gross_Spread_Backtest.html'
summary=json.loads((ROOT/'price_research/outputs/summary.json').read_text())
assert abs(summary['selected_improvement_pct']-16.569385948680292)<1e-8

story='''# NYC weather → electricity demand → price prediction → gross spread backtest

## What this combined walkthrough contains
This is the complete NYC research progression, combining the earlier electricity-demand study with the later finalized-price prediction study. It now includes three executed studies, all twelve charts, their calculations/tables, the reason for moving from demand to prices, the historical-data feasibility hurdle, the revised research question, source definitions and frozen methods. Baxter is a separate corporate-financial case study and is not part of this NYC analysis.

## The research story in plain English
We wanted a Python project that tests a weather-related economic hypothesis using enough consistent observations to evaluate a model on later dates. We began with NYC electricity demand because the load and temperature series could be aligned and checked across several years.

**Stage 1 — Understand demand.** Does temperature add information beyond the hour, weekday, season and holidays? Using 2021–2025 hourly NYC load and LaGuardia observed temperatures, we compared calendar-only, linear-temperature and nonlinear-temperature regressions. A modest temperature spline reduced 2025 mean absolute error by **39.2%, from 436.38 MW to 265.13 MW**, and improved every month. Linear temperature alone slightly worsened average error. This was retrospective modeling conditional on observed weather, not a day-ahead forecast.

**Why move to prices?** The demand result suggested that a nonlinear weather relationship could be worth testing in a market-relevant outcome. It did not prove that prices were predictable or that weather would add information beyond the market's existing expectations. We therefore asked a new question: can weather forecasts issued before a prediction cutoff improve estimates of a future electricity price?

**Stage 2 — Check historical timing.** We first considered a price-history/calendar baseline with archived weather forecasts. Genuine forecasts and price targets existed, but we could not establish complete historical versions of the lagged-price inputs. Current price archives can contain later corrections. We stopped that stricter extension before fitting. The initial proposed 08:00 cutoff was also too late for the documented 05:00 day-ahead market close, so the candidate cutoff became 04:00 New York time.

**Stage 3 — Ask the narrower, valid question.** The revised price experiment excluded historical prices, realized load, realized future temperature and demand-model outputs from inputs. It compared calendar-only against calendar plus a genuine archived temperature forecast. Corrected/finalized prices were allowed as the outcome being predicted. This removes the unresolved lagged-price vintage issue from the input set; it does not establish incremental value over a strong price-history baseline.

**Stage 4 — Test price prediction.** At 04:00 on the prior day, predict NYC's day-ahead electricity price for 18:00–19:00 the following day. We used the operational HRRR 06 UTC cycle's 40/41-hour temperature forecast at a grid point near LaGuardia. Every included forecast had matching embedded issue/valid times and archive-object timing before the cutoff buffer. Out of 1,826 daily dates, 1,809 passed the data gate; 17 were excluded without substituting later forecasts or actual weather. The selected spline reduced 2025 price MAE by **16.6%, from $35.16 to $29.33/MWh**, across 362 matched days, improving ten of twelve months.

**Stage 5 — Test a trading rule before costs.** We verified an NYC virtual electricity trade and fitted a new model for the **real-time minus day-ahead spread**, using the same available forecast/calendar inputs. At 04:00 on D−1, positive predicted spread means virtual load; negative means virtual supply. Gross payoff is side × (RT − DA), assuming one MWh clears. The weather model was selected using 2024 payoff, then evaluated on 362 eligible 2025 dates. Linear temperature was selected; the earlier price-level spline was not reused as a trading signal.

**Latest finding:** the selected rule earned **+$1,020.96 gross**, compared with **+$321.98 calendar-only** and **+$1,384.92 always virtual load / training-mean direction**. Its seven-day bootstrap interval for average daily payoff is **−$8.10 to +$18.29**; the increment over calendar is **−$0.72 to +$6.04/day**. Both cross zero, as do 14/28-day checks. The best day earned $1,768.53; all other dates together lost $747.57. Only three months were positive. **This test does not establish reliable gross alpha.** Costs were deliberately excluded, and clearing was assumed rather than demonstrated. The unselected spline is shown for transparency, not promoted after inspecting 2025.

## The connection between the studies
**The demand finding motivated the price experiment. The fitted demand model was NOT fed into the price model.** The demand and price studies are linked research questions, not one production pipeline that converts predicted demand into a trading order. Stage 1 uses realized temperature to study demand; The price experiment uses archived forecast temperature to predict finalized prices. Their percentages have different units, samples and baselines and must not be added or treated as returns.

## What the percentages actually mean
- **39.2%:** relative reduction in mean absolute demand-estimation error versus a calendar baseline, measured in MW.
- **16.6%:** relative reduction in mean absolute finalized-price prediction error versus a calendar baseline, measured in $/MWh.
- Neither percentage is an investment return, trading win rate, profit margin, or causal effect.

Mean absolute error (MAE) is the average magnitude of the estimate's miss, ignoring whether it is above or below the outcome. Lower is better. A spline is a regression that can bend at a few predefined temperature knots, allowing cold and hot conditions to have different associations. RMSE gives larger misses more weight.

## What makes the evidence useful—and what it cannot establish
All three studies used 2021–2023 for development fitting, 2024 for validation, and 2025 for evaluation after refitting on 2021–2024. Preprocessing and temperature knots used fitting data. There was no random hourly/day split. The price study disclosed that 2025 demand data and two source-feasibility price samples had already been inspected: its evaluation year was excluded from fitting and selection, but was not wholly unseen.

For demand, the seven-day paired block-bootstrap 95% interval for MAE improvement was 128.7–220.2 MW. For prices, it was $1.98–$9.82/MWh. Both price/demand improvements remained positive under 14/28-day block sensitivity checks. These are within-year dependent-error comparisons, not guarantees about future years or causal effects.

Important remaining errors are substantial. The demand spline underestimates load by 109 MW on average, and errors remain strongly serially dependent. The price spline underestimates finalized prices by $21.81/MWh on average, with $49.46/MWh RMSE. It worsens March and November and the spring aggregate. Hot-price performance covers only 16 days. A single NYC weather point cannot capture regional demand, fuel costs, outages, supply and congestion.

The price label is the corrected/latest historical archive snapshot retrieved for the study, called finalized here—not verified original auction publications or immutable settlements. Archive Last-Modified is historical object-availability evidence, not a complete first-NCEP-release or historical access-policy ledger. Retrospectively corrected fitting labels also mean this is not an exact simulation of the historical real-time training environment.

## Is this a signal or trading strategy?
Yes: Part III now tests a specific directional virtual-load/virtual-supply signal against calendar, constant-direction and flat benchmarks. This is a **hypothetical gross spread backtest conditional on clearing**, not an executable or net-profitability backtest. It uses finalized historical outcome prices, not verified original settlement vintages. Actual market access, bid acceptance, fees, uplift, financing and slippage have not been tested. The earlier 16.6% price-error improvement is not a return and did not translate into convincing incremental trading evidence. A strong price-history baseline remains untested.

Parts I and II retain their original conclusions from before the trading extension. Statements there about trading not yet being tested describe that earlier stage; Part III and this introduction provide the current status. 2025 had already been examined in the prior demand and price work, so the spread evaluation is excluded from fitting/selection but is not wholly unseen.

Delivery is normally 38 hours after the prediction cutoff (37/39 over DST), but the auction price is published the prior morning before delivery. The delivery horizon is not the same as time until price revelation.

## Complete studies and methods follow
The full executed demand walkthrough comes first, followed by the full executed price walkthrough and gross spread backtest. Source notes, experiment specifications and the original feasibility decision are included at the end. No modeling or results were changed when combining these documents.
'''

def markdown_to_html(text):
    import mistune
    return mistune.html(text)

head=BeautifulSoup(demand_path.read_text(),'html.parser').head
# Do not require network scripts or fonts for the combined reading file.
for tag in head.find_all(['script','link']):
    tag.decompose()
head.title.string='NYC Combined Research Walkthrough — Demand, Price Prediction and Gross Trading'
style='''<style>
html{scroll-behavior:smooth}body{margin:0;background:#f7f8fa;color:#1c2630;font-family:system-ui,-apple-system,sans-serif}
.combined-shell{max-width:1060px;margin:0 auto;padding:32px 24px 64px}.combined-intro{background:white;padding:32px;border-radius:12px;line-height:1.65}
.combined-intro h1{font-size:32px;line-height:1.2}.combined-intro h2{font-size:22px;margin-top:32px}.combined-intro p,.combined-intro li{font-size:16px}
.combined-nav{display:flex;flex-wrap:wrap;gap:12px;margin:20px 0}.combined-nav a{padding:9px 13px;background:#e8eff7;border-radius:6px;color:#174b7b;text-decoration:none}
.combined-section{background:white;margin-top:32px;padding:24px;border-radius:12px;scroll-margin-top:20px}.combined-section>h2{font-size:26px;color:#174b7b}
.combined-section .jp-Notebook{padding:0!important}.combined-section img{max-width:100%;height:auto}
.combined-section pre{white-space:pre-wrap;overflow-wrap:anywhere}.combined-section details{margin:18px 0}.combined-section summary{font-size:18px;font-weight:600;cursor:pointer;padding:12px 0}
.combined-section .jp-OutputArea-output{overflow-x:auto}.combined-footer{margin-top:24px;color:#536270;font-size:13px}
@media(max-width:600px){.combined-shell{padding:16px 8px}.combined-intro,.combined-section{padding:18px 12px}.combined-intro h1{font-size:26px}}
</style>'''

def embedded_study(path,prefix,is_price=False):
    soup=BeautifulSoup(path.read_text(),'html.parser')
    main=soup.find('main')
    for tag in main.find_all(id=True):
        tag['id']=prefix+tag['id']
    for tag in main.find_all('a',href=True):
        href=tag['href']
        if href.startswith('#'):tag['href']='#'+prefix+href[1:]
        elif not href.startswith(('http:','https:','mailto:')):
            tag['href']=os.path.relpath((path.parent/href).resolve(),OUT)
    for tag in main.find_all('script'):tag.decompose()
    return ''.join(str(tag) for tag in main.contents)

appendices=[('Demand experiment specification',ROOT/'EXPERIMENT.md'),('Demand sources and transformations',ROOT/'SOURCES.md'),
 ('Initial stricter price feasibility decision (historical scope)',ROOT/'price_feasibility/FEASIBILITY_BRIEF.md'),
 ('Revised price experiment specification',ROOT/'price_research/EXPERIMENT.md'),('Price sources and timing evidence',ROOT/'price_research/SOURCES.md'),
 ('Trading feasibility and official settlement evidence',ROOT/'trading_feasibility/FEASIBILITY_BRIEF.md'),
 ('Frozen gross spread experiment',ROOT/'spread_backtest/EXPERIMENT.md'),
 ('Gross spread findings and reproduction',ROOT/'spread_backtest/README.md')]
appendix_html=''.join(f'<details><summary>{escape(title)}</summary><pre>{escape(path.read_text())}</pre></details>' for title,path in appendices)
body=f'''<div class="combined-shell"><nav class="combined-nav" aria-label="Walkthrough sections"><a href="#research-story">Research story</a><a href="#demand-study">Demand: 39.2%</a><a href="#price-study">Prices: 16.6%</a><a href="#spread-study">Gross trading test</a><a href="#methods">Sources & methods</a></nav>
<article class="combined-intro" id="research-story">{markdown_to_html(story)}</article>
<section class="combined-section" id="demand-study"><h2>Part I · Complete electricity-demand study</h2>{embedded_study(demand_path,'demand-')}</section>
<section class="combined-section" id="price-study"><h2>Part II · Complete finalized-price prediction study</h2>{embedded_study(price_path,'price-',True)}</section>
<section class="combined-section" id="spread-study"><h2>Part III · Complete gross spread backtest</h2>{embedded_study(spread_path,'spread-')}</section>
<section class="combined-section" id="methods"><h2>Evidence and frozen methods</h2>{appendix_html}</section>
<p class="combined-footer">Combined on October 16, 2026. All three studies and all twelve chart images are contained in this file. Existing studies are preserved; Part III adds the frozen gross trading experiment; original studies remain preserved.</p></div>'''
html='<!DOCTYPE html><html lang="en">'+str(head).replace('</head>',style+'</head>')+'<body>'+body+'</body></html>'
output=OUT/'NYC_Combined_Research_Walkthrough.html';output.write_text(html)
# Plain text counterpart is portable to uploaders that do not accept HTML.
text=story
for title,path in [('Full demand findings and reproduction',ROOT/'DEMAND_STUDY.md'),('Full price findings and reproduction',ROOT/'price_research/README.md')]+appendices:
    text+='\n\n---\n\n# '+title+'\n\n'+path.read_text()
for title,path in [('Demand exact model scores',OUT/'test_metrics.csv'),('Demand validation scores',OUT/'validation_metrics.csv'),('Demand block uncertainty',OUT/'uncertainty.csv'),
                   ('Price exact model scores',ROOT/'price_research/outputs/test_metrics.csv'),('Price validation scores',ROOT/'price_research/outputs/validation_metrics.csv'),('Price block uncertainty',ROOT/'price_research/outputs/uncertainty.csv'),
 ('Gross trading metrics',ROOT/'spread_backtest/outputs/test_metrics.csv'),
 ('Gross trading validation selection',ROOT/'spread_backtest/outputs/validation_metrics.csv'),
 ('Gross trading uncertainty',ROOT/'spread_backtest/outputs/uncertainty.csv')]:
    text+='\n\n## '+title+'\n\n```csv\n'+path.read_text()+'```\n'
(OUT/'NYC_Combined_Research_Context.md').write_text(text)
soup=BeautifulSoup(html,'html.parser')
images=soup.find_all('img');assert len(images)==12 and all(img['src'].startswith('data:image/png') for img in images)
ids=[t['id'] for t in soup.find_all(id=True)];assert len(ids)==len(set(ids)), 'Duplicate anchors'
for a in soup.find_all('a',href=True):
    href=a['href']
    if href.startswith('#'):assert href[1:] in ids,href
    elif not href.startswith(('http:','https:','mailto:')):assert (output.parent/href).exists(),href
assert not soup.find_all('iframe') and not soup.find_all('script')
manifest={'combined_html':output.name,'embedded_charts':len(images),'source_documents':[],'validation':'Embedded images, internal anchors, local links and no remote script dependencies verified.'}
for path in [demand_path,price_path,spread_path]+[p for _,p in appendices]:
    manifest['source_documents'].append({'file':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(OUT/'combined_walkthrough_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Created:',output);print('Embedded charts:',len(images));print('HTML bytes:',output.stat().st_size);print('Upload-friendly text:',OUT/'NYC_Combined_Research_Context.md')
