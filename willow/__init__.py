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
from willow.states.pillow import PillowImageState
from willow.states.wand import WandImageState
from willow.states.opencv import OpenCVColorImageState, OpenCVGrayscaleImageState


_registry.register_state_class(JPEGImageFileState)
_registry.register_state_class(PNGImageFileState)
_registry.register_state_class(GIFImageFileState)

_registry.register_state_class(RGBImageBufferState)
_registry.register_state_class(RGBAImageBufferState)

_registry.register_state_class(PillowImageState)

_registry.register_state_class(WandImageState)

_registry.register_state_class(OpenCVColorImageState)
_registry.register_state_class(OpenCVGrayscaleImageState)

_registry.register_image_format('jpeg', JPEGImageFileState)
_registry.register_image_format('png', PNGImageFileState)
_registry.register_image_format('gif', GIFImageFileState)


__version__ = '0.1'
