"""Execute the source-only notebook in the current project Python environment."""
from pathlib import Path
import os,sys,json
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parent
os.environ['PATH']=str(Path(sys.executable).parent)+os.pathsep+os.environ['PATH']
os.environ['JUPYTER_PATH']=str(Path(sys.prefix)/'share/jupyter')
os.environ['JUPYTER_RUNTIME_DIR']='/tmp/nyc-price-feasibility-jupyter'
path=ROOT/'Feasibility_Checks.ipynb';n=nbformat.read(path,as_version=4)
NotebookClient(n,timeout=90,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
nbformat.validate(n);nbformat.write(n,path)
assert all(c.execution_count is not None for c in n.cells if c.cell_type=='code')
assert not any(o.output_type=='error' for c in n.cells if c.cell_type=='code' for o in c.outputs)
status={'decision':'STOP_before_fitting','forecast_samples_verified':8,'price_target_samples_verified':8,'lag_endpoints_checked':16,'price_models_fitted':0,'price_vintage_reconstruction_verified':False,'notebook_code_cells_executed':sum(c.cell_type=='code' for c in n.cells),'model_scores_or_trading_profit_claims':False}
(ROOT/'outputs/decision.json').write_text(json.dumps(status,indent=2)+'\n')
print(json.dumps(status,indent=2))
