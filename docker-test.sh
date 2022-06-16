# Runs the tests using the provided Dockerfile
# Saves having to install OpenCV locally

docker build -f Dockerfile.py3 -t willow-py3 .
docker run --rm -ti -v $(pwd):/src willow-py3 python3 runtests.py --opencv
