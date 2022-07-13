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
        SVGImageFile,
    )
    from willow.plugins import pillow, wand, opencv, svglib
    from willow.svg import SVGImage

    registry.register_image_class(JPEGImageFile)
    registry.register_image_class(PNGImageFile)
    registry.register_image_class(GIFImageFile)
    registry.register_image_class(BMPImageFile)
    registry.register_image_class(TIFFImageFile)
    registry.register_image_class(WebPImageFile)
    registry.register_image_class(RGBImageBuffer)
    registry.register_image_class(RGBAImageBuffer)
    registry.register_image_class(SVGImageFile)
    registry.register_image_class(SVGImage)

    registry.register_plugin(pillow)
    registry.register_plugin(wand)
    registry.register_plugin(opencv)
    registry.register_plugin(svglib)


setup()


__version__ = '1.4'
