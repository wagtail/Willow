from willow.image import Image
from willow.registry import registry as _registry

from willow.states.files import (
    JPEGImageFileState,
    PNGImageFileState,
    GIFImageFileState,
)
from willow.states.pillow import PillowImageState


_registry.register_state(JPEGImageFileState)
_registry.register_state(PNGImageFileState)
_registry.register_state(GIFImageFileState)
_registry.register_state(PillowImageState)

_registry.register_format('jpeg', JPEGImageFileState)
_registry.register_format('png', PNGImageFileState)
_registry.register_format('gif', GIFImageFileState)


__version__ = '0.1'
