#!/usr/bin/env python3

import zlib
from base64 import b64encode
from sys import argv

try:
    from PIL import Image
except ImportError:
    Image = None


# THIS IS ONLY MADE FOR 8x16 FONTS AND 256 CHARACTER CODE PAGES
def main(bdffile, unifile, *args):
    class Char:
        def __init__(self, name):
            self.name = name
            self.meta = {}
            self.bits = []

    with open(unifile, "r") as uf:
        uni = list(map(lambda x: int(x, base=16), uf.readlines()))

    chars = {}

    with open(bdffile, "r") as bf:
        while bf.readline().strip() != "ENDPROPERTIES":
            pass
        nchars = int(bf.readline().split()[1])
        for _ in range(nchars):
            token, name = bf.readline().split()
            assert token == "STARTCHAR"
            newchar = Char(name)
            while True:
                line = bf.readline().split()
                if line[0] == "BITMAP":
                    for _ in range(16):
                        newchar.bits += [bytes.fromhex(bf.readline().strip())]
                    assert bf.readline().strip() == "ENDCHAR"
                    chars[int(newchar.meta["ENCODING"])] = newchar
                    break
                else:
                    newchar.meta[line[0]] = line[1:] if len(line) > 2 else line[1]

    chars437 = [chars[n] for n in uni]
    with open("font.txt", "w") as f:
        print(
            """
This project uses a portion of the bold 16 pixel height Terminus font.

The Terminus font is released under the Open Font License, which is
copied in full below.

The full source code for the Terminus font is available at
<terminus-font.sourceforge.net>.

-----------------------------------------------------------
""",
            file=f,
        )

        with open("OFL.txt", "r") as licensefile:
            for line in licensefile.readlines():
                print(line, end="", file=f)
        print("", file=f)

        print("BASE64DATA:", file=f)
        blob = b64encode(zlib.compress(b"".join((b for c in chars437 for b in c.bits))))
        for n in range(0, len(blob), 72):
            print(blob[n : n + 72].decode(), file=f)

    if "--bitmap" in args:
        if not Image:
            print("Cannot create bitmap: Could not import Pillow")
        else:
            buf = bytearray()
            for row in range(16):
                for pixrow in range(16):
                    for col in range(16):
                        buf += chars437[16 * row + col].bits[pixrow]

            image = Image.frombytes("1", (128, 256), bytes(buf))
            image.save("fontsheet.bmp")


if __name__ == "__main__":
    main(*argv[1:])
