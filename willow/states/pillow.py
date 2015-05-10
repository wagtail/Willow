from __future__ import absolute_import

from .base import ImageState
from .files import (
    JPEGImageFileState,
    PNGImageFileState,
    GIFImageFileState,
)
from .buffers import (
    RGBImageBufferState,
    RGBAImageBufferState,
)

import PIL.Image


class PillowImageState(ImageState):
    def __init__(self, image):
        self.image = image

    @ImageState.operation
    def get_size(self):
        return self.image.size

    @ImageState.operation
    def has_alpha(self):
        img = self.image
        return img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)

    @ImageState.operation
    def has_animation(self):
        # Animation is not supported by PIL
        return False

    @ImageState.operation
    def resize(self, size):
        if self.image.mode in ['1', 'P']:
            image = self.image.convert('RGB')
        else:
            image = self.image

        image = image.resize(size, PIL.Image.ANTIALIAS)

        return PillowImageState(image)

    @ImageState.operation
    def crop(self, rect):
        return PillowImageState(self.image.crop(rect))

    @ImageState.operation
    def save_as_jpeg(self, f, quality=85):
        if self.image.mode in ['1', 'P']:
            image = self.image.convert('RGB')
        else:
            image = self.image

        image.save(f, 'JPEG', quality=quality)

    @ImageState.operation
    def save_as_png(self, f):
        self.image.save(f, 'PNG')

    @ImageState.operation
    def save_as_gif(self, f):
        if 'transparency' in self.image.info:
            self.image.save(f, 'GIF', transparency=self.image.info['transparency'])
        else:
            self.image.save(f, 'GIF')

    @classmethod
    @ImageState.converter_from(JPEGImageFileState)
    @ImageState.converter_from(PNGImageFileState)
    @ImageState.converter_from(GIFImageFileState)
    def open(cls, state):
        state.f.seek(0)
        image = PIL.Image.open(state.f)
        image.load()
        return cls(image)

    @ImageState.converter_to(RGBImageBufferState)
    def to_buffer_rgb(self):
        image = self.image

        if image.mode != 'RGB':
            image = image.convert('RGB')

        return RGBImageBufferState(image.size, image.tobytes())

    @ImageState.converter_to(RGBAImageBufferState)
    def to_buffer_rgba(self):
        image = self.image

        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        return RGBAImageBufferState(image.size, image.tobytes())
