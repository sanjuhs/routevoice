import odb,sys
D=odb.dbDatabase.create();odb.read_db(D,sys.argv[1]);b=D.getChip().getBlock()
for n in b.getNets():
 for w in n.getSWires():
  for s in w.getWires():
   if s.isVia():
    print([x for x in dir(s) if 'Via' in x or 'Tech' in x]);print(s.getViaXY());print(s.getBlockVia());print(s.getTechVia());raise SystemExit
