#!/bin/bash

set -e

export CFLAGS="-I $(python -c 'import numpy; print numpy.get_include()') $CFLAGS"
export CFLAGS="-I /usr/local/include/SDL2/ $CFLAGS"
# export CFLAGS="-L/usr/local/lib $CFLAGS"
export CFLAGS="$(sdl2-config --static-libs) $CFLAGS" # Too many variables, but gives the -L above

# ./clean.sh
# cp ~/Desktop/opcodes.c ~/Desktop/opcodes.so PyBoy/MB/CPU/

python setup.py build_ext --inplace

# python main.py dummy ROMs/pokemon_gold.gbc
python main.py SDL2 ROMs/pokemon_gold.gbc
