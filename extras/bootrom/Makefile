
.PHONY: build

all: build

PY := python3
ROOT_DIR := $(shell git rev-parse --show-toplevel)

build:
	${PY} logo_to_tiles.py
	rgbasm -o bootrom_dmg.obj bootrom_dmg.asm
	rgblink -m bootrom_dmg.map -n bootrom_dmg.sym -o bootrom_dmg.gb bootrom_dmg.obj
	rgbfix -p0 -v bootrom_dmg.gb
	head -c 256 bootrom_dmg.gb > ${ROOT_DIR}/pyboy/core/bootrom_dmg.bin

	${PY} logo_to_tiles.py
	rgbasm -o bootrom_cgb.obj bootrom_cgb.asm
	rgblink -m bootrom_cgb.map -n bootrom_cgb.sym -o bootrom_cgb.gb bootrom_cgb.obj
	rgbfix -p0 -v bootrom_cgb.gb
	head -c 256 bootrom_cgb.gb > ${ROOT_DIR}/pyboy/core/bootrom_cgb.bin

clean:
	rm -f logo.asm bootrom_*.map bootrom_*.obj bootrom_*.gb
