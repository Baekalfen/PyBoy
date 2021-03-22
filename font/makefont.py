#!/usr/bin/env python3


from sys import argv
from PIL import Image


# THIS IS ONLY MADE FOR 8x16 FONTS AND 256 CHARACTER CODE PAGES


def main(bdffile, unifile):

    class Char:
        def __init__(self, name):
            self.name = name
            self.meta = {}
            self.bits = []

    with open(unifile, 'r') as uf:
        uni = list(map(lambda x: int(x, base=16), uf.readlines()))

    chars = {}

    with open(bdffile, 'r') as bf:
        while bf.readline().strip() != 'ENDPROPERTIES':
            pass
        nchars = int(bf.readline().split()[1])
        for _ in range(nchars):
            token, name = bf.readline().split()
            assert token == 'STARTCHAR'
            newchar = Char(name)
            while True:
                line = bf.readline().split()
                if line[0] == 'BITMAP':
                    for _ in range(16):
                        newchar.bits += [bytes.fromhex(bf.readline().strip())]
                    assert bf.readline().strip() == 'ENDCHAR'
                    chars[int(newchar.meta['ENCODING'])] = newchar
                    break
                else:
                    newchar.meta[line[0]] = (line[1:] if len(line) > 2
                                             else line[1])

    chars437 = [chars[n] for n in uni]
    with open('fontstring.txt', 'w') as fs:
        for c in chars437:
            print(b''.join(c.bits).hex(), file=fs)

    buf = bytearray()
    for row in range(16):
        for pixrow in range(16):
            for col in range(16):
                buf += chars437[16*row+col].bits[pixrow]

    image = Image.frombytes('1', (128, 256), bytes(buf))
    image.save('fontsheet.bmp')


if __name__ == '__main__':
    main(*argv[1:])
