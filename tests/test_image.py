import io
import os
import unittest
from tempfile import NamedTemporaryFile, SpooledTemporaryFile
from unittest import mock
from xml.etree.ElementTree import ParseError as XMLParseError

import filetype

from willow.image import (
    AvifImageFile,
    BMPImageFile,
    GIFImageFile,
    HeicImageFile,
    IcoImageFile,
    Image,
    ImageFile,
    JPEGImageFile,
    PNGImageFile,
    SvgImageFile,
    TIFFImageFile,
    UnrecognisedImageFormatError,
    WebPImageFile,
)
from willow.optimizers.base import OptimizerBase
from willow.registry import registry


class BrokenImageFileImplementation(ImageFile):
    pass


class TestImageFile(unittest.TestCase):
    def test_image_format_must_be_implemented(self):
        broken = BrokenImageFileImplementation(None)
        with self.assertRaises(NotImplementedError):
            broken.format_name

    def test_mime_type_must_be_implemented(self):
        broken = BrokenImageFileImplementation(None)
        with self.assertRaises(NotImplementedError):
            broken.mime_type

    def test_implementations_have_required_methods(self):
        for image_class in ImageFile.__subclasses__():
            if image_class == BrokenImageFileImplementation:
                continue

            with self.subTest(image_class):
                self.assertTrue(hasattr(image_class, "mime_type"))
                self.assertTrue(hasattr(image_class, "format_name"))


