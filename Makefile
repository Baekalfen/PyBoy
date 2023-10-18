
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
SHELL:=zsh -o extended_glob +o nomatch -c

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
	${SHELL} 'rm -rf PyBoy.egg-info'
	${SHELL} 'rm -rf build'
	${SHELL} 'rm -rf dist'
	${SHELL} 'rm -rf pyboy/**/__pycache__'
	${SHELL} 'rm -rf pyboy/**/*.pyo'
	${SHELL} 'rm -rf pyboy/**/*.pyc'
	${SHELL} 'rm -rf pyboy/**/*.pyd'
	${SHELL} 'rm -rf pyboy/**/*.so'
	${SHELL} 'rm -rf pyboy/**/*.c'
	${SHELL} 'rm -rf pyboy/**/*.h'
	${SHELL} 'rm -rf pyboy/**/*.dll'
	${SHELL} 'rm -rf pyboy/**/*.lib'
	${SHELL} 'rm -rf pyboy/**/*.exp'
	${SHELL} 'rm -rf pyboy/**/*.html'

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
