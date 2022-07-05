import io
import unittest

import filetype

from willow.image import SVGImageFile, PNGImageFile
from willow.svg import SVGImage


class TestSvglibOperations(unittest.TestCase):
    def setUp(self):
        with open("tests/images/svg/appreciation.svg", "r") as f:
            self.image = SVGImage.open(SVGImageFile(f))

    def test_rasterise_to_png(self):
        rasterised = self.image.rasterise_to_png()
        self.assertEqual(filetype.guess_extension(rasterised.f), "png")
        self.assertIsInstance(rasterised, PNGImageFile)
