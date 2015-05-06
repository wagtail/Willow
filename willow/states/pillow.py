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

    @ImageState.converter_from(JPEGImageFileState)
    @ImageState.converter_from(PNGImageFileState)
    @ImageState.converter_from(GIFImageFileState)
    def open(f):
        return PillowImageState(PIL.Image.open(f))
