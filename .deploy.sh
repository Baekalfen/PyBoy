#!/bin/bash

set -e

if [[ "$OS" == "Windows_NT" && "$MSYS" == "" ]]; then
    echo "Native Windows"
    PY='/c/Program Files/Python37/python.exe'
else
    echo "Unix-like"
    PY=python3
fi

"$PY" -m pip install wheel twine

"$PY" setup.py sdist bdist_wheel
# $PY -m twine upload --non-interactive -u '__token__' -p $PYPI_TOKEN dist/*
"$PY" -m twine upload --non-interactive --repository-url https://test.pypi.org/legacy/ -u '__token__' -p $PYPI_TOKEN_TEST dist/* --verbose
