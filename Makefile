
.PHONY: build clean run install test

all: build

DEBUG ?= 1
ifeq ($(DEBUG), 1)
    CFLAGS='-w'
else
    CFLAGS='-w -DCYTHON_WITHOUT_ASSERTIONS'
endif

PY := python3
PYPY := pypy3
ROOT_DIR := $(shell git rev-parse --show-toplevel)

dist: clean build
	${PY} setup.py sdist bdist_wheel
	${PY} -m twine upload dist/pyboy-${version}*

codecov: clean
	@echo "Finding code coverage..."
	CFLAGS='-w -DCYTHON_TRACE=1' ${PY} setup.py build_ext --inplace --codecov-trace
	${PY} setup.py test --codecov-trace
	codecov

build:
	@echo "Building..."
	CFLAGS=$(CFLAGS) ${PY} setup.py build_ext --inplace

clean:
	@echo "Cleaning..."
	CFLAGS=$(CFLAGS) ${PY} setup.py clean --inplace

install: build
	${PY} -m pip install .

uninstall:
	${PY} -m pip uninstall pyboy

test: clean build
	${PY} setup.py test
	${PYPY} setup.py test

test_quick: clean build
	${PY} setup.py test

docs: clean
	pdoc --html --force pyboy
	cp html/pyboy/windowevent.html ${ROOT_DIR}/docs/
	cp html/pyboy/pyboy.html ${ROOT_DIR}/docs/
	cp -r html/pyboy/botsupport ${ROOT_DIR}/docs/
	rm -rf html
