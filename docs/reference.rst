Reference
=========


The ``Image`` class
-------------------

.. class:: Image

.. classmethod:: open(file)

    Opens the provided image file detects the format from the image header using
    Python's :mod:`filetype` module.

    Returns a subclass of :class:`ImageFile`

    If the image format is unrecognised, this throws a :class:`willow.image.UnrecognisedImageFormatError`
    (a subclass of :class:`IOError`)

.. classmethod:: operation

    A decorator for registering operations.

    The operations will be automatically registered when the image class is registered.

    .. code-block:: python

        from willow.image import Image

        class MyImage(Image):

            @Image.operation
            def resize(self, size):
                return MyImage(self.image.resize(size))

.. classmethod:: converter_from(other_classes, cost=100)

    A decorator for registering a "from" converter, which is a classmethod that
    converts an instance of another image class into an instance of this one.

    The ``other_classes`` parameter specifies which classes this converter can
    convert from. It can be a single class or a list.

    .. code-block:: python

        from willow.image import Image

        class MyImage(Image):
            ...

            @classmethod
            @Image.converter_from(JPEGImageFile)
            def open_jpeg_file(cls, image_file):
                return cls(image=open_jpeg(image_file.f))


    It can also be applied multiple times to the same function allowing different
    costs to be specified for different classes:

    .. code-block:: python

        @classmethod
        @Image.converter_from([JPEGImageFile, PNGImageFile])
        @Image.converter_from(GIFImageFile, cost=200)
        def open_file(cls, image_file):
            ...

.. classmethod:: converter_to(other_class, cost=100)

    A decorator for registering a "to" converter, which is a method that converts
    this image into an instance of another class.

    The ``other_class`` parameter specifies which class this function converts to.
    An individual "to" converter can only convert to a single class.

    .. code-block:: python

        from willow.image import Image

        class MyImage(Image):
            ...

            @Image.converter_to(PillowImage)
            def convert_to_pillow(self):
                image = PIL.Image()  # Code to create PIL image object here
                return PillowImage(image)

Builtin operations
------------------

Here's a full list of operations provided by Willow out of the box:

.. method:: get_size()

    Returns the size of the image as a tuple of two integers:

    .. code-block:: python

        width, height = image.get_size()

.. method:: get_frame_count()

    Returns the number of frames in an animated image:

    .. code-block:: python

        number_of_frames = image.get_frame_count()

.. method:: has_alpha

    Returns ``True`` if the image has an alpha channel.

    .. code-block:: python

        if image.has_alpha():
            # Image has alpha

.. method:: has_animation

    Returns ``True`` if the image is animated.

    .. code-block:: python

        if image.has_animation():
            # Image has animation

.. method:: resize(size)

    (supported natively for SVG, Pillow/Wand required for others)

    Stretches the image to fit the specified size. Size must be a sequence of two integers:

    .. code-block:: python

        # Resize the image to 100x100 pixels
        resized_image = source_image.resize((100, 100))

.. method:: crop(region)

    (supported natively for SVG, Pillow/Wand required for others)

    Cuts out the specified region of the image. The region must be a sequence of
    four integers (left, top, right, bottom):

    .. code-block:: python

        # Cut out a square from the middle of the image
        cropped_image = source_image.resize((100, 100, 200, 200))

    If the crop rectangle overlaps the image boundaries, it will be reduced to fit within those
    boundaries, resulting in an output image smaller than specified. If the crop rectangle is
    entirely outside the image, or the coordinates are out of range in any other way (such as
    a left coordinate greater than the right coordinate), this throws a
    :class:`willow.image.BadImageOperationError` (a subclass of :class:`ValueError`).

.. method:: set_background_color_rgb(color)

    (Pillow/Wand only)

    If the image has an alpha channel, this will add a background colour using
    the alpha channel as a mask. The alpha channel will be removed from the
    resulting image.

    The background colour must be specified as a tuple of three integers with
    values between 0 - 255.

    This operation will convert the image to RGB format, but will not do
    anything if there is not an alpha channel.

    .. code-block:: python

        # Set the background colour of the image to white
        image = source_image.set_background_color_rgb((255, 255, 255))

.. method:: auto_orient()

    (Pillow/Wand only)

    Some JPEG files have orientation data in an EXIF tag that needs to be applied
    to the image. This method applies this orientation to the image (it is a no-op
    for other image formats).

    This should be run before performing any other image operations.

    .. code-block:: python

        image = image.auto_orient()

