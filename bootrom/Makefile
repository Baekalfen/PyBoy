
.PHONY: build

all: build

build:
	python3 logo_to_tiles.py
	rgbasm -o bootrom.obj bootrom.asm
	rgblink -m bootrom.map -n bootrom.sym -o bootrom.gb bootrom.obj
	rgbfix -p0 -v bootrom.gb
	head -c 256 bootrom.gb > ../pyboy/core/bootrom.bin

clean:
	rm logo.asm bootrom.map bootrom.sym bootrom.obj bootrom.gb
