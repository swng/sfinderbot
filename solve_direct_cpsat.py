from ortools.sat.python import cp_model

def solve_set_cover_cp_sat(queues, fumens, queue_to_fumens, timeLimit=None, quiet=False, threads=8):
    model = cp_model.CpModel()

    fumen_vars = {}
    for fumen in fumens:
        fumen_vars[fumen] = model.NewBoolVar(f'subset_{fumen}')

    for queue in queues:
        covering_subsets = queue_to_fumens[queue]
        model.AddBoolOr([fumen_vars[s] for s in covering_subsets])

    model.Minimize(sum(fumen_vars.values()))

    solver = cp_model.CpSolver()
    
    solver.parameters.num_search_workers = threads
    
    if not quiet:
        solver.parameters.log_search_progress = True 

    if timeLimit is not None:
        solver.parameters.max_time_in_seconds = float(timeLimit)

    status = solver.Solve(model)

    selected_subsets = [s for s in fumens if solver.Value(fumen_vars[s])]
    return selected_subsets


