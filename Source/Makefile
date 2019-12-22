
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
	CFLAGS=$(CFLAGS) ${PY} setup.py clean

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
