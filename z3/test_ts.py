from z3 import *

x0, x1 = Consts('x0 x1', IntSort())
init = x0 == 1
trans = x1 == x0 + 1

#ii = And(x0 > 0, x1 > 0)
c1 = x0 > 0
c2 = Not(x1 > 0)

solver = Solver()
#solver.add(init)
solver.add(trans)
solver.add(c1)
solver.add(c2)

print(solver.check()) # want to see unsat

