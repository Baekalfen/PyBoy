FROM python:buster

RUN apt-get update && apt-get install -y \
  libsdl2-dev\
  build-essential\
 && rm -rf /var/lib/apt/lists/*

ADD . /source
WORKDIR /source


#TODO: make this not needed later (when run pip install . does deps aswell)
RUN pip install cython pysdl2 numpy pillow

RUN pip install .

WORKDIR /
