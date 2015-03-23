from __future__ import absolute_import

from willow.utils import deprecation

from .base import ImageBackend


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
        wand_image = cls.get_wand_image()
        wand_api = cls.get_wand_api()

        f.seek(0)

        image = wand_image.Image(file=f)
        image.wand = wand_api.library.MagickCoalesceImages(image.wand)
        return cls(image)

    @classmethod
    def get_wand_image(cls):
        import wand.image
        return wand.image

    @classmethod
    def get_wand_api(cls):    
        import wand.api
        return wand.api

    @classmethod
    def check(cls):
        cls.get_wand_image()
        cls.get_wand_api()


@WandBackend.register_operation('get_size')
def get_size(backend):
    return backend.image.size


@WandBackend.register_operation('resize')
@deprecation.deprecated_resize_parameters
def resize(backend, size):
    backend.image.resize(size[0], size[1])


@WandBackend.register_operation('crop')
@deprecation.deprecated_crop_parameters
def crop(backend, rect):
    backend.image.crop(left=rect[0], top=rect[1], right=rect[2], bottom=rect[3])


@WandBackend.register_operation('save_as_jpeg')
def save_as_jpeg(backend, f, quality=85):
    with backend.image.convert('jpeg') as converted:
        converted.compression_quality = quality
        converted.save(file=f)


@WandBackend.register_operation('save_as_png')
def save_as_png(backend, f):
    with backend.image.convert('png') as converted:
        converted.save(file=f)


@WandBackend.register_operation('save_as_gif')
def save_as_gif(backend, f):
    with backend.image.convert('gif') as converted:
        converted.save(file=f)


@WandBackend.register_operation('has_alpha')
def has_alpha(backend):
    return backend.image.alpha_channel


@WandBackend.register_operation('has_animation')
def has_animation(backend):
    return backend.image.animation


@WandBackend.register_operation('get_wand_image')
def get_wand_image(backend):
    return backend.image.clone()
