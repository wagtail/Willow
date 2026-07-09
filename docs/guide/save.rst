Saving images
=============

In Willow there are separate save operations for each image format:

 - :meth:`~Image.save_as_jpeg`
 - :meth:`~Image.save_as_jxl`
 - :meth:`~Image.save_as_png`
 - :meth:`~Image.save_as_gif`
 - :meth:`~Image.save_as_webp`
 - :meth:`~Image.save_as_svg`
 - :meth:`~Image.save_as_heic`
 - :meth:`~Image.save_as_avif`
 - :meth:`~Image.save_as_ico`


All three take one positional argument, the file-like object to write the image
data to.

For example, to save an image as a PNG file:

.. code-block:: python

    with open('out.png', 'wb') as f:
        i.save_as_png(f)

Changing the quality setting
----------------------------

:meth:`~Image.save_as_avif`, :meth:`~Image.save_as_jpeg`,
:meth:`~Image.save_as_jxl` and :meth:`~Image.save_as_webp` takes a ``quality``
keyword argument, which is a number between 1 and 100. Decreasing this number
will decrease the output file size at the cost of losing image quality.

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

Note: though the JPEG-XL format also supports progressive encoding, saving progressive JXL files is not currently supported in Willow.

Lossless JPEG-XL, AVIF, HEIC and WebP
-------------------------------------

You can encode the image to JPEG-XL, AVIF, HEIC (Pillow-only) and WebP without any loss by setting the
``lossless`` keyword argument to ``True``:

.. code-block:: python

    with open('lossless.jxl', 'wb') as f:
        i.save_as_jxl(f, lossless=True)

    with open('lossless.avif', 'wb') as f:
        i.save_as_avif(f, lossless=True)

    with open('lossless.heic', 'wb') as f:
        i.save_as_heic(f, lossless=True)

    with open('lossless.webp', 'wb') as f:
        i.save_as_webp(f, lossless=True)

Notes on saving JPEG-XL images
------------------------------

There are a few known limitations and other gotchas to note when saving JPEG-XL
images:

- CMYK images are not currently supported by the JPEG-XL encoder, if you
  try to save a CMYK image as .jxl, it will be converted to RGB first.
- ICC Color Profiles are not preserved when saving JPEG-XL images. The
  underlying ``jpegxl-rs`` encoder will replace the ICC profile with its own
  internal profile which is typically much smaller in size.
- Writing progressive JPEG-XL images is not currently supported.

Image optimization
------------------

:meth:`~Image.save_as_jpeg`, and :meth:`~Image.save_as_png` both take an
``optimize`` keyword that when set to true, will output an optimized image.

.. code-block:: python

    with open('optimized.jpg', 'wb') as f:
        i.save_as_jpeg(f, optimize=True)

This feature is currently only supported in the Pillow backend, if you use Wand
this argument will be ignored.
