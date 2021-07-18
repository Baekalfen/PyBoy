FROM ubuntu:18.04
RUN apt update && apt install -y \
  build-essential \
  libsdl2-dev \
  libtiff5-dev \
  libjpeg8-dev \
  zlib1g-dev \
  curl \
  && rm -rf /var/lib/apt/lists/*

ARG pypy_version=pypy3.6-v7.3.2-linux64
RUN curl -OL "https://downloads.python.org/pypy/$pypy_version.tar.bz2" && tar -xvf "$pypy_version.tar.bz2"
ENV PATH="/$pypy_version/bin:${PATH}"

RUN pypy3 -m ensurepip && pypy3 -m pip install --upgrade pip && pypy3 -m pip install pyboy

WORKDIR /
