from __future__ import absolute_import

import io
import os

from .base import ImageState
from .buffers import RGBImageBufferState


def _cv():
    import cv
    return cv


class BaseOpenCVImageState(ImageState):
    def __init__(self, image, size):
        self.image = image
        self.size = size

    @classmethod
    def check(cls):
        _cv()

    @ImageState.operation
    def get_size(self):
        return self.size

    @ImageState.operation
    def has_alpha(self):
        # Alpha is not supported by OpenCV
        return False

    @ImageState.operation
    def has_animation(self):
        # Animation is not supported by OpenCV
        return False


class OpenCVColorImageState(BaseOpenCVImageState):
    @classmethod
    @ImageState.converter_from(RGBImageBufferState)
    def from_buffer_rgb(cls, state):
        cv = _cv()

        image = cv.CreateImageHeader(state.size, cv.IPL_DEPTH_8U, 3)
        cv.SetData(image, state.data)
        return cls(image, state.size)

    # TODO: Converter back to RGBImageBufferState


class OpenCVGreyscaleImageState(BaseOpenCVImageState):
    @ImageState.operation
    def detect_features(self):
        cv = _cv()
        rows, cols = self.size

        eig_image = cv.CreateMat(rows, cols, cv.CV_32FC1)
        temp_image = cv.CreateMat(rows, cols, cv.CV_32FC1)
        points = cv.GoodFeaturesToTrack(self.image, eig_image, temp_image, 20, 0.04, 1.0, useHarris=False)

        return points

    @ImageState.operation
    def detect_faces(self, cascade_filename='haarcascade_frontalface_alt2.xml'):
        cv = _cv()

        # If a relative path was provided, check local cascades directory
        if not os.path.isabs(cascade_filename):
            cascade_filename = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'face_detection',
                cascade_filename,
            )

        # Load cascade file
        cascade = cv.Load(cascade_filename)

        # Equalise the images histogram
        equalised_image = cv.CloneImage(self.image)
        cv.EqualizeHist(self.image, equalised_image)

        # Detect faces
        min_size = (40, 40)
        haar_scale = 1.1
        min_neighbors = 3
        haar_flags = 0

        faces = cv.HaarDetectObjects(
            equalised_image, cascade, cv.CreateMemStorage(0),
            haar_scale, min_neighbors, haar_flags, min_size
        )

        return [
            (
                face[0][0],
                face[0][1],
                face[0][0] + face[0][2],
                face[0][1] + face[0][3],
            ) for face in faces
        ]

    @classmethod
    @ImageState.converter_from(OpenCVColorImageState)
    def from_color(cls, state):
        cv = _cv()

        image = cv.CreateImage(state.size, 8, 1)
        cv.CvtColor(state.image, image, cv.CV_RGB2GRAY)
        return cls(image, state.size)
