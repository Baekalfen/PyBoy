#!/bin/bash

set -e

python3 setup.py sdist bdist_wheel
# python3 -m twine upload --non-interactive -u '__token__' -p $PYPI_TOKEN dist/*
python3 -m twine upload --non-interactive --repository-url https://test.pypi.org/legacy/ -u '__token__' -p $PYPI_TOKEN_TEST dist/*
