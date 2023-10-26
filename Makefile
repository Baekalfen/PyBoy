
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
GITHUB_REF ?= "refs/tags/v0.0.0"
PYBOY_VERSION ?= $(shell echo ${GITHUB_REF} | cut -d'/' -f3)

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
	CFLAGS=$(CFLAGS) ${PY} setup.py build_ext -j $(shell getconf _NPROCESSORS_ONLN) --inplace

clean:
	@echo "Cleaning..."
	rm -rf PyBoy.egg-info
	rm -rf build
	rm -rf dist
	find pyboy/ -type f -name "*.pyo" -delete
	find pyboy/ -type f -name "*.pyc" -delete
	find pyboy/ -type f -name "*.pyd" -delete
	find pyboy/ -type f -name "*.so" -delete
	find pyboy/ -type f -name "*.c" -delete
	find pyboy/ -type f -name "*.h" -delete
	find pyboy/ -type f -name "*.dll" -delete
	find pyboy/ -type f -name "*.lib" -delete
	find pyboy/ -type f -name "*.exp" -delete
	find pyboy/ -type f -name "*.html" -delete
	find pyboy/ -type d -name "__pycache__" -delete

clean_tests:
	${SHELL} 'rm -rf blargg'
	${SHELL} 'rm -rf SameSuite'
	${SHELL} 'rm -rf mooneye'
	${SHELL} 'rm -rf "GB Tests"'

install: build
	${PY} -m pip install .

uninstall:
	${PY} -m pip uninstall pyboy

test: export DEBUG=1
test: clean build test_cython test_pypy

test_cython:
	${PY} -m pytest tests/ -n4 -v

test_pypy:
	${PYPY} -m pytest tests/ -n4 -v

test_all: test

docs: clean
	bash -O extglob -c 'rm -rf -- ${ROOT_DIR}/docs/!(templates|CNAME)'
	mkdir -p ${ROOT_DIR}/docs/templates
	pdoc --html --force -c latex_math=True -c sort_identifiers=False -c show_type_annotations=True --template-dir docs/templates pyboy
	cp -r html/pyboy/ ${ROOT_DIR}/docs/
	rm -rf html

repackage_secrets:
	python3 -c 'from tests.conftest import pack_secrets; pack_secrets()'
