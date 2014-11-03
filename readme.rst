.. image:: https://travis-ci.org/kaedroho/Willow.svg?branch=master
    :target: https://travis-ci.org/kaedroho/Willow


Willow image library
====================

Willow provides a unified and extensible interface to the many imaging libraries that are available for Python. It can also automatically switch between libraries at runtime allowing you to use features in all of the imaging libraries with any image. 

It includes backends for Pillow, Wand and OpenCV out of the box. It is easy to add new operations to existing backends or roll your own backend to add support for other imaging libraries.


Features
--------

* Simple, extensible API
* Basic resize and crop operations
* Animated GIFs
* Face and feature detection
* Supports Python 2.6, 2.7, 3.2, 3.3 and 3.4


Examples
--------

Resizing a PNG file
```````````````````

.. code-block:: python

   from willow.image import Image

   img = Image.open("test.png")

   # Resize the image to 100x100 pixels
   img.resize(100, 100)

   # Save it
   img.save_as_png("test_thumbnail.png")


This will open the image file with Pillow or Wand (if Pillow is unavailable).

It will then resize it to 100x100 pixels and save it back out as a PNG file.


Detecting faces
```````````````

.. code-block:: python

   from willow.image import Image

   img = Image.open("photo.png")

   # Find faces
   faces = img.detect_faces()


Like above, the image file will be loaded with either Pillow or Wand.

As neither Pillow nor Wand support detecting faces, Willow would automatically convert the image to OpenCV and use that to perform the detection.

