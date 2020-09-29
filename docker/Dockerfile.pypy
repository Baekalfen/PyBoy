FROM pypy:3

RUN apt-get update && apt-get install -y \
  build-essential \
  libsdl2-dev \
  libtiff5-dev \
  libjpeg-dev \
  zlib1g-dev \
  && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install pyboy

WORKDIR /
