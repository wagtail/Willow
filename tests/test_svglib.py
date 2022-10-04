import unittest

import filetype

from willow.image import SvgImageFile, PNGImageFile
from willow.svg import SvgImage


class TestRasteriseToPng(unittest.TestCase):
    def setUp(self):
        with open("tests/images/svg/layered-peaks-haikei.svg", "r") as f:
            # viewport aspect ratio is equivalent to user aspect
            # ratio, so input rects to crop won't be translated
            self.image = SvgImage.open(SvgImageFile(f))

    def test_rasterise_to_png(self):
        rasterised = self.image.rasterise_to_png()
        self.assertEqual(filetype.guess_extension(rasterised.f), "png")
        self.assertIsInstance(rasterised, PNGImageFile)

    def test_resize(self):
        resized = self.image.resize((45, 60)).rasterise_to_png()
        self.assertEqual(resized.get_size(), (45, 60))

    def test_crop(self):
        cropped = self.image.crop((10, 10, 100, 100)).rasterise_to_png()
        self.assertEqual(cropped.get_size(), (90, 90))

    def test_crop_then_resize(self):
        image = self.image.crop((0, 0, 100, 100)).resize((20, 20)).rasterise_to_png()
        self.assertEqual(image.get_size(), (20, 20))

    def test_resize_then_crop(self):
        image = (
            self.image.resize((300, 100))
            .crop((0, 0, 150, 50), transformer=None)
            .rasterise_to_png()
        )
        self.assertEqual(image.get_size(), (150, 50))

    def test_multiple_crops(self):
        image = (
            self.image.crop((0, 0, 100, 100)).crop((10, 10, 20, 20)).rasterise_to_png()
        )
        self.assertEqual(image.get_size(), (10, 10))

    def test_multiple_resizes(self):
        image = self.image.resize((300, 300)).resize((150, 20)).rasterise_to_png()
        self.assertEqual(image.get_size(), (150, 20))

    def test_has_animation(self):
        self.assertFalse(self.image.has_animation())
