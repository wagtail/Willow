import io
import os
import unittest
from subprocess import STDOUT, CalledProcessError
from tempfile import NamedTemporaryFile
from unittest import TestCase, mock

from willow.optimizers import Cwebp, Gifsicle, Jpegoptim, Pngquant
from willow.optimizers.base import OptimizerBase
from willow.optimizers.cjxl import Cjxl
from willow.registry import WillowRegistry


class OptimizerTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        class DummyOptimizer(OptimizerBase):
            library_name = "dummy"
            image_format = "FOO"

        cls.DummyOptimizer = DummyOptimizer

    def setUp(self) -> None:
        self.registry = WillowRegistry()

    @mock.patch("willow.optimizers.base.subprocess.check_output")
    def test_check_library(self, mock_check_output):
        self.assertTrue(self.DummyOptimizer.check_library())

    @mock.patch("willow.optimizers.base.subprocess.check_output")
    def test_check_library_fail(self, mock_check_output):
        mock_check_output.side_effect = CalledProcessError(-1, "dummy")
        self.assertFalse(self.DummyOptimizer.check_library())

        mock_check_output.side_effect = FileNotFoundError
        self.assertFalse(self.DummyOptimizer.check_library())

    def test_applies_to(self):
        self.assertTrue(self.DummyOptimizer.applies_to("foo"))
        self.assertTrue(self.DummyOptimizer.applies_to("FOO"))
        self.assertFalse(self.DummyOptimizer.applies_to("JPEG"))

    def test_get_check_library_arguments(self):
        self.assertEqual(self.DummyOptimizer.get_check_library_arguments(), ["--help"])

    def test_get_command_arguments(self):
        self.assertEqual(self.DummyOptimizer.get_command_arguments("file.png"), [])

    @mock.patch("willow.optimizers.base.subprocess.check_output")
    def test_process(self, mock_check_output):
        self.DummyOptimizer.process("file.png")
        mock_check_output.assert_called_once_with(["dummy"], stderr=STDOUT)

    @mock.patch("willow.optimizers.base.subprocess.check_output")
    def test_process_logs_any_issue(self, mock_check_output):
        # Simulates a CalledProcessError and tests that we log the error
        mock_check_output.side_effect = CalledProcessError(1, "dummy")
        with self.assertLogs("willow", level="ERROR") as log_output:
            self.DummyOptimizer.process("file.png")

        self.assertIn(
            "Error optimizing file.png with the 'dummy' library", log_output.output[0]
        )


class DefaultOptimizerTestBase:
    @classmethod
    def setUpClass(cls) -> None:
        with open(f"tests/images/optimizers/original.{cls.extension}", "rb") as f:
            cls.original_size = os.fstat(f.fileno()).st_size
            cls.original_image = f.read()

        with open(f"tests/images/optimizers/optimized.{cls.extension}", "rb") as f:
            f.seek(0, io.SEEK_END)
            cls.optimized_size = os.fstat(f.fileno()).st_size
            cls.optimized_image = f.read()

    def test_process_optimizes_image(self):
        try:
            with NamedTemporaryFile(delete=False) as named_temporary_file:
                named_temporary_file.write(self.original_image)
                image_file = named_temporary_file.name

            self.optimizer.process(image_file)

            with open(image_file, "rb") as f:
                processed_image_size = os.fstat(f.fileno()).st_size

                # If the image is larger than we expect based on the reference
                # target size we have, allow a delta of 60 bytes to account for
                # any minor differences in optimization.
                if processed_image_size > self.optimized_size:
                    self.assertAlmostEqual(
                        self.optimized_size, processed_image_size, delta=60
                    )
                # Smaller images can happen. Optimizers can get more efficient
                # over time. But if the image is *much* smaller than expected,
                # it could indicate a problem worth investigating.
                else:
                    # We allow a 10% difference
                    self.assertGreaterEqual(
                        processed_image_size, self.optimized_size * 0.9
                    )
        finally:
            os.unlink(image_file)


