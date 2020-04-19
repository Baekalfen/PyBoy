
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

docker-pypy:
	docker build -f docker/Dockerfile.pypy . -t pyboy:pypy-latest
	docker run -v "${ROOT_DIR}/ROMs:/pyboy/ROMs" -it pyboy:pypy-latest sh -c 'cd pyboy; TEST_CI=1 TEST_NO_UI=1 pypy3 setup.py test'

docker-pypy-slim:
	docker build -f docker/Dockerfile.pypy-slim . -t pyboy:pypy-slim-latest
	docker run -v "${ROOT_DIR}/ROMs:/pyboy/ROMs" -it pyboy:pypy-slim-latest sh -c 'cd pyboy; TEST_CI=1 TEST_NO_UI=1 pypy3 setup.py test'

docker-buster:
	docker build -f docker/Dockerfile.buster . -t pyboy:buster-latest
	docker run -v "${ROOT_DIR}/ROMs:/pyboy/ROMs" -it pyboy:buster-latest sh -c 'cd pyboy; TEST_CI=1 TEST_NO_UI=1 python setup.py test'

docker-alpine:
	docker build -f docker/Dockerfile.alpine . -t pyboy:alpine-latest
	docker run -v "${ROOT_DIR}/ROMs:/pyboy/ROMs" -it pyboy:alpine-latest sh -c 'cd pyboy; TEST_NO_EXAMPLES=1 TEST_CI=1 TEST_NO_UI=1 python setup.py test'

docker-ubuntu1804:
	docker build -f docker/Dockerfile.ubuntu1804 . -t pyboy:ubuntu1804-latest
	docker run -v "${ROOT_DIR}/ROMs:/pyboy/ROMs" -it pyboy:ubuntu1804-latest sh -c 'cd pyboy; TEST_CI=1 TEST_NO_UI=1 python3 setup.py test'

docker-ubuntu1804-ui:
	docker build -f docker/Dockerfile.ubuntu1804 . -t pyboy:ubuntu1804-latest
	docker run -v "${ROOT_DIR}/ROMs:/pyboy/ROMs" -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=host.docker.internal:0 -e XDG_RUNTIME_DIR=/tmp -it pyboy:ubuntu1804-latest sh -c 'cd pyboy; TEST_CI=1 python3 setup.py test'

docker-pypy-ubuntu1804:
	docker build -f docker/Dockerfile.pypy-ubuntu1804 . -t pyboy:pypy-ubuntu1804-latest
	docker run -v "${ROOT_DIR}/ROMs:/pyboy/ROMs" -it pyboy:pypy-ubuntu1804-latest sh -c 'cd pyboy; TEST_CI=1 TEST_NO_UI=1 pypy3 setup.py test'

clean:
	@echo "Cleaning..."
	CFLAGS=$(CFLAGS) ${PY} setup.py clean --inplace

install: build
	${PY} -m pip install .

uninstall:
	${PY} -m pip uninstall pyboy

test: clean build test_cython test_pypy

test_cython:
	${PY} setup.py test

test_pypy:
	${PYPY} setup.py test

test_all: test docker-pypy docker-pypy-slim docker-buster docker-alpine docker-ubuntu1804 docker-pypy-ubuntu1804

docs: clean
	pdoc --html --force -c latex_math=True -c sort_identifiers=False -c show_type_annotations=True --template-dir docs/templates pyboy
	cp -r html/pyboy/ ${ROOT_DIR}/docs/
	rm -rf html

repackage_secrets:
	tar cvf ci_secrets.tar $(shell ${PY} -c "import codecs, sys; print(codecs.encode('EBZf', 'rot13'), end='')")
	travis encrypt-file ci_secrets.tar --pro
	rm ci_secrets.tar
