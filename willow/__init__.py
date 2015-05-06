from willow.image import Image
from willow import states

from willow.states.files import (
    JPEGImageFileState,
    PNGImageFileState,
    GIFImageFileState,
)
from willow.states.pillow import PillowImageState

states.register_state(JPEGImageFileState)
states.register_state(PNGImageFileState)
states.register_state(GIFImageFileState)
states.register_state(PillowImageState)


__version__ = '0.1'
