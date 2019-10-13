import unittest
import io
import imghdr

from PIL import Image as PILImage

from willow.image import JPEGImageFile, PNGImageFile, GIFImageFile, WebPImageFile
from willow.plugins.pillow import _PIL_Image, PillowImage, UnsupportedRotation


no_webp_support = not PillowImage.is_format_supported("WEBP")


class TestPillowOperations(unittest.TestCase):
    def setUp(self):
        with open('tests/images/transparent.png', 'rb') as f:
            self.image = PillowImage.open(PNGImageFile(f))

    def test_get_size(self):
        width, height = self.image.get_size()
        self.assertEqual(width, 200)
        self.assertEqual(height, 150)

    def test_get_frame_count(self):
        frames = self.image.get_frame_count()
        self.assertEqual(frames, 1)

    def test_get_pixel_count(self):
        pixels = self.image.get_pixel_count()
        self.assertEqual(pixels, 200 * 150)

    def test_resize(self):
        resized_image = self.image.resize((100, 75))
        self.assertEqual(resized_image.get_size(), (100, 75))

    def test_crop(self):
        cropped_image = self.image.crop((10, 10, 100, 100))
        self.assertEqual(cropped_image.get_size(), (90, 90))

    def test_rotate(self):
        rotated_image = self.image.rotate(90)
        width, height = rotated_image.get_size()
        self.assertEqual((width, height), (150, 200))

    def test_rotate_without_multiple_of_90(self):
        with self.assertRaises(UnsupportedRotation) as e:
            rotated_image = self.image.rotate(45)

    def test_rotate_greater_than_360(self):
        # 450 should end up the same as a 90 rotation
        rotated_image = self.image.rotate(450)
        width, height = rotated_image.get_size()
        self.assertEqual((width, height), (150, 200))

    def test_rotate_multiple_of_360(self):
        rotated_image = self.image.rotate(720)
        width, height = rotated_image.get_size()
        self.assertEqual((width, height), (200, 150))

    def test_set_background_color_rgb(self):
        red_background_image = self.image.set_background_color_rgb((255, 0, 0))
        self.assertFalse(red_background_image.has_alpha())
        self.assertEqual(red_background_image.image.getpixel((10, 10)), (255, 0, 0))

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

    def test_save_as_gif_converts_back_to_supported_mode(self):
        output = io.BytesIO()

        with open('tests/images/transparent.gif', 'rb') as f:
            image = PillowImage.open_animated(GIFImageFile(f))
            image.frames[0] = image.frames[0].convert('RGB')

        image.save_as_gif(output)
        output.seek(0)

        image = _PIL_Image().open(output)
        self.assertEqual(image.mode, 'P')

    def test_save_as_gif_animated(self):
        with open('tests/images/newtons_cradle.gif', 'rb') as f:
            image = PillowImage.open_animated(GIFImageFile(f))

        output = io.BytesIO()
        return_value = image.save_as_gif(output)
        output.seek(0)

        loaded_image = PillowImage.open_animated(GIFImageFile(output))

        self.assertTrue(loaded_image.has_animation())
        self.assertEqual(loaded_image.get_frame_count(), 34)

    def test_has_alpha(self):
        has_alpha = self.image.has_alpha()
        self.assertTrue(has_alpha)

    def test_has_animation(self):
        has_animation = self.image.has_animation()
        self.assertFalse(has_animation)

    def test_transparent_gif(self):
        with open('tests/images/transparent.gif', 'rb') as f:
            image = PillowImage.open_animated(GIFImageFile(f))

        self.assertTrue(image.has_alpha())
        self.assertFalse(image.has_animation())

        # Check that the alpha of pixel 1,1 is 0
        self.assertEqual(image.image.convert('RGBA').getpixel((1, 1))[3], 0)

    def test_resize_transparent_gif(self):
        with open('tests/images/transparent.gif', 'rb') as f:
            image = PillowImage.open_animated(GIFImageFile(f))

        resized_image = image.resize((100, 75))

        self.assertTrue(resized_image.has_alpha())
        self.assertFalse(resized_image.has_animation())

        # Check that the alpha of pixel 1,1 is 0
        self.assertEqual(resized_image.image.convert('RGBA').getpixel((1, 1))[3], 0)

    def test_save_transparent_gif(self):
        with open('tests/images/transparent.gif', 'rb') as f:
            image = PillowImage.open_animated(GIFImageFile(f))

        # Save it into memory
        f = io.BytesIO()
        image.save_as_gif(f)

        # Reload it
        f.seek(0)
        image = PillowImage.open_animated(GIFImageFile(f))

        self.assertTrue(image.has_alpha())
        self.assertFalse(image.has_animation())

        # Check that the alpha of pixel 1,1 is 0
        self.assertEqual(image.image.convert('RGBA').getpixel((1, 1))[3], 0)

    def test_animated_gif(self):
        with open('tests/images/newtons_cradle.gif', 'rb') as f:
            image = PillowImage.open_animated(GIFImageFile(f))

        self.assertTrue(image.has_alpha())
        self.assertTrue(image.has_animation())

    def test_resize_animated_gif(self):
        with open('tests/images/newtons_cradle.gif', 'rb') as f:
            image = PillowImage.open_animated(GIFImageFile(f))

        resized_image = image.resize((100, 75))

        self.assertTrue(resized_image.has_alpha())
        self.assertTrue(resized_image.has_animation())

    def test_save_transparent_animated_gif(self):
        with open('tests/images/animatedgifwithtransparency.gif', 'rb') as f:
            image = PillowImage.open_animated(GIFImageFile(f))

        # Save it into memory
        f = io.BytesIO()
        image.save_as_gif(f)

        # Reload it
        f.seek(0)
        image = PillowImage.open_animated(GIFImageFile(f))

        self.assertTrue(image.has_alpha())
        self.assertTrue(image.has_animation())

    def test_get_pillow_image(self):
        pillow_image = self.image.get_pillow_image()

        self.assertIsInstance(pillow_image, _PIL_Image().Image)

    @unittest.skipIf(no_webp_support, "Pillow does not have WebP support")
    def test_save_as_webp(self):
        output = io.BytesIO()
        return_value = self.image.save_as_webp(output)
        output.seek(0)

        self.assertEqual(imghdr.what(output), 'webp')
        self.assertIsInstance(return_value, WebPImageFile)
        self.assertEqual(return_value.f, output)

    @unittest.skipIf(no_webp_support, "Pillow does not have WebP support")
    def test_open_webp(self):
        with open('tests/images/tree.webp', 'rb') as f:
            image = PillowImage.open(WebPImageFile(f))

        self.assertFalse(image.has_alpha())
        self.assertFalse(image.has_animation())

    @unittest.skipIf(no_webp_support, "Pillow does not have WebP support")
    def test_open_webp_w_alpha(self):
        with open('tests/images/tux_w_alpha.webp', 'rb') as f:
            image = PillowImage.open(WebPImageFile(f))

        self.assertTrue(image.has_alpha())
        self.assertFalse(image.has_animation())


class TestPillowImageOrientation(unittest.TestCase):
    def assert_orientation_landscape_image_is_correct(self, image):
        # Check that the image is the correct size (and not rotated)
        self.assertEqual(image.get_size(), (600, 450))

        # Check that the red flower is in the bottom left
        # The JPEGs have compressed slightly differently so the colours won't be spot on
        colour = image.image.convert('RGB').getpixel((155, 282))
        self.assertAlmostEqual(colour[0], 217, delta=25)
        self.assertAlmostEqual(colour[1], 38, delta=25)
        self.assertAlmostEqual(colour[2], 46, delta=25)

        # Check that the water is at the bottom
        colour = image.image.convert('RGB').getpixel((377, 434))
        self.assertAlmostEqual(colour[0], 85, delta=25)
        self.assertAlmostEqual(colour[1], 93, delta=25)
        self.assertAlmostEqual(colour[2], 65, delta=25)

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
