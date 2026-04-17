import re
import sys
if sys.argv.__len__() < 2:
    print("Usage: rendering.py [file1]")
    sys.exit(1)
fname = sys.argv[1]

pattern = re.compile(r'TAPE:\s*\n\s*(\d+)\s*\n\s*(.*)')

with open(fname) as f:
    file = f.read()

board = ""
for match in re.finditer(pattern, file):
    board = match.group(2)

##print(board)

for char in board:
    if char == '-':
        print('_ ', end='')
    elif char == '+':
        print('■ ', end='')
    elif char == '#':
        print('\n', end='')