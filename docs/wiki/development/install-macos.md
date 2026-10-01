# Install PyBoy on macOS

Install Python 3 if it is not already available. You can use
[Homebrew](https://brew.sh):

```sh
brew install python
```

## Recommended: install from PyPI

Create and activate a virtual environment, then install PyBoy from PyPI:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pyboy
```

## Build from source

If the Xcode Command Line Tools are not already installed, install them to get
the C compiler and `make`:

```sh
xcode-select --install
```

Install [RGBDS](https://rgbds.gbdev.io/install) to build the custom boot ROM
and example ROM. From the root of a PyBoy source checkout, use the virtual
environment created above. If you skipped the PyPI installation, create and
activate one with:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Then install the project requirements and build:

```sh
python -m pip install -r requirements.txt
make build
```

This compiles the Cython extensions and custom ROMs. To force a clean rebuild
when generated files may be stale, run `make clean && make`.

To install the source checkout as a package, run `python -m pip install .` from
the repository root. When testing an installed package, work from outside the
source tree so Python does not import the uncompiled local package.

To launch PyBoy and learn the keyboard controls, see
[Running PyBoy](getting-started).
