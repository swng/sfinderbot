import argparse
from util import parse_path_file
from collections import defaultdict
from solve_direct_ilp import solve_set_cover

# this file takes the same input as the normal sfinder-strict-minimals

def find_minimals(csv_path: str, output_path: str | None = None, timeLimit: int | None = None):
    queue_to_fumens = parse_path_file(csv_path)
    fumen_to_queues = get_inverse_relation(queue_to_fumens)  # actually not used but oh well

    queues = list(queue_to_fumens.keys())
    fumens = list(fumen_to_queues.keys())
    solution = solve_set_cover(queues, fumens, queue_to_fumens, timeLimit=timeLimit)
    
    if not solution:
        return
    
    output = "\n".join(solution)
    print(output)

    if output_path:
        with open(output_path, 'w') as f:
            f.write(output)
            print(f"Wrote output to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Find strict minimals for a path.csv file")
    parser.add_argument("csv_path", help="Path to the input path.csv file")
    parser.add_argument("--output", nargs="?", default=None, help="Optional output file. If omitted, only prints to stdout.")
    parser.add_argument("--timeLimit", type=int, default=None, help="Time limit for the solver in seconds. Default is no limit.")
    args = parser.parse_args()

    find_minimals(args.csv_path, args.output, args.timeLimit)

def get_inverse_relation(queue_to_fumens: dict[str, list[str]]) -> dict[str, list[str]]:
    fumen_to_queues: dict[str, list[str]] = defaultdict(list)
    for queue, fumens in queue_to_fumens.items():
        for fumen in fumens:
            fumen_to_queues[fumen].append(queue)

    return fumen_to_queues


if __name__ == '__main__':
    main()
