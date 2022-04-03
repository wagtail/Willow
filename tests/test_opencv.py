import unittest
import io
from numpy.testing import assert_allclose

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

        self.expected_features = [
            [41.0, 206.0], [16.0, 201.0], [243.0, 208.0], [79.0, 130.0], [120.0, 24.0], [43.0, 119.0], [40.0, 165.0],
            [37.0, 14.0], [250.0, 59.0], [98.0, 6.0], [78.0, 61.0], [201.0, 93.0], [8.0, 114.0], [189.0, 142.0],
            [292.0, 188.0], [201.0, 199.0], [7.0, 154.0], [198.0, 247.0], [235.0, 55.0], [22.0, 36.0]
        ]
        self.expected_faces = [(272, 89, 364, 181), (91, 165, 187, 261)]

    def test_get_size(self):
        width, height = self.image.get_size()
        self.assertEqual(width, 600)
        self.assertEqual(height, 400)

    def test_get_frame_count(self):
        frames = self.image.get_frame_count()
        self.assertEqual(frames, 1)

    def test_has_alpha(self):
        has_alpha = self.image.has_alpha()
        self.assertFalse(has_alpha)

    def test_has_animation(self):
        has_animation = self.image.has_animation()
        self.assertFalse(has_animation)

    def test_detect_features(self):
        features = self.image.detect_features()

        self.assertIsInstance(features, list)
        # There are 20 features in the image
        self.assertEqual(len(features), 20)
        assert_allclose(features, self.expected_features, atol=2)

    def test_detect_faces(self):
        faces = self.image.detect_faces()

        self.assertIsInstance(faces, list)
        # There are two faces in the image
        self.assertEqual(len(faces), 2)
        assert_allclose(faces, self.expected_faces, atol=2)
