Installation
============

Willow supports Python 3.8+. It is a pure Python library with no hard
dependencies so it doesn't require a C compiler for a basic installation.

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
