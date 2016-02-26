Installation
============

Willow supports Python 2.7+ and 3.3+. It's a pure-python library with no hard
dependencies so doesn't require a C compiler for a basic installation.

Installation using ``pip``
--------------------------

.. code-block:: shell

    pip install Willow==0.3b3

Installing underlying libraries
-------------------------------

In order for most features of Willow to work, you need to install either Pillow
or Wand.

 - `Pillow installation <http://pillow.readthedocs.org/en/3.0.x/installation.html#basic-installation>`_
 - `Wand installation <http://docs.wand-py.org/en/0.4.2/guide/install.html>`_

Note that Pillow doesn't support animated GIFs and Wand isn't as fast.
Installing both will give best results.
