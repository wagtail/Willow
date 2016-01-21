from __future__ import absolute_import

import os

from willow.image import Image


class BaseOpenCVImage(Image):
    def __init__(self, image, size):
        self.image = image
        self.size = size

    @classmethod
    def check(cls):
        raise ImportError()

    @Image.operation
    def get_size(self):
        return self.size

    @Image.operation
    def has_alpha(self):
        # Alpha is not supported by OpenCV
        return False

    @Image.operation
    def has_animation(self):
        # Animation is not supported by OpenCV
        return False

    def _find_cascade(self, cascade_filename):
        # If a relative path was provided, check local cascades directory
        if not os.path.isabs(cascade_filename):
            cascade_filename = os.path.join(
                    os.path.dirname(os.path.dirname(__file__)),
                    '..',
                    'data/cascades',
                    cascade_filename,
            )
        return cascade_filename


class BaseOpenCVColorImage(BaseOpenCVImage):
    @classmethod
    def from_buffer_rgb(cls, image_buffer):
        raise NotImplementedError()

    # TODO: Converter back to RGBImageBuffer


class BaseOpenCVGrayscaleImage(BaseOpenCVImage):
    face_min_size = (40, 40)
    face_haar_scale = 1.1
    face_min_neighbors = 3
    face_haar_flags = 0

    def detect_features(self):
        raise NotImplementedError()

    def detect_faces(self, cascade_filename='haarcascade_frontalface_alt2.xml'):
        raise NotImplementedError()

    @classmethod
    def from_color(cls, colour_image):
        raise NotImplementedError()
