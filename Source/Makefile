
.PHONY: build clean run install test

all: build

DEBUG ?= 1
ifeq ($(DEBUG), 1)
    CFLAGS='-w'
else
    CFLAGS='-w -DCYTHON_WITHOUT_ASSERTIONS'
endif

THREADS := 6
PY := python3
PYPY := pypy3
ROOT_DIR := $(shell git rev-parse --show-toplevel)

build:
	@echo "Building..."
	CFLAGS=$(CFLAGS) ${PY} setup.py build_ext --inplace

clean:
	@echo "Cleaning..."
	find ${ROOT_DIR}/Source/pyboy/ -name "*.pyo" -delete
	find ${ROOT_DIR}/Source/pyboy/ -name "*.pyc" -delete
	find ${ROOT_DIR}/Source/pyboy/ -name "*.so" -delete
	find ${ROOT_DIR}/Source/pyboy/ -name "*.c" -delete
	find ${ROOT_DIR}/Source/pyboy/ -name "*.h" -delete
	find ${ROOT_DIR}/Source/pyboy/ -name "*.dll" -delete
	find ${ROOT_DIR}/Source/pyboy/ -name "*.html" -delete
	find ${ROOT_DIR}/Source/pyboy/ -name "__pycache__" -delete
	rm -rf ${ROOT_DIR}/Source/build
	rm -rf ${ROOT_DIR}/Source/dist
	rm -rf ${ROOT_DIR}/Source/PyBoy.egg-info

run: build
	${PY} main.py SDL2 ${ROOT_DIR}/Source/ROMs/POKEMON\ BLUE.gb

install:
	CFLAGS=$(CFLAGS) ${PY} setup.py install build_ext

test: clean build
	${PY} tetris_bot.py ${ROOT_DIR}/Source/ROMs/Tetris.gb --quiet
	${PY} interface_example.py --quiet
	${PY} -m pytest -n${THREADS} -v
	${PYPY} tetris_bot.py ${ROOT_DIR}/Source/ROMs/Tetris.gb --quiet
	${PYPY} interface_example.py --quiet
	${PYPY} -m pytest -n${THREADS} -v

test_quick: clean build
	${PY} -m pytest -n${THREADS} -v

docs: clean
	pdoc --html --force pyboy
	cp html/pyboy/windowevent.html ${ROOT_DIR}/docs/
	cp html/pyboy/pyboy.html ${ROOT_DIR}/docs/
	cp -r html/pyboy/botsupport ${ROOT_DIR}/docs/
	rm -rf html
