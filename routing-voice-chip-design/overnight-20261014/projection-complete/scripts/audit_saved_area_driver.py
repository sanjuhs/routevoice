"""OpenROAD -python adapter; avoids relying on untested CLI argument passthrough."""
import os, runpy, sys
from pathlib import Path
script = Path(__file__).with_name('audit_saved_area.py')
sys.argv = [str(script), '--state', os.environ['W8_AREA_STATE'],
            '--output', os.environ['W8_AREA_OUTPUT']]
runpy.run_path(str(script), run_name='__main__')
