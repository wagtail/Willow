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
