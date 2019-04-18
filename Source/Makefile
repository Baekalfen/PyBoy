
.PHONY: build clean run install

all: build

PY := python3
NUMPY := $(shell ${PY} -c 'import numpy; print(numpy.get_include())')
SDL := $(shell sdl2-config --cflags --libs)

build:
	@echo "Building..."
	CFLAGS='-w' ${PY} setup.py build_ext --inplace -I${NUMPY} ${SDL}

clean:
	@echo "Cleaning..."
	find . -name "*.pyo" -delete
	find . -name "*.pyc" -delete
	find . -name "*.so" -delete
	find . -name "*.c" -delete
	find . -name "*.h" -delete
	find . -name "*.html" -delete
	find . -name "__pycache__" -d -delete
	rm -rf ./build

run: build
	${PY} main.py SDL2 ROMs/POKEMON\ BLUE.gb

install:
	${PY} setup.py install
