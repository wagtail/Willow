import imghdr
import warnings

from .registry import registry
from .utils.deprecation import RemovedInWillow05Warning


class UnrecognisedImageFormatError(IOError):
    pass


class Image(object):
    @classmethod
    def check(cls):
        pass

    @staticmethod
    def operation(func):
        func._willow_operation = True
        return func

    @staticmethod
    def converter_to(to_class, cost=None):
        def wrapper(func):
            func._willow_converter_to = (to_class, cost)
            return func

        return wrapper

    @staticmethod
    def converter_from(from_class, cost=None):
        def wrapper(func):
            if not hasattr(func, '_willow_converter_from'):
                func._willow_converter_from = []

            if isinstance(from_class, list):
                func._willow_converter_from.extend([
                    (sc, cost) for sc in from_class]
                )
            else:
                func._willow_converter_from.append((from_class, cost))

            return func

        return wrapper

    def __getattr__(self, attr):
        # Raise error if attr is not an operation
        if not registry.operation_exists(attr):
            raise AttributeError("%r object has no attribute %r" % (
                self.__class__.__name__, attr
            ))

        try:
            operation = registry.get_operation(type(self), attr)
            new_class = None
        except LookupError:
            operation, new_class, conversion_path, conversion_cost = registry.route_to_operation(type(self), attr)

        def wrapper(*args, **kwargs):
            image = self

            if new_class:
                for converter, _ in conversion_path:
                    image = converter(image)

            return operation(image, *args, **kwargs)

        return wrapper

    # A couple of helpful methods

    @classmethod
    def open(cls, f):
        # Detect image format
        image_format = imghdr.what(f)

        # Find initial class
        initial_class = INITIAL_IMAGE_CLASSES.get(image_format)

        # Give error if initial class not found
        if not initial_class:
            if image_format:
                raise UnrecognisedImageFormatError("Cannot load %s images" % image_format)
            else:
                raise UnrecognisedImageFormatError("Unknown image format")

        # Instantiate initial class
        image = initial_class(f)
        image._original_format = image_format
        return image

    @property
    def original_format(self):
        warnings.warn(
            "Image.original_format has been deprecated and will be removed in a future release.",
            RemovedInWillow05Warning)
        return getattr(self, '_original_format', None)

    def save(self, image_format, output):
        # Get operation name
        operation_name = 'save_as_' + image_format
        return getattr(self, operation_name)(output)


class ImageBuffer(Image):
    def __init__(self, size, data):
        self.size = size
        self.data = data

    @Image.operation
    def get_size(self):
        return self.size


class RGBImageBuffer(ImageBuffer):
    mode = 'RGB'

    @Image.operation
    def has_alpha(self):
        return False

    @Image.operation
    def has_animation(self):
        return False


class RGBAImageBuffer(ImageBuffer):
    mode = 'RGBA'

    @Image.operation
    def has_alpha(self):
        return True

    @Image.operation
    def has_animation(self):
        return False


class ImageFile(Image):
    format_name = None

    def __init__(self, f):
        self.f = f


class JPEGImageFile(ImageFile):
    format_name = 'jpeg'


class PNGImageFile(ImageFile):
    format_name = 'png'


class GIFImageFile(ImageFile):
    format_name = 'gif'


class BMPImageFile(ImageFile):
    format_name = 'bmp'


INITIAL_IMAGE_CLASSES = {
    # A mapping of image formats to their initial class
    'jpeg': JPEGImageFile,
    'png': PNGImageFile,
    'gif': GIFImageFile,
    'bmp': BMPImageFile,
}


# 12 - Make imghdr detect JPEGs based on first two bytes
def test_jpeg(h, f):
    if h[0:1] == b'\377':
        return 'jpeg'

imghdr.tests.append(test_jpeg)
