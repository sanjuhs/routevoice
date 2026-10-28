"""W9-local launcher; no installed LibreLane or repository tool edits."""
import os
from pathlib import Path
from librelane.steps.pyosys import Synthesis
from librelane.__main__ import cli

original=Synthesis.get_script_path(None)
os.environ['W9_ORIGINAL_SYNTH']=original
Synthesis.get_script_path=lambda self:str(Path(__file__).with_name('synthesize_pi.py'))
cli()
