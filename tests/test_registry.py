import unittest

from willow.states import ImageState
from willow.registry import WillowRegistry


class RegistryTestCase(unittest.TestCase):
    def setUp(self):
        self.registry = WillowRegistry()

        class TestState(ImageState):
            pass

        class AnotherTestState(ImageState):
            pass

        class UnregisteredTestState(ImageState):
            pass

        self.TestState = TestState
        self.AnotherTestState = AnotherTestState
        self.UnregisteredTestState = UnregisteredTestState

        self.registry._registered_state_classes = {TestState, AnotherTestState}


class TestRegisterOperation(RegistryTestCase):
    def test_register_operation(self):
        def test_operation(state):
            pass

        self.registry.register_operation(self.TestState, 'test', test_operation)

        self.assertEqual(test_operation, self.registry._registered_operations[self.TestState]['test'])

    @unittest.expectedFailure
    def test_register_operation_against_unregistered_state_class(self):
        def test_operation(state):
            pass

        self.registry.register_operation(self.UnregisteredTestState, 'test', test_operation)

        # Shouldn't register anything
        self.assertNotIn(self.UnregisteredTestState, self.registry._registered_operations)


class TestRegisterConverter(RegistryTestCase):
    def test_register_converter(self):
        def test_converter(state):
            pass

        self.registry.register_converter(self.TestState, self.AnotherTestState, test_converter)

        self.assertEqual(test_converter, self.registry._registered_converters[self.TestState, self.AnotherTestState])

    def test_register_converter_for_multiple_states(self):
        class YetAnotherTestState(ImageState):
            pass

        self.registry._registered_state_classes.add(YetAnotherTestState)

        def test_converter(state):
            pass

        self.registry.register_converter([self.TestState, YetAnotherTestState], self.AnotherTestState, test_converter)

        self.assertEqual(test_converter, self.registry._registered_converters[self.TestState, self.AnotherTestState])
        self.assertEqual(test_converter, self.registry._registered_converters[YetAnotherTestState, self.AnotherTestState])

    @unittest.expectedFailure
    def test_register_converter_from_unregistered_state(self):
        def test_converter(state):
            pass

        self.registry.register_converter(self.TestState, self.UnregisteredTestState, test_converter)

        self.assertNotIn((self.TestState, self.UnregisteredTestState), self.registry._registered_converters)

    @unittest.expectedFailure
    def test_register_converter_to_unregistered_state(self):
        def test_converter(state):
            pass

        self.registry.register_converter(self.UnregisteredTestState, self.AnotherTestState, test_converter)

        self.assertNotIn((self.UnregisteredTestState, self.AnotherTestState), self.registry._registered_converters)


class TestRegisterStateClass(RegistryTestCase):
    def test_register_state_class(self):
        class NewTestState(ImageState):
            pass

        self.registry.register_state_class(NewTestState)

        self.assertIn(NewTestState, self.registry._registered_state_classes)

    def test_register_state_class_with_operation(self):
        class NewTestState(ImageState):
            @ImageState.operation
            def operation(self):
                pass

        self.registry.register_state_class(NewTestState)

        self.assertEqual(NewTestState.operation, self.registry._registered_operations[NewTestState]['operation'])

    def test_register_state_class_with_multiple_operations(self):
        class NewTestState(ImageState):
            @ImageState.operation
            def operation(self):
                pass

            @ImageState.operation
            def another_operation(self):
                pass

        self.registry.register_state_class(NewTestState)

        self.assertEqual(NewTestState.operation, self.registry._registered_operations[NewTestState]['operation'])
        self.assertEqual(NewTestState.another_operation, self.registry._registered_operations[NewTestState]['another_operation'])

    def test_register_state_class_with_converter_from(self):
        class NewTestState(ImageState):
            @ImageState.converter_from(self.TestState)
            def converter(self):
                pass

        self.registry.register_state_class(NewTestState)

        self.assertEqual(NewTestState.converter, self.registry._registered_converters[self.TestState, NewTestState])

    def test_register_state_class_with_converter_from_multiple(self):
        class NewTestState(ImageState):
            @ImageState.converter_from([self.TestState, self.AnotherTestState])
            def converter(self):
                pass

        self.registry.register_state_class(NewTestState)

        self.assertEqual(NewTestState.converter, self.registry._registered_converters[self.TestState, NewTestState])
        self.assertEqual(NewTestState.converter, self.registry._registered_converters[self.AnotherTestState, NewTestState])

    def test_register_state_class_with_converter_from_multiple_lines(self):
        class NewTestState(ImageState):
            @ImageState.converter_from(self.TestState)
            @ImageState.converter_from(self.AnotherTestState)
            def converter(self):
                pass

        self.registry.register_state_class(NewTestState)

        self.assertEqual(NewTestState.converter, self.registry._registered_converters[self.TestState, NewTestState])
        self.assertEqual(NewTestState.converter, self.registry._registered_converters[self.AnotherTestState, NewTestState])

    def test_register_state_class_with_converter_to(self):
        class NewTestState(ImageState):
            @ImageState.converter_to(self.TestState)
            def converter(self):
                pass

        self.registry.register_state_class(NewTestState)

        self.assertEqual(NewTestState.converter, self.registry._registered_converters[NewTestState, self.TestState])


class TestRegisterImageFormat(RegistryTestCase):
    def test_register_image_format(self):
        self.registry.register_image_format('jpeg', self.TestState)

        self.assertIn('jpeg', self.registry._registered_image_formats)
        self.assertEqual(self.TestState, self.registry._registered_image_formats['jpeg'])

    @unittest.expectedFailure
    def test_register_image_format_against_unregistered_state(self):
        self.registry.register_image_format('jpeg', self.UnregisteredTestState)

        self.assertNotIn('jpeg', self.registry._registered_image_formats)


class TestGetInitialStateClass(RegistryTestCase):
    def test_get_initial_state_class(self):
        self.registry._registered_image_formats['jpeg'] = self.TestState

        self.assertEqual(self.TestState, self.registry.get_initial_state_class('jpeg'))

    def test_get_initial_state_class_noexistent_format(self):
        with self.assertRaises(LookupError):
            self.registry.get_initial_state_class('jpeg')


class TestGetOperation(RegistryTestCase):
    def test_get_operation(self):
        def test_operation(state):
            pass

        self.registry._registered_operations[self.TestState]['test'] = test_operation

        self.assertEqual(test_operation, self.registry.get_operation(self.TestState, 'test'))

    def test_get_operation_nonexistant(self):
        with self.assertRaises(LookupError):
            self.registry.get_operation(self.TestState, 'test')


class TestGetConverter(RegistryTestCase):
    def test_get_converter(self):
        def test_converter(state):
            pass

        self.registry._registered_converters[self.TestState, self.AnotherTestState] = test_converter

        self.assertEqual(test_converter, self.registry.get_converter(self.TestState, self.AnotherTestState))

    def test_get_converter_nonexistant(self):
        with self.assertRaises(LookupError):
            self.registry.get_converter(self.TestState, self.AnotherTestState)


class TestFindOperation(RegistryTestCase):
     pass # TODO
