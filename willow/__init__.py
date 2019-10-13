from willow.image import Image

def setup():
    from willow.registry import registry

    from willow.image import (
        JPEGImageFile,
        PNGImageFile,
        GIFImageFile,
        BMPImageFile,
        RGBImageBuffer,
        RGBAImageBuffer,
        TIFFImageFile,
        WebPImageFile,
    )
    from willow.plugins import pillow, wand, opencv
    from willow.generic_operations import get_pixel_count

    registry.register_image_class(JPEGImageFile)
    registry.register_image_class(PNGImageFile)
    registry.register_image_class(GIFImageFile)
    registry.register_image_class(BMPImageFile)
    registry.register_image_class(TIFFImageFile)
    registry.register_image_class(WebPImageFile)
    registry.register_image_class(RGBImageBuffer)
    registry.register_image_class(RGBAImageBuffer)

    registry.register_plugin(pillow)
    registry.register_plugin(wand)
    registry.register_plugin(opencv)

    registry.register_generic_operation(['get_size', 'get_frame_count'], 'get_pixel_count', get_pixel_count)

setup()


__version__ = '1.2'
