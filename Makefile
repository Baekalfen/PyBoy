
.PHONY: build clean run install test benchmark pgo docs docs_linkcheck generate-test-results docs-images

all: build

DEBUG ?= 1
ifeq ($(DEBUG), 1)
    CFLAGS = -w
else
    CFLAGS = -w -DCYTHON_WITHOUT_ASSERTIONS
endif

PY ?= python3
PYPY ?= pypy3
ROOT_DIR ?= $(shell git rev-parse --show-toplevel)
GITHUB_REF ?= "refs/tags/v0.0.0"
PYBOY_VERSION ?= $(shell echo ${GITHUB_REF} | cut -d'/' -f3)
PYTEST_ARGS ?= -n auto -v --dist loadscope
PGO_DIR ?= .pgo
PGO_PROFILE ?= $(PGO_DIR)/pyboy.profdata
PGO_GCC_PROFILE_DIR ?=
PGO_REUSE_PROFILE ?= 0
PGO_HOST_OS := $(shell uname -s)
PGO_ENGINE ?= $(if $(filter Darwin,$(PGO_HOST_OS)),clang,$(if $(filter Linux,$(PGO_HOST_OS)),gcc,unsupported))
PGO_BASE_CFLAGS ?= $(CFLAGS)
PGO_BASE_LDFLAGS ?= $(LDFLAGS)
PGO_BENCHMARKS ?= test_threads_baseline or test_threads_nogil
PGO_TAS_REPLAYS ?=
PGO_TAS_RUNS ?= 1
PGO_TAS_ITERATIONS ?= 1
PGO_TAS_ARGS ?=

ifeq ($(PGO_ENGINE),clang)
PGO_CC ?= clang
PGO_PROFILE_SUBDIR = raw
ifeq ($(shell uname -s),Darwin)
PGO_PROFDATA ?= xcrun llvm-profdata
else
PGO_PROFDATA ?= llvm-profdata
endif
else ifeq ($(PGO_ENGINE),gcc)
PGO_CC ?= $(if $(CC),$(CC),gcc)
PGO_PROFILE_SUBDIR = gcc-profile
else
PGO_PROFILE_SUBDIR = unsupported
PGO_PROFDATA ?= llvm-profdata
endif

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
	CFLAGS="$(CFLAGS)" LDFLAGS="$(LDFLAGS)" ${PY} setup.py build_ext -j $(shell getconf _NPROCESSORS_ONLN) --inplace

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

