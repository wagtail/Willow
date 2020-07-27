from __future__ import absolute_import

from PIL import ImageOps
from willow.image import (
    Image,
    JPEGImageFile,
    PNGImageFile,
    GIFImageFile,
    BMPImageFile,
    TIFFImageFile,
    WebPImageFile,
    RGBImageBuffer,
    RGBAImageBuffer,
)

class UnsupportedRotation(Exception): pass

def _PIL_Image():
    import PIL.Image
    return PIL.Image


class PillowImage(Image):
    def __init__(self, image):
        self.image = image

    @classmethod
    def check(cls):
        _PIL_Image()

    @classmethod
    def is_format_supported(cls, image_format):
        formats = _PIL_Image().registered_extensions()
        return image_format in formats.values()

    @Image.operation
    def get_size(self):
        return self.image.size

    @Image.operation
    def get_frame_count(self):
        # Animation is not supported by PIL
        return 1

    @Image.operation
    def has_alpha(self):
        img = self.image
        return img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)

    @Image.operation
    def has_animation(self):
        # Animation is not supported by PIL
        return False

    @Image.operation
    def resize(self, size):
        # Convert 1 and P images to RGB to improve resize quality
        # (palleted images don't get antialiased or filtered when minified)
        if self.image.mode in ['1', 'P']:
            if self.has_alpha():
                image = self.image.convert('RGBA')
            else:
                image = self.image.convert('RGB')
        else:
            image = self.image

        return PillowImage(image.resize(size, _PIL_Image().ANTIALIAS))

    @Image.operation
    def crop(self, rect):
        return PillowImage(self.image.crop(rect))

    @Image.operation
    def rotate(self, angle):
        """
        Accept a multiple of 90 to pass to the underlying Pillow function
        to rotate the image.
        """

        Image = _PIL_Image()
        ORIENTATION_TO_TRANSPOSE = {
            90: Image.ROTATE_90,
            180: Image.ROTATE_180,
            270: Image.ROTATE_270,
        }

        modulo_angle = angle % 360

        # is we're rotating a multiple of 360, it's the same as a no-op
        if not modulo_angle:
            return self

        transpose_code = ORIENTATION_TO_TRANSPOSE.get(modulo_angle)

        if not transpose_code:
            raise UnsupportedRotation(
                "Sorry - we only support right angle rotations - i.e. multiples of 90 degrees"
            )

        # We call "transpose", as it rotates the image,
        # updating the height and width, whereas using 'rotate'
        # only changes the contents of the image.
        rotated = self.image.transpose(transpose_code)

        return PillowImage(rotated)

    @Image.operation
    def set_background_color_rgb(self, color):
        if not self.has_alpha():
            # Don't change image that doesn't have an alpha channel
            return self

        # Check type of color
        if not isinstance(color, (tuple, list)) or not len(color) == 3:
            raise TypeError("the 'color' argument must be a 3-element tuple or list")

        # Convert non-RGB colour formats to RGB
        # As we only allow the background color to be passed in as RGB, we
        # convert the format of the original image to match.
        image = self.image.convert('RGBA')

        # Generate a new image with background colour and draw existing image on top of it
        # The new image must temporarily be RGBA in order for alpha_composite to work
        new_image = _PIL_Image().new('RGBA', self.image.size, (color[0], color[1], color[2], 255))

        if hasattr(new_image, 'alpha_composite'):
            new_image.alpha_composite(image)
        else:
            # Pillow < 4.2.0 fallback
            # This method may be slower as the operation generates a new image
            new_image = _PIL_Image().alpha_composite(new_image, image)

        return PillowImage(new_image.convert('RGB'))

    @Image.operation
    def save_as_jpeg(self, f, quality=85, optimize=False, progressive=False):
        if self.image.mode in ['1', 'P']:
            image = self.image.convert('RGB')
        else:
            image = self.image

        # Pillow only checks presence of optimize kwarg, not its value.
        kwargs = {}
        if optimize:
            kwargs['optimize'] = True
        if progressive:
            kwargs['progressive'] = True
        kwargs['icc_profile'] = image.info.get('icc_profile')

        exif = image.info.get('exif')
        if exif:
            kwargs['exif'] = exif

        # Try saving the image and catch potential Pillow errors caused by large
        # EXIF data. See the issue below for details about how Pillow could
        # crash:
        # https://github.com/python-pillow/Pillow/issues/148#issuecomment-578787435
        try:
            image.save(f, 'JPEG', quality=quality, **kwargs)
        except OSError as e:
            if 'exif' in kwargs:
                kwargs.pop('exif')
                image.save(f, 'JPEG', quality=quality, **kwargs)
            else:
                raise e

        return JPEGImageFile(f)

    @Image.operation
    def save_as_png(self, f, optimize=False):
        # Pillow only checks presence of optimize kwarg, not its value
        kwargs = {}
        if optimize:
            kwargs['optimize'] = True
        kwargs['icc_profile'] = self.image.info.get('icc_profile')

        self.image.save(f, 'PNG', **kwargs)
        return PNGImageFile(f)

    @Image.operation
    def save_as_gif(self, f):
        image = self.image

        # All gif files use either the L or P mode but we sometimes convert them
        # to RGB/RGBA to improve the quality of resizing. We must make sure that
        # they are converted back before saving.
        if image.mode not in ['L', 'P']:
            image = image.convert('P', palette=_PIL_Image().ADAPTIVE)

        if 'transparency' in image.info:
            image.save(f, 'GIF', transparency=image.info['transparency'])
        else:
            image.save(f, 'GIF')

        return GIFImageFile(f)

    @Image.operation
    def save_as_webp(self, f, quality=80, lossless=False):
        self.image.save(f, 'WEBP', quality=quality, lossless=lossless)
        return WebPImageFile(f)

    @Image.operation
    def auto_orient(self):
        # JPEG files can be orientated using an EXIF tag.
        # Make sure this orientation is applied to the data.
        image = ImageOps.exif_transpose(self.image)
        return PillowImage(image)

    @Image.operation
    def get_pillow_image(self):
        return self.image

    @classmethod
    @Image.converter_from(JPEGImageFile)
    @Image.converter_from(PNGImageFile)
    @Image.converter_from(GIFImageFile, cost=200)
    @Image.converter_from(BMPImageFile)
    @Image.converter_from(TIFFImageFile)
    @Image.converter_from(WebPImageFile)
    def open(cls, image_file):
        image_file.f.seek(0)
        image = _PIL_Image().open(image_file.f)
        image.load()

        return cls(image)

    @Image.converter_to(RGBImageBuffer)
    def to_buffer_rgb(self):
        image = self.image

        if image.mode != 'RGB':
            image = image.convert('RGB')

        return RGBImageBuffer(image.size, image.tobytes())

    @Image.converter_to(RGBAImageBuffer)
    def to_buffer_rgba(self):
        image = self.image

        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        return RGBAImageBuffer(image.size, image.tobytes())


willow_image_classes = [PillowImage]
