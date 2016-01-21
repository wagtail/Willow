try:
    from .opencv3 import OpenCVColorImage, OpenCVGrayscaleImage
except ImportError:
    try:
        from .opencv2 import OpenCVColorImage, OpenCVGrayscaleImage
    except ImportError:
        # Import the base class to access the check method for the registry.
        from .base import BaseOpenCVColorImage as OpenCVColorImage
        from .base import BaseOpenCVGrayscaleImage as OpenCVGrayscaleImage

willow_image_classes = [OpenCVColorImage, OpenCVGrayscaleImage]
