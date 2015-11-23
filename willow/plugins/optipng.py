from __future__ import absolute_import

from tempfile import NamedTemporaryFile
from shutil import copyfileobj
from subprocess import call

from willow.image import PNGImageFile


def optipng(image_file, level=2):
    # Write the input file to the disk, so it can be seen by optipng
    in_file = NamedTemporaryFile()
    image_file.f.seek(0)
    copyfileobj(image_file.f, in_file)
    in_file.flush()

    # Create output file
    out_file = NamedTemporaryFile()

    # Call optipng
    call(['optipng', in_file.name, '-o%d' % level, '-clobber', '-out', out_file.name])

    return PNGImageFile(out_file)


def optimise(image_file):
    return optipng(image_file)


willow_operations = [
    (PNGImageFile, 'optipng', optipng),
    (PNGImageFile, 'optimise', optimise),
]
