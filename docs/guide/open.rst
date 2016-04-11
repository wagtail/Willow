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
detected by inspecting the file header). In this case, it used
:class:`~JPEGImageFile` as the image we loaded was in JPEG format.

Using different image classes for different formats allows Willow to decide
which plugin to use for performing operations on the image. For example, Willow
will always favour Wand for resizing GIF images but will always favour Pillow
for resizing JPEG and PNG images.

From an existing Pillow object
------------------------------

You can create a Willow :class:`~willow.image.Image` from an existing
``PIL.Image`` object by creating an instance of the
:class:`~willow.plugins.pillow.PillowImage` class
(passing the ``PIL.Image`` object as the only parameter):

.. code-block:: python

    from willow.plugins.pillow import PillowImage

    pillow_image = PIL.Image.open(...)

    i = PillowImage(pillow_image)

    isinstance(i, PillowImage)

    from willow.image import Image
    isinstance(i, Image)

The same can be done with Wand and OpenCV, which use the
:class:`~willow.plugins.wand.WandImage` and
:class:`~willow.plugins.opencv.OpenCVColorImage` classes respectively.