class TestDetectImageFormatFromStream(unittest.TestCase):
    """
    Tests that Image.open responds correctly to different image headers.

    Note that Image.open is not responsible for verifying image contents so
    these tests do not require valid images.
    """

    def test_opens_jpeg(self):
        f = io.BytesIO()
        f.write(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00")
        f.seek(0)

        image = Image.open(f)
        self.assertIsInstance(image, JPEGImageFile)
        self.assertEqual(image.format_name, "jpeg")
        self.assertEqual(image.mime_type, "image/jpeg")

    def test_opens_png(self):
        f = io.BytesIO()
        f.write(b"\x89PNG\x0d\x0a\x1a\x0a")
        f.seek(0)

        image = Image.open(f)
        self.assertIsInstance(image, PNGImageFile)
        self.assertEqual(image.format_name, "png")
        self.assertEqual(image.mime_type, "image/png")

    def test_opens_gif(self):
        f = io.BytesIO()
        f.write(b"GIF89a")
        f.seek(0)

        image = Image.open(f)
        self.assertIsInstance(image, GIFImageFile)
        self.assertEqual(image.format_name, "gif")
        self.assertEqual(image.mime_type, "image/gif")

    def test_raises_error_on_invalid_header(self):
        f = io.BytesIO()
        f.write(b"Not an image")
        f.seek(0)

        with self.assertRaises(UnrecognisedImageFormatError):
            Image.open(f)

    def test_opens_svg(self):
        f = io.BytesIO(b"<svg></svg>")
        image = Image.open(f)
        self.assertIsInstance(image, SvgImageFile)
        self.assertEqual(image.format_name, "svg")
        self.assertEqual(image.mime_type, "image/svg+xml")

    def test_invalid_svg_raises(self):
        f = io.BytesIO(b"<svg><")
        with self.assertRaises(XMLParseError):
            Image.open(f)


class TestImageFormats(unittest.TestCase):
    """
    Tests image formats that are not well covered by the remaining tests.
    """

    def test_jpeg(self):
        with open("tests/images/flower.jpg", "rb") as f:
            image = Image.open(f)
            width, height = image.get_size()

        self.assertIsInstance(image, JPEGImageFile)
        self.assertEqual(width, 480)
        self.assertEqual(height, 360)
        self.assertEqual(image.mime_type, "image/jpeg")

    def test_png(self):
        with open("tests/images/transparent.png", "rb") as f:
            image = Image.open(f)
            width, height = image.get_size()

        self.assertIsInstance(image, PNGImageFile)
        self.assertEqual(width, 200)
        self.assertEqual(height, 150)
        self.assertEqual(image.mime_type, "image/png")

    def test_gif(self):
        with open("tests/images/newtons_cradle.gif", "rb") as f:
            image = Image.open(f)
            width, height = image.get_size()

        self.assertIsInstance(image, GIFImageFile)
        self.assertEqual(width, 480)
        self.assertEqual(height, 360)
        self.assertEqual(image.mime_type, "image/gif")

    def test_bmp(self):
        with open("tests/images/sails.bmp", "rb") as f:
            image = Image.open(f)
            width, height = image.get_size()

        self.assertIsInstance(image, BMPImageFile)
        self.assertEqual(width, 768)
        self.assertEqual(height, 512)
        self.assertEqual(image.mime_type, "image/bmp")

    def test_tiff(self):
        with open("tests/images/cameraman.tif", "rb") as f:
            image = Image.open(f)
            width, height = image.get_size()

        self.assertIsInstance(image, TIFFImageFile)
        self.assertEqual(width, 256)
        self.assertEqual(height, 256)
        self.assertEqual(image.mime_type, "image/tiff")

    def test_webp(self):
        with open("tests/images/tree.webp", "rb") as f:
            image = Image.open(f)
            width, height = image.get_size()

        self.assertIsInstance(image, WebPImageFile)
        self.assertEqual(width, 320)
        self.assertEqual(height, 241)
        self.assertEqual(image.mime_type, "image/webp")

    def test_heic(self):
        with open("tests/images/tree.heic", "rb") as f:
            image = Image.open(f)
            width, height = image.get_size()

        self.assertIsInstance(image, HeicImageFile)
        self.assertEqual(width, 320)
        self.assertEqual(height, 241)
        self.assertEqual(image.mime_type, "image/heic")

    def test_avif(self):
        with open("tests/images/tree.avif", "rb") as f:
            image = Image.open(f)
            width, height = image.get_size()

        self.assertIsInstance(image, AvifImageFile)
        self.assertEqual(width, 320)
        self.assertEqual(height, 241)
        self.assertEqual(image.mime_type, "image/avif")

    def test_ico(self):
        with open("tests/images/wagtail.ico", "rb") as f:
            image = Image.open(f)
            width, height = image.get_size()

        self.assertIsInstance(image, IcoImageFile)
        self.assertEqual(width, 48)
        self.assertEqual(height, 48)
        self.assertEqual(image.mime_type, "image/x-icon")


class TestSaveImage(unittest.TestCase):
    """
    Image.save must work out the name of the underlying operation based on the
    format name and call it. It must not however, allow an invalid image format
    name to be passed.
    """

    def test_save_as_jpeg(self):
        image = Image()
        image.save_as_jpeg = mock.MagicMock()

        image.save("jpeg", "outfile")
        image.save_as_jpeg.assert_called_with("outfile", apply_optimizers=True)

    def test_save_as_heic(self):
        with open("tests/images/sails.bmp", "rb") as f:
            image = Image.open(f)
            buf = io.BytesIO()
            image.save("heic", buf)
            buf.seek(0)
            image = Image.open(buf)
            self.assertIsInstance(image, HeicImageFile)
            self.assertEqual(image.mime_type, "image/heic")

    def test_save_as_avif(self):
        with open("tests/images/sails.bmp", "rb") as f:
            image = Image.open(f)
            buf = io.BytesIO()
            image.save("avif", buf)
            buf.seek(0)
            image = Image.open(buf)
            self.assertIsInstance(image, AvifImageFile)
            self.assertEqual(image.mime_type, "image/avif")

    def test_save_as_ico(self):
        with open("tests/images/sails.bmp", "rb") as f:
            image = Image.open(f)
            buf = io.BytesIO()
            image.save("ico", buf)
            buf.seek(0)
            image = Image.open(buf)
            self.assertIsInstance(image, IcoImageFile)
            self.assertEqual(image.mime_type, "image/x-icon")

    def test_save_as_foo(self):
        image = Image()
        image.save_as_jpeg = mock.MagicMock()

        with self.assertRaises(ValueError):
            image.save("foo", "outfile")

        self.assertFalse(image.save_as_jpeg.mock_calls)


@mock.patch("willow.optimizers.base.OptimizerBase.process")
class TestOptimizeImage(unittest.TestCase):
    class DummyOptimizer(OptimizerBase):
        library_name = "dummy"
        image_format = "jpeg"

        @classmethod
        def check_library(cls) -> bool:
            return True

    def setUp(self):
        with mock.patch.dict(os.environ, {"WILLOW_OPTIMIZERS": "true"}):
            registry.register_optimizer(self.DummyOptimizer)

        self.image = Image()

    def tearDown(self):
        # reset the registry as we get the global state
        registry._registered_optimizers = []

    def test_optimize_with_file_path(self, mock_process):
        self.image.optimize("outfile", "jpeg")
        mock_process.assert_called_with("outfile")

    @mock.patch("willow.image.NamedTemporaryFile")
    @mock.patch("willow.image.os.unlink")
    def test_optimize_with_bytes(
        self, mock_unlink, mock_named_temporary_file, mock_process
    ):
        mock_named_temporary_file.return_value.__enter__.return_value.name = "tempfile"
        self.image.optimize(b"outfile", "jpeg")
        mock_process.assert_called_with("tempfile")
        mock_unlink.assert_called_with("tempfile")

    @mock.patch("willow.image.NamedTemporaryFile")
    @mock.patch("willow.image.os.unlink")
    @mock.patch("builtins.open", mock.mock_open(read_data=b"test"))
    def test_optimize_with_spooled_temporary_file(
        self, mock_unlink, mock_named_temporary_file, mock_process
    ):
        mock_named_temporary_file.return_value.__enter__.return_value.name = "tempfile"
        with SpooledTemporaryFile() as spooled:
            self.image.optimize(spooled, "jpeg")
        mock_process.assert_called_with("tempfile")
        mock_unlink.assert_called_with("tempfile")

    @mock.patch("builtins.open", mock.mock_open(read_data=b"test"))
    def test_optimize_with_named_temporary_file(self, mock_process):
        with NamedTemporaryFile() as named_temporary_file:
            self.image.optimize(named_temporary_file, "jpeg")
            mock_process.assert_called_with(named_temporary_file.name)

    @mock.patch("willow.image.NamedTemporaryFile")
    @mock.patch("willow.image.os.unlink")
    def test_optimize_with_an_actual_file(
        self, mock_unlink, mock_named_temporary_file, mock_process
    ):
        # We are only interested in opening the actual file, and since optimize will write in place
        # let's preserve the original file by mocking the open call with it so we don't end up changing it.
        with open("tests/images/people.jpg", "rb") as f:
            original_value = f.read()
        with open("tests/images/people.jpg", "wb") as f, mock.patch(
            "builtins.open", mock.mock_open(read_data=original_value)
        ):
            self.image.optimize(f, "jpeg")
        mock_process.assert_called_with("tests/images/people.jpg")
        mock_unlink.assert_not_called()


class TestImghdrJPEGPatch(unittest.TestCase):
    def test_detects_photoshop3_jpeg(self):
        f = io.BytesIO()
        f.write(b"\xff\xd8\xff\xed\x00,Photoshop 3.0\x00")
        f.seek(0)

        image_format = filetype.guess_extension(f)

        self.assertEqual(image_format, "jpg")

    def test_junk(self):
        f = io.BytesIO()
        f.write(b"Not an image")
        f.seek(0)

        image_format = filetype.guess_extension(f)

        self.assertIsNone(image_format)
