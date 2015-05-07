from willow.image import Image
from willow.registry import registry as _registry
from willow import loader as _loader

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

_loader.register_format('jpeg', JPEGImageFileState)
_loader.register_format('png', PNGImageFileState)
_loader.register_format('gif', GIFImageFileState)


__version__ = '0.1'
