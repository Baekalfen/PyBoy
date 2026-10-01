# Install PyBoy on Windows

Install a current 64-bit release of
[Python 3](https://www.python.org/downloads/windows/). The Python installer
includes the `py` launcher used below.

## Recommended: install from PyPI

In PowerShell, create and activate a virtual environment, then install PyBoy
from PyPI:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pyboy
```

If PowerShell does not allow activation scripts, install using the virtual
environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install pyboy
```

To launch PyBoy without activating the environment, run
`.\.venv\Scripts\python.exe -m pyboy path\to\rom.gb`.

## Build from source

Install the Visual Studio
[Build Tools](https://visualstudio.microsoft.com/downloads/) and select
**Desktop development with C++** in the installer. From the root of a PyBoy
source checkout, use the virtual environment created above. If you skipped
the PyPI installation, create and activate one with:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project requirements and build the Cython extension in place:

```powershell
python -m pip install -r requirements.txt
python setup.py build_ext --inplace
```

Building the custom ROMs also requires [RGBDS](https://rgbds.gbdev.io/install)
and a `make`-compatible environment. To install the source checkout as a
package, run `python -m pip install .` from the repository root. When testing
an installed package, work from outside the source tree so Python does not
import the uncompiled local package.

## Windows Subsystem for Linux

From PowerShell, install an Ubuntu distribution with `wsl --install`. Then
follow the [Linux installation instructions](install-linux). For GUI and
audio support under WSL, install the required system libraries if they are
missing:

```sh
sudo apt install libgl1 libpulse0
```

WSL 1 requires a separately configured X server for graphical output. The
`DISPLAY` value and OpenGL settings depend on the X server and WSL network
configuration; consult the X server's setup instructions. To build from source
inside WSL, follow the source-build section of the
[Linux guide](install-linux).

To launch PyBoy and learn the keyboard controls, see
[Running PyBoy](getting-started).
