import types
import unittest

from willow.image import Image, setup

from willow.backends.base import ImageBackend


class ImageTestCase(unittest.TestCase):
    def setUp(self):
        # Reset Image class
        self.reset()

        # Make two fake backends and a bad backend
        class FakeBackend(ImageBackend):
            def to_buffer(self):
                pass

            @classmethod
            def from_buffer(cls, buf):
                return cls()

            @classmethod
            def from_file(cls, f):
                return cls()

        class AnotherFakeBackend(ImageBackend):
            def to_buffer(self):
                pass

            @classmethod
            def from_buffer(cls, buf):
                return cls()

            @classmethod
            def from_file(cls, f):
                return cls()

        class BadFakeBackend(ImageBackend):
            @classmethod
            def check(cls):
                raise ImportError("Bad image backend")

        self.FakeBackend = FakeBackend
        self.AnotherFakeBackend = AnotherFakeBackend
        self.BadFakeBackend = BadFakeBackend

        Image.register_backend(FakeBackend)
        Image.register_backend(AnotherFakeBackend)
        Image.register_backend(BadFakeBackend)

    @staticmethod
    def tearDownClass():
        # Make sure that Image is returned to its
        # default state after all tests have been run
        ImageTestCase.reset()
        setup(Image)

    @staticmethod
    def reset():
        Image.backends = []
        Image.loaders = {}


class TestRegisterLoader(ImageTestCase):
    """
    Tests the register_loader method on Image
    """
    def test_register_loader(self):
        """
        Tests basic usage of register_loader
        """
        Image.register_loader('jpeg', self.FakeBackend)

        self.assertEqual(Image.loaders, {
            'jpeg': [
                (0, self.FakeBackend),
            ],
        })

    def test_register_loader_priority(self):
        """
        Tests that register_loader saves priority
        """
        Image.register_loader('jpeg', self.FakeBackend, priority=100)

        self.assertEqual(Image.loaders, {
            'jpeg': [
                (100, self.FakeBackend),
            ],
        })

    def test_register_loader_priority_multiple(self):
        """
        Tests that register_loader keeps the loaders list sorted by priority
        """
        Image.register_loader('jpeg', self.FakeBackend, priority=100)
        Image.register_loader('jpeg', self.AnotherFakeBackend, priority=200)

        self.assertEqual(Image.loaders, {
            'jpeg': [
                (100, self.FakeBackend),
                (200, self.AnotherFakeBackend),
            ],
        })

    def test_register_loader_priority_multiple_other_way(self):
        """
        Tests that register_loader keeps the loaders list sorted by priority

        Same as above test, just inserting in opposite way to make sure the
        loaders are being sorted by priority (and not insertion order)
        """
        Image.register_loader('jpeg', self.FakeBackend, priority=200)
        Image.register_loader('jpeg', self.AnotherFakeBackend, priority=100)

        self.assertEqual(Image.loaders, {
            'jpeg': [
                (100, self.AnotherFakeBackend),
                (200, self.FakeBackend),
            ],
        })

    def test_register_loader_different_extension(self):
        """
        Tests that register_loader stores loaders for different extensions
        separately
        """
        Image.register_loader('jpeg', self.FakeBackend)
        Image.register_loader('gif', self.FakeBackend)

        self.assertEqual(Image.loaders, {
            'jpeg': [
                (0, self.FakeBackend),
            ],
            'gif': [
                (0, self.FakeBackend),
            ],
        })

    def test_register_loader_different_extension_at_same_time(self):
        """
        Tests that a single backend can be assigned to load two extensions
        with a single call to register_loader
        """
        Image.register_loader(['jpeg', 'gif'], self.FakeBackend)

        self.assertEqual(Image.loaders, {
            'jpeg': [
                (0, self.FakeBackend),
            ],
            'gif': [
                (0, self.FakeBackend),
            ],
        })

    def test_register_loader_different_extension_at_same_time_tuple(self):
        """
        Tests that a single backend can be assigned to load two extensions with
        a single call to register_loader using a tuple
        """
        Image.register_loader(('jpeg', 'gif'), self.FakeBackend)

        self.assertEqual(Image.loaders, {
            'jpeg': [
                (0, self.FakeBackend),
            ],
            'gif': [
                (0, self.FakeBackend),
            ],
        })

    def test_register_loader_different_extension_at_same_time_with_priority(self):
        """
        Tests that register_loader saves priority when using multipe extensions
        """
        Image.register_loader(['jpeg', 'gif'], self.FakeBackend, priority=100)

        self.assertEqual(Image.loaders, {
            'jpeg': [
                (100, self.FakeBackend),
            ],
            'gif': [
                (100, self.FakeBackend),
            ],
        })

    def test_register_loader_priority_same(self):
        """
        Tests that new loaders are placed after loaders that have the same
        priority
        """
        Image.register_loader('jpeg', self.FakeBackend)
        Image.register_loader('jpeg', self.AnotherFakeBackend)

        self.assertEqual(Image.loaders, {
            'jpeg': [
                (0, self.FakeBackend),
                (0, self.AnotherFakeBackend),
            ],
        })

    def test_register_loader_priority_same_other_way(self):
        """
        If multiple backends are inserted with the same priority, the last one
        should be placed last in the list

        Same as above test, just inserting in opposite way to make sure the
        loaders are being sorted by insertion time (and not name)
        """
        Image.register_loader('jpeg', self.AnotherFakeBackend)
        Image.register_loader('jpeg', self.FakeBackend)

        self.assertEqual(Image.loaders, {
            'jpeg': [
                (0, self.AnotherFakeBackend),
                (0, self.FakeBackend),
            ],
        })


