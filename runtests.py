import sys
import unittest

from tests.test_registry import *
from tests.test_pillow import *
from tests.test_wand import *
from tests.test_image import *


if __name__ == '__main__':
    args = list(sys.argv)

    if '--opencv' in args:
        from tests.test_opencv import *
        args.remove('--opencv')

    unittest.main(argv=args)
