FROM debian:jessie
MAINTAINER Karl Hobley <karlhobley10@gmail.com>

RUN apt-get update && apt-get install -y python3 python3-numpy python3-pillow python3-wand python3-mock

RUN apt-get install -y libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev build-essential cmake git pkg-config libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libatlas-base-dev gfortran python3.4-dev python3-numpy python3-scipy python3-matplotlib ipython3 python3-pandas ipython3-notebook python3-tk libtbb-dev libeigen3-dev yasm libopencore-amrnb-dev libopencore-amrwb-dev libtheora-dev libvorbis-dev libxvidcore-dev libx264-dev libqt4-dev libqt4-opengl-dev sphinx-common texlive-latex-extra libv4l-dev libdc1394-22-dev curl

ADD opencv-3.2.0.tar.gz /opencv

WORKDIR /opencv/opencv-3.2.0
RUN cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D PYTHON_EXECUTABLE=/usr/bin/python3 -D PYTHON_LIBRARY=/usr/lib/x86_64-linux-gnu/libpython3.4m.so -D PYTHON_INCLUDE_DIR=/usr/include/python3.4m/ -D PYTHON_INCLUDE_DIR2=/usr/include/x86_64-linux-gnu/python3.4m/ -D PYTHON_NUMPY_INCLUDE_DIRS=/usr/lib/python3/dist-packages/numpy/core/include/ -D BUILD_opencv_java=OFF .
RUN make && make install

VOLUME ["/src"]
WORKDIR /src
