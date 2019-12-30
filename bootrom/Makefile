
.PHONY: build

all: build

PY := python3
ROOT_DIR := $(shell git rev-parse --show-toplevel)

build:
	@echo "Building..."
	# Requires imagemagick
	convert -background none ${ROOT_DIR}/README/pyboy.svg pyboy.png
	${PY} png_to_tiles.py
	rgbasm -o bootrom.obj bootrom.asm
	rgblink -m bootrom.map -n bootrom.sym -o bootrom.gb bootrom.obj
	rgbfix -p0 -v bootrom.gb
	dd skip=0 count=256 if=bootrom.gb of=PYBOY_ROM.bin bs=1
	cp PYBOY_ROM.bin ${ROOT_DIR}/pyboy/core/bootrom.bin
	rm logo.asm pyboy.png PYBOY_ROM.bin
	rm bootrom.gb bootrom.map bootrom.sym bootrom.obj
