# Contributing

Contributions are welcome. Please review the open issues and discuss larger
changes with the community before starting work. If you have a question or
want to discuss an idea, join the [PyBoy Discord](https://discord.gg/wUbag3KNqQ).

For build requirements and compiling PyBoy, see [Getting
started](getting-started). For the emulator structure and test commands, see
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

## Make changes easy to review

Keep each change focused and explain the behavior it changes. Add a regression
test when fixing a bug or changing a public behavior. Prefer small, targeted
tests while developing, then run the complete relevant suite before requesting
review.

For changes to the compiled core or Cython-backed code, rebuild before testing:

```sh
make clean
make
python3 -m pytest tests/ -v
```

Run the API and documentation doctests against the compiled extension:

```sh
make build
python3 -m pytest pyboy/ docs/ -v
```

When changing documentation, build it locally and check generated links:

```sh
make docs
make docs-linkcheck
```

Docstrings contain pytest-managed examples. Keep those examples executable
when changing public APIs.
