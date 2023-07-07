import os
import unittest
from unittest import mock

from willow.image import Image
from willow.optimizers.base import OptimizerBase
from willow.registry import (
    UnavailableOperationError,
    UnrecognisedOperationError,
    UnroutableOperationError,
    WillowRegistry,
)


class RegistryTestCase(unittest.TestCase):
    def setUp(self):
        self.registry = WillowRegistry()

        class TestImage(Image):
            pass

        class AnotherTestImage(Image):
            pass

        class UnregisteredTestImage(Image):
            pass

        self.TestImage = TestImage
        self.AnotherTestImage = AnotherTestImage
        self.UnregisteredTestImage = UnregisteredTestImage

        self.registry._registered_image_classes = {TestImage, AnotherTestImage}


class TestRegisterOperation(RegistryTestCase):
    def test_register_operation(self):
        def test_operation(image):
            pass

        self.registry.register_operation(self.TestImage, "test", test_operation)

        self.assertEqual(
            test_operation, self.registry._registered_operations[self.TestImage]["test"]
        )

    @unittest.expectedFailure
    def test_register_operation_against_unregistered_image_class(self):
        def test_operation(image):
            pass

        self.registry.register_operation(
            self.UnregisteredTestImage, "test", test_operation
        )

        # Shouldn't register anything
        self.assertNotIn(
            self.UnregisteredTestImage, self.registry._registered_operations
        )


class TestRegisterConverter(RegistryTestCase):
    def test_register_converter(self):
        def test_converter(image):
            pass

        self.registry.register_converter(
            self.TestImage, self.AnotherTestImage, test_converter
        )

        self.assertEqual(
            test_converter,
            self.registry._registered_converters[self.TestImage, self.AnotherTestImage],
        )

    @unittest.expectedFailure
    def test_register_converter_from_unregistered_image_class(self):
        def test_converter(image):
            pass

        self.registry.register_converter(
            self.TestImage, self.UnregisteredTestImage, test_converter
        )

        self.assertNotIn(
            (self.TestImage, self.UnregisteredTestImage),
            self.registry._registered_converters,
        )

    @unittest.expectedFailure
    def test_register_converter_to_unregistered_image_class(self):
        def test_converter(image):
            pass

        self.registry.register_converter(
            self.UnregisteredTestImage, self.AnotherTestImage, test_converter
        )

        self.assertNotIn(
            (self.UnregisteredTestImage, self.AnotherTestImage),
            self.registry._registered_converters,
        )


class TestRegisterImageClass(RegistryTestCase):
    def test_register_image_class(self):
        class NewTestImage(Image):
            pass

        self.registry.register_image_class(NewTestImage)

        self.assertIn(NewTestImage, self.registry._registered_image_classes)

    def test_register_image_class_with_operation(self):
        class NewTestImage(Image):
            @Image.operation
            def operation(self):
                pass

        self.registry.register_image_class(NewTestImage)

        self.assertEqual(
            NewTestImage.operation,
            self.registry._registered_operations[NewTestImage]["operation"],
        )

    def test_register_image_class_with_multiple_operations(self):
        class NewTestImage(Image):
            @Image.operation
            def operation(self):
                pass

            @Image.operation
            def another_operation(self):
                pass

        self.registry.register_image_class(NewTestImage)

        self.assertEqual(
            NewTestImage.operation,
            self.registry._registered_operations[NewTestImage]["operation"],
        )
        self.assertEqual(
            NewTestImage.another_operation,
            self.registry._registered_operations[NewTestImage]["another_operation"],
        )

    def test_register_image_class_with_converter_from(self):
        class NewTestImage(Image):
            @Image.converter_from(self.TestImage)
            def converter(self):
                pass

        self.registry.register_image_class(NewTestImage)

        self.assertEqual(
            NewTestImage.converter,
            self.registry._registered_converters[self.TestImage, NewTestImage],
        )

    def test_register_image_class_with_converter_from_multiple(self):
        class NewTestImage(Image):
            @Image.converter_from([self.TestImage, self.AnotherTestImage])
            def converter(self):
                pass

        self.registry.register_image_class(NewTestImage)

        self.assertEqual(
            NewTestImage.converter,
            self.registry._registered_converters[self.TestImage, NewTestImage],
        )
        self.assertEqual(
            NewTestImage.converter,
            self.registry._registered_converters[self.AnotherTestImage, NewTestImage],
        )

    def test_register_image_class_with_converter_from_multiple_lines(self):
        class NewTestImage(Image):
            @Image.converter_from(self.TestImage)
            @Image.converter_from(self.AnotherTestImage)
            def converter(self):
                pass

        self.registry.register_image_class(NewTestImage)

        self.assertEqual(
            NewTestImage.converter,
            self.registry._registered_converters[self.TestImage, NewTestImage],
        )
        self.assertEqual(
            NewTestImage.converter,
            self.registry._registered_converters[self.AnotherTestImage, NewTestImage],
        )

    def test_register_image_class_with_converter_to(self):
        class NewTestImage(Image):
            @Image.converter_to(self.TestImage)
            def converter(self):
                pass

        self.registry.register_image_class(NewTestImage)

        self.assertEqual(
            NewTestImage.converter,
            self.registry._registered_converters[NewTestImage, self.TestImage],
        )


