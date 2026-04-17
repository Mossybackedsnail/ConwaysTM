import re
import sys
if sys.argv.__len__() < 3:
    print("Usage: merger.py [file1] [file2]")
    sys.exit(1)
fname1 = sys.argv[1]
fname2 = sys.argv[2]
oname = "merged.txt"

pattern = re.compile(r"(\d+)\s+([\d\.]+)\s+([\d\.]+)\s+(true|false)\s+(true|false)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)")
trpattern = re.compile(r"(\d+)\s+(\d+)\s+(\S| )\s+(\S| )\s+(LEFT|RIGHT|STAY)")

F1states = []
F1transitions = []
F2states = []
F2transitions = []

F1pairs = {}
F2pairs = {}


curr = 0

maxx = float(0)

with open(fname1) as f:
    file1 = f.read()

for match in re.finditer(pattern, file1):
    F1states.append(list(match.groups()))
    F1pairs[F1states[curr][0]] = curr
    F1states[curr][0] = curr
    xval = float(F1states[curr][1])
    if xval > float(maxx):
        maxx = F1states[curr][1]
    curr += 1

tcurr = 0
for match in re.finditer(trpattern, file1):
    tfrom = match.groups()[0]
    tto = match.groups()[1]
    F1transitions.append(list(match.groups()))
    F1transitions[tcurr][0] = F1states[F1pairs[tfrom]][0]
    F1transitions[tcurr][1] = F1states[F1pairs[tto]][0]
    tcurr += 1


with open(fname2) as f:
    file2 = f.read()

x = 0
for match in re.finditer(pattern, file2):
    F2states.append(list(match.groups()))
    F2pairs[F2states[x][0]] = x
    F2states[x][0] = curr
    newx = float(F2states[x][1]) + float(maxx)
    F2states[x][1] = newx
    x += 1
    curr += 1

tcurr = 0
for match in re.finditer(trpattern, file2):
    tfrom = match.groups()[0]
    tto = match.groups()[1]
    F2transitions.append(list(match.groups()))
    F2transitions[tcurr][0] = F2states[F2pairs[tfrom]][0]
    F2transitions[tcurr][1] = F2states[F2pairs[tto]][0]
    tcurr += 1


with open(oname, "w", newline='') as f:
    print("// Save File for STEM\n// Version 1.11\n\n// State Format: name x y start accept",file=f);
    print("STATES:", file=f)
    for state in F1states:
        print("\t", file=f, end='')
        print(*state, file=f, end='')
        print("\n", file=f, end='')
    for state in F2states:
        print("\t", file=f, end='')
        print(*state, file=f, end='')
        print("\n", file=f, end='')
    print("\n// Transition format: fromStateId toStateId readChar writeChar moveDirection\n// The Character '~' is the catchall character\nTRANSITION:", file=f)
    for tr in F1transitions:
        print("\t", file=f, end='')
        print(*tr, file=f, end='')
        print("\n", file=f, end='')
    for tr in F2transitions:
        print("\t", file=f, end='')
        print(*tr, file=f, end='')
        print("\n", file=f, end='')
    print("\n// Tape format: tapeChar(0) tapeChar(1) ... tapeChar(n)\nTAPE:\n\t0\n\t", file=f)
    print("// Comment format: text:x:y\nCOMMENTS:\n// Comments End\n// Comment box format: x:y:width:height:color", file=f)
    print("COMMENT BOXES:\n// Comment Box End\n", file=f)
    print("Start Triangle Position:0", file=f)