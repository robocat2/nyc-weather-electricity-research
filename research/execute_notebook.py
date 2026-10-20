"""Execute with the active Python environment, then export self-contained HTML."""
import os,sys
from pathlib import Path
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
ROOT=Path(__file__).resolve().parent
os.environ['PATH']=str(Path(sys.executable).parent)+os.pathsep+os.environ['PATH']
os.environ.setdefault('MPLCONFIGDIR','/tmp/nyc-weather-mpl')
os.environ.setdefault('JUPYTER_RUNTIME_DIR','/tmp/nyc-weather-jupyter')
os.environ['JUPYTER_PATH']=str(Path(sys.prefix)/'share/jupyter')
path=ROOT/'NYC_Weather_Electricity.ipynb'
notebook=nbformat.read(path,as_version=4)
NotebookClient(notebook,timeout=180,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
nbformat.validate(notebook);nbformat.write(notebook,path)
exporter=HTMLExporter(template_name='lab');html,_=exporter.from_notebook_node(notebook)
html=html.replace('href="EXPERIMENT.md"','href="../EXPERIMENT.md"')
(ROOT/'outputs/NYC_Weather_Electricity.html').write_text(html)
print('Executed',sum(c.cell_type=='code' for c in notebook.cells),'code cells and exported HTML.')
