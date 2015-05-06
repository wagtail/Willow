from __future__ import absolute_import

import imghdr

from .states.files import (
    JPEGImageFileState,
    PNGImageFileState,
    GIFImageFileState,
)


class LoaderRegistry(object):
    _registered_image_formats = {}

    def register_format(self, image_format, initial_state):
        self._registered_image_formats[image_format] = initial_state

    def get_initial_state(self, image_format):
        return self._registered_image_formats[image_format]


registry = LoaderRegistry()
register_format = registry.register_format


def load_image(f):
    image_format = imghdr.what(f)
    initial_state = registry.get_initial_state(image_format)
    return initial_state(f)
