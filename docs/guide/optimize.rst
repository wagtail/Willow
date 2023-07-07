Optimizing images
=================

Aside from the basic optimizations that the Pillow backend provides, Willow supports using dedicated libraries to
optimize images. Out of the box, Willow comes with optimizers for `gifsicle <https://www.lcdf.org/gifsicle/>`_,
`jpegoptim <https://www.kokkonen.net/tjko/projects.html>`_, `optipng <https://optipng.sourceforge.net/>`_,
`pngquant <https://pngquant.org/>`_ and `cwebp <https://developers.google.com/speed/webp/docs/cwebp>`_.

They can be enabled by setting the ``WILLOW_OPTIMIZERS`` environment variable to ``true``. To enable a specific
subset of optimizers, set the ``WILLOW_OPTIMIZERS`` environment variable to a comma-separated list of their
library names. For example, to enable only ``jpegoptim`` and ``optipng``:

.. code-block:: ini

    WILLOW_OPTIMIZERS=jpegoptim,optipng

or if using Django:

.. code-block:: python

    WILLOW_OPTIMIZERS = "jpegoptim,optipng"
    # or as a list of optimizer library names
    WILLOW_OPTIMIZERS = ["jpegoptim", "optipng"]
