Saving images
=============

In Willow there are separate save operations for each image format:

 - :meth:`~Image.save_as_jpeg`
 - :meth:`~Image.save_as_png`
 - :meth:`~Image.save_as_gif`
 - :meth:`~Image.save_as_webp`

All three take one positional argument, the file-like object to write the image
data to.

For example, to save an image as a PNG file:

.. code-block:: python

    with open('out.png', 'wb') as f:
        i.save_as_png(f)

Changing the quality setting
---------------------------------

:meth:`~Image.save_as_jpeg` and :meth:`~Image.save_as_webp` takes a ``quality`` 
keyword argument, which is a number between 1 and 100. It defaults to 85 
for :meth:`~Image.save_as_jpeg` and 80 for :meth:`~Image.save_as_webp`. 
Decreasing this number will decrease the output file size at the cost 
of losing image quality.

For example, to save an image with low quality:

.. code-block:: python

    with open('low_quality.jpg', 'wb') as f:
        i.save_as_jpeg(f, quality=40)

Progressive JPEGs
-----------------

By default, JPEG's are saved in the same format as their source file but you
can force Willow to always save a "progressive" JPEG file by setting the
``progressive`` keyword argument to ``True``:

.. code-block:: python

    with open('progressive.jpg', 'wb') as f:
        i.save_as_jpeg(f, progressive=True)

Lossless WebP
-----------------

You can encode the image to WebP without any loss by setting the
``lossless`` keyword argument to ``True``:

.. code-block:: python

    with open('lossless.webp', 'wb') as f:
        i.save_as_webp(f, lossless=True)

Image optimisation
------------------

:meth:`~Image.save_as_jpeg` and :meth:`~Image.save_as_png` both take an
``optimize`` keyword that when set to true, will output an optimized image.

.. code-block:: python

    with open('optimized.jpg', 'wb') as f:
        i.save_as_jpeg(f, optimize=True)

This feature is currently only supported in the Pillow backend, if you use Wand
this argument will be ignored.
