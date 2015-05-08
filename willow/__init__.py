from willow.image import Image
from willow.registry import registry as _registry

from willow.states.files import (
    JPEGImageFileState,
    PNGImageFileState,
    GIFImageFileState,
)
from willow.states.pillow import PillowImageState


_registry.register_state_class(JPEGImageFileState)
_registry.register_state_class(PNGImageFileState)
_registry.register_state_class(GIFImageFileState)
_registry.register_state_class(PillowImageState)

_registry.register_format('jpeg', JPEGImageFileState)
_registry.register_format('png', PNGImageFileState)
_registry.register_format('gif', GIFImageFileState)


__version__ = '0.1'
