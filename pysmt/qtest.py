from pysmt.shortcuts import ForAll, Exists, Symbol, And, Not, Equals, NotEquals, is_sat
from pysmt.typing import PySMTType, Type

#server = PySMTType
server = Type("server")
s = Symbol("s", server)
t = Symbol("t", server)
f = ForAll([s,t], NotEquals(s, t))

sat = is_sat(f)
print("is_sat(f): {}".format(sat))
