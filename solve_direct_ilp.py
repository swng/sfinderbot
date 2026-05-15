import pulp

def solve_set_cover(queues, fumens, queue_to_fumens, timeLimit=None):
    prob = pulp.LpProblem("Set_Cover_Optimization", pulp.LpMinimize)

    fumen_vars = pulp.LpVariable.dicts("f", fumens, cat=pulp.LpBinary)

    # objective function to minimise
    prob += pulp.lpSum([fumen_vars[f] for f in fumens])

    for q in queues:
        covering_sets = queue_to_fumens.get(q, [])
        if not covering_sets:
            print(f"{q} has no covering solutions!!")
            continue
        
        # at least one solution covers this queue
        prob += pulp.lpSum([fumen_vars[f] for f in covering_sets]) >= 1

    # --------------------------------------- solver called here (can try different parameters like genRel)
    if timeLimit is None:
        solver = pulp.getSolver('HiGHS', threads=16)
    else:
        solver = pulp.getSolver('HiGHS', threads=16, timeLimit=timeLimit)
    prob.solve(solver)

    if pulp.LpStatus[prob.status] == 'Optimal':
        selected = [f for f in fumens if pulp.value(fumen_vars[f]) > 0.5]
        return selected
    else:
        print(f"Solver failed with {pulp.LpStatus[prob.status]}")
        return None
