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
