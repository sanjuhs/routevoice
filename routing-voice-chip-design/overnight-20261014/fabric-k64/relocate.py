"""Rebase this self-contained workspace after copying it to a CPU machine."""
from pathlib import Path
import json
W=Path(__file__).resolve().parent
sample=json.loads((W/'configs/sc_rom.json').read_text())
old=str(Path(sample['VERILOG_FILES'][0]).parents[1])
for folder in ['configs','tb']:
 for p in (W/folder).glob('*'):
  if p.suffix in ['.json','.sv']:p.write_text(p.read_text().replace(old,str(W)))
print(f'Rebased {old} -> {W}')
