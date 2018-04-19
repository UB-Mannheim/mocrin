# docker build -t mocrin .
# docker run -it -v `PWD`:/home/developer/coding/mocrin  mocrin

FROM ubuntu:18.04
ENV PYTHONIOENCODING utf8
COPY  requirements.txt /tmp/

RUN apt-get update && apt-get install --no-install-recommends -y \
  python3 python3-dev python3-pip python3-setuptools python3-tk\
  gcc git openssh-client libutf8proc-dev build-essential \
  libtesseract-dev libleptonica-dev autoconf automake libtool \
  autoconf-archive pkg-config libpng-dev libjpeg8-dev libtiff5-dev  zlib1g-dev tesseract-ocr && \
  pip3 install --upgrade wheel && \
  pip3 install -r ./tmp/requirements.txt &&\
  mkdir -p /home/developer/coding/mocrin/ && \
  cd /home/developer/coding/ &&\
  # git clone https://github.com/tesseract-ocr/tesseract  && \
  git clone https://github.com/JKamlah/tesserocr && \
  python3 ./tesserocr/setup.py build_ext -I/usr/local/include && \
  git clone https://github.com/JKamlah/ocropy/tree/extended-hocr && \
  python3 ./ocropy/setup.py install && \
  apt-get clean


#ENV PATH=$PATH:/home/developer/coding/isri-ocr-evaluation-tools/bin/

WORKDIR /home/developer/coding/ocromore/
