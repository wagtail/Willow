import logging
import subprocess
from typing import ClassVar, List

logger = logging.getLogger("willow")


class OptimizerBase:
    binary: ClassVar[str] = ""
    image_format: ClassVar[str] = ""

    class Meta:
        abstract = True

    @classmethod
    def applies_to(cls, image_format: str) -> bool:
        return image_format.lower() == cls.image_format.lower()

    @classmethod
    def check_binary(cls) -> bool:
        args = [
            cls.binary,
            "--help",
        ]  # note: using --help as that doesn't exit with status code 1
        try:
            subprocess.check_output(args, stderr=subprocess.STDOUT)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    @classmethod
    def get_command_arguments(cls, file_path: str) -> List[str]:
        """Return a list of arguments for the given optimizer binary."""
        return []

    @classmethod
    def process(cls, file_path: str):
        args = [cls.binary] + cls.get_command_arguments(file_path)
        try:
            subprocess.check_output(args, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as exc:
            logger.exception(
                "Error optimizing %s with the '%s' binary with error: %s",
                file_path,
                cls.binary,
                exc.output,
            )
