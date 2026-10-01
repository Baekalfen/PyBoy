# Install PyBoy on Linux

These instructions are for Ubuntu, Debian, and Raspberry Pi OS. Install Python
3 and the virtual-environment support with your system package manager:

```sh
sudo apt update
sudo apt install python3 python3-venv
```

## Recommended: install from PyPI

Create and activate a virtual environment, then install PyBoy from PyPI:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install pyboy
```

On Raspberry Pi OS, compatible ARM wheels may be available through
[piwheels](https://www.piwheels.org/project/pyboy/). Whether pip uses piwheels
depends on your pip configuration.

## Build from source

Install a C compiler and `make`:

```sh
sudo apt install build-essential
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
