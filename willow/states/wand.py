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


def _wand_image():
    import wand.image
    return wand.image


def _wand_api():
    import wand.api
    return wand.api


class WandImageState(ImageState):
    def __init__(self, image):
        self.image = image

    @classmethod
    def check(cls):
        _wand_image()
        _wand_api()

    @ImageState.operation
    def get_size(self):
        return self.image.size

    @ImageState.operation
    def has_alpha(self):
        return self.image.alpha_channel

    @ImageState.operation
    def has_animation(self):
        return self.image.animation

    @ImageState.operation
    def resize(self, size):
        self.image.resize(size[0], size[1])
        return self

    @ImageState.operation
    def crop(self, rect):
        self.image.crop(left=rect[0], top=rect[1], right=rect[2], bottom=rect[3])
        return self

    @ImageState.operation
    def save_as_jpeg(self, f, quality=85):
        with self.image.convert('jpeg') as converted:
            converted.compression_quality = quality
            converted.save(file=f)

    @ImageState.operation
    def save_as_png(self, f):
        with self.image.convert('png') as converted:
            converted.save(file=f)

    @ImageState.operation
    def save_as_gif(self, f):
        with self.image.convert('gif') as converted:
            converted.save(file=f)

    @classmethod
    @ImageState.converter_from(JPEGImageFileState)
    @ImageState.converter_from(PNGImageFileState)
    @ImageState.converter_from(GIFImageFileState)
    def open(cls, state):
        image = _wand_image().Image(file=state.f)
        image.wand = _wand_api().library.MagickCoalesceImages(image.wand)
        return cls(image)

    @ImageState.converter_to(RGBImageBufferState)
    def to_buffer_rgb(self):
        return RGBImageBufferState(self.image.size, self.image.make_blob('RGB'))

    @ImageState.converter_to(RGBAImageBufferState)
    def to_buffer_rgba(self):
        return RGBImageBufferState(self.image.size, self.image.make_blob('RGBA'))
