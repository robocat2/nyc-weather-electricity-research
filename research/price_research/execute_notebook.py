"""Execute the finalized-price research notebook with this Python environment."""
from pathlib import Path
import os, sys
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
ROOT = Path(__file__).resolve().parent
os.environ['PATH'] = str(Path(sys.executable).parent)+os.pathsep+os.environ['PATH']
os.environ['JUPYTER_PATH'] = str(Path(sys.prefix)/'share/jupyter')
os.environ['JUPYTER_RUNTIME_DIR'] = '/tmp/nyc-price-research-jupyter'
os.environ['MPLCONFIGDIR'] = '/tmp/nyc-price-research-mpl'
path = ROOT/'NYC_Finalized_Price_Research.ipynb'
notebook = nbformat.read(path,as_version=4)
NotebookClient(notebook,timeout=180,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
nbformat.validate(notebook)
nbformat.write(notebook,path)
html,_ = HTMLExporter(template_name='lab').from_notebook_node(notebook)
for name in ['EXPERIMENT.md','SOURCES.md']:
    html = html.replace(f'href="{name}"',f'href="../{name}"')
(ROOT/'outputs/NYC_Finalized_Price_Research.html').write_text(html)
print('Executed',sum(cell.cell_type=='code' for cell in notebook.cells),'code cells; HTML exported.')