class TestGetOperation(RegistryTestCase):
    def test_get_operation(self):
        def test_operation(image):
            pass

        self.registry._registered_operations[self.TestImage]["test"] = test_operation

        self.assertEqual(
            test_operation, self.registry.get_operation(self.TestImage, "test")
        )

    def test_get_operation_nonexistant(self):
        with self.assertRaises(LookupError):
            self.registry.get_operation(self.TestImage, "test")


class TestGetConverter(RegistryTestCase):
    def test_get_converter(self):
        def test_converter(image):
            pass

        self.registry._registered_converters[
            self.TestImage, self.AnotherTestImage
        ] = test_converter

        self.assertEqual(
            test_converter,
            self.registry.get_converter(self.TestImage, self.AnotherTestImage),
        )

    def test_get_converter_nonexistant(self):
        with self.assertRaises(LookupError):
            self.registry.get_converter(self.TestImage, self.AnotherTestImage)


class TestGetConvertersFrom(RegistryTestCase):
    def test_get_converters_from(self):
        def test_converter(image):
            return image

        def test_converter_2(image):
            return image

        def test_converter_3(image):
            return image

        self.registry._registered_converters[
            self.TestImage, self.AnotherTestImage
        ] = test_converter
        self.registry._registered_converters[
            self.TestImage, self.UnregisteredTestImage
        ] = test_converter_2
        self.registry._registered_converters[
            self.AnotherTestImage, self.TestImage
        ] = test_converter_3

        result = list(self.registry.get_converters_from(self.TestImage))
        self.assertIn((test_converter, self.AnotherTestImage), result)
        self.assertIn((test_converter_2, self.UnregisteredTestImage), result)
        self.assertNotIn((test_converter_3, self.TestImage), result)
        self.assertNotIn((test_converter_3, self.AnotherTestImage), result)


class PathfindingTestCase(RegistryTestCase):
    def setUp(self):
        super().setUp()

        self.ImageA = type("ImageA", (Image,), {})
        self.ImageB = type("ImageB", (Image,), {})
        self.ImageC = type("ImageC", (Image,), {})
        self.ImageD = type("ImageD", (Image,), {})
        self.ImageE = type("ImageE", (Image,), {})

        # In real life, these would be functions. But as we're not calling them
        # we'll just use strings instead as it's easier to see what's going on.
        self.conv_a_to_b = "a_to_b"
        self.conv_b_to_a = "b_to_a"
        self.conv_a_to_c = "a_to_c"
        self.conv_c_to_a = "c_to_a"
        self.conv_b_to_d = "b_to_d"
        self.conv_d_to_b = "d_to_b"
        self.conv_c_to_d = "c_to_d"
        self.conv_d_to_c = "d_to_c"
        self.conv_d_to_e = "d_to_e"
        self.conv_e_to_d = "e_to_d"

        self.registry._registered_image_classes = {
            self.ImageA,
            self.ImageB,
            self.ImageC,
            self.ImageD,
            self.ImageE,
        }
        self.registry._registered_converters = {
            (self.ImageA, self.ImageB): self.conv_a_to_b,
            (self.ImageB, self.ImageA): self.conv_b_to_a,
            (self.ImageA, self.ImageC): self.conv_a_to_c,
            (self.ImageC, self.ImageA): self.conv_c_to_a,
            (self.ImageB, self.ImageD): self.conv_b_to_d,
            (self.ImageD, self.ImageB): self.conv_d_to_b,
            (self.ImageC, self.ImageD): self.conv_c_to_d,
            (self.ImageD, self.ImageC): self.conv_d_to_c,
            (self.ImageD, self.ImageE): self.conv_d_to_e,
            (self.ImageE, self.ImageD): self.conv_e_to_d,
        }


