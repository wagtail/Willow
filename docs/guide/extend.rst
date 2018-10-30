Extending Willow
================

This section describes how to extend Willow with custom operations, image formats
and plugins.

Don't forget to look at the :doc:`concepts </concepts>` section first!

Implementing new operations
---------------------------

You can add operations to any existing image class and register them by calling the
:meth:`Registry.register_operation` method passing it the image class, name of
the operation and the function to call when the operation is used.

For example, let's implement a ``blur`` operation for both the
:class:`~willow.plugins.pillow.PillowImage` and :class:`~willow.plugins.wand.WandImage`
classes:

.. code-block:: python

    from willow.registry import registry
    from willow.plugins.pillow import PillowImage
    from willow.plugins.wand import WandImage

    def pillow_blur(image):
        from PIL import ImageFilter

        blurred_image = image.image.filter(ImageFilter.BLUR)
        return PillowImage(blurred_image)

    def wand_blur(image):
        # Wand modifies images in place so clone it first to prevent
        # altering the original image
        blurred_image = image.image.clone()
        blurred_image.gaussian_blur()
        return WandImage(blurred_image)


    # Register the operations in Willow

    registry.register_operation(PillowImage, 'blur', pillow_blur)
    registry.register_operation(WandImage, 'blur', wand_blur)

It is not required to support both :class:`~willow.plugins.pillow.PillowImage`
and :class:`~willow.plugins.wand.WandImage` but it's recommended that libraries
support both for maximum compatibility. You must support Wand if you need
animated GIF support.

Implementing custom image classes
---------------------------------

You can create your own image classes and register them by calling the
:meth:`Registry.register_image_class` method. All image classes must be a
subclass of :class:`willow.image.Image`.

Methods on image classes can be decorated with ``@Image.operation``,
``@Image.converter_from`` or ``@Image.converter_to`` which will make Willow
automatically register those methods as operations or converters.

For example, let's implement our own image class for Pillow:

.. code-block:: python

    from __future__ import absolute_import

    import PIL.Image

    from willow.image import (
        Image,
        JPEGImageFile,
        PNGImageFile,
        GIFImageFile,
    )


    class NewPillowImage(Image):
        def __init__(self, image):
            self.image = image


        # Informational operations

        @Image.operation
        def get_size(self):
            return self.image.size

        @Image.operation
        def has_alpha(self):
            img = self.image
            return img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info)

        @Image.operation
        def has_animation(self):
            # Animation is not supported by PIL
            return False


        # Resize and crop operations

        @Image.operation
        def resize(self, size):
            return PillowImage(image.resize(size, PIL.Image.ANTIALIAS))

        @Image.operation
        def crop(self, rect):
            return PillowImage(self.image.crop(rect))


        # Converter from supported file formats, this is where the image is opened

        # Pillow doesn't support GIFs very well. Adding a cost will make Willow try
        # a different image class first. The default cost for all converters is 100.

        @classmethod
        @Image.converter_from(JPEGImageFile)
        @Image.converter_from(PNGImageFile)
        @Image.converter_from(GIFImageFile, cost=200)
        @Image.converter_from(BMPImageFile)
        def open(cls, image_file):
            image_file.f.seek(0)
            image = PIL.Image.open(image_file.f)

            return cls(image)

The image class can then be registered by calling :meth:`Registry.register_image_class`:

.. code-block:: python

    from willow.registry import registry

    from newpillow import NewPillowImage

    registry.register_image_class(NewPillowImage)

This will also register all operations and converters defined on the class.


Plugins
-------

Plugins allow multiple image classes and/or operations to be registered together.
They are Python modules with any of the following attributes defined:
``willow_image_classes``, ``willow_operations`` or ``willow_converters``.

For example, we can convert the Python module in the example above into a Willow
plugin by adding the following line at the bottom of the file:

.. code-block:: python

    willow_image_classes = [NewPillowImage]

It can now be registered using the :meth:`Registry.register_plugin` method:

.. code-block:: python

    from willow.registry import registry

    import newpillow

    registry.register_plugin(newpillow)
