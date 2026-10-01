# Contributing

Contributions are welcome. Before starting a substantial change, check the
[open issues](https://github.com/Baekalfen/PyBoy/issues) and discuss the
approach with the community. Questions and proposals can also be discussed on
the [PyBoy Discord](https://discord.gg/wUbag3KNqQ).

For test dependencies, see [Getting started](getting-started); for source
build requirements, see [Install and build](installation).
For emulator architecture and the canonical test commands, see
[Development](development).

## Pre-commit

PyBoy uses [pre-commit](https://pre-commit.com/) to run formatting and linting
before commits. Install it and register the Git hook once:

```sh
python3 -m pip install pre-commit
pre-commit install
```

Run the hooks manually on all files with:

```sh
pre-commit run --all-files
```

The normal commit hook checks staged files. The repository configuration uses
Ruff for linting and formatting, and enables Ruff's automatic fixes. Generated
files such as `opcodes.py`, `manager.py`, and `manager.pxd` are excluded from
the hooks.

## Prepare changes for review

Keep each change focused and describe the behavior it changes. Add or update
regression tests when fixing a bug or changing public behavior. Run the
appropriate test suites from [Development](development) before requesting
review.

For Cython-backed changes, rebuild before testing as described in
[Install and build](installation). Keep docstring and Wiki examples
executable when changing public APIs. For documentation changes, build the site
and check generated links:

```sh
make docs
make docs_linkcheck
```

## Pull requests

Use a separate branch for each contribution. In the pull request description,
explain the problem and solution, link related issues, and list the checks you
ran. Include screenshots for user-visible changes when they help reviewers.
Contributions are distributed under the project's LGPL license; do not include
commercial game ROMs or other files you do not have permission to redistribute.
