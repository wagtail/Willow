from __future__ import absolute_import

from .base import ImageBackend


def import_wand_image():
    import wand.image
    return wand.image


def import_wand_api():
    import wand.api
    return wand.api


class WandBackend(ImageBackend):
    def __init__(self, image):
        self.image = image

    def to_buffer(self):
        return 'RGB', self.image.size, self.image.make_blob('RGB')

# DOESNT WORK. SEE: https://github.com/dahlia/wand/issues/123
#    @classmethod
#    def from_buffer(cls, buf):
#        mode, size, data = buf
#        return cls(Image(blob=data, format=mode, width=size[0], height=size[1]))

    @classmethod
    def from_file(cls, f):
        wand_image = import_wand_image()
        wand_api = import_wand_api()

        f.seek(0)

        image = wand_image.Image(file=f)
        image.wand = wand_api.library.MagickCoalesceImages(image.wand)
        return cls(image)

    @classmethod
    def check(cls):
        import_wand_image()
        import_wand_api()

    @ImageBackend.operation
    def get_size(backend):
        return backend.image.size

    @ImageBackend.operation
    def resize(backend, size):
        backend.image.resize(size[0], size[1])

    @ImageBackend.operation
    def crop(backend, rect):
        backend.image.crop(left=rect[0], top=rect[1], right=rect[2], bottom=rect[3])

    @ImageBackend.operation
    def save_as_jpeg(backend, f, quality=85):
        with backend.image.convert('jpeg') as converted:
            converted.compression_quality = quality
            converted.save(file=f)

    @ImageBackend.operation
    def save_as_png(backend, f):
        with backend.image.convert('png') as converted:
            converted.save(file=f)

    @ImageBackend.operation
    def save_as_gif(backend, f):
        with backend.image.convert('gif') as converted:
            converted.save(file=f)

    @ImageBackend.operation
    def has_alpha(backend):
        return backend.image.alpha_channel

    @ImageBackend.operation
    def has_animation(backend):
        return backend.image.animation

    @ImageBackend.operation
    def get_wand_image(backend):
        return backend.image.clone()
