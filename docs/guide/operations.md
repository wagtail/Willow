# Basic image operations

Here's where Willow gets fancy, all operations in all plugins are available as
methods on every image. If an operation is called but doesn't exist in the
image's current class, a conversion will be performed under the hood.

Willow will do it's best to maintain the quality of the image, it'll decide how
to convert based on the images format and whether it has animation or transparency.
However it is not always easy

This means you can focus on making the code look clear and leave Willow to choose
which plugin is best to perform an operation.

## Getting the image size

You can call the :meth:`~Image.get_size` method which returns the width and
height as a tuple of two integers:

```python
# For example, 'i' is a 200x200 pixel image
i.get_size() == (200, 200)
```

## Resizing images

To resize an image, call the :meth:`~Image.resize` method. This stretches the
image to fit the new size.

It takes a single argument, a two element sequence of integers containing the
width and height of the final image.

It returns a new :class:`~Image` object containing the resized image. The
original image is not modified.

```python
i = i.resize((100, 100))

isinstance(i, Image)
i.get_size() == (100, 100)
```

## Cropping images

To crop an image, call the :meth:`~Image.crop` method. This cuts the specified
rectangle from the source image.

It takes a single argument, a four element sequence of integers containing the
location of the left, top, right and bottom edges to cut out.

It returns a new :class:`~Image` object containing the cropped region. The
original image is not modified.

```python
i = i.crop((100, 100, 300, 300))

isinstance(i, Image)
i.get_size() == (200, 200)
```

## Detecting features

Feature detection in Willow is provided by OpenCV so make sure it's installed first.

To detect features in an image, use the  :meth:`~Image.detect_features` operation.
This will return a list of tuples, containing the x and y coordinates of each
feature that was detected in the image.

```python
features = i.detect_features()

features == [
    (12, 53),
    (74, 44),
    ...
]
```

Under the hood, this uses OpenCV's GoodFeaturesToTrack_ function that finds the
prominent corners in the image.

.. _GoodFeaturesToTrack: http://docs.opencv.org/3.0-beta/modules/imgproc/doc/feature_detection.html#goodfeaturestotrack

## Detecting faces

Face detection in Willow is provided by OpenCV so make sure it's installed first.

To detect features in an image, use the  :meth:`~Image.detect_faces` operation.
This will return a list of tuples, containing the left, top, right and bottom
positions in the image where each face appears.

```python
faces = i.detect_faces()

faces == [
    (12, 53, 65, 102),
    (1, 44, 74, 93),
    ...
]
```

Under the hood, this uses OpenCV's HaarDetectObjects_ function that performs
Haar cascade classification on the image. The default cascade file that gets
used is ``haarcascade_frontalface_alt2`` from OpenCV, but this can be changed
by setting the ``cascade_filename`` keyword argument to an absolute path
pointing to the file:

```python
import os

faces = i.detect_faces(cascade_filename=os.abspath('cascades/my_cascade_file.xml'))

faces == [
    (12, 53, 65, 102),
    (1, 44, 74, 93),
    ...
]
```

.. _HaarDetectObjects: http://docs.opencv.org/2.4/modules/objdetect/doc/cascade_classification.html#CvSeq*%20cvHaarDetectObjects%28const%20CvArr*%20image,%20CvHaarClassifierCascade*%20cascade,%20CvMemStorage*%20storage,%20double%20scale_factor,%20int%20min_neighbors,%20int%20flags,%20CvSize%20min_size,%20CvSize%20max_size%29
