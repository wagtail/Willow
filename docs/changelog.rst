Changelog
=========

Unreleased
----------

1.7.0 (2023-11-26)
------------------

Note: due to various limitations, version 1.6.3 includes some of the fixes present in 1.7.x, most importantly the
ICC profile and EXIF data when saving a JPEG to PNG, WebP, AVIF.

- Test with Python 3.12 (@zerolab)
- Add optional dependencies for Pillow/Wand (@zerolab)
  One can run ``pip install Willow[Pillow]`` or ``Willow[Wand]`` and get the correct Pillow or Wand versions.
- Replace wrong unicode character in the `image/heic` mime type (Stephan Lachnit)
- Fix color management by keeping ICC color profiles and EXIF data in addition (André Fuchs, Stefan Istrate)

1.6.3 (2023-11-26)
------------------

- Replace wrong unicode character in the `image/heic` mime type (Stephan Lachnit)
- Fix color management by keeping ICC color profiles and EXIF data in addition (André Fuchs, Stefan Istrate)

1.6.2 (2023-09-06)
------------------

- Ensure SVG files are given a mime type (Jake Howard)


1.6.1 (2023-08-04)
------------------

 - Fix ``NUMBER_PATTERN`` regex for parsing SVG viewboxes (Joshua Munn)


1.6 (2023-07-13)
----------------

 - Configure linting with black, ruff and pre-commit. Add coverage reports (@zerolab)
 - Switch to flit for packaging, and PyPI trusted publishing (@zerolab)
 - Drop support for Python 3.7
 - Add AVIF support (Aman Pandey)
 - Add support for image optimization libraries via :ref:`optimizer classes <concept-optimizers>` (@zerolab)
 - Add check for CMYK when saving as PNG (Stan Mattingly, @zerolab)


1.5.3 (2023-09-06)
------------------

- Ensure SVG files are given a mime type (Jake Howard)


1.5.2 (2023-08-04)
------------------

 - Fix ``NUMBER_PATTERN`` regex for parsing SVG viewboxes (Joshua Munn)


1.5.1 (2023-07-06)
------------------

 - Fix SVG cropping (Joshua Munn)


1.5 (2023-03-29)
----------------

 - Drop support for Python versions below 3.7
 - Drop support for Pillow versions below 9.1 and fix Pillow 10 deprecation warnings (Alex Tomkins)
 - Replace deprecated ``imghdr`` with ``filetype``. This allows detecting newer image formats such as HEIC (Herbert Poul)
 - Add SVG support (Joshua Munn)
 - Add HEIF support via the ``pillow-heif`` library (Alexander Piskun)


1.4.1 (2022-02-25)
------------------

 - Drop support for Python 3.4
 - Imagemagick 7 compatibility fixes (Matt Westcott)
 - Fix: Implemented consistent behavior between Pillow and Wand for out-of-bounds crop rectangles (Matt Westcott)

1.4 (2020-05-26)
----------------

 - Implemented save quality/lossless options for WebP (@mozgsml)
 - Added missing docs for WebP support (@mozgsml)

1.3 (2019-10-16)
----------------

 - Added ``.get_frame_count()`` operation (@kaedroho)

1.2 (2019-10-11)
----------------

 - Added WebP support (@frmdstryr)
 - Added ``.rotate()`` operation (@mrchrisadams & @simo97)

1.1 (2017-12-04)
----------------

 - Added `set_background_color_rgb` operation
 - Update MANIFEST.in (Sanny Kumar)

1.0 (2017-08-04)
----------------

 - OpenCV 3 support (Will Giddens)
 - Removed Apple copyrighted ICC profile from orientation test images (Christopher Hoskin)
 - Fix: Altered `detect_features` in OpenCV 3 to return a list instead of a numpy array (Trent Holliday)
 - Support for TIFF files (Maik Hoepfel)
 - Support for BMP files was made official (Maik Hoepfel)

0.4 (2016-10-05)
----------------

 - Support for image optimization and saving progressive JPEG files
 - Added documentation

0.3.1 (2016-05-16)
------------------

 - Fixed crash in the Pillow auto_orient operation when the image has an invalid Orientation EXIF Tag (Sigurdur J Eggertsson)
 - The ``auto_orient`` operation now catches all errors raised while reading EXIF data (Tomas Olander)
 - Palette formatted PNG and GIF files that have transparency no longer lose their transparency when resizing them

0.3 (2016-03-09)
----------------

A major internals refactor has taken place in this release, there are a number of breaking changes:

 - The Image class is now immutable. Previously, "resize" and "crop" operations altered the image in-place but now they now always return a new image leaving the original untouched.
 - There are now multiple Image classes. Each one represents possible state the image can be in (for example in a file, loaded in Pillow, etc). Operations can return an image in a different class to what the operation was performed on.
 - The "backends" have been renamed to "plugins".
 - A new registry module has been added which can be used for registering new plugins and operations.
 - The "original_format" attribute has been deprecated.

Other changes in this release:

- Added auto_orient operation

0.2.1 (2015-05-27)
------------------

- JPEGs are now detected from first two bytes of their file. Allowing non JFIF/EXIF JPEG images to be loaded

0.2 (2015-04-01)
----------------

- Added loader for BMP files
- Added has_alpha and has_animation operations
- Added get_pillow_image and get_wand_image operations
- Added save_as_{jpeg,png,gif} operations
- Crop and resize now all arguments in a tuple (Similar to Pillow)
- Dropped Python 2.6 and 3.2 support
- Formats now detected using images header instead of extension
- Now possible to specify alternative cascade file for face detection
- Fix: Images now saved in the same format they were loaded
- Fix: 1 and P formatted images now converted to RGB when saving to JPEG

0.1 (2015-02-22)
----------------

Initial release
