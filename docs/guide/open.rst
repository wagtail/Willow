Opening images
==============

Images can be either opened from a file or an existing Pillow/Wand object.

From a file
-----------

To open an image, call :meth:`Image.open` passing in a file-like object that
contains the image data.

.. code-block:: python

    from willow.image import Image

    with open('test.jpg', 'rb') as f:
        i = Image.open(f)

        isinstance(i, Image)

        from willow.image import ImageFile, JPEGImageFile
        isinstance(i, ImageFile)
        isinstance(i, JPEGImageFile)

If it succeeded, this will return a subclass of :class:`~ImageFile` (which itself
is a subclass of :class:`~Image`).

The :class:`~ImageFile` subclass it chooses depends on the format of the image (
detected by inspecting the header). In this case, it used :class:`~JPEGImageFile`
as the image we loaded was a JPEG.

This concept of different image classes for different formats helps Willow decide
which plugin to use for resizing the image. For example, Willow will always
favour Wand for resizing GIF images but will always favour Pillow for JPEG and
PNG images.

From an existing Pillow object
------------------------------

If the image has already been loaded with Pillow, you can very easily instantiate
an :class:`~Image` object using the :class:`~willow.plugins.pillow.PillowImage`
class:

.. code-block:: python

    from willow.plugins.pillow import PillowImage

    pillow_image = PIL.Image.open(...)

    i = PillowImage(pillow_image)

    isinstance(i, PillowImage)

    from willow.image import Image
    isinstance(i, Image)

The same can be done for Wand and OpenCV.
