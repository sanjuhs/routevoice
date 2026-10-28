from pathlib import Path
import json
W=Path(__file__).resolve().parent
pvts=['tt_025C_3v30','ss_125C_3v00','ff_n40C_3v60']
for v in ['array_port','sc_rom']:
 p=W/'configs'/f'{v}.json';c=json.loads(p.read_text())
 c.update(VDD_PIN_VOLTAGE=3.3,DEFAULT_CORNER='nom_tt_025C_3v30',STA_CORNERS=[f'{r}_{p}' for r in ['nom','min','max'] for p in pvts],TIMING_VIOLATION_CORNERS=['*'])
 c['LIB']={f'*_{p}':[str(W/'pdks/gf180mcuD/libs.ref/gf180mcu_fd_sc_mcu7t5v0/lib'/f'gf180mcu_fd_sc_mcu7t5v0__{p}.lib')] for p in pvts}
 p.write_text(json.dumps(c,indent=2)+'\n')
