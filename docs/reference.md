# Reference

## The ``Image`` class

### ``.open(file)``

Opens the provided image file detects the format from the image header using
Python's :mod:`imghdr` module.

Returns a subclass of :class:`ImageFile`

If the image format is unrecognised, this throws a :class:`willow.image.UnrecognisedImageFormatError`
(a subclass of :class:`IOError`)

### classmethod ``.operation()``

A decorator for registering operations.

The operations will be automatically registered when the image class is registered.

```python
from willow.image import Image

class MyImage(Image):

    @Image.operation
    def resize(self, size):
        return MyImage(self.image.resize(size))
```

### classmethod ``.converter_from(other_classes, cost=100)``

A decorator for registering a "from" converter, which is a classmethod that
converts an instance of another image class into an instance of this one.

The ``other_classes`` parameter specifies which classes this converter can
convert from. It can be a single class or a list.

```python
from willow.image import Image

class MyImage(Image):
    ...

    @classmethod
    @Image.converter_from(JPEGImageFile)
    def open_jpeg_file(cls, image_file):
        return cls(image=open_jpeg(image_file.f))
```

It can also be applied multiple times to the same function allowing different
costs to be specified for different classes:

```python
class MyImage(Image):
    ...

    @classmethod
    @Image.converter_from([JPEGImageFile, PNGImageFile])
    @Image.converter_from(GIFImageFile, cost=200)
    def open_file(cls, image_file):
        ...
```

### classmethod ``.converter_to(other_class, cost=100)``

A decorator for registering a "to" converter, which is a method that converts
this image into an instance of another class.

The ``other_class`` parameter specifies which class this function converts to.
An individual "to" converter can only convert to a single class.

```python
from willow.image import Image

class MyImage(Image):
    ...

    @Image.converter_to(PillowImage)
    def convert_to_pillow(self):
        image = PIL.Image()  # Code to create PIL image object here
        return PillowImage(image)
```

## Builtin operations

Here's a full list of operations provided by Willow out of the box:

### ``.get_size()``

Returns the size of the image as a tuple of two integers:

```python
width, height = image.get_size()
```

### ``.has_alpha()``

Returns ``True`` if the image has an alpha channel.

```python
if image.has_alpha():
    # Image has alpha
```

### ``.has_animation()``

Returns ``True`` if the image is animated.

```python
if image.has_animation():
    # Image has animation
```

### ``.resize(size)``

*(Pillow/Wand only)*

Stretches the image to fit the specified size. Size must be a sequence of two integers:

```python
# Resize the image to 100x100 pixels
resized_image = source_image.resize((100, 100))
```

### ``.crop(region)``

*(Pillow/Wand only)*

Cuts out the specified region of the image. The region must be a sequence of
four integers (top, left, right, bottom):

```python
# Cut out a square from the middle of the image
cropped_image = source_image.resize((100, 100, 200, 200))
```

### ``.auto_orient()``

*(Pillow/Wand only)*

Some JPEG files have orientation data in an EXIF tag that needs to be applied
to the image. This method applies this orientation to the image (it is a no-op
for other image formats).

This should be run before performing any other image operations.

```python
image = image.auto_orient()
```

### ``.detect_features()``

*(OpenCV only)*

Uses OpenCV to find the most prominent corners in the image.
Useful for detecting interesting features for cropping against.

Returns a list of two integer tuples containing the coordinates of each
point on the image

```python
points = image.detect_features()
```

### ``.detect_faces(cascade_filename)``

*(OpenCV only)*

Uses OpenCV's `cascade classification
<http://docs.opencv.org/2.4/modules/objdetect/doc/cascade_classification.html>`_
to detect faces in the image.

By default the ``haarcascade_frontalface_alt2.xml`` (provided by OpenCV)
cascade file is used. You can specifiy the filename to a different cascade
file in the first parameter.

Returns a list of four integer tuples containing the left, top, right, bottom
locations of each face detected in the image.

```python
faces = image.detect_faces()
```

### ``.save_as_jpeg(file, quality=85, optimize=False)``

*(Pillow/Wand only)*

Saves the image to the specified file-like object in JPEG format.

Returns a ``JPEGImageFile`` wrapping the file.

```python
with open('out.jpg', 'wb') as f:
    image.save_as_jpeg(f)
```

### ``.save_as_png(file, optimize=False)``

*(Pillow/Wand only)*

Saves the image to the specified file-like object in PNG format.

Returns a ``PNGImageFile`` wrapping the file.

```python
with open('out.png', 'wb') as f:
    image.save_as_png(f)
```

### ``.save_as_gif(file)``

*(Pillow/Wand only)*

Saves the image to the specified file-like object in GIF format.

returns a ``GIFImageFile`` wrapping the file.

```python
with open('out.gif', 'wb') as f:
    image.save_as_gif(f)
```

### ``.get_pillow_image()``

*(Pillow only)*

Returns a ``PIL.Image`` object for the specified image. This may be useful
for reusing existing code that requires a Pillow image.

```python
do_thing(image.get_pillow_image())
```

You can convert a ``PIL.Image`` object back into a Willow :class:`Image`
using the ``PillowImage`` class:

```python
import PIL.Image
from willow.plugins.pillow import PillowImage

pillow_image = PIL.Image.open('test.jpg')
image = PillowImage(pillow_image)

# Now you can use any Willow operation on that image
faces = image.detect_faces()
```

### ``.get_wand_image()``

*(Wand only)*

Returns a ``Wand.Image`` object for the specified image. This may be useful
for reusing existing code that requires a Wand image.

```python
do_thing(image.get_wand_image())
```

You can convert a ``Wand.Image` object back into a Willow :class:`Image`
using the ``WandImage`` class:

```python
from wand.image import Image
from willow.plugins.wand import WandImage

# wand_image is an instance of Wand.Image
wand_image = Image(filename='pikachu.png')
image = WandImage(wand_image)

# Now you can use any Willow operation on that image
faces = image.detect_faces()
```