class TestFindLoader(ImageTestCase):
    """
    Tests the find_loader method on Image
    """
    def test_find_loader(self):
        """
        Tests basic usage of find_loader
        """
        Image.loaders = {
            'jpeg': [
                (0, self.FakeBackend),
            ],
        }

        self.assertEqual(Image.find_loader('jpeg'), self.FakeBackend)

    def test_find_loader_unknown_extension(self):
        """
        Tests that a LoaderError is raised when find_loader is called with an
        unknown extension
        """
        Image.loaders = {
            'jpeg': [
                (0, self.FakeBackend),
            ],
        }

        self.assertRaises(Image.LoaderError, Image.find_loader, '.jpeg')

    def test_find_loader_multiple_extensions(self):
        """
        Tests that find_loader works well when multiple extensions are
        registered
        """
        Image.loaders = {
            'jpeg': [
                (0, self.FakeBackend),
            ],
            'gif': [
                (100, self.AnotherFakeBackend),
            ],
        }

        self.assertEqual(Image.find_loader('jpeg'), self.FakeBackend)

    def test_find_loader_priority(self):
        """
        Tests that find_loader gets the backend with the highest priority
        """
        Image.loaders = {
            'jpeg': [
                (100, self.FakeBackend),
                (200, self.AnotherFakeBackend),
            ],
        }

        self.assertEqual(Image.find_loader('jpeg'), self.AnotherFakeBackend)

    def test_find_loader_priority_same(self):
        """
        Tests that find_loader picks the last backend when there are multiple
        backends with the same priority
        """
        Image.loaders = {
            'jpeg': [
                (0, self.FakeBackend),
                (0, self.AnotherFakeBackend),
            ],
        }

        self.assertEqual(Image.find_loader('jpeg'), self.AnotherFakeBackend)

    def test_find_loader_priority_same_other_way(self):
        """
        Tests that find_loader picks the last backend when there are multiple
        backends with the same priority
        """
        Image.loaders = {
            'jpeg': [
                (0, self.AnotherFakeBackend),
                (0, self.FakeBackend),
            ],
        }

        self.assertEqual(Image.find_loader('jpeg'), self.FakeBackend)

    def test_find_loader_with_bad_image_backend(self):
        """
        Tests that find_loader ignores bad backends even if they have a higher
        priority
        """
        Image.loaders = {
            'jpeg': [
                (0, self.FakeBackend),
                (100, self.BadFakeBackend),
            ],
        }

        self.assertEqual(Image.find_loader('jpeg'), self.FakeBackend)

    def test_find_loader_with_only_bad_image_backend(self):
        """
        Tests that find_loader raises a LoaderError when there are no good
        backends available
        """
        Image.loaders = {
            'jpeg': [
                (100, self.BadFakeBackend),
            ],
        }

        self.assertRaises(Image.LoaderError, Image.find_loader, 'jpeg')