class TestFindAllPaths(PathfindingTestCase):
    def test_find_all_paths_a_to_e(self):
        result = self.registry.find_all_paths(self.ImageA, self.ImageE)

        self.assertEqual(len(result), 2)

        self.assertIn(
            [
                (self.conv_a_to_b, self.ImageB),
                (self.conv_b_to_d, self.ImageD),
                (self.conv_d_to_e, self.ImageE),
            ],
            result,
        )

        self.assertIn(
            [
                (self.conv_a_to_c, self.ImageC),
                (self.conv_c_to_d, self.ImageD),
                (self.conv_d_to_e, self.ImageE),
            ],
            result,
        )

    def test_find_all_paths_e_to_b(self):
        result = self.registry.find_all_paths(self.ImageE, self.ImageB)

        self.assertEqual(len(result), 2)

        self.assertIn(
            [
                (self.conv_e_to_d, self.ImageD),
                (self.conv_d_to_b, self.ImageB),
            ],
            result,
        )

        self.assertIn(
            [
                (self.conv_e_to_d, self.ImageD),
                (self.conv_d_to_c, self.ImageC),
                (self.conv_c_to_a, self.ImageA),
                (self.conv_a_to_b, self.ImageB),
            ],
            result,
        )


class TestFindShortestPath(PathfindingTestCase):
    def test_find_shortest_path(self):
        path, cost = self.registry.find_shortest_path(self.ImageE, self.ImageB)

        self.assertEqual(
            path,
            [
                (self.conv_e_to_d, self.ImageD),
                (self.conv_d_to_b, self.ImageB),
            ],
        )

        self.assertEqual(cost, 200)

    def test_find_shortest_path_with_cost(self):
        # Make conversion between d -> b very expensive so it takes the long way around
        self.registry._registered_converter_costs = {
            (self.ImageD, self.ImageB): 1000,
        }

        path, cost = self.registry.find_shortest_path(self.ImageE, self.ImageB)

        self.assertEqual(
            path,
            [
                (self.conv_e_to_d, self.ImageD),
                (self.conv_d_to_c, self.ImageC),
                (self.conv_c_to_a, self.ImageA),
                (self.conv_a_to_b, self.ImageB),
            ],
        )

        self.assertEqual(cost, 400)


