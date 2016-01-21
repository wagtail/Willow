from __future__ import absolute_import

import cv

from willow.image import Image, RGBImageBuffer
from willow.plugins.opencv.base import BaseOpenCVColorImage
from willow.plugins.opencv.base import BaseOpenCVGrayscaleImage


class OpenCVColorImage(BaseOpenCVColorImage):
    @classmethod
    def check(cls):
        cv

    @classmethod
    @Image.converter_from(RGBImageBuffer)
    def from_buffer_rgb(cls, image_buffer):
        image = cv.CreateImageHeader(image_buffer.size, cv.IPL_DEPTH_8U, 3)
        cv.SetData(image, image_buffer.data)
        return cls(image, image_buffer.size)

        # TODO: Converter back to RGBImageBuffer


class OpenCVGrayscaleImage(BaseOpenCVGrayscaleImage):
    @classmethod
    def check(cls):
        cv

    @Image.operation
    def detect_features(self):
        rows, cols = self.size

        eig_image = cv.CreateMat(rows, cols, cv.CV_32FC1)
        temp_image = cv.CreateMat(rows, cols, cv.CV_32FC1)
        points = cv.GoodFeaturesToTrack(self.image, eig_image, temp_image, 20, 0.04, 1.0, useHarris=False)

        return points

    @Image.operation
    def detect_faces(self, cascade_filename='haarcascade_frontalface_alt2.xml'):
        cascade_filename = self._find_cascade(cascade_filename)

        # Load cascade file
        cascade = cv.Load(cascade_filename)

        # Equalise the images histogram
        equalised_image = cv.CloneImage(self.image)
        cv.EqualizeHist(self.image, equalised_image)

        # Detect faces
        faces = cv.HaarDetectObjects(
                equalised_image, cascade, cv.CreateMemStorage(0),
                self.haar_scale, self.min_neighbors, self.haar_flags, self.min_size
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
    @Image.converter_from(OpenCVColorImage)
    def from_color(cls, colour_image):
        image = cv.CreateImage(colour_image.size, 8, 1)
        cv.CvtColor(colour_image.image, image, cv.CV_RGB2GRAY)
        return cls(image, colour_image.size)
