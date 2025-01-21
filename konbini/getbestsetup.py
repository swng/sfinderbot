from json import loads

allpcdata = {}
for i in range(1, 8):
    allpcdata[i] = {}
    allpcdata[i]["data"] = loads(open(f"konbini/cover{i}.json").read())
    allpcdata[i]["setups"] = open(f"konbini/setups{i}.txt").read().splitlines()
    allpcdata[i]["percent"] = open(f"konbini/percent{i}.txt").read().splitlines()

allpieces = "Tioszjl"
pcnumber = 4

allpieces = allpieces.upper()
allsetups = []

for piecelength in range(3, 7):
    testsetup = allpieces[:piecelength]
    if(testsetup in allpcdata[pcnumber]["data"]):
        workingsetups = allpcdata[pcnumber]["data"][testsetup]
        [allsetups.append(i) for i in workingsetups]

allsetups.sort()
print(allpcdata[pcnumber]["setups"][allsetups[0]])
print(allpcdata[pcnumber]["percent"][allsetups[0]])
