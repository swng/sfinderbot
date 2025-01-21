import json
from os import system as ossystem

# Load JSON data from file
data = open("konbini/dpc.txt").read().splitlines()
pieces = open("konbini/dpcpieces.txt").read().splitlines()

import itertools

debug = True
def system(command):
    global lastcommand
    if(debug):
        print(command)
    ossystem(command)

def generate_permutations(bag, permutation_length):
    elements = list(bag)

    if elements and elements[0] == '^':
        # Negate the list of elements
        elements = [p for p in "IOSZJLT" if p not in elements[1:]]
    else:
        elements = elements[1:-1] if elements[0] == '[' and elements[-1] == ']' else elements

    permutations = [[]]
    result = set()

    # Generate all permutations of the given length
    for i in range(permutation_length):
        permutations = [p + [e] for p in permutations for e in elements if e not in p]

    # Convert each permutation back to a string and add to the result set
    for p in permutations:
        result.add(''.join(p))

    # Convert the result set to a list and return it
    return list(result)

def combine_lists(lists):
    if not lists:
        return []

    result = []

    def combine(index, current):
        if index == len(lists):
            result.append(''.join(current))
            return
        for i in range(len(lists[index])):
            combine(index + 1, current + [lists[index][i]])

    combine(0, [])
    return result

def countpieces(string):
    count = 0
    if("^" in string):
        string = [p for p in "IOSZJLT" if p not in string[string.index("^"):]]
    for char in string:
        if(char in "IOSZJLT"):
            count += 1
    return count

def sfinder_all_permutations(input_str):
    inputs = input_str.split(',')

    # Generate all permutations for each input
    permutations = []
    for input_str in inputs:
        input_str = input_str.replace("^", "[^]").replace("!", "p" + str(countpieces(input_str)))
        if(not "p" in input_str):
            input_str += "p1"
        bag_with_brackets, permutation_length = input_str.split('p')
        if not permutation_length:
            permutation_length = 1

        bag = bag_with_brackets.replace('*', '[IOSZJLT]').replace('[','').replace(']','').upper()

        permutations.append(generate_permutations(bag, int(permutation_length)))

    return combine_lists(permutations)

def repeat_first(s):
    """
    Takes a 4-letter string and returns the string with the repeated character first.
    """
    # Count the number of occurrences of each character in the string
    counts = {}
    for c in s:
        if c in counts:
            counts[c] += 1
        else:
            counts[c] = 1

    # Find the character that occurs more than once
    repeat_char = None
    for c in counts:
        if counts[c] > 1:
            repeat_char = c
            break

    # If there is no repeated character, return the original string
    if repeat_char is None:
        return s

    # Reorder the string so that the repeated character comes first
    first_part = ""
    second_part = ""
    for c in s:
        if c == repeat_char:
            first_part += c
        else:
            second_part += c

    return first_part + second_part

def findrepeat(string):
    unique = []
    for i in string:
        if(i in unique):
            return False
        else:
            unique.append(i)
    return True

queuetogenerate = "*p1,*p7"
permutations = sfinder_all_permutations(queuetogenerate)
# Create an empty dictionary with permutations as keys and empty lists as values
permutations_dict = {}
for i in permutations:
    permutations_dict[i] = []

print(len(data))
for setupindex, glued in enumerate(data):
    print(f"On setup {setupindex + 1}")
    dpcpiece = pieces[setupindex]
    system(f'java -jar sfinder.jar cover --tetfu {glued} -p {dpcpiece},*p7 > coverdata.txt')
    queuescovered = []
    coverdata = [i.split(",") for i in open("output/cover.csv").read().splitlines()[1:]]
    for cover in coverdata:
        if(cover[1] == "O"):
            permutations_dict[cover[0]].append(setupindex)

# Opens a new json file called data-3-covered.json, and then writes the output to the file
with open('konbini/dpccover.json', 'w', encoding="utf-8") as f:
    json.dump(permutations_dict, f)
