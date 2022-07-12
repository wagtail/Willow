import unittest

import filetype

from willow.image import SVGImageFile, PNGImageFile, BadImageOperationError
from willow.svg import SVGImage


class TestSvglibOperations(unittest.TestCase):
    def setUp(self):
        with open("tests/images/svg/layered-peaks-haikei.svg", "r") as f:
            self.image = SVGImage.open(SVGImageFile(f))

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

    def test_crop_out_of_bounds(self):
        # original is 900x600
        # crop rectangle should be clamped to the image boundaries
        bottom_right_cropped_image = self.image.crop(
            (850, 550, 950, 650)
        ).rasterise_to_png()
        self.assertEqual(bottom_right_cropped_image.get_size(), (50, 50))

        top_left_cropped_image = self.image.crop((-50, -50, 50, 50)).rasterise_to_png()
        self.assertEqual(top_left_cropped_image.get_size(), (50, 50))

        # fail if the crop rectangle is entirely to the left of the image
        with self.assertRaises(BadImageOperationError):
            self.image.crop((-100, 50, -50, 100))
        # right edge of crop rectangle is exclusive, so 0 is also invalid
        with self.assertRaises(BadImageOperationError):
            self.image.crop((-50, 50, 0, 100))

        # fail if the crop rectangle is entirely above the image
        with self.assertRaises(BadImageOperationError):
            self.image.crop((50, -100, 100, -50))
        # bottom edge of crop rectangle is exclusive, so 0 is also invalid
        with self.assertRaises(BadImageOperationError):
            self.image.crop((50, -50, 100, 0))

        # fail if the crop rectangle is entirely to the right of the image
        with self.assertRaises(BadImageOperationError):
            self.image.crop((950, 50, 1000, 100))
        with self.assertRaises(BadImageOperationError):
            self.image.crop((900, 50, 950, 100))

        # fail if the crop rectangle is entirely below the image
        with self.assertRaises(BadImageOperationError):
            self.image.crop((50, 650, 100, 700))
        with self.assertRaises(BadImageOperationError):
            self.image.crop((50, 600, 100, 750))

        # fail if left edge >= right edge
        with self.assertRaises(BadImageOperationError):
            self.image.crop((125, 25, 25, 125))
        with self.assertRaises(BadImageOperationError):
            self.image.crop((100, 25, 100, 125))

        # fail if bottom edge >= top edge
        with self.assertRaises(BadImageOperationError):
            self.image.crop((25, 125, 125, 25))
        with self.assertRaises(BadImageOperationError):
            self.image.crop((25, 100, 125, 100))

    def test_crop_then_resize(self):
        image = self.image.crop((0, 0, 100, 100)).resize((20, 20)).rasterise_to_png()
        self.assertEqual(image.get_size(), (20, 20))

    def test_resize_then_crop(self):
        image = self.image.resize((100, 100)).crop((20, 20, 40, 40)).rasterise_to_png()
        self.assertEqual(image.get_size(), (20, 20))

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
