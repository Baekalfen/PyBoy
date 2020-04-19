"""Outputs a .asm file that holds the tile data for the boot rom logo"""

TILES = {
    "P1": """
........
........
........
.xxxxx..
.xxxxxx.
.xx..xx.
.xx..xx.
.xx..xx.""",
    "P2": """
.xxxxxx.
.xxxxx..
.xx.....
.xx.....
.xx.....
.xx.....
.xx.....
........""",
    "Y1": """
........
.xx..xx.
.xx..xx.
.xx..xx.
.xx..xx.
.xxxxxx.
..xxxx..
...xxx..""",
    "Y2": """
...xx...
xxxx....
xxx.....
........
........
........
........
........""",
    "O": """
........
..xxxx..
.xxxxxx.
.xx..xx.
.xx..xx.
.xxxxxx.
..xxxx..
........""",
    "B2": """
.xxxxxx.
.xxxxx..
.xx..xx.
.xx..xx.
.xx..xx.
.xxxxxx.
.xxxxx..
........"""
}

asm_out = ".logo:\n"
for name in ["P1", "P2", "Y1", "B2", "O", "Y2"]: # Order is important, so we can't iterate on TILES
    rows = [int(f"0b{row.replace('.', '0').replace('x', '1')}", base=2) for row in TILES[name].split()]
    asm_out += f".{name}\n"
    asm_out += "    DB "
    line = []
    for row in rows:
        line.append(f"${row:02x}")
    asm_out += ", ".join(line)
    asm_out += "\n"

with open("logo.asm", "w") as f:
    f.write(asm_out)
