import unittest
import io
import imghdr

from willow.backends import wand as wand_backend


class TestWandOperations(unittest.TestCase):
    def setUp(self):
        with open('tests/images/transparent.png', 'rb') as f:
            self.backend = wand_backend.WandBackend.from_file(f)

    def test_get_size(self):
        width, height = wand_backend.get_size(self.backend)
        self.assertEqual(width, 200)
        self.assertEqual(height, 150)

    def test_resize(self):
        wand_backend.resize(self.backend, 100, 75)
        self.assertEqual(self.backend.image.size, (100, 75))

    def test_crop(self):
        wand_backend.crop(self.backend, 10, 10, 100, 100)
        self.assertEqual(self.backend.image.size, (90, 90))

    def test_save_as_jpeg(self):
        output = io.BytesIO()
        wand_backend.save_as_jpeg(self.backend, output)
        output.seek(0)

        self.assertEqual(imghdr.what(output), 'jpeg')

    def test_save_as_png(self):
        output = io.BytesIO()
        wand_backend.save_as_png(self.backend, output)
        output.seek(0)

        self.assertEqual(imghdr.what(output), 'png')

    def test_save_as_gif(self):
        output = io.BytesIO()
        wand_backend.save_as_gif(self.backend, output)
        output.seek(0)

        self.assertEqual(imghdr.what(output), 'gif')

    def test_has_alpha(self):
        has_alpha = wand_backend.has_alpha(self.backend)
        self.assertTrue(has_alpha)

    def test_has_animation(self):
        has_animation = wand_backend.has_animation(self.backend)
        self.assertFalse(has_animation)

    def test_transparent_gif(self):
        with open('tests/images/transparent.gif', 'rb') as f:
            backend = wand_backend.WandBackend.from_file(f)

        self.assertTrue(wand_backend.has_alpha(backend))
        self.assertFalse(wand_backend.has_animation(backend))

        # Check that the alpha of pixel 1,1 is 0
        self.assertEqual(backend.image[1][1].alpha, 0)

    def test_resize_transparent_gif(self):
        with open('tests/images/transparent.gif', 'rb') as f:
            backend = wand_backend.WandBackend.from_file(f)

        wand_backend.resize(backend, 100, 75)

        self.assertTrue(wand_backend.has_alpha(backend))
        self.assertFalse(wand_backend.has_animation(backend))

        # Check that the alpha of pixel 1,1 is 0
        self.assertAlmostEqual(backend.image[1][1].alpha, 0, places=6)

    def test_animated_gif(self):
        with open('tests/images/newtons_cradle.gif', 'rb') as f:
            backend = wand_backend.WandBackend.from_file(f)

        self.assertTrue(wand_backend.has_animation(backend))

    def test_resize_animated_gif(self):
        with open('tests/images/newtons_cradle.gif', 'rb') as f:
            backend = wand_backend.WandBackend.from_file(f)

        wand_backend.resize(self.backend, 100, 75)

        self.assertTrue(wand_backend.has_animation(backend))


class TestWandImageOrientation(unittest.TestCase):
    def assert_orientation_landscape_image_is_correct(self, image):
        # Check that the image is the correct size (and not rotated)
        self.assertEqual(image.get_size(), (600, 450))

        # Check that the red flower is in the bottom left
        # The JPEGs have compressed slightly differently so the colours won't be spot on
        colour = image.image[282][155]
        self.assertAlmostEqual(colour.red * 255, 217, delta=10)
        self.assertAlmostEqual(colour.green * 255, 38, delta=11)
        self.assertAlmostEqual(colour.blue * 255, 46, delta=13)

        # Check that the water is at the bottom
        colour = image.image[434][377]
        self.assertAlmostEqual(colour.red * 255, 85, delta=11)
        self.assertAlmostEqual(colour.green * 255, 93, delta=12)
        self.assertAlmostEqual(colour.blue * 255, 65, delta=11)

    def test_jpeg_with_orientation_1(self):
        with open('tests/images/orientation/landscape_1.jpg', 'rb') as f:
            image = wand_backend.WandBackend.from_file(f)
        image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_2(self):
        with open('tests/images/orientation/landscape_2.jpg', 'rb') as f:
            image = wand_backend.WandBackend.from_file(f)
        image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_3(self):
        with open('tests/images/orientation/landscape_3.jpg', 'rb') as f:
            image = wand_backend.WandBackend.from_file(f)
        image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_4(self):
        with open('tests/images/orientation/landscape_4.jpg', 'rb') as f:
            image = wand_backend.WandBackend.from_file(f)
        image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_5(self):
        with open('tests/images/orientation/landscape_5.jpg', 'rb') as f:
            image = wand_backend.WandBackend.from_file(f)
        image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_6(self):
        with open('tests/images/orientation/landscape_6.jpg', 'rb') as f:
            image = wand_backend.WandBackend.from_file(f)
        image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_7(self):
        with open('tests/images/orientation/landscape_7.jpg', 'rb') as f:
            image = wand_backend.WandBackend.from_file(f)
        image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)

    def test_jpeg_with_orientation_8(self):
        with open('tests/images/orientation/landscape_8.jpg', 'rb') as f:
            image = wand_backend.WandBackend.from_file(f)
        image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)
