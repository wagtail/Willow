import unittest
import io
import imghdr

from PIL import Image as PILImage

from willow.image import (
    GIFImageFile, BadImageOperationError, WebMVP9ImageFile, OggTheoraImageFile, MP4H264ImageFile
)
from willow.plugins.ffmpeg import FFMpegLazyVideo, probe


class TestFFMpegOperations(unittest.TestCase):
    def setUp(self):
        self.f = open('tests/images/newtons_cradle.gif', 'rb')
        self.image = FFMpegLazyVideo.open(GIFImageFile(self.f))

    def tearDown(self):
        self.f.close()

    def test_get_size(self):
        width, height = self.image.get_size()
        self.assertEqual(width, 480)
        self.assertEqual(height, 360)

    def test_get_frame_count(self):
        frames = self.image.get_frame_count()
        self.assertEqual(frames, 34)

    def test_resize(self):
        resized_image = self.image.resize((100, 75))
        self.assertEqual(resized_image.get_size(), (100, 75))

    def test_crop(self):
        cropped_image = self.image.crop((10, 10, 100, 100))

        # Cropping not supported, but image will be resized
        self.assertEqual(cropped_image.get_size(), (90, 90))

    def test_rotate(self):
        rotated_image = self.image.rotate(90)
        width, height = rotated_image.get_size()

        # Not supported, image will not be rotated
        self.assertEqual((width, height), (480, 360))

    def test_set_background_color_rgb(self):
        # Not supported, would do nothing
        red_background_image = self.image.set_background_color_rgb((255, 0, 0))
        self.assertFalse(red_background_image.has_alpha())

    def test_save_as_webm_vp9(self):
        output = io.BytesIO()
        return_value = self.image.save_as_webm_vp9(output)
        output.seek(0)

        probe_data = probe(output)

        self.assertEqual(probe_data['format']['format_name'], 'matroska,webm')
        self.assertEqual(probe_data['streams'][0]['codec_name'], 'vp9')
        self.assertIsInstance(return_value, WebMVP9ImageFile)
        self.assertEqual(return_value.f, output)

    def test_save_as_ogg_theora(self):
        output = io.BytesIO()
        return_value = self.image.save_as_ogg_theora(output)
        output.seek(0)

        probe_data = probe(output)

        self.assertEqual(probe_data['format']['format_name'], 'ogg')
        self.assertEqual(probe_data['streams'][0]['codec_name'], 'theora')
        self.assertIsInstance(return_value, OggTheoraImageFile)
        self.assertEqual(return_value.f, output)

    def test_save_as_mp4_h264(self):
        output = io.BytesIO()
        return_value = self. image.save_as_mp4_h264(output)
        output.seek(0)

        probe_data = probe(output)

        self.assertEqual(probe_data['format']['format_name'], 'mov,mp4,m4a,3gp,3g2,mj2')
        self.assertEqual(probe_data['streams'][0]['codec_name'], 'h264')
        self.assertIsInstance(return_value, MP4H264ImageFile)
        self.assertEqual(return_value.f, output)

    def test_has_alpha(self):
        has_alpha = self.image.has_alpha()
        self.assertFalse(has_alpha)

    def test_has_animation(self):
        has_animation = self.image.has_animation()
        self.assertTrue(has_animation)

    def test_transparent_gif(self):
        with open('tests/images/transparent.gif', 'rb') as f:
            image = FFMpegLazyVideo.open(GIFImageFile(f))

            # Transparency not supported
            self.assertFalse(image.has_alpha())
