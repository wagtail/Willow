from __future__ import absolute_import

from .base import ImageState


class ImageBufferState(ImageState):
    def __init__(self, size, data):
        self.size = size
        self.data = data

    @ImageState.operation
    def get_size(self):
        return self.size


class RGBImageBufferState(ImageBufferState):
    mode = 'RGB'

    @ImageState.operation
    def has_alpha(self):
        return False

    @ImageState.operation
    def has_animation(self):
        return False


class RGBAImageBufferState(ImageBufferState):
    mode = 'RGBA'

    @ImageState.operation
    def has_alpha(self):
        return True

    @ImageState.operation
    def has_animation(self):
        return False
