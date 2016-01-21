from __future__ import absolute_import

import cv2
import numpy

from willow.image import Image, RGBImageBuffer
from willow.plugins.opencv.base import BaseOpenCVColorImage
from willow.plugins.opencv.base import BaseOpenCVGrayscaleImage


class OpenCVColorImage(BaseOpenCVColorImage):
    @classmethod
    def check(cls):
        pass

    @classmethod
    @Image.converter_from(RGBImageBuffer)
    def from_buffer_rgb(cls, image_buffer):
        image = numpy.frombuffer(image_buffer.data, dtype=numpy.uint8)
        image = image.reshape(image_buffer.size[1], image_buffer.size[0], 3)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return cls(image, image_buffer.size)


class OpenCVGrayscaleImage(BaseOpenCVGrayscaleImage):
    @classmethod
    def check(cls):
        pass

    @Image.operation
    def detect_features(self):
        points = cv2.goodFeaturesToTrack(self.image, 20, 0.04, 1.0)
        return points

    @Image.operation
    def detect_faces(self, cascade_filename='haarcascade_frontalface_alt2.xml'):
        # If a relative path was provided, check local cascades directory
        cascade_filename = self._find_cascade(cascade_filename)

        # Load cascade file
        cascade = cv2.CascadeClassifier(cascade_filename)

        # Equalise the images histogram
        equalised_image = cv2.equalizeHist(self.image)

        # Detect faces
        faces = cascade.detectMultiScale(equalised_image,
                                         self.face_haar_scale,
                                         self.face_min_neighbors,
                                         self.face_haar_flags,
                                         self.face_min_size)
        return [
            (
                face[0],
                face[1],
                face[0] + face[2],
                face[1] + face[3],
            ) for face in faces
            ]

    @classmethod
    @Image.converter_from(BaseOpenCVColorImage)
    def from_color(cls, colour_image):
        image = cv2.cvtColor(colour_image.image, cv2.COLOR_BGR2GRAY)
        return cls(image, colour_image.size)
