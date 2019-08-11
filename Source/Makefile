
.PHONY: build clean run install test

all: build

PY := python3
PYPY := pypy3
NUMPY := $(shell ${PY} -c 'import numpy; print(numpy.get_include())')
SDL := $(shell sdl2-config --cflags --libs)

build:
	@echo "Building..."
	CFLAGS='-w' ${PY} setup.py build_ext --inplace -I${NUMPY} ${SDL}

clean:
	@echo "Cleaning..."
	find pyboy/ -name "*.pyo" -delete
	find pyboy/ -name "*.pyc" -delete
	find pyboy/ -name "*.so" -delete
	find pyboy/ -name "*.c" -delete
	find pyboy/ -name "*.h" -delete
	find pyboy/ -name "*.html" -delete
	find pyboy/ -name "__pycache__" -d -delete
	rm -rf ./build
	rm -rf ./dist
	rm -rf ./PyBoy.egg-info


run: build
	${PY} main.py SDL2 ROMs/POKEMON\ BLUE.gb

install:
	CFLAGS='-w' ${PY} setup.py install build_ext -I${NUMPY} ${SDL}

test: clean build
	${PY} tetris_bot.py ROMs/Tetris.gb
	${PYPY} tetris_bot.py ROMs/Tetris.gb
	${PY} -m pytest
	${PYPY} -m pytest


