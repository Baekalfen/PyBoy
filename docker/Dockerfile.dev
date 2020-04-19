FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
  build-essential \
  libsdl2-dev \
  python3 \
  python3-pip \
  python3-dev \
  libtiff5-dev \
  libjpeg8-dev \
  zlib1g-dev \
  curl \
  && rm -rf /var/lib/apt/lists/*

ARG pypy_version=pypy3.6-v7.3.0-linux64
RUN curl -OL "https://bitbucket.org/pypy/pypy/downloads/$pypy_version.tar.bz2" && tar -xvf "$pypy_version.tar.bz2"
ENV PATH="/$pypy_version/bin:${PATH}"

COPY requirements.txt /
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
RUN pypy3 -m ensurepip && pypy3 -m pip install --upgrade pip && pypy3 -m pip install --no-cache-dir -r requirements.txt

WORKDIR /pyboy

# Work on Mac:
# $ /usr/X11/bin/xhost + 127.0.0.1
# $ docker run -v "$(pwd):/pyboy/" -v "$(pwd)/ROMs:/pyboy/ROMs" -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=host.docker.internal:0 -e XDG_RUNTIME_DIR=/tmp -it baekalfen/pyboy:dev-latest bash

# Work on Ubuntu:
# $ /usr/X11/bin/xhost + 127.0.0.1
# $ docker run -v "$(pwd):/pyboy/" -v "$(pwd)/ROMs:/pyboy/ROMs" -v /tmp/.X11-unix:/tmp/.X11-unix:rw --device=/dev/dri -e DISPLAY -e XDG_RUNTIME_DIR=/tmp -it baekalfen/pyboy:dev-latest bash

# Inside the Docker container:
# Run the cythonized version in CPython:
# $ make clean && make && python3 -m pyboy ROMs/gamerom.gb # ROM path and any other arguments
# Run the PyPy version:
# $ pypy3 -m pyboy ROMs/gamerom.gb # ROM path and any other arguments
