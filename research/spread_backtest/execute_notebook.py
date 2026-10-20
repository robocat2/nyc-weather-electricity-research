"""Execute the gross backtest notebook and export its self-contained walkthrough."""
from pathlib import Path
import os,sys
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
ROOT=Path(__file__).resolve().parent
os.environ['PATH']=str(Path(sys.executable).parent)+os.pathsep+os.environ['PATH']
os.environ['JUPYTER_PATH']=str(Path(sys.prefix)/'share/jupyter')
os.environ['JUPYTER_RUNTIME_DIR']='/tmp/nyc-spread-jupyter'
os.environ['MPLCONFIGDIR']='/tmp/nyc-spread-mpl'
p=ROOT/'NYC_Gross_Spread_Backtest.ipynb';n=nbformat.read(p,as_version=4)
NotebookClient(n,timeout=180,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
nbformat.validate(n);nbformat.write(n,p)
html,_=HTMLExporter(template_name='lab').from_notebook_node(n)
html=html.replace('href="EXPERIMENT.md"','href="../EXPERIMENT.md"').replace('href="../trading_feasibility/','href="../../trading_feasibility/')
(ROOT/'outputs/NYC_Gross_Spread_Backtest.html').write_text(html)
print('Executed',sum(c.cell_type=='code' for c in n.cells),'code cells; exported HTML')
