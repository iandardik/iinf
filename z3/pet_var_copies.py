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
            p1 != p2,
            ForAll(p, Or(p == p1, p == p2)),
            ForAll(p, pc(p) >= 1),
            ForAll(p, pc(p) <= 6),
            ForAll(p, pc_(p) >= 1),
            ForAll(p, pc_(p) <= 6),
            #Or(turn == p1, turn == p2),
            #Or(turn_ == p1, turn_ == p2),
        )
init = And(turn == p1, flag(p1) == False, flag(p2) == False, pc(p1) == 1, pc(p2) == 1)

trans = And(
            Exists([p,q],
                And(
                    p != q,
                    Or(
                        And(pc(p) == 1, pc_(p) == 2, flag_(p) == flag(p), turn_ == turn),
                        And(pc(p) == 2, pc_(p) == 3, flag_(p) == True, turn_ == turn),
                        And(pc(p) == 3, pc_(p) == 4, turn_ != turn, flag_(p) == flag(p)),
                        And(pc(p) == 4, pc_(p) == 5, Or(flag(q) == False, turn == p), flag_(p) == flag(p), turn_ == turn),
                        And(pc(p) == 5, pc_(p) == 6, flag_(p) == flag(p), turn_ == turn),
                        And(pc(p) == 6, pc_(p) == 1, flag_(p) == False, turn_ == turn)
                    )
                )),
            # allows stuttering, works because |ProcSet| = 2
            Exists(p,
                And(pc(p) == pc_(p),
                    flag(p) == flag_(p)
                ))
        )

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
inv2 = ForAll([p,q], Implies(
                    And( pc(p) == 5, p != q ),
                    Or(pc(q) != 4, turn == p)
                ))
inv2_ = ForAll([p,q], Implies(
                    And( pc_(p) == 5, p != q ),
                    Or(pc_(q) != 4, turn_ == p)
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
#solver.add( Not(ii_) )
#solver.add( mutex )
solver.add( Not(mutex_) )
consec = unsat == solver.check()
print("consecution: {}".format(consec))
if not consec:
    print(solver.model())

