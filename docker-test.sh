# Runs the tests using the provided Dockerfile
# Saves having to install OpenCV locally

docker build -t willow-opencv .
docker run --rm -ti -v $(pwd):/code willow-opencv python runtests.py --opencv
