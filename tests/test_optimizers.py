from subprocess import STDOUT, CalledProcessError
from unittest import TestCase, mock

from willow.optimizers import Cwebp, Gifsicle, Jpegoptim, Optipng, Pngquant
from willow.optimizers.base import OptimizerBase
from willow.registry import WillowRegistry


class OptimizerTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        class DummyOptimizer(OptimizerBase):
            binary = "dummy"
            image_format = "FOO"

        cls.DummyOptimizer = DummyOptimizer

    def setUp(self) -> None:
        self.registry = WillowRegistry()

    @mock.patch("willow.optimizers.base.subprocess.check_output")
    def test_check_binary(self, mock_check_output):
        self.assertTrue(self.DummyOptimizer.check_binary())

    @mock.patch("willow.optimizers.base.subprocess.check_output")
    def test_check_binary_fail(self, mock_check_output):
        mock_check_output.side_effect = CalledProcessError(-1, "dummy")
        self.assertFalse(self.DummyOptimizer.check_binary())

        mock_check_output.side_effect = FileNotFoundError
        self.assertFalse(self.DummyOptimizer.check_binary())

    def test_applies_to(self):
        self.assertTrue(self.DummyOptimizer.applies_to("foo"))
        self.assertTrue(self.DummyOptimizer.applies_to("FOO"))
        self.assertFalse(self.DummyOptimizer.applies_to("JPEG"))

    def test_applies_to_for_default_optimizers(self):
        self.assertTrue(Cwebp.applies_to("webp"))
        self.assertFalse(Cwebp.applies_to("gif"))
        self.assertTrue(Gifsicle.applies_to("gif"))
        self.assertFalse(Gifsicle.applies_to("png"))
        self.assertFalse(Gifsicle.applies_to("txt"))
        self.assertTrue(Jpegoptim.applies_to("jpeg"))
        self.assertFalse(Jpegoptim.applies_to("png"))
        self.assertTrue(Optipng.applies_to("png"))
        self.assertFalse(Optipng.applies_to("gif"))
        self.assertTrue(Pngquant.applies_to("png"))
        self.assertFalse(Pngquant.applies_to("jpeg"))

    def test_get_command_arguments(self):
        self.assertEqual(self.DummyOptimizer.get_command_arguments("file.png"), [])

    def test_get_command_arguments_for_default_optimizers(self):
        self.assertListEqual(
            Cwebp.get_command_arguments("file.webp"),
            ["-q 80", "-m 6", "-pass 10", "-mt", "file.webp", "-o file.webp"],
        )
        self.assertListEqual(
            Gifsicle.get_command_arguments("file.gif"), ["-b", "-O3", "file.gif"]
        )
        self.assertListEqual(
            Jpegoptim.get_command_arguments("file.jpg"),
            ["--strip-all", "--max=85", "--all-progressive", "file.jpg"],
        )
        self.assertListEqual(
            Optipng.get_command_arguments("file.png"),
            ["-quiet", "-o2", "-i0", "file.png"],
        )
        self.assertListEqual(
            Pngquant.get_command_arguments("file.png"),
            ["--force", "--skip-if-larger", "file.png", "--output", "file.png"],
        )

    @mock.patch("willow.optimizers.base.subprocess.check_output")
    def test_process(self, mock_check_output):
        self.DummyOptimizer.process("file.png")
        mock_check_output.assert_called_once_with(["dummy"], stderr=STDOUT)

    @mock.patch("willow.optimizers.base.subprocess.check_output")
    def test_process_for_default_optimizers(self, mock_check_output):
        Cwebp.process("file.webp")
        mock_check_output.called_with(
            ["cwebp", "-q 80", "-m 6", "-pass 10", "-mt", "file.webp", "-o file.webp"]
        )

        Gifsicle.process("file.gif")
        mock_check_output.called_with(["gifsicle", "-b", "-O3", "file.gif"])

        Jpegoptim.process("file.jpg")
        mock_check_output.called_with("jpegoptim", "--strip-all", "file.jpg")

        Optipng.process("file.png")
        mock_check_output.called_with(["optipng", "-quiet", "-o2", "-i0", "file.png"])

        Pngquant.process("file.png")
        mock_check_output.called_with(
            [
                "pngquant",
                "--force",
                "--skip-if-larger",
                "file.png",
                "--output",
                "file.png",
            ]
        )

    @mock.patch("willow.optimizers.base.subprocess.check_output")
    def test_process_logs_any_issue(self, mock_check_output):
        # Simulates a CalledProcessError and tests that we log the error
        mock_check_output.side_effect = CalledProcessError(1, "dummy")
        with self.assertLogs("willow", level="ERROR") as log_output:
            self.DummyOptimizer.process("file.png")

        self.assertIn(
            "Error optimizing file.png with the 'dummy' binary", log_output.output[0]
        )
