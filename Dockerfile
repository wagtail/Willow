# This Dockerfile is used to easily run the OpenCV tests without having to install OpenCV on the host machine.
FROM python:3.15-slim-trixie
RUN apt update && apt install -y imagemagick
# Unpin depending on outcome of https://github.com/opencv/opencv-python/issues/1244
RUN pip install "opencv-contrib-python-headless<=5.0.0"

WORKDIR /code
COPY . ./
RUN pip install -e .[testing]
CMD [ "python", "./runtests.py", "-v", "--opencv" ]
