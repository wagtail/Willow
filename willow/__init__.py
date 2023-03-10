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
        WebMVP9ImageFile,
        OggTheoraImageFile,
        MP4H264ImageFile,
    )
    from willow.plugins import pillow, wand, opencv, ffmpeg

    registry.register_image_class(JPEGImageFile)
    registry.register_image_class(PNGImageFile)
    registry.register_image_class(GIFImageFile)
    registry.register_image_class(BMPImageFile)
    registry.register_image_class(TIFFImageFile)
    registry.register_image_class(WebPImageFile)
    registry.register_image_class(WebMVP9ImageFile)
    registry.register_image_class(OggTheoraImageFile)
    registry.register_image_class(MP4H264ImageFile)
    registry.register_image_class(RGBImageBuffer)
    registry.register_image_class(RGBAImageBuffer)

    registry.register_plugin(pillow)
    registry.register_plugin(wand)
    registry.register_plugin(opencv)
    registry.register_plugin(ffmpeg)

setup()


__version__ = '1.4'
