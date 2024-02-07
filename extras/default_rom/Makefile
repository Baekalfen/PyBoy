
.PHONY: build

all: build

ROOT_DIR := $(shell git rev-parse --show-toplevel)

build:
	rgbasm -o default_rom.obj default_rom.asm
	rgblink -m default_rom.map -n default_rom.sym -o default_rom.gb default_rom.obj
	rgbfix -p0 -f hg default_rom.gb
	cp default_rom.gb ${ROOT_DIR}/pyboy/default_rom.gb

	rgbasm -o default_rom_cgb.obj default_rom_cgb.asm
	rgblink -m default_rom_cgb.map -n default_rom_cgb.sym -o default_rom_cgb.gb default_rom_cgb.obj
	rgbfix -p0 -f hg default_rom_cgb.gb
	cp default_rom_cgb.gb ${ROOT_DIR}/pyboy/default_rom_cgb.gb

clean:
	rm -f default_rom.map default_rom.obj
	rm -f default_rom_cgb.map default_rom_cgb.obj
