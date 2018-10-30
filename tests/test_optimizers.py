from subprocess import STDOUT, CalledProcessError
from unittest import TestCase, mock

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
            "Error optimizing file.png with the 'dummy' binary", log_output.output[0]
        )
