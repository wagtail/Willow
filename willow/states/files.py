
from __future__ import absolute_import

from .base import ImageState


class ImageFileState(ImageState):
    def __init__(self, f):
        self.f = f


class JPEGImageFileState(ImageFileState):
    pass


class PNGImageFileState(ImageFileState):
    pass


class GIFImageFileState(ImageFileState):
    pass
