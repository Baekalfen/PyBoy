
.PHONY: build clean run install test benchmark docs

all: build

DEBUG ?= 1
ifeq ($(DEBUG), 1)
    CFLAGS='-w'
else
    CFLAGS='-w -DCYTHON_WITHOUT_ASSERTIONS'
endif

PY ?= python3
PYPY ?= pypy3
ROOT_DIR := $(shell git rev-parse --show-toplevel)
GITHUB_REF ?= "refs/tags/v0.0.0"
PYBOY_VERSION ?= $(shell echo ${GITHUB_REF} | cut -d'/' -f3)
PYTEST_ARGS ?= -n auto -v

dist: clean build
	${PY} setup.py sdist bdist_wheel
	${PY} -m twine upload dist/pyboy-${version}*

codecov: clean
	@echo "Finding code coverage..."
	CFLAGS='-w -DCYTHON_TRACE=1' ${PY} setup.py build_ext --inplace --codecov-trace
	${PY} setup.py test --codecov-trace
	codecov

build_rom:
	@echo "Building ROMs..."
	cd ${ROOT_DIR}/extras/default_rom && $(MAKE)
	cd ${ROOT_DIR}/extras/bootrom && $(MAKE)

build_pyboy:
	@echo "Building PyBoy..."
	CFLAGS=$(CFLAGS) ${PY} setup.py build_ext -j $(shell getconf _NPROCESSORS_ONLN) --inplace

build: build_rom build_pyboy

clean:
	@echo "Cleaning..."
	cd ${ROOT_DIR}/extras/default_rom && $(MAKE) clean
	cd ${ROOT_DIR}/extras/bootrom && $(MAKE) clean
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
test: clean test_pypy test_cpython_doctest build test_cython benchmark

test_cpython_doctest:
	${PY} -m pytest pyboy/ ${PYTEST_ARGS}

test_cython:
	${PY} -m pytest tests/ ${PYTEST_ARGS}

test_pypy:
	${PYPY} -m pytest tests/ pyboy/ ${PYTEST_ARGS}

test_all: test

benchmark:
	${PY} -m pytest -m benchmark tests/test_benchmark.py --benchmark-enable --benchmark-min-rounds=10

docs: clean
	find ./docs -type f ! -path "./docs/templates/*" ! -path "./docs/CNAME" ! -name "*.png" -exec rm -rf {} +
	mkdir -p ${ROOT_DIR}/docs/templates
	cd ${ROOT_DIR}/pyboy/plugins && ${PY} manager_gen.py
	pdoc --html --force -c latex_math=True -c sort_identifiers=False -c show_type_annotations=True --template-dir docs/templates pyboy
	cp -r html/pyboy/ ${ROOT_DIR}/docs/
	rm -rf html

repackage_secrets:
	python3 -c 'from tests.conftest import pack_secrets; pack_secrets()'
