import numpy as np

P = (
"        "
"        "
"        "
" xxxxx  "
" xxxxxx "
" xx  xx "
" xx  xx "
" xx  xx "
)

P_ = (
" xxxxxx "
" xxxxx  "
" xx     "
" xx     "
" xx     "
" xx     "
" xx     "
"        "
)

y = (
"        "
" xx  xx "
" xx  xx "
" xx  xx "
" xx  xx "
" xxxxxx "
"  xxxx  "
"   xxx  "
)

y_ = (
"   xx   "
"xxxx    "
"xxx     "
"        "
"        "
"        "
"        "
"        "
)

o = (
"        "
"  xxxx  "
" xxxxxx "
" xx  xx "
" xx  xx "
" xxxxxx "
"  xxxx  "
"        "
)

B_ = (
" xxxxxx "
" xxxxx  "
" xx  xx "
" xx  xx "
" xx  xx "
" xxxxxx "
" xxxxx  "
"        "
)


# https://stackoverflow.com/questions/9475241/split-string-every-nth-character
def split_by_n(seq, n):
    '''A generator to divide a sequence into chunks of n units.'''
    while seq:
        yield seq[:n]
        seq = seq[n:]


np_im_list = []
for tile in [P, P_, y, B_, o, y_]:
    np_im_list.append([[255 if y == ' ' else 0 for y in x] for x in split_by_n(tile, 8)])

np_im = np.array(np_im_list)
tile_count, new_h, new_w = np_im.shape
assert new_w == 8 and new_h == 8, "Only works on tiles"

###########################
# PIL to GB tiles
###########################
data = list(map(lambda x: [], range(tile_count)))
for t in range(tile_count):
    for y in range(8):
        byte = 0
        for x in range(8):
            # B/W color palette
            color = int(np_im[t, y, x] != 255)
            # We pack the pixels as single bits in bytes of 8 pixels.
            # If we write the byte twice in a row, the GB hardware will understand the format.
            byte += (color & 0b1) << (7-x)
        data[t].append(byte)

# print("\n".join(["\n".join([bin(y) for y in x]) for x in data]))
asm_out = ".logo:\n"
for name, t in zip(['P1', 'P2', 'Y1', 'B2', 'O', 'Y2'], data):
    asm_out += f".{name}\n"
    asm_out += "    DB "
    row = []
    for y in t:
        row.append(f"${y:02x}")
    asm_out += ', '.join(row)
    asm_out += '\n'

with open('logo.asm', 'w') as f:
    f.write(asm_out)
