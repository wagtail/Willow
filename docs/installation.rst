Installation
============

Willow supports Python 3.9+. It is a pure Python library with no hard
dependencies so it doesn't require a C compiler for a basic installation.

Installation using ``pip``
--------------------------

.. code-block:: shell

    pip install Willow

Installing underlying libraries
-------------------------------

In order for most features of Willow to work, you need to install either Pillow
or Wand. You can follow the installation instructions for each of them:

 - `Pillow installation <https://pillow.readthedocs.io/en/stable/installation.html#basic-installation>`_
 - `Wand installation <https://docs.wand-py.org/en/stable/guide/install.html>`_

or you can install them together with Willow when using ``pip``:

.. code-block:: shell

    pip install Willow[Pillow]
    # or
    pip install Willow[Wand]


Note that Pillow doesn't support animated GIFs and Wand isn't as fast.
Installing both will give best results.


HEIC and AVIF support
^^^^^^^^^^^^^^^^^^^^^

When using Pillow, you need to install ``pillow-heif`` for HEIC support:

.. code-block:: shell

    pip install pillow-heif
    # or
    pip install Willow[heif]

When using Wand, you will need ImageMagick version 7.0.25 or newer.

Both Pillow and Wand require ``libheif`` to be installed on your system for full HEIC support.
