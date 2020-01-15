FROM python:buster

RUN apt-get update && apt-get install -y \
  build-essential \
  libsdl2-dev \
  && rm -rf /var/lib/apt/lists/*


RUN pip install -r requierments.txt

COPY . /source
WORKDIR /source

RUN pip install .

WORKDIR /
