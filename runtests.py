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

    unittest.main(argv=args)
