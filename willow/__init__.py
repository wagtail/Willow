from willow.image import Image

def setup():
    from willow.registry import registry

    from willow.states import (
        JPEGImageFileState,
        PNGImageFileState,
        GIFImageFileState,
        RGBImageBufferState,
        RGBAImageBufferState,
    )
    from willow.plugins import pillow, wand, opencv

    registry.register_state_class(JPEGImageFileState)
    registry.register_state_class(PNGImageFileState)
    registry.register_state_class(GIFImageFileState)
    registry.register_state_class(RGBImageBufferState)
    registry.register_state_class(RGBAImageBufferState)

    registry.register_image_format('jpeg', JPEGImageFileState)
    registry.register_image_format('png', PNGImageFileState)
    registry.register_image_format('gif', GIFImageFileState)

    registry.register_plugin(pillow)
    registry.register_plugin(wand)
    registry.register_plugin(opencv)

setup()

__version__ = '0.1'