@unittest.skipUnless(Gifsicle.check_library(), "gifsicle not installed")
class GifsicleOptimizer(DefaultOptimizerTestBase, TestCase):
    extension = "gif"
    optimizer = Gifsicle

    def test_applies_to(self):
        with self.subTest("applies to", ext="gif"):
            self.assertTrue(Gifsicle.applies_to("gif"))

        for ext in ("png", "jpeg", "webp", "tiff", "bmp"):
            with self.subTest("does not apply to", ext=ext):
                self.assertFalse(Gifsicle.applies_to(ext))

    def test_get_command_arguments(self):
        self.assertListEqual(
            Gifsicle.get_command_arguments("file.gif"), ["-b", "-O3", "file.gif"]
        )


@unittest.skipUnless(Jpegoptim.check_library(), "jpegoptim not installed")
class JpegoptimOptimizer(DefaultOptimizerTestBase, TestCase):
    extension = "jpg"
    optimizer = Jpegoptim

    def test_applies_to(self):
        with self.subTest("applies to", ext="jpeg"):
            self.assertTrue(Jpegoptim.applies_to("jpeg"))

        for ext in ("png", "gif", "webp", "tiff", "bmp"):
            with self.subTest("does not apply to", ext=ext):
                self.assertFalse(Jpegoptim.applies_to(ext))

    def test_get_command_arguments(self):
        self.assertListEqual(
            Jpegoptim.get_command_arguments("file.jpg"),
            ["--strip-all", "--max=85", "--all-progressive", "file.jpg"],
        )


@unittest.skipUnless(Pngquant.check_library(), "pngquant not installed")
class PngquantOptimizer(DefaultOptimizerTestBase, TestCase):
    extension = "png"
    optimizer = Pngquant

    def test_applies_to(self):
        self.assertTrue(Pngquant.applies_to("png"))
        for ext in ("gif", "jpeg", "webp", "tiff", "bmp"):
            self.assertFalse(Pngquant.applies_to(ext))

    def test_get_command_arguments(self):
        self.assertListEqual(
            Pngquant.get_command_arguments("file.png"),
            [
                "--force",
                "--strip",
                "--skip-if-larger",
                "file.png",
                "--output",
                "file.png",
            ],
        )


@unittest.skipUnless(Cwebp.check_library(), "cwebp not installed")
class CwebpOptimizer(DefaultOptimizerTestBase, TestCase):
    extension = "webp"
    optimizer = Cwebp

    def test_applies_to(self):
        with self.subTest("applies to", ext="webp"):
            self.assertTrue(Cwebp.applies_to("webp"))

        for ext in ("png", "jpeg", "gif", "tiff", "bmp"):
            with self.subTest("does not apply to", ext=ext):
                self.assertFalse(Cwebp.applies_to(ext))

    def test_get_command_arguments(self):
        self.assertListEqual(
            Cwebp.get_command_arguments("file.webp"),
            [
                "-m",
                "6",
                "-mt",
                "-pass",
                "10",
                "-q",
                "75",
                "file.webp",
                "-o",
                "file.webp",
            ],
        )

    def get_check_library_command_arguments(self):
        self.assertListEqual(
            Cwebp.get_check_library_arguments(),
            [],
        )


@unittest.skipUnless(Cjxl.check_library(), "cjxl not installed")
class CjxlOptimizer(DefaultOptimizerTestBase, TestCase):
    extension = "jxl"
    optimizer = Cjxl

    def test_applies_to(self):
        with self.subTest("applies to", ext="jxl"):
            self.assertTrue(Cjxl.applies_to("jxl"))

        for ext in ("png", "jpeg", "gif", "tiff", "bmp"):
            with self.subTest("does not apply to", ext=ext):
                self.assertFalse(Cjxl.applies_to(ext))

    def test_get_command_arguments(self):
        self.assertListEqual(
            Cjxl.get_command_arguments("file.jxl"),
            [
                "file.jxl",
                "file.jxl",
                "-e",
                "9",
                "--brotli_effort",
                "11",
                "--num_threads",
                "-1",
            ],
        )
        self.assertListEqual(
            Cjxl.get_command_arguments(
                "file.jxl", lossless=True, progressive=True, effort=10
            ),
            [
                "file.jxl",
                "file.jxl",
                "-e",
                "10",
                "--brotli_effort",
                "11",
                "--num_threads",
                "-1",
                "--progressive",
                "--distance=1",
            ],
        )

    def get_check_library_command_arguments(self):
        self.assertListEqual(
            Cjxl.get_check_library_arguments(),
            [],
        )
