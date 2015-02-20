import unittest2

from willow.backends import pillow as pillow_backend


class TestPillowOperations(unittest2.TestCase):
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

    def test_has_alpha(self):
        has_alpha = pillow_backend.has_alpha(self.backend)
        self.assertTrue(has_alpha)

    def test_has_animation(self):
        has_animation = pillow_backend.has_animation(self.backend)
        self.assertFalse(has_animation)
