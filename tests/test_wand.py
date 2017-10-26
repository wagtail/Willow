import unittest
import io
import imghdr

from wand.color import Color

from PIL import Image as PILImage

from willow.image import JPEGImageFile, PNGImageFile, GIFImageFile
from willow.plugins.wand import _wand_image, WandImage


class TestWandOperations(unittest.TestCase):
    def setUp(self):
        with open('tests/images/transparent.png', 'rb') as f:
            self.image = WandImage.open(PNGImageFile(f))

    def test_get_size(self):
        width, height = self.image.get_size()
        self.assertEqual(width, 200)
        self.assertEqual(height, 150)

    def test_resize(self):
        resized_image = self.image.resize((100, 75))
        self.assertEqual(resized_image.get_size(), (100, 75))

    def test_crop(self):
        cropped_image = self.image.crop((10, 10, 100, 100))
        self.assertEqual(cropped_image.get_size(), (90, 90))

    def test_set_background_color_rgb(self):
        red_background_image = self.image.set_background_color_rgb((255, 0, 0))
        self.assertFalse(red_background_image.has_alpha())
        colour = red_background_image.image[10][10]
        self.assertEqual(colour.red, 1.0)
        self.assertEqual(colour.green, 0.0)
        self.assertEqual(colour.blue, 0.0)

    def test_set_background_color_rgb_color_argument_check(self):
        with self.assertRaises(TypeError) as e:
            self.image.set_background_color_rgb('rgb(255, 0, 0)')

        self.assertEqual(str(e.exception), "the 'color' argument must be a 3-element tuple or list")

    def test_save_as_jpeg(self):
        # Remove alpha channel from image
        image = self.image.set_background_color_rgb((255, 255, 255))

        output = io.BytesIO()
        return_value = image.save_as_jpeg(output)
        output.seek(0)

        self.assertEqual(imghdr.what(output), 'jpeg')
        self.assertIsInstance(return_value, JPEGImageFile)
        self.assertEqual(return_value.f, output)

    @unittest.expectedFailure
    def test_save_as_jpeg_optimised(self):
        # Remove alpha channel from image
        image = self.image.set_background_color_rgb((255, 255, 255))

        unoptimised = image.save_as_jpeg(io.BytesIO())
        optimised = image.save_as_jpeg(io.BytesIO(), optimize=True)

        # Optimised image must be smaller than unoptimised image
        self.assertTrue(optimised.f.tell() < unoptimised.f.tell())

    def test_save_as_jpeg_progressive(self):
        # Remove alpha channel from image
        image = self.image.set_background_color_rgb((255, 255, 255))

        image = image.save_as_jpeg(io.BytesIO(), progressive=True)

        self.assertTrue(PILImage.open(image.f).info['progressive'])

    def test_save_as_png(self):
        output = io.BytesIO()
        return_value = self.image.save_as_png(output)
        output.seek(0)

        self.assertEqual(imghdr.what(output), 'png')
        self.assertIsInstance(return_value, PNGImageFile)
        self.assertEqual(return_value.f, output)

    @unittest.expectedFailure
    def test_save_as_png_optimised(self):
        unoptimised = self.image.save_as_png(io.BytesIO())
        optimised = self.image.save_as_png(io.BytesIO(), optimize=True)

        # Optimised image must be smaller than unoptimised image
        self.assertTrue(optimised.f.tell() < unoptimised.f.tell())

    def test_save_as_gif(self):
        output = io.BytesIO()
        return_value = self.image.save_as_gif(output)
        output.seek(0)

        self.assertEqual(imghdr.what(output), 'gif')
        self.assertIsInstance(return_value, GIFImageFile)
        self.assertEqual(return_value.f, output)

    def test_has_alpha(self):
        has_alpha = self.image.has_alpha()
        self.assertTrue(has_alpha)

    def test_has_animation(self):
        has_animation = self.image.has_animation()
        self.assertFalse(has_animation)

    def test_transparent_gif(self):
        with open('tests/images/transparent.gif', 'rb') as f:
            image = WandImage.open(GIFImageFile(f))

        self.assertTrue(image.has_alpha())
        self.assertFalse(image.has_animation())

        # Check that the alpha of pixel 1,1 is 0
        self.assertEqual(image.image[1][1].alpha, 0)

    def test_resize_transparent_gif(self):
        with open('tests/images/transparent.gif', 'rb') as f:
            image = WandImage.open(GIFImageFile(f))

        resized_image = image.resize((100, 75))

        self.assertTrue(resized_image.has_alpha())
        self.assertFalse(resized_image.has_animation())

        # Check that the alpha of pixel 1,1 is 0
        self.assertAlmostEqual(resized_image.image[1][1].alpha, 0, places=6)

    def test_animated_gif(self):
        with open('tests/images/newtons_cradle.gif', 'rb') as f:
            image = WandImage.open(GIFImageFile(f))

        self.assertTrue(image.has_animation())

    def test_resize_animated_gif(self):
        with open('tests/images/newtons_cradle.gif', 'rb') as f:
            image = WandImage.open(GIFImageFile(f))

        resized_image = image.resize((100, 75))

        self.assertTrue(resized_image.has_animation())

    def test_get_wand_image(self):
        wand_image = self.image.get_wand_image()

        self.assertIsInstance(wand_image, _wand_image().Image)


class TestWandImageOrientation(unittest.TestCase):
    def assert_orientation_landscape_image_is_correct(self, image):
        # Check that the image is the correct size (and not rotated)
        self.assertEqual(image.get_size(), (600, 450))

        # Check that the red flower is in the bottom left
        # The JPEGs have compressed slightly differently so the colours won't be spot on
        colour = image.image[282][155]
        self.assertAlmostEqual(colour.red * 255, 217, delta=12)
        self.assertAlmostEqual(colour.green * 255, 38, delta=11)
        self.assertAlmostEqual(colour.blue * 255, 46, delta=13)

        # Check that the water is at the bottom
        colour = image.image[434][377]
        self.assertAlmostEqual(colour.red * 255, 85, delta=11)
        self.assertAlmostEqual(colour.green * 255, 93, delta=12)
        self.assertAlmostEqual(colour.blue * 255, 65, delta=11)

    def test_jpeg_with_orientation_1(self):
        with open('tests/images/orientation/landscape_1.jpg', 'rb') as f:
            image = WandImage.open(JPEGImageFile(f))

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_2(self):
        with open('tests/images/orientation/landscape_2.jpg', 'rb') as f:
            image = WandImage.open(JPEGImageFile(f))

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_3(self):
        with open('tests/images/orientation/landscape_3.jpg', 'rb') as f:
            image = WandImage.open(JPEGImageFile(f))

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_4(self):
        with open('tests/images/orientation/landscape_4.jpg', 'rb') as f:
            image = WandImage.open(JPEGImageFile(f))

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_5(self):
        with open('tests/images/orientation/landscape_5.jpg', 'rb') as f:
            image = WandImage.open(JPEGImageFile(f))

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_6(self):
        with open('tests/images/orientation/landscape_6.jpg', 'rb') as f:
            image = WandImage.open(JPEGImageFile(f))

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_7(self):
        with open('tests/images/orientation/landscape_7.jpg', 'rb') as f:
            image = WandImage.open(JPEGImageFile(f))

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_8(self):
        with open('tests/images/orientation/landscape_8.jpg', 'rb') as f:
            image = WandImage.open(JPEGImageFile(f))

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)
