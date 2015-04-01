import unittest
import io
import imghdr

from willow.backends import pillow as pillow_backend


class TestPillowOperations(unittest.TestCase):
    def setUp(self):
        with open('tests/images/transparent.png', 'rb') as f:
            self.backend = pillow_backend.PillowBackend.from_file(f)

    def test_get_size(self):
        width, height = pillow_backend.get_size(self.backend)
        self.assertEqual(width, 200)
        self.assertEqual(height, 150)

    def test_resize(self):
        pillow_backend.resize(self.backend, 100, 75)
        self.assertEqual(self.backend.image.size, (100, 75))

    def test_crop(self):
        pillow_backend.crop(self.backend, 10, 10, 100, 100)
        self.assertEqual(self.backend.image.size, (90, 90))

    def test_save_as_jpeg(self):
        output = io.BytesIO()
        pillow_backend.save_as_jpeg(self.backend, output)
        output.seek(0)

        self.assertEqual(imghdr.what(output), 'jpeg')

    def test_save_as_png(self):
        output = io.BytesIO()
        pillow_backend.save_as_png(self.backend, output)
        output.seek(0)

        self.assertEqual(imghdr.what(output), 'png')

    def test_save_as_gif(self):
        output = io.BytesIO()
        pillow_backend.save_as_gif(self.backend, output)
        output.seek(0)

        self.assertEqual(imghdr.what(output), 'gif')

    def test_has_alpha(self):
        has_alpha = pillow_backend.has_alpha(self.backend)
        self.assertTrue(has_alpha)

    def test_has_animation(self):
        has_animation = pillow_backend.has_animation(self.backend)
        self.assertFalse(has_animation)

    def test_transparent_gif(self):
        with open('tests/images/transparent.gif', 'rb') as f:
            backend = pillow_backend.PillowBackend.from_file(f)

        self.assertTrue(pillow_backend.has_alpha(backend))
        self.assertFalse(pillow_backend.has_animation(backend))

        # Check that the alpha of pixel 1,1 is 0
        self.assertEqual(backend.image.convert('RGBA').getpixel((1, 1))[3], 0)

    def test_resize_transparent_gif(self):
        with open('tests/images/transparent.gif', 'rb') as f:
            backend = pillow_backend.PillowBackend.from_file(f)

        pillow_backend.resize(self.backend, 100, 75)

        self.assertTrue(pillow_backend.has_alpha(backend))
        self.assertFalse(pillow_backend.has_animation(backend))

        # Check that the alpha of pixel 1,1 is 0
        self.assertEqual(backend.image.convert('RGBA').getpixel((1, 1))[3], 0)

    def test_save_transparent_gif(self):
        with open('tests/images/transparent.gif', 'rb') as f:
            backend = pillow_backend.PillowBackend.from_file(f)

        # Save it into memory
        f = io.BytesIO()
        pillow_backend.save_as_gif(backend, f)

        # Reload it
        f.seek(0)
        backend = pillow_backend.PillowBackend.from_file(f)

        self.assertTrue(pillow_backend.has_alpha(backend))
        self.assertFalse(pillow_backend.has_animation(backend))

        # Check that the alpha of pixel 1,1 is 0
        self.assertEqual(backend.image.convert('RGBA').getpixel((1, 1))[3], 0)

    @unittest.expectedFailure # Pillow doesn't support animation
    def test_animated_gif(self):
        with open('tests/images/newtons_cradle.gif', 'rb') as f:
            backend = pillow_backend.PillowBackend.from_file(f)

        self.assertFalse(pillow_backend.has_alpha(backend))
        self.assertTrue(pillow_backend.has_animation(backend))

    @unittest.expectedFailure # Pillow doesn't support animation
    def test_resize_animated_gif(self):
        with open('tests/images/newtons_cradle.gif', 'rb') as f:
            backend = pillow_backend.PillowBackend.from_file(f)

        pillow_backend.resize(self.backend, 100, 75)

        self.assertFalse(pillow_backend.has_alpha(backend))
        self.assertTrue(pillow_backend.has_animation(backend))
