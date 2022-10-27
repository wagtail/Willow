from willow.image import Image


def setup():
    from xml.etree import ElementTree
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
        SvgImageFile,
        HeicImageFile,
    )
    from willow.plugins import pillow, wand, opencv
    from willow.svg import SvgImage

    registry.register_image_class(JPEGImageFile)
    registry.register_image_class(PNGImageFile)
    registry.register_image_class(GIFImageFile)
    registry.register_image_class(BMPImageFile)
    registry.register_image_class(TIFFImageFile)
    registry.register_image_class(WebPImageFile)
    registry.register_image_class(HeicImageFile)
    registry.register_image_class(RGBImageBuffer)
    registry.register_image_class(RGBAImageBuffer)
    registry.register_image_class(SvgImageFile)
    registry.register_image_class(SvgImage)

    registry.register_plugin(pillow)
    registry.register_plugin(wand)
    registry.register_plugin(opencv)

    # Prevents etree from prefixing XML tag names with anonymous
    # namespaces, e.g. "<ns0:svg ..."
    ElementTree.register_namespace("", "http://www.w3.org/2000/svg")


setup()


__version__ = "1.4"
