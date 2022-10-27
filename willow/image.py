import re

import filetype
import warnings

from defusedxml import ElementTree
from filetype.types import image as image_types

from .registry import registry
from .utils.deprecation import RemovedInWillow05Warning


class UnrecognisedImageFormatError(IOError):
    pass


class BadImageOperationError(ValueError):
    """
    Raised when the arguments to an image operation are invalid,
    e.g. a crop where the left coordinate is greater than the right coordinate
    """
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
        try:
            operation, _, conversion_path, _ = registry.find_operation(type(self), attr)
        except LookupError:
            # Operation doesn't exist
            raise AttributeError("%r object has no attribute %r" % (
                self.__class__.__name__, attr
            ))

        def wrapper(*args, **kwargs):
            image = self

            for converter, _ in conversion_path:
                image = converter(image)

            return operation(image, *args, **kwargs)

        return wrapper

    # A couple of helpful methods

    @classmethod
    def open(cls, f):
        # Detect image format
        image_format = filetype.guess_extension(f)

        if image_format is None and cls.maybe_xml(f):
            image_format = "svg"

        # Find initial class
        initial_class = INITIAL_IMAGE_CLASSES.get(image_format)
        if not initial_class:
            if image_format:
                raise UnrecognisedImageFormatError("Cannot load %s images (%r)" % (image_format, INITIAL_IMAGE_CLASSES))
            else:
                raise UnrecognisedImageFormatError("Unknown image format")

        return initial_class(f)

    @classmethod
    def maybe_xml(cls, f):
        # Check if it looks like an XML doc, it will be validated
        # properly when we parse it in SvgImageFile
        f.seek(0)
        pattern = re.compile(rb"^\s*<")
        for line in f:
            if pattern.match(line):
                f.seek(0)
                return True
        f.seek(0)
        return False

    def save(self, image_format, output):
        # Get operation name
        if image_format not in ['jpeg', 'png', 'gif', 'bmp', 'tiff', 'webp', 'svg', 'heic']:
            raise ValueError("Unknown image format: %s" % image_format)

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

    @property
    def format_name(self):
        """ 
        Willow internal name for the image format 
        ImageFile implementations MUST override this.
        """
        raise NotImplementedError

    @property
    def mime_type(self):
        """
        Returns the MIME type of the image file
        ImageFile implementations MUST override this.
        """
        raise NotImplementedError

    @property
    def original_format(self):
        warnings.warn(
            "Image.original_format has been renamed to Image.format_name.",
            RemovedInWillow05Warning)

        return self.format_name

    def __init__(self, f):
        self.f = f


class JPEGImageFile(ImageFile):
    @property
    def format_name(self):
        return "jpeg"

    @property
    def mime_type(self):
        return "image/jpeg"


class PNGImageFile(ImageFile):
    @property
    def format_name(self):
        return "png"

    @property
    def mime_type(self):
        return "image/png"


class GIFImageFile(ImageFile):
    @property
    def format_name(self):
        return "gif"

    @property
    def mime_type(self):
        return "image/gif"


class BMPImageFile(ImageFile):
    @property
    def format_name(self):
        return "bmp"

    @property
    def mime_type(self):
        return "image/bmp"


class TIFFImageFile(ImageFile):
    @property
    def format_name(self):
        return "tiff"

    @property
    def mime_type(self):
        return "image/tiff"


class WebPImageFile(ImageFile):
    @property
    def format_name(self):
        return "webp"

    @property
    def mime_type(self):
        return "image/webp"


class SvgImageFile(ImageFile):
    format_name = "svg"

    def __init__(self, f, dom=None):
        if dom is None:
            f.seek(0)
            # Will raise xml.etree.ElementTree.ParseError if invalid
            self.dom = ElementTree.parse(f)
            f.seek(0)
        else:
            self.dom = dom
        super().__init__(f)


class HeicImageFile(ImageFile):
    @property
    def format_name(self):
        return "heic"

    @property
    def mime_type(self):
        return "image/heiс"


INITIAL_IMAGE_CLASSES = {
    # A mapping of image formats to their initial class
    image_types.Jpeg().extension: JPEGImageFile,
    image_types.Png().extension: PNGImageFile,
    image_types.Gif().extension: GIFImageFile,
    image_types.Bmp().extension: BMPImageFile,
    image_types.Tiff().extension: TIFFImageFile,
    image_types.Webp().extension: WebPImageFile,
    "svg": SvgImageFile,
    image_types.Heic().extension: HeicImageFile,
}
