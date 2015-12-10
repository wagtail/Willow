import unittest
import io
import imghdr

from willow.image import JPEGImageFile, PNGImageFile, GIFImageFile
from willow.plugins.pillow import _PIL_Image, PillowImage


class TestPillowOperations(unittest.TestCase):
    def setUp(self):
        with open('tests/images/transparent.png', 'rb') as f:
            self.image = PillowImage.open(PNGImageFile(f))

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

    def test_save_as_jpeg(self):
        output = io.BytesIO()
        return_value = self.image.save_as_jpeg(output)
        output.seek(0)

        self.assertEqual(imghdr.what(output), 'jpeg')
        self.assertIsInstance(return_value, JPEGImageFile)
        self.assertEqual(return_value.f, output)

    def test_save_as_png(self):
        output = io.BytesIO()
        return_value = self.image.save_as_png(output)
        output.seek(0)

        self.assertEqual(imghdr.what(output), 'png')
        self.assertIsInstance(return_value, PNGImageFile)
        self.assertEqual(return_value.f, output)

    def test_save_as_gif(self):
        output = io.BytesIO()
        return_value = self.image.save_as_gif(output)
        output.seek(0)

        self.assertEqual(imghdr.what(output), 'gif')
        self.assertIsInstance(return_value, GIFImageFile)
        self.assertEqual(return_value.f, output)

    def test_save_as_gif_converts_back_to_supported_mode(self):
        output = io.BytesIO()

        with open('tests/images/transparent.gif', 'rb') as f:
            image = PillowImage.open(GIFImageFile(f))
            image.image = image.image.convert('RGB')

        image.save_as_gif(output)
        output.seek(0)

        image = _PIL_Image().open(output)
        self.assertEqual(image.mode, 'P')

    def test_has_alpha(self):
        has_alpha = self.image.has_alpha()
        self.assertTrue(has_alpha)

    def test_has_animation(self):
        has_animation = self.image.has_animation()
        self.assertFalse(has_animation)

    def test_transparent_gif(self):
        with open('tests/images/transparent.gif', 'rb') as f:
            image = PillowImage.open(GIFImageFile(f))

        self.assertTrue(image.has_alpha())
        self.assertFalse(image.has_animation())

        # Check that the alpha of pixel 1,1 is 0
        self.assertEqual(image.image.convert('RGBA').getpixel((1, 1))[3], 0)

    @unittest.expectedFailure
    def test_resize_transparent_gif(self):
        with open('tests/images/transparent.gif', 'rb') as f:
            image = PillowImage.open(GIFImageFile(f))

        resized_image = image.resize((100, 75))

        self.assertTrue(resized_image.has_alpha())
        self.assertFalse(resized_image.has_animation())

        # Check that the alpha of pixel 1,1 is 0
        self.assertEqual(resized_image.image.convert('RGBA').getpixel((1, 1))[3], 0)

    def test_save_transparent_gif(self):
        with open('tests/images/transparent.gif', 'rb') as f:
            image = PillowImage.open(GIFImageFile(f))

        # Save it into memory
        f = io.BytesIO()
        image.save_as_gif(f)

        # Reload it
        f.seek(0)
        image = PillowImage.open(GIFImageFile(f))

        self.assertTrue(image.has_alpha())
        self.assertFalse(image.has_animation())

        # Check that the alpha of pixel 1,1 is 0
        self.assertEqual(image.image.convert('RGBA').getpixel((1, 1))[3], 0)

    @unittest.expectedFailure  # Pillow doesn't support animation
    def test_animated_gif(self):
        with open('tests/images/newtons_cradle.gif', 'rb') as f:
            image = PillowImage.open(GIFImageFile(f))

        self.assertFalse(image.has_alpha())
        self.assertTrue(image.has_animation())

    @unittest.expectedFailure  # Pillow doesn't support animation
    def test_resize_animated_gif(self):
        with open('tests/images/newtons_cradle.gif', 'rb') as f:
            image = PillowImage.open(GIFImageFile(f))

        resized_image = image.resize((100, 75))

        self.assertFalse(resized_image.has_alpha())
        self.assertTrue(resized_image.has_animation())


class TestPillowImageOrientation(unittest.TestCase):
    def assert_orientation_landscape_image_is_correct(self, image):
        # Check that the image is the correct size (and not rotated)
        self.assertEqual(image.get_size(), (600, 450))

        # Check that the red flower is in the bottom left
        # The JPEGs have compressed slightly differently so the colours won't be spot on
        colour = image.image.convert('RGB').getpixel((155, 282))
        self.assertAlmostEqual(colour[0], 217, delta=10)
        self.assertAlmostEqual(colour[1], 38, delta=11)
        self.assertAlmostEqual(colour[2], 46, delta=13)

        # Check that the water is at the bottom
        colour = image.image.convert('RGB').getpixel((377, 434))
        self.assertAlmostEqual(colour[0], 85, delta=11)
        self.assertAlmostEqual(colour[1], 93, delta=12)
        self.assertAlmostEqual(colour[2], 65, delta=11)

    def test_jpeg_with_orientation_1(self):
        with open('tests/images/orientation/landscape_1.jpg', 'rb') as f:
            image = PillowImage.open(JPEGImageFile(f))

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_2(self):
        with open('tests/images/orientation/landscape_2.jpg', 'rb') as f:
            image = PillowImage.open(JPEGImageFile(f))

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_3(self):
        with open('tests/images/orientation/landscape_3.jpg', 'rb') as f:
            image = PillowImage.open(JPEGImageFile(f))

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_4(self):
        with open('tests/images/orientation/landscape_4.jpg', 'rb') as f:
            image = PillowImage.open(JPEGImageFile(f))

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_5(self):
        with open('tests/images/orientation/landscape_5.jpg', 'rb') as f:
            image = PillowImage.open(JPEGImageFile(f))

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_6(self):
        with open('tests/images/orientation/landscape_6.jpg', 'rb') as f:
            image = PillowImage.open(JPEGImageFile(f))

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_7(self):
        with open('tests/images/orientation/landscape_7.jpg', 'rb') as f:
            image = PillowImage.open(JPEGImageFile(f))

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_8(self):
        with open('tests/images/orientation/landscape_8.jpg', 'rb') as f:
            image = PillowImage.open(JPEGImageFile(f))

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)
