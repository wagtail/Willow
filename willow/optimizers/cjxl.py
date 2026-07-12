from typing import ClassVar

from .base import OptimizerBase

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
        cls, file_path: str, progressive: bool = False, lossless=False, effort: int = 9
    ) -> list[str]:
        options = [
            file_path,
            file_path,
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
