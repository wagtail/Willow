from .base import ImageBackend


class PillowBackend(ImageBackend):
    def __init__(self, image):
        self.image = image

    def to_buffer(self):
        image = self.image

        if image.mode not in ['RGB', 'RGBA']:
            if 'A' in image.mode:
                image = image.convert('RGBA')
            else:
                image = image.convert('RGB')

        return image.mode, image.size, image.tobytes()

    @classmethod
    def from_buffer(cls, buf):
        mode, size, data = buf
        return cls(cls.get_pillow_image().frombytes(mode, size, data))

    def to_file(self, f):
        return self.image.save(f, 'PNG')

    @classmethod
    def from_file(cls, f):
        f.seek(0)
        image = cls.get_pillow_image().open(f)
        image.load()
        return cls(image)

    @classmethod
    def get_pillow_image(cls):
        import PIL.Image
        return PIL.Image

    @classmethod
    def check(cls):
        cls.get_pillow_image()


@PillowBackend.register_operation('get_size')
def pillow_get_size(backend):
    return backend.image.size


@PillowBackend.register_operation('resize')
def pillow_resize(backend, width, height):
    if backend.image.mode in ['1', 'P']:
        backend.image = backend.image.convert('RGB')

    backend.image = backend.image.resize(
        (width, height), backend.get_pillow_image().ANTIALIAS)


@PillowBackend.register_operation('crop')
def pillow_crop(backend, left, top, right, bottom):
    backend.image = backend.image.crop((left, top, right, bottom))


@PillowBackend.register_operation('save_as_jpeg')
def pillow_save_as_jpeg(backend, f, quality=85):
    backend.image.save(f, 'JPEG', quality=quality)


@PillowBackend.register_operation('save_as_png')
def pillow_save_as_png(backend, f):
    backend.image.save(f, 'PNG')
