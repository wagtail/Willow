from __future__ import absolute_import

import imghdr

from .registry import registry


def load_image(f):
    image_format = imghdr.what(f)
    initial_state = registry.get_initial_state(image_format)
    return initial_state(f)