class TestOpen(ImageTestCase):
    def test_image_format_detection(self):
        Image.loaders = {
            'png': [
                (0, self.FakeBackend),
            ],
            'jpeg': [
                (100, self.AnotherFakeBackend),
            ],
        }

        self.assertIsInstance(Image.open('tests/images/transparent.png').backend, self.FakeBackend)
        self.assertIsInstance(Image.open('tests/images/flower.jpg').backend, self.AnotherFakeBackend)


class TestLoaderDefaultConfiguration(ImageTestCase):
    pass


class TestRegisterOperation(ImageTestCase):
    """
    Tests the register_operation method on Image
    """
    def test_register_operation(self):
        """
        Tests basic usage of register_operation
        """
        @self.FakeBackend.register_operation('test')
        def myop(backend):
            pass

        self.assertEqual(self.FakeBackend.operations, {
            'test': myop,
        })

    def test_register_operation_multiple(self):
        """
        Tests that register_operation can register multiple operations
        """
        @self.FakeBackend.register_operation('test')
        def myop(backend):
            pass

        @self.FakeBackend.register_operation('test2')
        def myotherop(backend):
            pass

        self.assertEqual(self.FakeBackend.operations, {
            'test': myop,
            'test2': myotherop,
        })

    def test_register_operation_multiple_samename(self):
        """
        Tests that register_operation will replace a previously registered
        operation if they have the same name
        """
        @self.FakeBackend.register_operation('test')
        def myop(backend):
            pass

        @self.FakeBackend.register_operation('test')
        def myotherop(backend):
            pass

        self.assertEqual(self.FakeBackend.operations, {
            'test': myotherop,
        })

    def test_register_operation_multiple_samename_other_way(self):
        """
        Tests that register_operation will replace a previously registered
        operation if they have the same name
        """
        @self.FakeBackend.register_operation('test')
        def myotherop(backend):
            pass

        @self.FakeBackend.register_operation('test')
        def myop(backend):
            pass

        self.assertEqual(self.FakeBackend.operations, {
            'test': myop,
        })


class TestFindOperation(ImageTestCase):
    """
    Tests the find_operation method on Image
    """
    def test_find_operation(self):
        """
        Tests basic usage of find_operation
        """
        def myop(backend):
            pass

        self.FakeBackend.operations = {
            'test': myop,
        }

        self.assertEqual(Image.find_operation('test'), (
            self.FakeBackend,
            myop,
        ))

    def test_find_operation_unknown_operation(self):
        """
        Tests find_operation returns None when the operation name is not
        registered
        """
        def myop(backend):
            pass

        self.FakeBackend.operations = {
            'test': myop,
        }

        self.assertIsNone(Image.find_operation('test2'))

    def test_find_operation_multiple_backends(self):
        """
        Tests find_operation picks the first available backend if the operation
        has been registered by multiple backends
        """
        def myop(backend):
            pass

        self.FakeBackend.operations = {
            'test': myop,
        }

        self.AnotherFakeBackend.operations = {
            'test': myop,
        }

        self.assertEqual(Image.find_operation('test'), (
            self.FakeBackend,
            myop,
        ))

    def test_find_operation_multiple_backends_preferred(self):
        """
        Tests find_operation will priorities the preferred backend
        """
        def myop(backend):
            pass

        self.FakeBackend.operations = {
            'test': myop,
        }

        self.AnotherFakeBackend.operations = {
            'test': myop,
        }

        self.assertEqual(Image.find_operation('test', preferred_backend=self.AnotherFakeBackend), (
            self.AnotherFakeBackend,
            myop,
        ))

    def test_find_operation_with_bad_backend(self):
        """
        Tests that find_operation ignores bad backends
        """
        def myop(backend):
            pass

        self.BadFakeBackend.operations = {
            'test': myop,
        }

        self.AnotherFakeBackend.operations = {
            'test': myop,
        }

        self.assertEqual(Image.find_operation('test'), (
            self.AnotherFakeBackend,
            myop,
        ))

    def test_find_operation_with_only_bad_backend(self):
        """
        Tests that find_operation raises a RuntimeError when there are no good
        backends available
        """
        def myop(backend):
            pass

        self.BadFakeBackend.operations = {
            'test': myop,
        }

        self.assertRaises(RuntimeError, Image.find_operation, 'test')


