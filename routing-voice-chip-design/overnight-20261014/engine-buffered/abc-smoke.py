from pathlib import Path
import subprocess,json
W=Path('/workspace/rv/overnight-20261014/engine-buffered'); D=W/'evidence/abc-smoke';D.mkdir(exist_ok=True)
lib=next((W/'runs/buf-v3/tmp').glob('*.lib'))
n=3000
(D/'fixture.blif').write_text('.model fixture\n.inputs x '+' '.join(f'x{i}' for i in range(n))+'\n.outputs '+' '.join(f'y{i}' for i in range(n))+'\n'+''.join(f'.gate gf180mcu_fd_sc_mcu7t5v0__and2_1 A1=x A2=x{i} Z=y{i}\n' for i in range(n))+'.end\n')
(D/'constraints.sdc').write_text('set_driving_cell gf180mcu_fd_sc_mcu7t5v0__inv_1\nset_load 72.91\n')
cmd=f'read_lib -w {lib}; read_blif {D}/fixture.blif; read_constr {D}/constraints.sdc; buffer -p -N 16 -S 3000; print_stats; write_blif {D}/buffered.blif'
p=subprocess.run(['/nix/store/f1q0w7rd0a4ny4hqvfxlhs4cmariidcy-yosys-0.62/bin/yosys-abc','-c',cmd],capture_output=True,text=True)
(D/'abc.log').write_text(p.stdout+p.stderr)
assert p.returncode==0 and 'Cannot find' not in p.stdout and (D/'buffered.blif').exists(),p.stdout+p.stderr
from collections import Counter
c=Counter()
for l in (D/'buffered.blif').read_text().splitlines():
 if l.startswith('.gate '):
  for pair in l.split()[2:-1]:c[pair.split('=')[1]]+=1
r={'returncode':p.returncode,'initial_shared_pi_fanout':n,'final_shared_pi_fanout':c['x'],'max_net_fanout':max(c.values()),'abc_command':cmd}
(D/'result.json').write_text(json.dumps(r,indent=2));print(json.dumps(r));assert c['x']<=16
