from z3 import *

ProcSet = DeclareSort("ProcSet")

flag = Function("flag", ProcSet, BoolSort())
turn = Const("turn", ProcSet)
pc = Function("pc", ProcSet, IntSort())

flag_ = Function("flag_", ProcSet, BoolSort())
turn_ = Const("turn_", ProcSet)
pc_ = Function("pc_", ProcSet, IntSort())

p1 = Const("p1", ProcSet)
p2 = Const("p2", ProcSet)

p = Const("p", ProcSet)
q = Const("q", ProcSet)
typeok = And(
            ForAll(p, Or(p == p1, p == p2)),
            pc(p1) >= 1,
            pc(p2) <= 6
        )
init = And(turn == p1, flag(p1) == False, flag(p2) == False, pc(p1) == 1, pc(p2) == 1)

def other(p):
    if p == p1: return p2
    else:       return p1

trans = ForAll(p,
            Or(
                And(pc(p) == 1, pc_(p) == 2, flag_(p) == flag(p), turn_ == turn),
                And(pc(p) == 2, pc_(p) == 3, flag_(p) == True, turn_ == turn),
                And(pc(p) == 3, pc_(p) == 4, turn_ == other(turn), flag_(p) == flag(p)),
                And(pc(p) == 4, pc_(p) == 5, Or(flag(other(p)) == False, turn == p), flag_(p) == flag(p), turn_ == turn),
                And(pc(p) == 5, pc_(p) == 6, flag_(p) == flag(p), turn_ == turn),
                And(pc(p) == 6, pc_(p) == 1, flag_(p) == False, turn_ == turn)
            ))

mutex = ForAll([p,q], Implies(And(pc(p) == 5, pc(q) == 5), p == q))
mutex_ = ForAll([p,q], Implies(And(pc_(p) == 5, pc_(q) == 5), p == q))
inv1 = ForAll(p, Implies(
                    Or(pc(p) == 3, pc(p) == 4, pc(p) == 5),
                    flag(p) == True
                ))
inv1_ = ForAll(p, Implies(
                    Or(pc_(p) == 3, pc_(p) == 4, pc_(p) == 5),
                    flag_(p) == True
                ))
inv2 = ForAll(p, Implies(
                    pc(p) == 5,
                    Or(pc(other(p)) != 4, turn == p)
                ))
inv2_ = ForAll(p, Implies(
                    pc_(p) == 5,
                    Or(pc_(other(p)) != 4, turn_ == p)
                ))

ii = And(mutex, inv1, inv2)
ii_ = And(mutex_, inv1_, inv2_)

# initiation
isolver = Solver()
isolver.add(typeok)
isolver.add( And(init, Not(ii)) )
print("initiation: {}".format(unsat == isolver.check()))

# consecution
solver = Solver()
solver.add(typeok)
solver.add(trans)
solver.add( ii )
solver.add( Not(ii_) )
#solver.add( mutex )
#solver.add( Not(mutex_) )
print("consecution: {}".format(unsat == solver.check()))
if solver.check() == sat:
    print(solver.model())

