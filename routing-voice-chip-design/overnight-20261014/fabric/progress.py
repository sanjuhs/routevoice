from pathlib import Path
import json,shutil,time
r=Path(__file__).resolve().parent
print('free GiB',round(shutil.disk_usage(r).free/1024**3,2))
for p in sorted((r/'runs').glob('*')):
    steps=sorted([s for s in p.iterdir() if s.is_dir() and s.name[:2].isdigit()])
    print(p.name,'latest',steps[-1].name if steps else 'none')
    log=r/'logs'/f'{p.name}.flow.log'
    if log.exists():
        with log.open('rb') as f:
            f.seek(max(0,log.stat().st_size-1800));print(f.read().decode(errors='replace')[-1200:])
