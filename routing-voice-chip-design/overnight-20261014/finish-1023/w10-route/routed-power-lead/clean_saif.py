"""Drop (INSTANCE $name ...) blocks (Verilator-traced cell-model UDP internals) that OpenSTA's SAIF parser rejects.
Keeps every other line byte-identical; reports how many blocks/lines were removed."""
import sys,re
src,dst=sys.argv[1],sys.argv[2]
skip=0; removed_blocks=0; removed_lines=0
pat=re.compile(r'^\s*\(INSTANCE \$')
with open(src) as f, open(dst,'w') as g:
    for line in f:
        if skip:
            skip+=line.count('(')-line.count(')'); removed_lines+=1
            continue
        if pat.match(line):
            depth=line.count('(')-line.count(')'); removed_blocks+=1; removed_lines+=1
            if depth>0: skip=depth
            continue
        g.write(line)
print({'removed_blocks':removed_blocks,'removed_lines':removed_lines})
