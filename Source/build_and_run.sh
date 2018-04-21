#!/bin/bash

set -e

export CFLAGS="-I $(python -c 'import numpy; print numpy.get_include()') $CFLAGS"

./clean.sh && cp ~/Desktop/opcodes.c ~/Desktop/opcodes.so PyBoy/MB/CPU/

python setup.py build_ext --inplace

python main.py dummy ROMs/pokemon_gold.gbc
