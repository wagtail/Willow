#!/usr/bin/env python

import sys
import unittest

from tests.test_image import *  # noqa: F403
from tests.test_optimizers import *  # noqa: F403
from tests.test_pillow import *  # noqa: F403
from tests.test_registry import *  # noqa: F403
from tests.test_svg_coordinate_transforms import *  # noqa: F403
from tests.test_svg_image import *  # noqa: F403
from tests.test_wand import *  # noqa: F403

if __name__ == "__main__":
    args = list(sys.argv)

    if "--opencv" in args:
        from tests.test_opencv import *  # noqa: F403

        args.remove("--opencv")

    if "--check-wand" in args:
        from willow.plugins.wand import WandImage

        args.remove("--check-wand")

        jpeg_supported = WandImage.is_format_supported("JPEG")
        png_supported = WandImage.is_format_supported("PNG")
        gif_supported = WandImage.is_format_supported("GIF")
        webp_supported = WandImage.is_format_supported("WEBP")
        avif_supported = WandImage.is_format_supported("AVIF")

        sys.stdout.write("\nChecking ImageMagick format support via Wand plugin:\n")

        sys.stdout.write(f"  JPEG support: {'yes' if jpeg_supported else 'no'}\n")
        sys.stdout.write(f"  PNG support: {'yes' if png_supported else 'no'}\n")
        sys.stdout.write(f"  GIF support: {'yes' if gif_supported else 'no'}\n")
        sys.stdout.write(f"  WEBP support: {'yes' if webp_supported else 'no'}\n")
        sys.stdout.write(f"  AVIF support: {'yes' if avif_supported else 'no'}\n")
        if not all(
            [
                jpeg_supported,
                png_supported,
                gif_supported,
                webp_supported,
                avif_supported,
            ]
        ):
            sys.stdout.write(
                "\nOne or more required formats are not supported by ImageMagick.\n"
            )
            sys.stdout.write(
                "This is likely an issue with your ImageMagick installation.\nIt may not be compiled with the correct features enabled.\n"
            )
            sys.stdout.write(
                "\nHint: check the output of `[convert|imagemagick] -list format` to see the formats supported\n"
                "by your ImageMagick installation. The format must have 'rw+' to indicate read and write functionality.\n"
            )
            sys.exit(1)
        else:
            sys.exit(0)

    unittest.main(argv=args)
