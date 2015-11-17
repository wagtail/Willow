import io
import unittest

from willow.image import Image


class TestImghdrJPEGPatch(unittest.TestCase):
    def test_detects_photoshop3_jpeg(self):
        import imghdr

        f = io.BytesIO()
        f.write(b'\xff\xd8\xff\xed\x00,Photoshop 3.0\x00')
        f.seek(0)

        image_format = imghdr.what(f)

        self.assertEqual(image_format, 'jpeg')

    def test_junk(self):
        import imghdr

        f = io.BytesIO()
        f.write(b'Not an image')
        f.seek(0)

        image_format = imghdr.what(f)

        self.assertIsNone(image_format)
