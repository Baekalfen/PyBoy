#!/bin/bash

#PyPy + Pygame
# brew install pypy cairo jpeg sdl sdl_image sdl_mixer sdl_ttf libpng libjpeg
# git clone https://github.com/CTPUG/pygame_cffi.git
# pypy setup.py build build_ext -n -I/usr/local/include
# sudo pypy setup.py install build_ext -n -I/usr/local/include

#PyPy + SDL2 + NumPy
brew install pypy sdl2
brew link sdl2
brew install sdl2 sdl2_gfx sdl2_image
pip_pypy install git+https://bitbucket.org/pypy/numpy.git
# Install pySDL2
# https://bitbucket.org/marcusva/py-sdl2/downloads
# extract and do $pypy setup.py install
