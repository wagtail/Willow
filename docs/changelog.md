# Changelog

## 0.4 (05/10/2016)

 - Support for image optimisation and saving progressive JPEG files
 - Added documentation

## 0.3.1 (16/05/2016)

 - Fixed crash in the Pillow auto_orient operation when the image has an invalid Orientation EXIF Tag (Sigurdur J Eggertsson)
 - The ``auto_orient`` operation now catches all errors raised while reading EXIF data (Tomas Olander)
 - Palette formatted PNG and GIF files that have transparency no longer lose their transparency when resizing them

## 0.3 (09/03/2016)

A major internals refactor has taken place in this release, there are a number of breaking changes:

 - The Image class is now immutable. Previously, "resize" and "crop" operations altered the image in-place but now they now always return a new image leaving the original untouched.
 - There are now multiple Image classes. Each one represents possible state the image can be in (eg, in a file, loaded in Pillow, etc). Operations can return an image in a different class to what the operation was performed on.
 - The "backends" have been renamed to "plugins".
 - A new registry module has been added which can be used for registering new plugins and operations.
 - The "original_format" attribute has been deprecated.

Other changes in this release:

- Added auto_orient operation

## 0.2.1 (27/05/2015)

- JPEGs are now detected from first two bytes of their file. Allowing non JFIF/EXIF JPEG images to be loaded

## 0.2 (01/04/2015)

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

## 0.1 (22/02/2015)

Initial release