class TestGetAttribute(ImageTestCase):
    """
    This tests the __getattr__ method on Image
    """
    def test_getattr_operation(self):
        """
        Tests that __getattr__ looks up operations correctly
        """
        def myop(backend):
            pass

        self.FakeBackend.operations = {
            'test': myop,
        }

        image = Image(self.FakeBackend(), 'jpeg')

        self.assertIsInstance(image.test, types.FunctionType)

    def test_getattr_operation_unknown(self):
        """
        Tests that __getattr__ raises an AttributeError when the requested
        attribute is not an operation
        """
        def myop(backend):
            pass

        self.FakeBackend.operations = {
            'test': myop,
        }

        image = Image(self.FakeBackend(), 'jpeg')

        self.assertRaises(AttributeError, getattr, image, 'test2')


class TestCallOperation(ImageTestCase):
    """
    Tests calling an operation that has been registered in Image
    """
    def test_calls_function(self):
        """
        Tests that calling the operation calls the underlying function
        """
        def myop(backend):
            backend.func_called = True

        self.FakeBackend.operations = {
            'test': myop,
        }

        image = Image(self.FakeBackend(), 'jpeg')
        image.backend.func_called = False
        image.test()

        self.assertTrue(image.backend.func_called)

    def test_args_get_passed_through(self):
        """
        Tests that args get passed through to the underlying function
        """
        def myop(backend, *args, **kwargs):
            backend.passed_args = args
            backend.passed_kwargs = kwargs

        self.FakeBackend.operations = {
            'test': myop,
        }

        image = Image(self.FakeBackend(), 'jpeg')
        image.backend.passed_args = None
        image.backend.passed_kwargs = None
        image.test('Hello', 'World', name="Karl")

        self.assertEqual(image.backend.passed_args, ('Hello', 'World'))
        self.assertEqual(image.backend.passed_kwargs, {'name': "Karl"})

    def test_return_value_gets_passed_back(self):
        """
        Tests that the return value of the underlying function gets passed back
        to the caller
        """
        def myop(backend):
            return "Hello world!"

        self.FakeBackend.operations = {
            'test': myop,
        }

        image = Image(self.FakeBackend(), 'jpeg')

        self.assertEqual(image.test(), "Hello world!")

    def test_switches_backend(self):
        """
        Tests that calling an operation will switch backend if the current
        backend doesn't support it
        """
        def say_hello(backend):
            return "Hello world!"

        self.FakeBackend.operations = {
            'say_hello': say_hello,
        }

        def say_goodbye(backend):
            return "Goodbye!"

        self.AnotherFakeBackend.operations = {
            'say_goodbye': say_goodbye,
        }

        image = Image(self.FakeBackend(), 'jpeg')
        self.assertIsInstance(image.backend, self.FakeBackend)

        image.say_goodbye()
        self.assertIsInstance(image.backend, self.AnotherFakeBackend)

        image.say_hello()
        self.assertIsInstance(image.backend, self.FakeBackend)


class TestRegisterBackend(ImageTestCase):
    """
    Tests the register_backend method on Image
    """
    def setUp(self):
        super(TestRegisterBackend, self).setUp()
        self.reset()

    def test_register_backend(self):
        """
        Tests basic usage of register_backend
        """
        Image.register_backend(self.FakeBackend)

        self.assertEqual(Image.backends, [self.FakeBackend])

    def test_register_backend_multiple(self):
        """
        Tests register_backend can register multiple backends
        """
        Image.register_backend(self.FakeBackend)
        Image.register_backend(self.AnotherFakeBackend)

        self.assertEqual(Image.backends, [self.FakeBackend, self.AnotherFakeBackend])

    def test_register_backend_removes_duplicates(self):
        """
        Tests register_backend won't insert the same backend more than once
        """
        Image.register_backend(self.FakeBackend)
        Image.register_backend(self.FakeBackend)

        self.assertEqual(Image.backends, [self.FakeBackend])


class TestCheckBackends(ImageTestCase):
    pass


class TestSwitchBackend(ImageTestCase):
    pass

    # TODO


if __name__ == '__main__':
    unittest.main()
