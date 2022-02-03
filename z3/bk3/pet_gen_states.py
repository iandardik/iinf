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
            Exists(p, p == p1),
            Exists(p, p == p2),
            ForAll(p, Xor(p == p1, p == p2)),
            ForAll(p, pc(p) >= 1),
            ForAll(p, pc(p) <= 6),
            Xor(turn == p1, turn == p2),
        )
typeok_ = And(
            p1 != p2,
            Exists(p, p == p1),
            Exists(p, p == p2),
            ForAll(p, Xor(p == p1, p == p2)),
            ForAll(p, pc_(p) >= 1),
            ForAll(p, pc_(p) <= 6),
            Xor(turn_ == p1, turn_ == p2),
        )
init = And(turn == p1, flag(p1) == False, flag(p2) == False, pc(p1) == 1, pc(p2) == 1)

trans = And(
            Exists([p,q],
                And(
                    p != q,
                    Or(
                        And(pc(p) == 1, pc_(p) == 2, flag_(p) == flag(p), turn_ == turn),
                        And(pc(p) == 2, pc_(p) == 3, flag_(p) == True, turn_ == turn),
                        And(pc(p) == 3, pc_(p) == 4, turn_ != turn, flag_(p) == flag(p), flag_(q) == flag(q)),
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
    cube = And(pc(p1) == m.eval(pc(p1), True),
               pc(p2) == m.eval(pc(p2), True),
               flag(p1) == m.eval(flag(p1), True),
               flag(p2) == m.eval(flag(p2), True),
               turn == m.eval(turn, True),
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
    #s.add( And(c, Not(mutex)) )
    #safe = s.check() == unsat
    s.add( And(c, mutex) )
    safe = s.check() == sat

    if safe:
        num_safe = num_safe+1
    else:
        num_unsafe = num_unsafe+1

print("num_sates: {}".format(num_states))
print("num_safe: {}".format(num_safe))
print("num_unsafe: {}".format(num_unsafe))



def is_inductive_old(P, P_, cubes):
    for c in cubes:
        s = Solver()
        s.add(typeok)
        s.add(typeok_)
        s.add(And(c, P))
        s.add(trans)
        s.add(Not(P_))
        if s.check() == sat:
            print("cex: {}\n ->\n {}".format(c,s.model()))
            return False
    return True
def is_inductive(P, P_):
    s = Solver()
    s.add(typeok)
    s.add(typeok_)
    s.add(P)
    s.add(trans)
    s.add(Not(P_))
    if s.check() == sat:
        #print("cex:\n {}".format(s.model()))
        return False
    return True


inv1 = ForAll(p, Implies(
                    Or(pc(p) == 3, pc(p) == 4, pc(p) == 5, pc(p) == 6),
                    flag(p) == True
                ))
inv1_ = ForAll(p, Implies(
                    Or(pc_(p) == 3, pc_(p) == 4, pc_(p) == 5, pc_(p) == 6),
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
inv3 = ForAll(p, Implies(
                    Or(pc(p) == 1, pc(p) == 2),
                    flag(p) == False
                ))
inv3_ = ForAll(p, Implies(
                    Or(pc_(p) == 1, pc_(p) == 2),
                    flag_(p) == False
                ))

ii = And(mutex, inv1, inv2)
ii_ = And(mutex_, inv1_, inv2_)

#mut_ind = is_inductive(mutex, mutex_, cubes)
#print("mut_ind: {}\n".format(mut_ind))

#ii_ind = is_inductive(ii, ii_, cubes)
#print("ii_ind: {}\n".format(ii_ind))


A1 = ForAll(p, Implies(
                Or(pc(p) == 3, pc(p) == 4, pc(p) == 5, pc(p) == 6),
                flag(p) == True
            ))
A1_ = ForAll(p, Implies(
                Or(pc_(p) == 3, pc_(p) == 4, pc_(p) == 5, pc_(p) == 6),
                flag_(p) == True
            ))
A2 = ForAll([p,q], Implies(
                    And( Or(pc(p) == 4, pc(p) == 5, pc(p) == 6), turn == p, p != q ),
                    pc(q) == 4
            ))
A2_ = ForAll([p,q], Implies(
                    And( Or(pc_(p) == 4, pc_(p) == 5, pc_(p) == 6), turn_ == p, p != q ),
                    pc_(q) == 4
            ))

wii = And(mutex, A1, A2)
wii_ = And(mutex_, A1_, A2_)
#wii_ind = is_inductive(wii, wii_, cubes)
#print("wii_ind: {}".format(wii_ind))


reach1 = ForAll([p,q],
        And(
            Implies(
                And(p != q, pc(p) == 1, Or(pc(q) == 4, pc(q) == 5, pc(q) == 6)),
                turn == p),
            Implies(
                And(p != q, pc(p) == 2, Or(pc(q) == 4, pc(q) == 5, pc(q) == 6)),
                turn == p),
            Implies(
                And(p != q, pc(p) == 3, Or(pc(q) == 4, pc(q) == 5, pc(q) == 6)),
                turn == p),
            Implies(
                And(p != q, pc(p) == 4, turn == p),
                pc(q) == 4),
            Implies(
                And(p != q, pc(p) == 5, turn == p),
                pc(q) == 4),
            Implies(
                And(p != q, pc(p) == 6, turn == p),
                pc(q) == 4)
        ))
reach1_ = ForAll([p,q],
        And(
            Implies(
                And(p != q, pc_(p) == 1, Or(pc_(q) == 4, pc_(q) == 5, pc_(q) == 6)),
                turn_ == p),
            Implies(
                And(p != q, pc_(p) == 2, Or(pc_(q) == 4, pc_(q) == 5, pc_(q) == 6)),
                turn_ == p),
            Implies(
                And(p != q, pc_(p) == 3, Or(pc_(q) == 4, pc_(q) == 5, pc_(q) == 6)),
                turn_ == p),
            Implies(
                And(p != q, pc_(p) == 4, turn_ == p),
                pc_(q) == 4),
            Implies(
                And(p != q, pc_(p) == 5, turn_ == p),
                pc_(q) == 4),
            Implies(
                And(p != q, pc_(p) == 6, turn_ == p),
                pc_(q) == 4)
        ))

reach = And(typeok, mutex, inv1, inv2, inv3, reach1)
reach_ = And(typeok_, mutex_, inv1_, inv2_, inv3_, reach1_)
#reach_ind = is_inductive_old(reach, reach_, cubes)
#reach_ind = is_inductive(reach, reach_)
#print("reach_ind: {}".format(reach_ind))


# init -> P
# unsat(P ^ ~init)
def initiation(P):
    s = Solver()
    s.add(init)
    s.add(Not(P))
    return s.check() == unsat

# P -> mutex
def is_safe(P):
    s = Solver()
    s.add(P)
    s.add(Not(mutex))
    return s.check() == unsat

# P -> Q
def implies(P, Q):
    s = Solver()
    s.add(Not(Implies(P,Q)))
    return s.check() == unsat

def dfs_mutex(raw_ind, depth):
    if depth > 4:
        return None
    ind = ForAll([p,q], raw_ind)
    if implies(ind, mutex) and initiation(ind): # and is_inductive(ind, mutex_):
        return ind

    rv = dfs_mutex(Not(raw_ind), depth+1)
    if rv is not None: return rv
    for i in range(5):
        rv = dfs_mutex(And(pc(p) == i+1, raw_ind), depth+1)
        if rv is not None: return rv
    rv = dfs_mutex(And(turn == p, raw_ind), depth+1)
    if rv is not None: return rv
    rv = dfs_mutex(And(turn == q, raw_ind), depth+1)
    if rv is not None: return rv
    rv = dfs_mutex(And(flag(p) == True, raw_ind), depth+1)
    if rv is not None: return rv
    rv = dfs_mutex(And(flag(p) == False, raw_ind), depth+1)
    if rv is not None: return rv
    return None

def dfs_ii(raw_ind, raw_ind_, depth):
    if depth > 2:
        return None
    ind = ForAll([p,q], raw_ind)
    ind_ = ForAll([p,q], raw_ind_)
    if initiation(ind) and is_inductive(ind, ind_) and is_safe(ind):
        return (ind, ind_)

    rv = dfs_ii(Not(raw_ind), Not(raw_ind_), depth+1)
    if rv is not None: return rv
    for i in range(5):
        rv = dfs_ii(And(pc(p) == i+1, raw_ind), And(pc_(p) == i+1, raw_ind_), depth+1)
        if rv is not None: return rv
    rv = dfs_ii(And(turn == p, raw_ind), And(turn_ == p, raw_ind_), depth+1)
    if rv is not None: return rv
    rv = dfs_ii(And(turn == q, raw_ind), And(turn_ == q, raw_ind_), depth+1)
    if rv is not None: return rv
    rv = dfs_ii(And(flag(p) == True, raw_ind), And(flag_(p) == True, raw_ind_), depth+1)
    if rv is not None: return rv
    rv = dfs_ii(And(flag(p) == False, raw_ind), And(flag_(p) == False, raw_ind_), depth+1)
    if rv is not None: return rv
    return None

result = dfs_mutex(And(True), 0)
#result = dfs_mutex(mutex, 0)
print result
#result = dfs_ii(And(True), And(True), 0)
#result = None
#if result is not None:
    #print("")
    #print(result[0])
    #print("")
    #print(result[1])
#else:
    #print("no solution found")
