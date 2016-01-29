FROM debian:jessie
MAINTAINER Karl Hobley <karlhobley10@gmail.com>

RUN apt-get update && apt-get install -y python python-opencv python-numpy python-pillow python-wand python-mock

VOLUME ["/src"]
WORKDIR /src
