
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

archive-pyboy:
	git archive -v -o pyboy.tar.gz --format=tar.gz HEAD

docker-pypy: archive-pyboy
	docker build -f Dockerfile.pypy . -t pyboy:pypy-latest
	docker run -v ROMs:/pyboy/ROMs -v "${ROOT_DIR}/tests/BlarggROMs":/pyboy/tests/BlarggROMs -it pyboy:pypy-latest sh -c 'cd pyboy; TEST_DOCKER=1 TEST_NO_UI=1 pypy3 setup.py test'

docker-pypy-slim: archive-pyboy
	docker build -f Dockerfile.pypy-slim . -t pyboy:pypy-slim-latest
	docker run -v ROMs:/pyboy/ROMs -v "${ROOT_DIR}/tests/BlarggROMs":/pyboy/tests/BlarggROMs -it pyboy:pypy-slim-latest sh -c 'cd pyboy; TEST_DOCKER=1 TEST_NO_UI=1 pypy3 setup.py test'

docker-buster: archive-pyboy
	docker build -f Dockerfile.buster . -t pyboy:buster-latest
	docker run -v ROMs:/pyboy/ROMs -v "${ROOT_DIR}/tests/BlarggROMs":/pyboy/tests/BlarggROMs -it pyboy:buster-latest sh -c 'cd pyboy; TEST_DOCKER=1 TEST_NO_UI=1 python setup.py test'

docker-alpine: archive-pyboy
	docker build -f Dockerfile.alpine . -t pyboy:alpine-latest
	docker run -v ROMs:/pyboy/ROMs -v "${ROOT_DIR}/tests/BlarggROMs":/pyboy/tests/BlarggROMs -it pyboy:alpine-latest sh -c 'cd pyboy; TEST_NO_EXAMPLES=1 TEST_DOCKER=1 TEST_NO_UI=1 python setup.py test'

docker-ubuntu1804: archive-pyboy
	docker build -f Dockerfile.ubuntu1804 . -t pyboy:ubuntu1804-latest
	docker run -v ROMs:/pyboy/ROMs -v "${ROOT_DIR}/tests/BlarggROMs":/pyboy/tests/BlarggROMs -it pyboy:ubuntu1804-latest sh -c 'cd pyboy; TEST_DOCKER=1 TEST_NO_UI=1 python3 setup.py test'

docker-ubuntu1804-ui: archive-pyboy
	docker build -f Dockerfile.ubuntu1804 . -t pyboy:ubuntu1804-latest
	docker run -v ROMs:/pyboy/ROMs -v "${ROOT_DIR}/tests/BlarggROMs":/pyboy/tests/BlarggROMs -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=host.docker.internal:0 -e XDG_RUNTIME_DIR=/tmp -it pyboy:ubuntu1804-latest sh -c 'cd pyboy; TEST_DOCKER=1 python3 setup.py test'

docker-pypy-ubuntu1804: archive-pyboy
	docker build -f Dockerfile.pypy-ubuntu1804 . -t pyboy:pypy-ubuntu1804-latest
	docker run -v ROMs:/pyboy/ROMs -v "${ROOT_DIR}/tests/BlarggROMs":/pyboy/tests/BlarggROMs -it pyboy:pypy-ubuntu1804-latest sh -c 'cd pyboy; TEST_DOCKER=1 TEST_NO_UI=1 pypy3 setup.py test'

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

test_all: test docker-pypy docker-pypy-slim docker-buster docker-alpine docker-ubuntu1804 docker-pypy-ubuntu1804

docs: clean
	pdoc --html --force pyboy
	cp html/pyboy/windowevent.html ${ROOT_DIR}/docs/
	cp html/pyboy/pyboy.html ${ROOT_DIR}/docs/
	cp -r html/pyboy/botsupport ${ROOT_DIR}/docs/
	rm -rf html
