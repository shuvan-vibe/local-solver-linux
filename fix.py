import sys

filename = r'd:\NoCapFoxi\local-solver\main.py'
with open(filename, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Dedent lines 100 to 164 (index 99 to 163) by 4 spaces
for i in range(99, 165):
    if lines[i].startswith("    "):
        lines[i] = lines[i][4:]

with open(filename, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed indentation!")
