from z3 import *
index = 0
def fresh(round, s):
    global index
    index += 1
    return Const("!f%d_%d" % (round, index), s)

def zipp(xs, ys):
    return [p for p in zip(xs, ys)]

def bmc(init, trans, goal, fvs, xs, xns):
    s = Solver()
    s.add(init)
    count = 0
    while True:
        print("iteration ", count)
        count += 1
        p = fresh(count, BoolSort())
        s.add(Implies(p, goal))
        if sat == s.check(p):
            print (s.model())
            return
        s.add(trans)
        ys = [fresh(count, x.sort()) for x in xs]
        nfvs = [fresh(count, x.sort()) for x in fvs]
        trans = substitute(trans, 
                           zipp(xns + xs + fvs, ys + xns + nfvs))
        goal = substitute(goal, zipp(xs, xns))
        xs, xns, fvs = xns, ys, nfvs


#x0, x1 = Consts('x0 x1', BitVecSort(4))
#bmc(x0 == 0, x1 == x0 + 3, x0 == 10, [], [x0], [x1])

#x0, x1 = Consts('x0 x1', IntSort())
#bmc(x0 == 0, x1 == x0 + 1, x0 == 10, [], [x0], [x1])


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

bmc(And(init, typeok), And(typeok, trans), Exists(p, pc(p) == 6), [], [flag,pc], [flag_,pc_])
