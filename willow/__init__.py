from willow.image import Image
from willow.registry import registry as _registry

from willow.states.files import (
    JPEGImageFileState,
    PNGImageFileState,
    GIFImageFileState,
)
from willow.states.buffers import (
    RGBImageBufferState,
    RGBAImageBufferState,
)
from willow.plugins import pillow, wand, opencv

_registry.register_state_class(JPEGImageFileState)
_registry.register_state_class(PNGImageFileState)
_registry.register_state_class(GIFImageFileState)

_registry.register_state_class(RGBImageBufferState)
_registry.register_state_class(RGBAImageBufferState)

_registry.register_image_format('jpeg', JPEGImageFileState)
_registry.register_image_format('png', PNGImageFileState)
_registry.register_image_format('gif', GIFImageFileState)

_registry.register_plugin(pillow)
_registry.register_plugin(wand)
_registry.register_plugin(opencv)


__version__ = '0.1'
