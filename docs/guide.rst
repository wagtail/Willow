===========
Usage guide
===========

This guide will show you how to use Willow!

Make sure you've installed Willow and either Pillow or Wand.

Basic usage
===========

Opening an image
----------------

.. code-block:: python

    from willow.image import Image

    with open('test.jpg', 'rb') as f:
        i = Image.open(f)

    isinstance(i, Image)

Resizing and cropping
---------------------

Operations that alter the image always return a new image object.

The old image will be untouched so another operation can be run on it.

.. code-block:: python

    i = i.resize((100, 100))


.. code-block:: python

    i = i.crop((100, 100, 100, 100))

Saving the image
----------------

.. code-block:: python

    with open('out.jpeg', 'wb') as f:
        i.save_as_jpeg(f)

Also, ``save_as_png`` and ``save_as_gif``

Face and feature detection
--------------------------

TODO

Advanced usage
==============

The Image class
---------------

Write a little about the Image class here

To open an image:

.. code-block:: python

    from willow.image import Image, JPEGImageFile

    with open('test.jpg', 'rb') as f:
       i = Image.open(f)

    isinstance(i, Image)
    isinstance(i, JPEGImageFile)
    i.format_name == 'jpeg'

The returned image is an instance of ``JPEGImageFile``

Now let's call an operation on the image:

.. code-block:: python

    i_resized = i.resize((100, 100))

    i_resized.get_size() == (100, 100)

    from willow.plugins.pillow import PillowImage
    isinstance(i_resized, PillowImage)

The returned image is an instance of ``PillowImage``.


Now, we should save this new image, we can call ``save_as_jpeg``

.. code-block:: python

    with open('out.jpg', 'wb') as f:
        image_file = i_resized.save_as_jpeg(f)

        isinstance(image_file, JPEGImageFile)
        image_file.format_name == 'jpeg'
        image_file.f == f

The save_as_* operations write the image to the specified file object and return an instance of one of the ImageFile classes wrapping that file.


Writing custom operations
-------------------------

TODO
