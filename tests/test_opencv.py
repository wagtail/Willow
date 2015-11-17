import unittest
import io
import imghdr

from willow.image import JPEGImageFile
from willow.plugins.pillow import PillowImage
from willow.plugins.opencv import OpenCVColorImage, OpenCVGrayscaleImage


class TestOpenCVOperations(unittest.TestCase):
    def setUp(self):
        with open('tests/images/people.jpg', 'rb') as f:
            # Open the image via Pillow
            pillow_image = PillowImage.open(JPEGImageFile(f))
            buffer_rgb = pillow_image.to_buffer_rgb()
            colour_image = OpenCVColorImage.from_buffer_rgb(buffer_rgb)
            self.image = OpenCVGrayscaleImage.from_color(colour_image)

    def test_get_size(self):
        width, height = self.image.get_size()
        self.assertEqual(width, 600)
        self.assertEqual(height, 400)

    def test_has_alpha(self):
        has_alpha = self.image.has_alpha()
        self.assertFalse(has_alpha)

    def test_has_animation(self):
        has_animation = self.image.has_animation()
        self.assertFalse(has_animation)

    def test_detect_features(self):
        features = self.image.detect_features()

        # There are 20 features in the image
        self.assertEqual(len(features), 20)

    def test_detect_faces(self):
        faces = self.image.detect_faces()

        # There are two faces in the image
        self.assertEqual(len(faces), 2)
