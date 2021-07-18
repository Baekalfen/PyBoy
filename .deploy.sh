#!/bin/bash

set -e

if [[ "$OS" == "Windows_NT" && "$MSYS" == "" ]]; then
    echo "Native Windows"
    if [[ "$SDL2_ARCH" == "x64" ]]; then
        echo "x64 $PYTHON_PATH"
        PY="/c/Program Files/Python$PYTHON_PATH/python.exe"
    else
        echo "x86 $PYTHON_PATH"
        PY="/c/Program Files (x86)/Python$PYTHON_PATH-32/python.exe"
    fi
else
    echo "Unix-like"
    PY=python3
fi

echo "$PY"
"$PY" -m pip install wheel twine
"$PY" setup.py sdist bdist_wheel

if [ "$MANYLINUX" ]; then
    "$PY" -m pip install auditwheel
    auditwheel repair dist/*.whl

    # Patching in the correct SDL2
    cd wheelhouse

    yum -y install zip
    for f in *.whl; do
        echo "Patching $f file..."
        SDLNAME=$(unzip -l $f | egrep -wo "(pyboy.libs/libSDL2.*$)")
        mkdir -p pyboy.libs
        cp /usr/local/lib/libSDL2-2.0.so.0 $SDLNAME
        # Updating single SDL2 file in the .zip (.whl)
        zip $f $SDLNAME
    done
    cd ..

    rm -rf dist/*.whl
    mv wheelhouse/*.whl dist/
fi

"$PY" -m twine upload --non-interactive -u '__token__' -p $PYPI_TOKEN dist/*.whl
# "$PY" -m twine upload --non-interactive --repository-url https://test.pypi.org/legacy/ -u '__token__' -p $PYPI_TOKEN_TEST dist/*.whl --verbose

if [ "$PYPI_SOURCE" ]; then
    # Pure source. We can only upload it once. It's randomly done from the mac platform
    "$PY" -m twine upload --non-interactive -u '__token__' -p $PYPI_TOKEN dist/*.tar.gz
    # "$PY" -m twine upload --non-interactive --repository-url https://test.pypi.org/legacy/ -u '__token__' -p $PYPI_TOKEN_TEST dist/*.tar.gz

    # Initiate the Docker Hub build process
    curl -X POST $DOCKER_HUB_BUILD_POST
fi
