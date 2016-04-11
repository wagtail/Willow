Extending Willow
================

This section describes how to extend Willow with custom operations, image formats
and plugins.

Don't forget to look at the :doc:`concepts </concepts>` section first!

Implementing new operations
---------------------------

You can add operations to any existing image class by calling the
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

Implementing new plugins
------------------------

Implementing new image formats
------------------------------
