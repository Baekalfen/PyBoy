FROM python:3-alpine

RUN apk add \
  build-base \
  jpeg-dev \
  sdl2 \
  sdl2-dev \
  zlib-dev

RUN pip install --upgrade pip && pip install pyboy

WORKDIR /
