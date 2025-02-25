# This Dockerfile is used to easily run the OpenCV tests without having to install OpenCV on the host machine.
FROM python:3.13-slim-bookworm
RUN apt update && apt install -y imagemagick
RUN pip install opencv-python-headless

WORKDIR /code
COPY . ./
RUN pip install -e .[testing]
CMD [ "python", "./runtests.py", "-v", "--opencv" ]
