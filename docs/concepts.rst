Concepts
========

Image classes
-------------

An image can either be a file, an image loaded into an underlying library or a
simple buffer of pixels. Each of these states has its own Python class
(subclass of :class:`willow.image.Image`).

For example ``JPEGImageFile``, ``PillowImage`` and ``RGBAImageBuffer`` are three
of the image classes in Willow.

Operations
----------

These are functions that perform actions on an image in a particular state. For
example, ``resize`` and ``crop``.

Operations can either be defined as methods on the image class or as functions
registered separately.

All operations are registered in a central registry and will appear as a method
on all other image classes. If it's called from a class that doesn't implement
the operation, the image will be automatically converted to the nearest image
class that supports it and the operation is run on that.

Operations that alter an image return a new image object instead of altering the
source one. This also means that if a conversion took place, the new image's
class would be different.

Converters
----------

These are functions that convert an image between two image classes. For
example, a converter from ``JPEGImageFile`` to ``PillowImage`` would simply be a
function that calls ``PIL.Image.open`` on the underlying file to get a Pillow
image.

Like operations, these can either be methods on the image class or registered
separately.

Each converter has a cost which helps Willow decide which is the best available
image library to use for a particular file format.

Registry
--------

The registry is where all image classes, operations and converters are
registered. It contains methods to allow you to register new items and even
override existing ones.

It also is responsible for finding operations and planning routes between image
classes.

Plugins
-------

These are used to group related image classes, operations and converters
together allowing them to be registered as a single unit.

The convention within Willow is to create a single plugin for each underlying
library. The default ones are "pillow", "wand" and "opencv".

Plugins can be registered even if the underlying library is not installed. This
allows Willow to generate a useful error message if an operation is requested
that only exists in a plugin without an underlying library.
