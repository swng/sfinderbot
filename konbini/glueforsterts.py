from os import system

unglueddata = open("konbini/second.txt").read().splitlines()
glueddata = open("konbini/second.txt", "w")

def glue(glued):
    system(f"node glueFumens.js {glued} > ezsfinder.txt")
    return(open("ezsfinder.txt").read().replace("\n", ""))

v = len(unglueddata)
print(v)
for v, i in enumerate(unglueddata):
    print(v)
    glueddata.write(glue(i))
    glueddata.write("\n")

glueddata.close()
