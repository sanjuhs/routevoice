"""Read-only independently inspect retained GDS joins, terminals and arithmetic.

This is a geometry check, not a replacement for DRC/LVS/PEX/IR/EM.
"""
from pathlib import Path
import hashlib,json,os
os.environ['OMP_NUM_THREADS']='1'
import klayout.db as k
HERE=Path(__file__).resolve().parent
W=HERE.parent
def run(rows):
    d=W/f'r{rows}-v2';l=k.Layout();l.read(str(d/'bank.gds'))
    top=l.cell(f'PITCH_BANK_R{rows}');b=top.dbbox();checks=0
    def region(c,layer):return k.Region(c.shapes(l.layer(layer,0)))
    def cover(reg,x1,y1,x2,y2):
        nonlocal checks
        box=k.Box(round(x1*1000),round(y1*1000),round(x2*1000),round(y2*1000))
        assert (k.Region(box)-reg).is_empty(),(x1,y1,x2,y2)
        checks+=1
    for g in range(10):
        j=l.cell(f'PITCH_JOINED_R{rows}_G{g:02d}')
        m2,m3,m4,v2,v3=[region(j,x) for x in [36,42,46,38,40]]
        r=l.cell(f'PITCH_RECEIVER_G{g:02d}');rm2=region(r,36)
        for bc in range(128):
            # Formula derives physical sixteen-bit groups, independent of JSON route list.
            grp,local=divmod(bc,16);x=10+2.33+grp*11.56+local*.66
            rr=bc%8;cc=bc//8;rx=10+.09+(cc//2)*11.56+(cc%2)*5.28+2.24
            y=rr*14.4+12.5
            cover(m2,x-.19,124.81,x+.19,126.69)
            cover(m4,x-.19,y-.19,x+.19,125.19)
            cover(m3,min(x,rx)-.19,y-.19,max(x,rx)+.19,y+.19)
            cover(m2,rx-.19,rr*14.4+2,rx+.19,y+.19)
            for reg,xx,yy in [(v2,x,125),(v3,x,125),(v3,x,y),(v2,rx,y)]:
                cover(reg,xx-.13,yy-.13,xx+.13,yy+.13)
            cover(rm2,rx-10-.19,rr*14.4+2,rx-10+.19,rr*14.4+2.1)
        for shp in r.shapes(l.layer(36,10)).each():
            if shp.is_text() and shp.text.string.startswith('OUT'):
                p=shp.text.trans.disp
                assert not (k.Region(k.Box(p.x-1,p.y-1,p.x+1,p.y+1)) & rm2).is_empty()
                checks+=1
        # Receiver spines have all eight via3 connections to real phase/supply buses.
        rr4,rrv3=[region(r,n) for n in [46,40]]
        for xx,offset in [(-3,.38),(-2,10),(-1,11.34)]:
            cover(rr4,xx-.19,.19,xx+.19,112.33)
            for row in range(8):
                yy=row*14.4+offset;cover(rrv3,xx-.13,yy-.13,xx+.13,yy+.13)
    return dict(rows=rows,gds_sha256=hashlib.sha256((d/'bank.gds').read_bytes()).hexdigest(),
        bounds_um=[b.left,b.bottom,b.right,b.top],dimensions_um=[b.width(),b.height()],
        area_um2=b.width()*b.height(),um2_per_selection=b.width()*b.height()/(rows*320),
        route_and_pin_geometry_checks=checks,pass_all=True,
        scope='Direct GDS M2/M3/M4 joins, via2/via3,1280 OUT labels on metal,receiver supply/PC eight-row spines. Does not prove all-layer connectivity or electrical integrity.')
results=[run(n) for n in [64,1280]]
a=results[1]['um2_per_selection'];model=a*31457280/1e6
report=dict(geometry=results,area_audit=dict(uniform_model_mm2=model,october_array_receiver_mm2=153.833+11.004,
    october_other_components_mm2=25.002+30.369+.269+.944,mixed_mm2=model+25.002+30.369+.269+.944,
    mixed_increase_over_october_mm2=model-(153.833+11.004),
    native_local_bit_pitch_um=.66,average_pitch_including_every16_corridor_um=11.56/16,
    bank_width_per_bitline_um=results[1]['dimensions_um'][0]/1280))
(HERE/'geometry-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print('W6-STATUS: independent geometry/area audit PASS',json.dumps(report))
