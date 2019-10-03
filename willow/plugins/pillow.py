from __future__ import absolute_import

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


def is_format_supported(image_format):
    formats = _PIL_Image().registered_extensions()
    return image_format in formats.values()


def image_has_alpha(image):
    return image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info)


class PillowImage(Image):
    def __init__(self, image_or_frames):
        if isinstance(image_or_frames, _PIL_Image().Image):
            self.frames = [image_or_frames]
        else:
            self.frames = list(image_or_frames)

    @property
    def image(self):
        # TODO: Deprecation warning
        return self.frames[0]

    @classmethod
    def check(cls):
        _PIL_Image()

    @classmethod
    def is_format_supported(cls, image_format):
        return is_format_supported(image_format)

    @Image.operation
    def get_size(self):
        return self.frames[0].size

    @Image.operation
    def get_frame_count(self):
        return len(self.frames)

    @Image.operation
    def has_alpha(self):
        return any(image_has_alpha(frame) for frame in self.frames)

    @Image.operation
    def has_animation(self):
        return self.get_frame_count() > 1

    @Image.operation
    def resize(self, size):
        def _resize_frame(frame):
            # Convert 1 and P images to RGB to improve resize quality
            # (palleted images don't get antialiased or filtered when minified)
            if frame.mode in ['1', 'P']:
                if image_has_alpha(frame):
                    frame = frame.convert('RGBA')
                else:
                    frame = frame.convert('RGB')

            return frame.resize(size, _PIL_Image().ANTIALIAS)

        return PillowImage([_resize_frame(frame) for frame in self.frames])

    @Image.operation
    def crop(self, rect):
        return PillowImage([frame.crop(rect) for frame in self.frames])

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
        rotated = [frame.transpose(transpose_code) for frame in self.frames]

        return PillowImage(rotated)

    @Image.operation
    def set_background_color_rgb(self, color):
        if not self.has_alpha():
            # Don't change image that doesn't have an alpha channel
            return self

        # Check type of color
        if not isinstance(color, (tuple, list)) or not len(color) == 3:
            raise TypeError("the 'color' argument must be a 3-element tuple or list")

        def _set_frame_background_color_rgb(frame):
            # Convert non-RGB colour formats to RGB
            # As we only allow the background color to be passed in as RGB, we
            # convert the format of the original image to match.
            frame = frame.convert('RGBA')

            # Generate a new image with background colour and draw existing image on top of it
            # The new image must temporarily be RGBA in order for alpha_composite to work
            new_frame = _PIL_Image().new('RGBA', frame.size, (color[0], color[1], color[2], 255))

            if hasattr(new_frame, 'alpha_composite'):
                new_frame.alpha_composite(frame)
            else:
                # Pillow < 4.2.0 fallback
                # This method may be slower as the operation generates a new image
                new_frame = _PIL_Image().alpha_composite(new_frame, frame)

            return new_frame.convert('RGB')

        return PillowImage([_set_frame_background_color_rgb(frame) for frame in self.frames])

    @Image.operation
    def save_as_jpeg(self, f, quality=85, optimize=False, progressive=False):
        if self.has_animation():
            pass  # TODO: Raise warning

        frame = self.frames[0]

        if frame.mode in ['1', 'P']:
            frame = frame.convert('RGB')

        # Pillow only checks presence of optimize kwarg, not its value
        kwargs = {}
        if optimize:
            kwargs['optimize'] = True
        if progressive:
            kwargs['progressive'] = True

        frame.save(f, 'JPEG', quality=quality, **kwargs)
        return JPEGImageFile(f)

    @Image.operation
    def save_as_png(self, f, optimize=False):
        if self.has_animation():
            pass  # TODO: Raise warning

        frame = self.frames[0]

        # Pillow only checks presence of optimize kwarg, not its value
        kwargs = {}
        if optimize:
            kwargs['optimize'] = True

        frame.save(f, 'PNG', **kwargs)
        return PNGImageFile(f)

    @Image.operation
    def save_as_gif(self, f):
        frames = self.frames

        # All gif files use either the L or P mode but we sometimes convert them
        # to RGB/RGBA to improve the quality of resizing. We must make sure that
        # they are converted back before saving.
        if frames[0].mode not in ['L', 'P']:
            frames = [
                frame.convert('P', palette=_PIL_Image().ADAPTIVE)
                for frame in frames
            ]

        if self.has_animation():
            params = {
                'save_all': True,
                'duration': frames[0].info['duration'],
                'append_images': [frame for frame in frames[1:]]
            }
        else:
            params = {}

        if 'transparency' in frames[0].info:
            params['transparency'] = frames[0].info['transparency']

        frames[0].save(f, 'GIF', **params)

        return GIFImageFile(f)

    @Image.operation
    def save_as_webp(self, f):
        if self.has_animation():
            pass  # TODO: Raise warning

        frame = self.frames[0]

        frame.save(f, 'WEBP')
        return WebPImageFile(f)

    @Image.operation
    def auto_orient(self):
        # JPEG files can be orientated using an EXIF tag.
        # Make sure this orientation is applied to the data
        if hasattr(self.frames[0], '_getexif'):
            try:
                exif = self.frames[0]._getexif()
            except Exception:
                # Blanket cover all the ways _getexif can fail in.
                exif = None
            if exif is not None:
                # 0x0112 = Orientation
                orientation = exif.get(0x0112, 1)

                if 1 <= orientation <= 8:
                    Image = _PIL_Image()
                    ORIENTATION_TO_TRANSPOSE = {
                        1: (),
                        2: (Image.FLIP_LEFT_RIGHT,),
                        3: (Image.ROTATE_180,),
                        4: (Image.ROTATE_180, Image.FLIP_LEFT_RIGHT),
                        5: (Image.ROTATE_270, Image.FLIP_LEFT_RIGHT),
                        6: (Image.ROTATE_270,),
                        7: (Image.ROTATE_90, Image.FLIP_LEFT_RIGHT),
                        8: (Image.ROTATE_90,),
                    }

                    def _orient_frame(frame):
                        for transpose in ORIENTATION_TO_TRANSPOSE[orientation]:
                            frame = frame.transpose(transpose)

                        return frame

                    return PillowImage([_orient_frame(frame) for frame in self.frames])

        return self

    @Image.operation
    def get_pillow_image(self):
        # TODO: Deprecation warning
        return self.frames[0]

    @classmethod
    @Image.converter_from(JPEGImageFile)
    @Image.converter_from(PNGImageFile)
    @Image.converter_from(BMPImageFile)
    @Image.converter_from(TIFFImageFile)
    @Image.converter_from(WebPImageFile)
    def open(cls, image_file):
        image_file.f.seek(0)
        image = _PIL_Image().open(image_file.f)
        image.load()

        return cls(image)

    @classmethod
    @Image.converter_from(GIFImageFile)
    def open_animated(cls, image_file):
        image_file.f.seek(0)
        image = _PIL_Image().open(image_file.f)

        frame = image
        frames = []
        while frame:
            frames.append(frame.copy())

            try:
                image.seek(image.tell() + 1)
            except EOFError:
                break

        return cls(frames)

    @Image.converter_to(RGBImageBuffer)
    def to_buffer_rgb(self):
        if self.has_animation():
            pass  # TODO: Raise warning

        frame = self.frames[0]

        if image.mode != 'RGB':
            frame = frame.convert('RGB')

        return RGBImageBuffer(frame.size, frame.tobytes())

    @Image.converter_to(RGBAImageBuffer)
    def to_buffer_rgba(self):
        if self.has_animation():
            pass  # TODO: Raise warning

        frame = self.frames[0]

        if frame.mode != 'RGBA':
            frame = frame.convert('RGBA')

        return RGBAImageBuffer(frame.size, frame.tobytes())


willow_image_classes = [PillowImage]
