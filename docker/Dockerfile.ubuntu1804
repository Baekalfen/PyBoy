FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
  build-essential \
  libsdl2-dev \
  python3 \
  python3-pip \
  python3-dev \
  && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip && pip3 install pyboy

WORKDIR /
