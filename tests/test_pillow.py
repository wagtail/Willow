import unittest
import io
import imghdr

from willow.states.files import PNGImageFileState, GIFImageFileState
from willow.states.pillow import PillowImageState


class TestPillowOperations(unittest.TestCase):
    def setUp(self):
        with open('tests/images/transparent.png', 'rb') as f:
            self.image = PillowImageState.open(PNGImageFileState(f))

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
        self.image.save_as_jpeg(output)
        output.seek(0)

        self.assertEqual(imghdr.what(output), 'jpeg')

    def test_save_as_png(self):
        output = io.BytesIO()
        self.image.save_as_png(output)
        output.seek(0)

        self.assertEqual(imghdr.what(output), 'png')

    def test_save_as_gif(self):
        output = io.BytesIO()
        self.image.save_as_gif(output)
        output.seek(0)

        self.assertEqual(imghdr.what(output), 'gif')

    def test_has_alpha(self):
        has_alpha = self.image.has_alpha()
        self.assertTrue(has_alpha)

    def test_has_animation(self):
        has_animation = self.image.has_animation()
        self.assertFalse(has_animation)

    def test_transparent_gif(self):
        with open('tests/images/transparent.gif', 'rb') as f:
            image = PillowImageState.open(GIFImageFileState(f))

        self.assertTrue(image.has_alpha())
        self.assertFalse(image.has_animation())

        # Check that the alpha of pixel 1,1 is 0
        self.assertEqual(image.image.convert('RGBA').getpixel((1, 1))[3], 0)

    @unittest.expectedFailure
    def test_resize_transparent_gif(self):
        with open('tests/images/transparent.gif', 'rb') as f:
            image = PillowImageState.open(GIFImageFileState(f))

        resized_image = image.resize((100, 75))

        self.assertTrue(resized_image.has_alpha())
        self.assertFalse(resized_image.has_animation())

        # Check that the alpha of pixel 1,1 is 0
        self.assertEqual(resized_image.image.convert('RGBA').getpixel((1, 1))[3], 0)

    def test_save_transparent_gif(self):
        with open('tests/images/transparent.gif', 'rb') as f:
            image = PillowImageState.open(GIFImageFileState(f))

        # Save it into memory
        f = io.BytesIO()
        image.save_as_gif(f)

        # Reload it
        f.seek(0)
        image = PillowImageState.open(GIFImageFileState(f))

        self.assertTrue(image.has_alpha())
        self.assertFalse(image.has_animation())

        # Check that the alpha of pixel 1,1 is 0
        self.assertEqual(image.image.convert('RGBA').getpixel((1, 1))[3], 0)

    @unittest.expectedFailure # Pillow doesn't support animation
    def test_animated_gif(self):
        with open('tests/images/newtons_cradle.gif', 'rb') as f:
            image = PillowImageState.open(GIFImageFileState(f))

        self.assertFalse(image.has_alpha())
        self.assertTrue(image.has_animation())

    @unittest.expectedFailure # Pillow doesn't support animation
    def test_resize_animated_gif(self):
        with open('tests/images/newtons_cradle.gif', 'rb') as f:
            image = PillowImageState.open(GIFImageFileState(f))

        resized_image = image.resize((100, 75))

        self.assertFalse(resized_image.has_alpha())
        self.assertTrue(resized_image.has_animation())
