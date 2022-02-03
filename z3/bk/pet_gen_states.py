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


solver = Solver()
solver.add(typeok)
solver.add(trans)
#solver.add(mutex)
#solver.add(mutex_)

models = []
cubes = []
for i in range(288):
    solver.check()
    m = solver.model()
    cube = Not( And(pc(p1) == m.eval(pc(p1)),
                    pc(p2) == m.eval(pc(p2)),
                    pc_(p1) == m.eval(pc_(p1)),
                    pc_(p2) == m.eval(pc_(p2)),
                    flag(p1) == m.eval(flag(p1)),
                    flag(p2) == m.eval(flag(p2)),
                    flag_(p1) == m.eval(flag_(p1)),
                    flag_(p2) == m.eval(flag_(p2)),
                    turn == m.eval(turn),
                    turn_ == m.eval(turn_)
                ))
    solver.add(cube)
    models.append(m)
    cubes.append(cube)
                         

num_safe = 0
num_unsafe = 0

for m,c in zip(models,cubes):
    #print(m)
    s = Solver()
    #s.add( And(c, Not(Or(mutex,mutex_))) )
    #s.add( And(c, And(mutex,mutex_)) )
    s.add( And(c, Not(mutex)) )
    safe = s.check() == unsat

    if safe:
        #print(c)
        #print(safe)
        num_safe = num_safe+1
    else:
        num_unsafe = num_unsafe+1

print("num_safe: {}".format(num_safe))
print("num_unsafe: {}".format(num_unsafe))
