# coding=utf-8
import csv
import sys
import argparse
from py_fumen_util import assemble

parser = argparse.ArgumentParser()
parser.add_argument("--csv-path", default=r".\output\cover.csv", help=r"Defaults to output\cover.csv.")
parser.add_argument("--output-file-path", default="", help="Appends '_to_path' to the input csv file by default. Note to keep the .csv extenstion.")
args = parser.parse_args(sys.argv[1:])

InputCSV = []
for row in csv.reader(open(args.csv_path, 'r')):
    InputCSV.append(row)
# print(InputCSV)

# grabs the list of fumens and convert to a one-page fumen for path format
ungluedRow = assemble(InputCSV[0][1:])
# print(ungluedRow)

OutputCSV = []
OutputCSV.append(["pattern", "solutionCount", "solutions", "unusedMinos", "fumens"]) # QoL, not read by strict-minimal

for row in InputCSV[1:]: 
    sequence = row[0]

    # collect all fumens that can be built by the current queue according to cover
    SuccessFumens = []
    for element, fumen in zip(row[1:], ungluedRow):
        if (element == 'O'):
            SuccessFumens.append(fumen)
            # print(SuccessFumens)
    OutputCSV.append([sequence, len(SuccessFumens), '', '', ";".join(SuccessFumens)])
# print(OutputCSV)

# use specified output file path, otherwise append "_to_path" to the input csv file
OutputFilePath = ""
if (args.output_file_path != ""):
    OutputFilePath = args.output_file_path
else:
    extentionPos = args.csv_path.find(".csv")
    OutputFilePath = args.csv_path[:extentionPos] + "_to_path" + args.csv_path[extentionPos:]

print(f"writing to file: {OutputFilePath}")

# overwrites file if it exists
OutputFileWriter = csv.writer(open(OutputFilePath, 'w', newline=''))
for row in OutputCSV:
    OutputFileWriter.writerow(row)