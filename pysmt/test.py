from pysmt.shortcuts import Symbol, And, Not, is_sat

varA = Symbol("A")
varB = Symbol("B")

f = And(varA, Not(varB))
sat = is_sat(f)

print("is_sat(f): {}".format(sat))