class TestFindOperation(PathfindingTestCase):
    def setUp(self):
        super().setUp()

        # Unreachable image class
        self.ImageF = type("ImageF", (Image,), {})
        self.registry._registered_image_classes.add(self.ImageF)

        # Add some operations
        self.b_foo = "b_foo"
        self.e_foo = "e_foo"
        self.f_unreachable = "f_unreachable"

        self.registry._registered_operations = {
            self.ImageB: {
                "foo": self.b_foo,
            },
            self.ImageE: {
                "foo": self.e_foo,
            },
            self.ImageF: {
                "unreachable": self.f_unreachable,
            },
        }

    def test_find_operation_foo_from_a(self):
        func, image_class, path, cost = self.registry.find_operation(self.ImageA, "foo")

        self.assertEqual(func, self.b_foo)
        self.assertEqual(image_class, self.ImageB)
        self.assertEqual(path, [(self.conv_a_to_b, self.ImageB)])
        self.assertEqual(cost, 100)

    def test_find_operation_foo_from_a_avoids_unavailable(self):
        # Make ImageB unavailable so it uses ImageE instead
        self.registry._unavailable_image_classes[self.ImageB] = ImportError(
            "missing image library"
        )

        func, image_class, path, cost = self.registry.find_operation(self.ImageA, "foo")

        self.assertEqual(func, self.e_foo)
        self.assertEqual(image_class, self.ImageE)
        self.assertEqual(
            path,
            [
                (self.conv_a_to_c, self.ImageC),
                (self.conv_c_to_d, self.ImageD),
                (self.conv_d_to_e, self.ImageE),
            ],
        )
        self.assertEqual(cost, 300)

    def test_find_operation_foo_from_b(self):
        func, image_class, path, cost = self.registry.find_operation(self.ImageB, "foo")

        self.assertEqual(func, self.b_foo)
        self.assertEqual(image_class, self.ImageB)
        self.assertEqual(path, [])
        self.assertEqual(cost, 0)

    def test_find_operation_unknown_from_a(self):
        with self.assertRaises(UnrecognisedOperationError) as e:
            func, image_class, path, cost = self.registry.find_operation(
                self.ImageA, "unknown"
            )

        self.assertEqual(
            e.exception.args,
            ("Could not find image class with the 'unknown' operation",),
        )

    def test_find_operation_foo_from_a_all_unavailable(self):
        # Make ImageB and ImageE unavailable so an error is raised
        self.registry._unavailable_image_classes[self.ImageB] = ImportError(
            "missing image library"
        )
        self.registry._unavailable_image_classes[self.ImageE] = ImportError(
            "another missing image library"
        )

        with self.assertRaises(UnavailableOperationError) as e:
            func, image_class, path, cost = self.registry.find_operation(
                self.ImageA, "foo"
            )

        self.assertIn(
            "The operation 'foo' is available in the following image classes but they all raised errors:",
            str(e.exception),
        )
        self.assertIn("ImageB: missing image library", str(e.exception))
        self.assertIn("ImageE: another missing image library", str(e.exception))

    def test_find_operation_unreachable_from_a(self):
        with self.assertRaises(UnroutableOperationError) as e:
            func, image_class, path, cost = self.registry.find_operation(
                self.ImageA, "unreachable"
            )

        self.assertEqual(
            e.exception.args,
            (
                "The operation 'unreachable' is available in the image class 'ImageF' but it can't be converted to from 'ImageA'",
            ),
        )


class TestRegisterOptimizer(RegistryTestCase):
    class DummyOptimizer(OptimizerBase):
        binary = "dummy"

        @classmethod
        def check_binary(cls) -> bool:
            return True

    class UnusedOptimizer(OptimizerBase):
        binary = "unused"

        @classmethod
        def check_binary(cls) -> bool:
            return True

    def test_register_optimizer_with_no_configuration(self):
        self.registry.register_optimizer(self.DummyOptimizer)

        self.assertNotIn(self.DummyOptimizer, self.registry._registered_optimizers)

    def test_register_optimizer_with_willow_optimizers_set_to_a_falsey_value(self):
        with mock.patch.dict(os.environ, {"WILLOW_OPTIMIZERS": ""}):
            self.registry.register_optimizer(self.DummyOptimizer)

            self.assertNotIn(self.DummyOptimizer, self.registry._registered_optimizers)

        with mock.patch.dict(os.environ, {"WILLOW_OPTIMIZERS": "false"}):
            self.registry.register_optimizer(self.DummyOptimizer)
            self.assertNotIn(self.DummyOptimizer, self.registry._registered_optimizers)

    @mock.patch.dict(os.environ, {"WILLOW_OPTIMIZERS": "true"})
    def test_register_optimizer_with_optimizers_enabled(self):
        self.registry.register_optimizer(self.DummyOptimizer)

        self.assertIn(self.DummyOptimizer, self.registry._registered_optimizers)

    @mock.patch.dict(os.environ, {"WILLOW_OPTIMIZERS": "true"})
    def test_register_optimizer_without_binary(self):
        class BadBinaryOptimizer(OptimizerBase):
            @classmethod
            def check_binary(cls) -> bool:
                return False

        self.registry.register_optimizer(BadBinaryOptimizer)

        self.assertNotIn(BadBinaryOptimizer, self.registry._registered_optimizers)

    @mock.patch.dict(os.environ, {"WILLOW_OPTIMIZERS": "dummy"})
    def test_register_optimizer_with_specific_willow_optimizers_set(self):
        self.registry.register_optimizer(self.DummyOptimizer)
        self.registry.register_optimizer(self.UnusedOptimizer)

        self.assertIn(self.DummyOptimizer, self.registry._registered_optimizers)
        self.assertNotIn(self.UnusedOptimizer, self.registry._registered_optimizers)