.. method:: detect_features()

    (OpenCV only)

    Uses OpenCV to find the most prominent corners in the image.
    Useful for detecting interesting features for cropping against.

    Returns a list of two integer tuples containing the coordinates of each
    point on the image

    .. code-block:: python

        points = image.detect_features()

.. method:: detect_faces(cascade_filename)

    (OpenCV only)

    Uses OpenCV's `cascade classification
    <http://docs.opencv.org/2.4/modules/objdetect/doc/cascade_classification.html>`_
    to detect faces in the image.

    By default the ``haarcascade_frontalface_alt2.xml`` (provided by OpenCV)
    cascade file is used. You can specifiy the filename to a different cascade
    file in the first parameter.

    Returns a list of four integer tuples containing the left, top, right, bottom
    locations of each face detected in the image.

    .. code-block:: python

        faces = image.detect_faces()

.. method:: save_as_jpeg(file, quality=85, optimize=False)

    (Pillow/Wand only)

    Saves the image to the specified file-like object in JPEG format.

    Note: If the image has an alpha channel, this operation may raise an
    exception or save a broken image (depending on the backend being used).
    To resolve this, use the :meth:`~Image.set_background_color_rgb` method to
    replace the alpha channel with a solid background color before saving as JPEG.

    Returns a ``JPEGImageFile`` wrapping the file.

    .. code-block:: python

        with open('out.jpg', 'wb') as f:
            image.save_as_jpeg(f)

.. method:: save_as_png(file, optimize=False)

    (Pillow/Wand only)

    Saves the image to the specified file-like object in PNG format.

    Returns a ``PNGImageFile`` wrapping the file.

    .. code-block:: python

        with open('out.png', 'wb') as f:
            image.save_as_png(f)

.. method:: save_as_gif(file)

    (Pillow/Wand only)

    Saves the image to the specified file-like object in GIF format.

    returns a ``GIFImageFile`` wrapping the file.

    .. code-block:: python

        with open('out.gif', 'wb') as f:
            image.save_as_gif(f)

.. method:: save_as_webp(file, quality=80, lossless=False)

    (Pillow/Wand only)

    Saves the image to the specified file-like object in WEBP format.

    returns a ``WebPImageFile`` wrapping the file.

    .. code-block:: python

        with open('out.webp', 'wb') as f:
            image.save_as_webp(f)


.. method:: save_as_heic(file, quality=80, lossless=False)

    (Pillow only; requires the pillow-heif library)

    Saves the image to the specified file-like object in HEIF format.

    returns a ``HeicImageFile`` wrapping the file.

    .. code-block:: python

        with open('out.heic', 'wb') as f:
            image.save_as_heic(f)


.. method:: save_as_svg(file)

    (SVG images only)

    Saves the image to the specified file-like object in SVG format.

    returns a ``SvgImageFile`` wrapping the file.

    .. code-block:: python

        with open('out.svg', 'w') as f:
            image.save_as_svg(f)


.. method:: get_pillow_image()

    (Pillow only)

    Returns a ``PIL.Image`` object for the specified image. This may be useful
    for reusing existing code that requires a Pillow image.

    .. code-block:: python

        do_thing(image.get_pillow_image())

    You can convert a ``PIL.Image`` object back into a Willow :class:`Image`
    using the ``PillowImage`` class:

    .. code-block:: python

        import PIL.Image
        from willow.plugins.pillow import PillowImage

        pillow_image = PIL.Image.open('test.jpg')
        image = PillowImage(pillow_image)

        # Now you can use any Willow operation on that image
        faces = image.detect_faces()

.. method:: get_wand_image()

    (Wand only)

    Returns a ``Wand.Image`` object for the specified image. This may be useful
    for reusing existing code that requires a Wand image.

    .. code-block:: python

        do_thing(image.get_wand_image())

    You can convert a ``Wand.Image`` object back into a Willow :class:`Image`
    using the ``WandImage`` class:

    .. code-block:: python

        from wand.image import Image
        from willow.plugins.wand import WandImage

        # wand_image is an instance of Wand.Image
        wand_image = Image(filename='pikachu.png')
        image = WandImage(wand_image)

        # Now you can use any Willow operation on that image
        faces = image.detect_faces()
