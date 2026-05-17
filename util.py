import csv


def get_reachable_queues(queue_str: str):
    """
    Returns an iterator over every queue that is reachable, using 'hold', from the input queue
    """
    if not queue_str:
        yield ""
        return
    
    if len(queue_str) == 1:
        yield queue_str
        return

    for sub_order in get_reachable_queues(queue_str[1:]):
        yield queue_str[0] + sub_order

    for sub_order in get_reachable_queues(queue_str[0] + queue_str[2:]):
        yield queue_str[1] + sub_order


def get_queue_to_holdless(all_queues: list[str], length: int) -> dict[str, list[str]]:
    return {
        queue: [holdless_queue[:length] for holdless_queue in get_reachable_queues(queue)]
        for queue in all_queues
    }

def parse_path_file(filename: str) -> dict[str, list[str]]:
    queue_to_fumens: dict[str, list[str]] = {}

    with open(filename, mode='r') as f:
        csv_reader = csv.reader(f)
        
        # ignore headings
        next(csv_reader, None)
        
        for row in csv_reader:
            assert len(row) == 5

            queue = row[0]
            # Value is semicolon separated strings
            fumen_strings = row[4]
            fumen_list = [v.strip() for v in fumen_strings.split(';')] if fumen_strings else []
            
            queue_to_fumens[queue] = fumen_list

    return queue_to_fumens


def preprocess(    
    queues: list[str], 
    fumens: list[str], 
    holdless_seqs: list[str], 
    holdless_to_fumens: dict[str, list[str]], 
    queue_to_holdless: dict[str, list[str]]
):
    valid_holdless_seqs = [seq for seq in holdless_seqs if holdless_to_fumens.get(seq)]
    valid_holdless_set = set(valid_holdless_seqs)

    new_holdless_to_fumens = {seq: holdless_to_fumens[seq] for seq in valid_holdless_seqs}

    valid_queues = []
    new_queue_to_holdless = {}
    for q in queues:
        valid_connected = [seq for seq in queue_to_holdless.get(q, []) if seq in valid_holdless_set]
        if valid_connected:
            valid_queues.append(q)
            new_queue_to_holdless[q] = valid_connected

    return valid_queues, fumens, valid_holdless_seqs, new_holdless_to_fumens, new_queue_to_holdless


# only removes queues that are not covered
# problem minimisation is done by the solver itself
def prune_uncovered(
    queues: list[str],
    fumens: list[str],
    queue_to_fumens: dict[str, list[str]]
):
    queue_to_fumens_pruned = {
        queue: fumens for queue, fumens in queue_to_fumens.items() if fumens != []
    }
    queues_pruned = [queue for queue in queues if queue in queue_to_fumens_pruned.keys()]

    return queues_pruned, fumens, queue_to_fumens_pruned