pgo:
	@set -eu; \
	case "$(PGO_ENGINE)" in clang|gcc) ;; *) echo "PGO is supported on macOS (clang) and Linux (gcc); got $(PGO_ENGINE)" >&2; exit 2;; esac; \
	case "$(PGO_REUSE_PROFILE)" in 0|1) ;; *) echo "PGO_REUSE_PROFILE must be 0 or 1" >&2; exit 2;; esac; \
	pgo_run="$(PGO_DIR)/run-$$(date +%Y%m%d-%H%M%S)-$$$$"; \
	pgo_profile='$(PGO_GCC_PROFILE_DIR)'; \
	if [ "$(PGO_ENGINE)" = gcc ] && [ -z "$$pgo_profile" ]; then pgo_profile="$$pgo_run/gcc-profile"; fi; \
	if [ "$(PGO_ENGINE)" = clang ]; then \
		generate_flags="-fprofile-instr-generate"; \
		use_flags="-fprofile-instr-use=$(PGO_PROFILE)"; \
	else \
		generate_flags="-fprofile-generate=$$pgo_profile"; \
		use_flags="-fprofile-use=$$pgo_profile"; \
	fi; \
	profile_ready=0; \
	if [ "$(PGO_REUSE_PROFILE)" = 1 ]; then \
		if [ "$(PGO_ENGINE)" = clang ] && [ -s "$(PGO_PROFILE)" ]; then \
			profile_ready=1; \
		elif [ "$(PGO_ENGINE)" = gcc ] && [ -d "$$pgo_profile" ] && find "$$pgo_profile" -type f -name '*.gcda' -print -quit | grep -q .; then \
			profile_ready=1; \
		fi; \
	fi; \
	if [ "$$profile_ready" = 1 ]; then \
		echo "Reusing cached $(PGO_ENGINE) PGO profile"; \
	else \
		if [ -z '$(strip $(PGO_BENCHMARKS))' ] && [ -z '$(strip $(PGO_TAS_REPLAYS))' ]; then \
			echo "No PGO training workloads selected; set PGO_BENCHMARKS or PGO_TAS_REPLAYS." >&2; exit 2; \
		fi; \
		if [ -n '$(strip $(PGO_TAS_REPLAYS))' ]; then \
			for replay in $(PGO_TAS_REPLAYS); do \
				if [ ! -f "$$replay" ]; then echo "TAS replay not found: $$replay" >&2; exit 2; fi; \
				if [ ! -f "$${replay%.replay}" ]; then echo "TAS replay has no adjacent ROM: $$replay" >&2; exit 2; fi; \
			done; \
		fi; \
		mkdir -p "$$pgo_run/$(PGO_PROFILE_SUBDIR)" "$(dir $(PGO_PROFILE))"; \
		if [ "$(PGO_ENGINE)" = gcc ]; then mkdir -p "$$pgo_profile"; fi; \
		echo "Training $(PGO_ENGINE) PGO profile in $$pgo_run"; \
		$(MAKE) clean; \
		$(MAKE) CC="$(PGO_CC)" CFLAGS="$(PGO_BASE_CFLAGS) $$generate_flags" LDFLAGS="$(PGO_BASE_LDFLAGS) $$generate_flags" build_pyboy; \
		if [ -n '$(strip $(PGO_BENCHMARKS))' ]; then \
			TEST_NO_UI=1 TEST_VERBOSE_IMAGES=0 LLVM_PROFILE_FILE="$$pgo_run/raw/%m-%p.profraw" \
				$(PY) -m pytest -q --benchmark-disable -m benchmark tests/test_benchmark.py -k '$(PGO_BENCHMARKS)'; \
		else \
			echo "Skipping pytest PGO workloads because PGO_BENCHMARKS is empty."; \
		fi; \
		if [ -n '$(strip $(PGO_TAS_REPLAYS))' ]; then \
			LLVM_PROFILE_FILE="$$pgo_run/raw/%m-%p.profraw" \
				$(PY) -m tools.benchmark_tas $(foreach replay,$(PGO_TAS_REPLAYS),--replay "$(replay)") \
					--runs "$(PGO_TAS_RUNS)" --iterations "$(PGO_TAS_ITERATIONS)" $(PGO_TAS_ARGS); \
		else \
			echo "Skipping TAS training; set PGO_TAS_REPLAYS to explicit, non-serial replay files to include TAS workloads."; \
		fi; \
	fi; \
	if [ "$(PGO_ENGINE)" = clang ]; then \
		if [ "$$profile_ready" = 0 ]; then \
			set -- "$$pgo_run"/raw/*.profraw; \
			if [ ! -f "$$1" ]; then echo "No LLVM raw profiles were produced in $$pgo_run/raw" >&2; exit 1; fi; \
			$(PGO_PROFDATA) merge -output="$(PGO_PROFILE)" "$$pgo_run"/raw/*.profraw; \
		fi; \
	else \
		if ! find "$$pgo_profile" -type f -name '*.gcda' -print -quit | grep -q .; then \
			echo "No GCC profile data was produced in $$pgo_profile" >&2; exit 1; \
		fi; \
		echo "GCC profile data in $$pgo_profile"; \
	fi; \
	$(MAKE) clean; \
	$(MAKE) CC="$(PGO_CC)" CFLAGS="$(PGO_BASE_CFLAGS) $$use_flags" LDFLAGS="$(PGO_BASE_LDFLAGS) $$use_flags" build_pyboy; \
	if [ "$(PGO_ENGINE)" = clang ]; then profile_path="$(PGO_PROFILE)"; else profile_path="$$pgo_profile"; fi; \
	echo "$(PGO_ENGINE) PGO-optimized build complete; profile data: $$profile_path"

generate-test-results:
	${PY} ${ROOT_DIR}/docs/generate_test_results.py

docs-images:
	${PY} -m pytest ${ROOT_DIR}/pyboy ${ROOT_DIR}/tests/test_replay.py ${PYTEST_ARGS}
	${PY} -m pytest ${ROOT_DIR}/docs ${PYTEST_ARGS}

docs: generate-test-results
	cd ${ROOT_DIR}/pyboy/plugins && ${PY} manager_gen.py
	${PY} -m sphinx -E -W --keep-going -b html ${ROOT_DIR}/docs ${ROOT_DIR}/docs/_build/html

docs_linkcheck: generate-test-results
	cd ${ROOT_DIR}/pyboy/plugins && ${PY} manager_gen.py
	${PY} -m sphinx -E -W --keep-going -b linkcheck ${ROOT_DIR}/docs ${ROOT_DIR}/docs/_build/linkcheck

repackage_secrets:
	python3 -c 'from conftest import pack_secrets; pack_secrets()'
