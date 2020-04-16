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

if [ "$MANYLINUX" ]; then
    "$PY" -m pip install auditwheel
    auditwheel repair dist/*.whl
    rm -rf dist/*.whl
    mv wheelhouse/*.whl dist/
    # Pure source. We can only upload it once. It's randomly done from the manylinux platform
    "$PY" -m twine upload --non-interactive --repository-url https://test.pypi.org/legacy/ -u '__token__' -p $PYPI_TOKEN_TEST dist/*.tar.gz --verbose
fi

# "$PY" -m twine upload --non-interactive -u '__token__' -p $PYPI_TOKEN dist/*
"$PY" -m twine upload --non-interactive --repository-url https://test.pypi.org/legacy/ -u '__token__' -p $PYPI_TOKEN_TEST dist/*.whl --verbose

if [ "$PYPI_SOURCE" ]; then
    # Initiate the Docker Hub build process
    curl -X POST $DOCKER_HUB_BUILD_POST
fi
