
.PHONY: build

all: build

ROOT_DIR := $(shell git rev-parse --show-toplevel)

build:
	rgbasm -o default_rom.obj default_rom.asm
	rgblink -m default_rom.map -n default_rom.sym -o default_rom.gb default_rom.obj
	rgbfix -p0 -f hg default_rom.gb
	cp default_rom.gb ${ROOT_DIR}/pyboy/default_rom.gb

clean:
	rm -f default_rom.map default_rom.obj
