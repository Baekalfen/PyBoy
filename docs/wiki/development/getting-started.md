# Getting started

This page covers the Python and native build requirements for developing
PyBoy, followed by compiling the project from source. For the emulator
architecture and test suites, see [Development](development).

## Prerequisites

You need Python 3, a C/C++ compiler for Cython, and
[RGBDS](https://rgbds.gbdev.io/install) to build the custom boot ROM and example
ROM. A virtual environment is recommended.

Clone the repository, activate the virtual environment, and install the
development dependencies:

```sh
python3 -m pip install -r requirements.txt
```

## Building from source

Build PyBoy and the ROM artifacts from the root of the repository:

```sh
make build
```

This compiles the Cython extensions and builds the custom ROMs. Run `make build`
again after changing code backed by Cython. If old generated or compiled files
cause unexpected behavior, clean the repository first:

```sh
make clean
make build
```

To install the current source tree as a package, use:

```sh
python3 -m pip install .
```

When testing an installed package, run PyBoy from a directory outside the
source tree. Otherwise Python may choose the uncompiled `pyboy/` directory in
the repository instead of the compiled package.

## Verify the build

Run a ROM directly from the source tree to verify the build:

```sh
python3 -m pyboy path/to/rom.gb
```
