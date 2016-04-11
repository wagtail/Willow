Basic image operations
======================

Here's where Willow gets fancy, all operations in all plugins are available as
methods on every image. If an operation is called but doesn't exist in the
image's current class, a conversion will be performed under the hood.

Willow will do it's best to maintain the quality of the image, it'll decide how
to convert based on the images format and whether it has animation or transparency.
However it is not always easy

This means you can focus on making the code look clear and leave Willow to choose
which plugin is best to perform an operation.

Getting the image size
----------------------

You can call the :meth:`~Image.get_size` method which returns the width and
height as a tuple of two integers:

.. code-block:: python

    # For example, 'i' is a 200x200 pixel image
    i.get_size() == (200, 200)

Resizing images
---------------

To resize an image, call the :meth:`~Image.resize` method. This stretches the
image to fit the new size.

It takes a single argument, a two element sequence of integers containing the
width and height of the final image.

It returns a new :class:`~Image` object containing the resized image. The
original image is not modified.

.. code-block:: python

    i = i.resize((100, 100))

    isinstance(i, Image)
    i.get_size() == (100, 100)

Cropping images
---------------

To crop an image, call the :meth:`~Image.crop` method. This cuts the specified
rectangle from the source image.

It takes a single argument, a four element sequence of integers containing the
location of the left, top, right and bottom edges to cut out.

It returns a new :class:`~Image` object containing the cropped region. The
original image is not modified.

.. code-block:: python

    i = i.crop((100, 100, 300, 300))

    isinstance(i, Image)
    i.get_size() == (200, 200)

Detecting features
------------------

Detecting faces
---------------
