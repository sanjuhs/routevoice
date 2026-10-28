"""W9 ABC PI buffering and correction of ABC-only driving-cell syntax."""
import os
import sys
from pathlib import Path

original=Path(os.environ['W9_ORIGINAL_SYNTH'])
sys.path.insert(0,str(original.parent))
from construct_abc_script import ABCScriptCreator

base_init=ABCScriptCreator.__init__
def pi_init(self,*args,**kwargs):
    base_init(self,*args,**kwargs)
    assert 'buffer -N ' in self.fine_tune, self.fine_tune
    self.fine_tune=self.fine_tune.replace('buffer -N ','buffer -p -N ')
ABCScriptCreator.__init__=pi_init
source=original.read_text()
old="{config['SYNTH_DRIVING_CELL']}"
assert source.count(old)==1
source=source.replace(old,"{config['SYNTH_DRIVING_CELL'].split('/')[0]}")
exec(compile(source,str(original),'exec'),{'__name__':'__main__','__file__':str(original)})
