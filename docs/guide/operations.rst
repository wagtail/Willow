Basic image operations
======================

Here's where Willow gets fancy, all operations in all plugins are available as
methods on every image. If an operation is called but doesn't exist in the
image's current class, a conversion will be performed under the hood.

Willow will do it's best to maintain the quality of the image, it'll decide how
to convert based on the images format and whether it has animation or transparency.
However it is not always easy

This means you can focus on making the code look clear and leave Willow to choose
which plugin is best to perform an operation.

Getting the image size
----------------------

You can call the :meth:`~Image.get_size` method which returns the width and
height as a tuple of two integers:

.. code-block:: python

    # For example, 'i' is a 200x200 pixel image
    i.get_size() == (200, 200)

For animated GIFs, you can get the number of frames by calling the :meth:`Image.get_frame_count` method:

.. code-block:: python

    i.get_frame_count() == 34

Resizing images
---------------

To resize an image, call the :meth:`~Image.resize` method. This stretches the
image to fit the new size.

It takes a single argument, a two element sequence of integers containing the
width and height of the final image.

It returns a new :class:`~Image` object containing the resized image. The
original image is not modified.

.. code-block:: python

    i = i.resize((100, 100))

    isinstance(i, Image)
    i.get_size() == (100, 100)

Rotating images
---------------

To rotate an image, call the :meth:`~Image.rotate` method. This rotates the image clockwise, by a multiple of 90 degrees (i.e 90, 180, 270).

It returns a new :class:`~Image` object containing the rotated image. The
original image is not modified.

.. code-block:: python

    # in this case, assume 'i' is a 300x150 pixel image
    i = i.rotate(90)
    isinstance(i, Image)
    i.get_size() == (150, 300)


Cropping images
---------------

To crop an image, call the :meth:`~Image.crop` method. This cuts the specified
rectangle from the source image.

It takes a single argument, a four element sequence of integers containing the
location of the left, top, right and bottom edges to cut out.

It returns a new :class:`~Image` object containing the cropped region. The
original image is not modified.

.. code-block:: python

    i = i.crop((100, 100, 300, 300))

    isinstance(i, Image)
    i.get_size() == (200, 200)

Setting a background colour
---------------------------

If the image has transparency, you can replace the transparency with a solid
background colour using the :meth:`~Image.set_background_color_rgb` method.

It takes the background color as a three element tuple of integers between
0 - 255 (representing the red, green and blue channels respectively).

It returns a new :class:`~Image` object containing the background color and
the alpha channel removed. The original image is not modified.

.. code-block:: python

    # Sets background color to white
    i = i.set_background_color_rgb((255, 255, 255))

    isinstance(i, Image)
    i.has_alpha() == False

Detecting features
------------------

Feature detection in Willow is provided by OpenCV so make sure it's installed first.

To detect features in an image, use the  :meth:`~Image.detect_features` operation.
This will return a list of tuples, containing the x and y coordinates of each
feature that was detected in the image.

.. code-block:: python

    features = i.detect_features()

    features == [
        (12, 53),
        (74, 44),
        ...
    ]

Under the hood, this uses OpenCV's GoodFeaturesToTrack_ function that finds the
prominent corners in the image.

.. _GoodFeaturesToTrack: http://docs.opencv.org/3.0-beta/modules/imgproc/doc/feature_detection.html#goodfeaturestotrack

Detecting faces
---------------

Face detection in Willow is provided by OpenCV so make sure it's installed first.

To detect features in an image, use the  :meth:`~Image.detect_faces` operation.
This will return a list of tuples, containing the left, top, right and bottom
positions in the image where each face appears.

.. code-block:: python

    faces = i.detect_faces()

    faces == [
        (12, 53, 65, 102),
        (1, 44, 74, 93),
        ...
    ]

Under the hood, this uses OpenCV's HaarDetectObjects_ function that performs
Haar cascade classification on the image. The default cascade file that gets
used is ``haarcascade_frontalface_alt2`` from OpenCV, but this can be changed
by setting the ``cascade_filename`` keyword argument to an absolute path
pointing to the file:

.. code-block:: python

    import os

    faces = i.detect_faces(cascade_filename=os.abspath('cascades/my_cascade_file.xml'))

    faces == [
        (12, 53, 65, 102),
        (1, 44, 74, 93),
        ...
    ]

.. _HaarDetectObjects: http://docs.opencv.org/2.4/modules/objdetect/doc/cascade_classification.html#CvSeq*%20cvHaarDetectObjects%28const%20CvArr*%20image,%20CvHaarClassifierCascade*%20cascade,%20CvMemStorage*%20storage,%20double%20scale_factor,%20int%20min_neighbors,%20int%20flags,%20CvSize%20min_size,%20CvSize%20max_size%29
