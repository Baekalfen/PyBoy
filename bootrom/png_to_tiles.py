import numpy
import PIL.ImageOps
from PIL import Image

###########################
# PNG loading and resizing
###########################
im = Image.open("pyboy.png")
orig_w, orig_h = im.size

# Find the bbox and crop the rest away. Then we can resize to the target dimensions.
bbox = im.getbbox() # Get bbox before inverting colors. Apparently works by default on black borders.
im = im.crop(bbox)

h = 16
w = int(orig_w * (h/orig_h))

im = im.convert("L") # Convert to b/w.
im = im.resize((w, h), PIL.Image.NEAREST)
im = PIL.ImageOps.invert(im) # b/w looks better when inverted

###########################
# PIL to GB tiles
###########################
data = [[], []]
np_im = numpy.array(im)
new_w, new_h = im.size
for x in range(0, new_w, 8):
    for y in range(new_h):
        byte = 0
        for b in range(8):
            # B/W color palette
            color = int(np_im[y, x+b] != 255)
            # We pack the pixels as single bits in bytes of 8 pixels.
            # If we write the byte twice in a row, the GB hardware will understand the format.
            byte += (color & 0b1) << (7-b)

        # We sort the first and second row of tiles.
        data[(y//8) % 2].append(byte)

row = []

asm_out = f"; bytes: {len(data)}, width: {w}, height: {h}\n"
asm_out += ".logo:\n"
for b in data[0]+data[1]:
    if len(row) == 0:
        asm_out += "    DB "
    row.append(f"${b:02x}")
    if len(row) == 8:
        asm_out += ', '.join(row)
        row = []
        asm_out += '\n'

with open('logo.asm', 'w') as f:
    f.write(asm_out)
