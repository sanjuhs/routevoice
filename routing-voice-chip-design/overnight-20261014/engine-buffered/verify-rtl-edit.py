"""Check that W9's RTL edit only adds mirror registers and redirects decode selectors."""
import hashlib,json,re
from pathlib import Path
W=Path(__file__).resolve().parent
original=(W.parent/'fabric-k64/rtl/engine.sv').read_text()
changed=(W/'rtl/engine_dup.sv').read_text()
pattern=r'// W9: independent register and decode domain for lanes [^\n]+\n\(\* keep = 1, dont_touch = 1 \*\) reg \[10:0\] w9_row_g\d+;\nwire \[4:0\] w9_domain_g\d+ = w9_row_g\d+\[10:6\];\n\(\* keep = 1 \*\) always @\(posedge clk\) begin\n if \(reset\) w9_row_g\d+ <= 0;\n else if \(state == IDLE && start\) w9_row_g\d+ <= 0;\n else if \(state == ACCUM && step_enable && row != 11\'d1279\) w9_row_g\d+ <= row \+ 1\'b1;\nend\n'
pattern += r'\n'
blocks=list(re.finditer(pattern,changed));assert len(blocks)==10,len(blocks)
restored=re.sub(pattern,'',changed)
restored=restored.replace('case({w9_domain_g0,','case({codebook_row_domain,')
for i in range(1,10):restored=restored.replace(f'case({{w9_domain_g{i},','case({codebook_row_domain,')
# Restore original declaration at the start of the inserted block range.
pos=blocks[0].start()
restored=restored[:pos]+'wire [4:0] codebook_row_domain = row >> 6;\n'+restored[pos:]
import difflib
if restored!=original: print(''.join(difflib.unified_diff(original.splitlines(True),restored.splitlines(True)))[:2500])
assert restored==original,'Unexpected RTL difference beyond row duplication and selector redirection'
r={'exact_reverse_patch_matches_original':True,'row_mirror_blocks':len(blocks),'original_sha256':hashlib.sha256(original.encode()).hexdigest(),'modified_sha256':hashlib.sha256(changed.encode()).hexdigest()}
(W/'evidence/rtl-edit-audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
