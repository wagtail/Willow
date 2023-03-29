Installation
============

Willow supports Python 3.7+. It's a pure-python library with no hard
dependencies so doesn't require a C compiler for a basic installation.

Installation using ``pip``
--------------------------

.. code-block:: shell

    pip install Willow

Installing underlying libraries
-------------------------------

In order for most features of Willow to work, you need to install either Pillow
or Wand.

 - `Pillow installation <https://pillow.readthedocs.io/en/stable/installation.html#basic-installation>`_
 - `Wand installation <https://docs.wand-py.org/en/stable/guide/install.html>`_

Note that Pillow doesn't support animated GIFs and Wand isn't as fast.
Installing both will give best results.
