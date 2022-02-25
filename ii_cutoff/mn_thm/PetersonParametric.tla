------------------------- MODULE PetersonParametric -------------------------

EXTENDS TLC, Naturals, FiniteSets, FiniteSetTheorems
        
VARIABLE flag, turn

\* The program counter for each process.
VARIABLE pc

vars == << flag, turn, pc >>

\* The set of processes.
\* ProcSet == ({0,1})
CONSTANT ProcSet

Init == 
    /\ flag = [i \in ProcSet |-> FALSE]
    /\ turn = 0 \*CHOOSE p \in ProcSet : TRUE
    /\ pc = [self \in ProcSet |-> "a1"]

a1(p) == /\ pc[p] = "a1"
         /\ pc' = [pc EXCEPT ![p] = "a2"]
         /\ UNCHANGED << flag, turn >>

a2(p) == /\ pc[p] = "a2"
         /\ flag' = [flag EXCEPT ![p] = TRUE]
         /\ pc' = [pc EXCEPT ![p] = "a3"]
         /\ turn' = turn

a3(p,q) == /\ pc[p] = "a3"
           /\ turn' = q
           /\ pc' = [pc EXCEPT ![p] = "a4"]
           /\ flag' = flag

a4(p,q) ==  /\ pc[p] = "a4"
            /\ (flag[q] = FALSE) \/ (turn = p)
            /\ pc' = [pc EXCEPT ![p] = "cs"]
            /\ UNCHANGED << flag, turn >>

cs(p) == /\ pc[p] = "cs"
         /\ pc' = [pc EXCEPT ![p] = "a5"]
         /\ UNCHANGED << flag, turn >>

a5(p) == /\ pc[p] = "a5"
         /\ flag' = [flag EXCEPT ![p] = FALSE]
         /\ pc' = [pc EXCEPT ![p] = "a1"]
         /\ turn' = turn

\* in PNF
Next == 
    \E p,q \in ProcSet :
      /\ p # q
      /\ \/ a1(p)
         \/ a2(p) 
         \/ a3(p,q) 
         \/ a4(p,q) 
         \/ cs(p) 
         \/ a5(p)

Spec == /\ Init /\ [][Next]_vars

Mutex == \A p,q \in ProcSet : (p # q) => ~(pc[p] = "cs" /\ pc[q] = "cs")

Symmetry == Permutations(ProcSet)

Req == \A p,q \in ProcSet :
           /\ pc[p] \in {"a3","a4","cs"} => flag[p]
           \* if p is in cs while q is in a4, then it must be p's turn
           /\ (p#q /\ pc[p] = "cs" /\ pc[q] = "a4") => turn = p
           \* mutex
           /\ (p # q) => ~(pc[p] = "cs" /\ pc[q] = "cs")

TypeOK ==
    /\ turn \in ProcSet
    /\ pc \in [ProcSet -> {"a1","a2","a3","a4","cs","a5"}]
    /\ flag \in [ProcSet -> {TRUE,FALSE}]

\* in PNF
IInv == /\ TypeOK
        /\ Req
        
Initiation == Init => IInv

=============================================================================
\* Modification History
\* Last modified Thu Feb 24 23:57:27 EST 2022 by ianda
\* Created Tue Feb 08 09:55:03 EST 2022 by ianda
