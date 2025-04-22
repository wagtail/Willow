import unittest

from pillow_heif import AvifImageFile as PillowHeif_AvifImageFile

from willow.image import Image, PNGImageFile
from willow.plugins.pillow import PillowImage

no_avif_support = not PillowImage.is_format_supported("AVIF")


class TestPillowAVIFPlugin(unittest.TestCase):
    def setUp(self):
        # Open an image of a different format first, this ensures that Pillow
        # registers its own AVIF format support *before* pillow_heif does.
        # The order of registration carries significance.
        with open("tests/images/transparent.png", "rb") as f:
            self.image = PillowImage.open(PNGImageFile(f))

    @unittest.skipIf(no_avif_support, "Pillow does not have AVIF support")
    def test_avif_plugin_loads_correctly(self):
        # Opening an AVIF image after opening a different format image
        # should not cause any issues with AVIF support.
        with open("tests/images/tree.avif", "rb") as f:
            image = Image.open(f)
            pillow = PillowImage.open(image)

            # The image should have been opened using pillow_heif
            # and not the default AVIF plugin.
            self.assertIsInstance(pillow.image, PillowHeif_AvifImageFile)
