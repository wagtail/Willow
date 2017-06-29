.. image:: https://travis-ci.org/wagtail/Willow.svg?branch=master
    :target: https://travis-ci.org/wagtail/Willow

.. image:: http://drone4.kaed.uk/api/badges/torchbox/Willow/status.svg
    :target: http://drone4.kaed.uk/torchbox/Willow

Willow image library
====================

A Python image library that sits on top of Pillow, Wand and OpenCV

`Documentation <http://willow.readthedocs.org/en/latest/index.html>`_

Overview
--------

Willow is a simple image library that combines the APIs of Pillow, Wand and OpenCV. It converts the image between the libraries when necessary.

Willow currently has basic resize and crop operations, face and feature detection and animated GIF support. New operations and library integrations can also be `easily implemented <http://willow.readthedocs.org/en/latest/guide/extend.html>`_.

It is written in pure-Python (versions 2.7, 3.3, 3.4, 3.5 and 3.6 are supported)

Examples
--------

Resizing an image
`````````````````

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

`Documentation <http://willow.readthedocs.org/en/latest/reference.html#builtin-operations>`_

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
``get_pillow_image()``              ✓
``get_wand_image()``                                     ✓
``detect_features()``                                                         ✓
``detect_faces(cascade_filename)``                                            ✓
=================================== ==================== ==================== ====================

\* Always returns ``False``
