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
            #ForAll(p, pc_(p) >= 1),
            #ForAll(p, pc_(p) <= 6)
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
            Exists(p,
                And(pc(p) == pc_(p),
                    flag(p) == flag_(p)
                ))
        )

mutex = ForAll([p,q], Implies(And(pc(p) == 5, pc(q) == 5), p == q))
mutex_ = ForAll([p,q], Implies(And(pc_(p) == 5, pc_(q) == 5), p == q))


solver = Solver()
solver.add(typeok)
#solver.add(trans)
#solver.add(mutex)
#solver.add(mutex_)


# figure out the number of states and record each one
cap = 1000
models = []
cubes = []
num_states = 0
while solver.check() == sat and num_states < cap:
    m = solver.model()
    cube = And(pc(p1) == m.eval(pc(p1)),
               pc(p2) == m.eval(pc(p2)),
               #pc_(p1) == m.eval(pc_(p1)),
               #pc_(p2) == m.eval(pc_(p2)),
               flag(p1) == m.eval(flag(p1)),
               flag(p2) == m.eval(flag(p2)),
               #flag_(p1) == m.eval(flag_(p1)),
               #flag_(p2) == m.eval(flag_(p2)),
               turn == m.eval(turn),
               #turn_ == m.eval(turn_)
            )
    solver.add(Not(cube)) # block the cube
    models.append(m)
    cubes.append(cube)
    num_states = num_states+1

num_safe = 0
num_unsafe = 0

for m,c in zip(models,cubes):
    s = Solver()
    s.add(typeok)
    s.add( And(c, Not(mutex)) )
    #s.add( And(c, Not(And(mutex,mutex_))) )
    safe = s.check() == unsat

    if safe:
        num_safe = num_safe+1
    else:
        num_unsafe = num_unsafe+1

print("num_sates: {}".format(num_states))
print("num_safe: {}".format(num_safe))
print("num_unsafe: {}".format(num_unsafe))
