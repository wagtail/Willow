# Runs the tests using the provided Dockerfile
# Saves having to install OpenCV locally

docker build -t willow .
docker run --rm -ti -v $(pwd):/src willow python runtests.py --opencv
