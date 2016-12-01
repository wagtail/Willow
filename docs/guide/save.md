# Saving images

In Willow there are separate save operations for each image format:

 - :meth:`~Image.save_as_jpeg`
 - :meth:`~Image.save_as_png`
 - :meth:`~Image.save_as_gif`

All three take one positional argument, the file-like object to write the image
data to.

For example, to save an image as a PNG file:

```python
with open('out.png', 'wb') as f:
    i.save_as_png(f)
```

## Changing the JPEG quality setting

:meth:`~Image.save_as_jpeg` takes a ``quality`` keyword argument, which is a
number between 1 and 100 which defaults to 85. Decreasing this number will
decrease the output file size at the cost of losing image quality.

For example, to save an image with low quality:

```python
with open('low_quality.jpg', 'wb') as f:
    i.save_as_jpeg(f, quality=40)
```

## Progressive JPEGs

By default, JPEG's are saved in the same format as their source file but you
can force Willow to always save a "progressive" JPEG file by setting the
``progressive`` keyword argument to ``True``:

```python
with open('progressive.jpg', 'wb') as f:
    i.save_as_jpeg(f, progressive=True)
```

## Image optimisation

:meth:`~Image.save_as_jpeg` and :meth:`~Image.save_as_png` both take an
``optimize`` keyword that when set to true, will output an optimized image.

```python
with open('optimized.jpg', 'wb') as f:
    i.save_as_jpeg(f, optimize=True)
```

This feature is currently only supported in the Pillow backend, if you use Wand
this argument will be ignored.
