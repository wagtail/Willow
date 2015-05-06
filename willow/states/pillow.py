from __future__ import absolute_import

from .base import ImageState
from .files import (
    JPEGImageFileState,
    PNGImageFileState,
    GIFImageFileState,
)


class PillowImageState(ImageState):
    def __init__(self, image):
        self.image = image

    @ImageState.operation('get_size')
    def get_size(self):
        return self.image.size

    @ImageState.converter_from(JPEGImageFileState)
    @ImageState.converter_from(PNGImageFileState)
    @ImageState.converter_from(GIFImageFileState)
    def open(f):
        return PillowImageState(PIL.Image.open(f))
