
.PHONY: build

all: build

PY := python3
ROOT_DIR := $(shell git rev-parse --show-toplevel)

build:
	${PY} logo_to_tiles.py
	rgbasm -o bootrom.obj bootrom.asm
	rgblink -m bootrom.map -n bootrom.sym -o bootrom.gb bootrom.obj
	rgbfix -p0 -v bootrom.gb
	head -c 256 bootrom.gb > ${ROOT_DIR}/pyboy/core/bootrom.bin

clean:
	rm logo.asm bootrom.map bootrom.sym bootrom.obj bootrom.gb
