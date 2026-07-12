import os
import subprocess
from tempfile import NamedTemporaryFile
from typing import ClassVar

from .base import OptimizerBase, logger

__all__ = ["Cjxl"]


class Cjxl(OptimizerBase):
    """https://github.com/libjxl/libjxl"""

    library_name: ClassVar[str] = "cjxl"
    image_format: ClassVar[str] = "jxl"

    @classmethod
    def get_check_library_arguments(cls) -> list[str]:
        # running just cjxl gives basic info and returns a zero exit code
        return []

    @classmethod
    def get_command_arguments(
        cls,
        file_path: str,
        output_file_path: str | None = None,
        progressive: bool = False,
        lossless: bool = False,
        effort: int = 9,
    ) -> list[str]:
        if output_file_path is None:
            output_file_path = file_path

        options = [
            file_path,
            output_file_path,
            "-e",  # effort
            str(effort),  # effort level (0-10). 10 is the slowest but best compression.
            "--brotli_effort",  # effort for brotli compression
            "11",
            "--num_threads",  # number of threads to use
            "-1",  # use all available threads
        ]
        if progressive:
            options.append("--progressive")
        if lossless:
            options.append("--distance=1")  # Visually lossless compression
        return options

    @classmethod
    def process(cls, file_path: str):
        with NamedTemporaryFile(
            dir=os.path.dirname(file_path), suffix=".jxl", delete=False
        ) as temp_output_file:
            temp_output_path = temp_output_file.name

        args = [cls.library_name] + cls.get_command_arguments(
            file_path, output_file_path=temp_output_path
        )

        try:
            subprocess.check_output(args, stderr=subprocess.STDOUT)
            os.replace(temp_output_path, file_path)
        except subprocess.CalledProcessError as exc:
            logger.exception(
                "Error optimizing %s with the '%s' library with error: %s",
                file_path,
                cls.library_name,
                exc.output,
            )
        finally:
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)
