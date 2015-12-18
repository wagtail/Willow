====================
Willow image library
====================

Willow is a pure Python library that aims to unite many Python imaging libraries under a single interface.

Out of the box, Willow can work with Pillow, Wand or OpenCV. None of these image libraries are required (but you should have either Pillow or Wand installed to use most features). It also has a plugin interface which allows you to add support for more libraries, image formats and operations.

Installation
============

Willow supports Python 2.7+ and 3.3+. It's a pure-python library with no hard dependencies so doesn't require a C compiler for a basic installation.

Installation using ``pip``
--------------------------

.. code-block:: shell

    pip install Willow==0.3b3

Installing underlying libraries
-------------------------------

In order for most features of Willow to work, you need to install either Pillow or Wand.

 - `Pillow installation <http://pillow.readthedocs.org/en/3.0.x/installation.html#basic-installation>`_
 - `Wand installation <http://docs.wand-py.org/en/0.4.2/guide/install.html>`_

Note that Pillow doesn't support animated GIFs and Wand isn't as fast. Installing both will give best results.

Concepts
========

States
------

An image can either be a file, an image loaded into an underlying library or a simple buffer of pixels. These are known as "states".

Each state is a Python class that wraps the underlying file/image/buffer. For example ``JPEGImageFile``, ``PillowImage`` and ``RGBAImageBuffer`` are three of the state classes in Willow.

Operations
----------

These are functions that perform actions on an image in a particular state. For example, ``resize`` and ``crop``.

Operations can either be defined as methods on the state class or as functions registered separately.

Converters
----------

These are functions that convert an image between two states. For example, a converter from ``JPEGImageFile`` to ``PillowImage`` would simply be a function that calls ``PIL.Image.open`` on the underlying file to get a Pillow image.

Like operations, these can either be methods on the state class or registered separately.

Each converter has a cost which helps Willow decide which is the best available image library to use for a particular file format.

Registry
--------

The registry is where all states, operations and converters are registered. It contains methods to allow you to register new items and even override existing ones.

It also is responsible for finding operations and planning routes between states.

Plugins
-------

These are used to group related states, operations and converters together allowing them to be registered as a single unit.

The convention within Willow is to create a single plugin for each underlying lubrary. The default ones are "pillow", "wand" and "opencv".

Plugins can be registered even if the underlying library is not installed. This allows Willow to generate a useful error message if an operation is requested that only exists in a plugin without an underlying library.

Index
=====

.. toctree::
   :maxdepth: 2
   :titlesonly:
