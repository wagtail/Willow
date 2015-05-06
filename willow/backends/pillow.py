from __future__ import absolute_import

from .base import ImageBackend


def import_pil_image():
    import PIL.Image
    return PIL.Image


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
        return cls(import_pil_image().frombytes(mode, size, data))

    def to_file(self, f):
        return self.image.save(f, 'PNG')

    @classmethod
    def from_file(cls, f):
        f.seek(0)
        image = import_pil_image().open(f)
        image.load()
        return cls(image)

    @classmethod
    def check(cls):
        import_pil_image()

    @ImageBackend.operation
    def get_size(backend):
        return backend.image.size

    @ImageBackend.operation
    def resize(backend, size):
        if backend.image.mode in ['1', 'P']:
            backend.image = backend.image.convert('RGB')

        backend.image = backend.image.resize(
            size, import_pil_image().ANTIALIAS)

    @ImageBackend.operation
    def crop(backend, rect):
        backend.image = backend.image.crop(rect)

    @ImageBackend.operation
    def save_as_jpeg(backend, f, quality=85):
        if backend.image.mode in ['1', 'P']:
            backend.image = backend.image.convert('RGB')

        backend.image.save(f, 'JPEG', quality=quality)

    @ImageBackend.operation
    def save_as_png(backend, f):
        backend.image.save(f, 'PNG')

    @ImageBackend.operation
    def save_as_gif(backend, f):
        if 'transparency' in backend.image.info:
            backend.image.save(f, 'GIF', transparency=backend.image.info['transparency'])
        else:
            backend.image.save(f, 'GIF')

    @ImageBackend.operation
    def has_alpha(backend):
        img = backend.image
        return img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)

    @ImageBackend.operation
    def has_animation(backend):
        # Animation not supported by PIL
        return False

    @ImageBackend.operation
    def get_pillow_image(backend):
        return backend.image.copy()
