Changelog
=========

1.5 (29/03/2023)
----------------

 - Drop support for Python versions below 3.7
 - Drop support for Pillow versions below 9.1 and fix Pillow 10 deprecation warnings (Alex Tomkins)
 - Replace deprecated ``imghdr`` with ``filetype``. This allows detecting newer image formats such as HEIC (Herbert Poul)
 - Add SVG support (Joshua Munn)
 - Add HEIF support via the ``pillow-heif`` library (Alexander Piskun)


1.4.1 (25/02/2022)
------------------

 - Drop support for Python 3.4
 - Imagemagick 7 compatibility fixes (Matt Westcott)
 - Fix: Implemented consistent behaviour between Pillow and Wand for out-of-bounds crop rectangles (Matt Westcott)

1.4 (26/05/2020)
----------------

 - Implemented save quality/lossless options for WebP (@mozgsml)
 - Added missing docs for WebP support (@mozgsml)

1.3 (16/10/2019)
----------------

 - Added ``.get_frame_count()`` operaton (@kaedroho)

1.2 (11/10/2019)
----------------

 - Added WebP support (@frmdstryr)
 - Added ``.rotate()`` operaton (@mrchrisadams & @simo97)

1.1 (04/12/2017)
----------------

 - Added `set_background_color_rgb` operation
 - Update MANIFEST.in (Sanny Kumar)

1.0 (04/08/2017)
----------------

 - OpenCV 3 support (Will Giddens)
 - Removed Apple copyrighted ICC profile from orientation test images (Christopher Hoskin)
 - Fix: Altered `detect_features` in OpenCV 3 to return a list instead of a numpy array (Trent Holliday)
 - Support for TIFF files (Maik Hoepfel)
 - Support for BMP files was made official (Maik Hoepfel)

0.4 (05/10/2016)
----------------

 - Support for image optimisation and saving progressive JPEG files
 - Added documentation

0.3.1 (16/05/2016)
------------------

 - Fixed crash in the Pillow auto_orient operation when the image has an invalid Orientation EXIF Tag (Sigurdur J Eggertsson)
 - The ``auto_orient`` operation now catches all errors raised while reading EXIF data (Tomas Olander)
 - Palette formatted PNG and GIF files that have transparency no longer lose their transparency when resizing them

0.3 (09/03/2016)
----------------

A major internals refactor has taken place in this release, there are a number of breaking changes:

 - The Image class is now immutable. Previously, "resize" and "crop" operations altered the image in-place but now they now always return a new image leaving the original untouched.
 - There are now multiple Image classes. Each one represents possible state the image can be in (eg, in a file, loaded in Pillow, etc). Operations can return an image in a different class to what the operation was performed on.
 - The "backends" have been renamed to "plugins".
 - A new registry module has been added which can be used for registering new plugins and operations.
 - The "original_format" attribute has been deprecated.

Other changes in this release:

- Added auto_orient operation

0.2.1 (27/05/2015)
------------------

- JPEGs are now detected from first two bytes of their file. Allowing non JFIF/EXIF JPEG images to be loaded

0.2 (01/04/2015)
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

0.1 (22/02/2015)
----------------

Initial release
