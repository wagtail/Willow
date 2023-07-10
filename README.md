# [Willow image library](https://pypi.org/project/Willow/)

[![PyPI](https://img.shields.io/pypi/v/Willow.svg)](https://pypi.org/project/Willow/)
[![PyPI downloads](https://img.shields.io/pypi/dm/Willow.svg)](https://pypi.org/project/Willow/)
[![Build Status](https://github.com/torchbox/Willow/workflows/CI/badge.svg)](https://github.com/wagtail/Willow/actions)

A wrapper that combines the functionality of multiple Python image libraries into one API.

[Documentation](https://willow.readthedocs.io/en/latest/index.html)

## Overview

Willow is a simple image library that combines the APIs of [Pillow](https://pillow.readthedocs.io/), [Wand](https://docs.wand-py.org) and [OpenCV](https://opencv.org/). 
It converts the image between the libraries when necessary.

Willow currently has basic resize and crop operations, face and feature detection and animated GIF support. 
New operations and library integrations can also be [easily implemented](https://willow.readthedocs.org/en/latest/guide/extend.html).

The library is written in pure Python and supports versions 3.8 3.9, 3.10 and 3.11.

## Examples

### Resizing an image

```python
from willow.image import Image

f = open('test.png', 'rb')
img = Image.open(f)

# Resize the image to 100x100 pixels
img = img.resize((100, 100))

# Save it
with open('test_thumbnail.png', 'wb') as out:
   img.save_as_png(out)
```

This will open the image file with Pillow or Wand (if Pillow is unavailable).

It will then resize it to 100x100 pixels and save it back out as a PNG file.


### Detecting faces

```python
from willow.image import Image

f = open('photo.png', 'rb')
img = Image.open(f)

# Find faces
faces = img.detect_faces()
```

Like above, the image file will be loaded with either Pillow or Wand.

As neither Pillow nor Wand support detecting faces, Willow would automatically convert the image to OpenCV and use that to perform the detection.

## Available operations

[Documentation](https://willow.readthedocs.org/en/latest/reference.html#builtin-operations)

| Operation                               | Pillow | Wand | OpenCV |
|-----------------------------------------|--------|------|--------|
| `get_size()`                            | ✓      | ✓    | ✓      |
| `get_frame_count()`                     | ✓**    | ✓    | ✓**    |
| `resize(size)`                          | ✓      | ✓    |        |
| `crop(rect)`                            | ✓      | ✓    |        |
| `rotate(angle)`                         | ✓      | ✓    |        |
| `set_background_color_rgb(color)`       | ✓      | ✓    |        |
| `auto_orient()`                         | ✓      | ✓    |        |
| `save_as_jpeg(file, quality)`           | ✓      | ✓    |        |
| `save_as_png(file)`                     | ✓      | ✓    |        |
| `save_as_gif(file)`                     | ✓      | ✓    |        |
| `save_as_webp(file, quality)`           | ✓      | ✓    |        |
| `save_as_heif(file, quality, lossless)` | ✓⁺     |      |        |
| `save_as_avif(file, quality, lossless)` | ✓⁺     | ✓⁺   |        |
| `has_alpha()`                           | ✓      | ✓    | ✓*     |
| `has_animation()`                       | ✓*     | ✓    | ✓*     |
| `get_pillow_image()`                    | ✓      |      |        |
| `get_wand_image()`                      |        | ✓    |        |
| `detect_features()`                     |        |      | ✓      |
| `detect_faces(cascade_filename)`        |        |      | ✓      |

\* Always returns `False`

\** Always returns `1`

⁺ Requires the [pillow-heif](https://pypi.org/project/pillow-heif/) library
