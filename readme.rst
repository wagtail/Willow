.. image:: https://travis-ci.org/torchbox/Willow.svg?branch=master
    :target: https://travis-ci.org/torchbox/Willow

.. image:: http://drone4.kaed.uk/api/badges/torchbox/Willow/status.svg
    :target: http://drone4.kaed.uk/torchbox/Willow

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
* Supports Python 2.7, 3.3, 3.4 and 3.5


Examples
--------

Resizing a PNG file
```````````````````

.. code-block:: python

   from willow.image import Image

   f = open('test.png', 'rb')
   img = Image.open(f)

   # Resize the image to 100x100 pixels
   img = img.resize((100, 100))

   # Save it
   with open('test_thumbnail.png', 'wb') as out:
       img.save_as_png(out)


This will open the image file with Pillow or Wand (if Pillow is unavailable).

It will then resize it to 100x100 pixels and save it back out as a PNG file.


Detecting faces
```````````````

.. code-block:: python

   from willow.image import Image

   f = open('photo.png', 'rb')
   img = Image.open(f)

   # Find faces
   faces = img.detect_faces()


Like above, the image file will be loaded with either Pillow or Wand.

As neither Pillow nor Wand support detecting faces, Willow would automatically convert the image to OpenCV and use that to perform the detection.

Available operations
--------------------

=================================== ==================== ==================== ====================
Operation                           Pillow               Wand                 OpenCV
=================================== ==================== ==================== ====================
``get_size()``                      ✓                    ✓                    ✓
``resize(size)``                    ✓                    ✓
``crop(rect)``                      ✓                    ✓
``auto_orient()``                   ✓                    ✓
``save_as_jpeg(file, quality)``     ✓                    ✓
``save_as_png(file)``               ✓                    ✓
``save_as_gif(file)``               ✓                    ✓
``has_alpha()``                     ✓                    ✓                    ✓*
``has_animation()``                 ✓*                   ✓                    ✓*
``detect_features()``                                                         ✓
``detect_faces(cascade_filename)``                                            ✓
=================================== ==================== ==================== ====================

\* Always returns ``False``
