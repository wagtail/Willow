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


class TestGetConvertersFrom(RegistryTestCase):
    def test_get_converters_from(self):
        test_converter = lambda state: state
        test_converter_2 = lambda state: state
        test_converter_3 = lambda state: state

        self.registry._registered_converters[self.TestState, self.AnotherTestState] = test_converter
        self.registry._registered_converters[self.TestState, self.UnregisteredTestState] = test_converter_2
        self.registry._registered_converters[self.AnotherTestState, self.TestState] = test_converter_3

        result = list(self.registry.get_converters_from(self.TestState))
        self.assertIn((test_converter, self.AnotherTestState), result)
        self.assertIn((test_converter_2, self.UnregisteredTestState), result)
        self.assertNotIn((test_converter_3, self.TestState), result)
        self.assertNotIn((test_converter_3, self.AnotherTestState), result)


class PathfindingTestCase(RegistryTestCase):
    def setUp(self):
        super(PathfindingTestCase, self).setUp()

        self.StateA = type('StateA', (ImageState, ), {})
        self.StateB = type('StateB', (ImageState, ), {})
        self.StateC = type('StateC', (ImageState, ), {})
        self.StateD = type('StateD', (ImageState, ), {})
        self.StateE = type('StateE', (ImageState, ), {})

        # In real life, these would be functions. But as we're not calling them
        # we'll just use strings instead as it's easier to see what's going on.
        self.conv_a_to_b = 'a_to_b'
        self.conv_b_to_a = 'b_to_a'
        self.conv_a_to_c = 'a_to_c'
        self.conv_c_to_a = 'c_to_a'
        self.conv_b_to_d = 'b_to_d'
        self.conv_d_to_b = 'd_to_b'
        self.conv_c_to_d = 'c_to_d'
        self.conv_d_to_c = 'd_to_c'
        self.conv_d_to_e = 'd_to_e'
        self.conv_e_to_d = 'e_to_d'

        self.registry._registered_state_classes = {
            self.StateA, self.StateB, self.StateC, self.StateD, self.StateE}
        self.registry._registered_converters = {
            (self.StateA, self.StateB): self.conv_a_to_b,
            (self.StateB, self.StateA): self.conv_b_to_a,
            (self.StateA, self.StateC): self.conv_a_to_c,
            (self.StateC, self.StateA): self.conv_c_to_a,
            (self.StateB, self.StateD): self.conv_b_to_d,
            (self.StateD, self.StateB): self.conv_d_to_b,
            (self.StateC, self.StateD): self.conv_c_to_d,
            (self.StateD, self.StateC): self.conv_d_to_c,
            (self.StateD, self.StateE): self.conv_d_to_e,
            (self.StateE, self.StateD): self.conv_e_to_d,
        }


class TestFindAllPaths(PathfindingTestCase):
    def test_find_all_paths_a_to_e(self):
        result = self.registry.find_all_paths(self.StateA, self.StateE)

        self.assertEqual(len(result), 2)

        self.assertIn([
            (self.conv_a_to_b, self.StateB),
            (self.conv_b_to_d, self.StateD),
            (self.conv_d_to_e, self.StateE),
        ], result)

        self.assertIn([
            (self.conv_a_to_c, self.StateC),
            (self.conv_c_to_d, self.StateD),
            (self.conv_d_to_e, self.StateE),
        ], result)

    def test_find_all_paths_e_to_b(self):
        result = self.registry.find_all_paths(self.StateE, self.StateB)

        self.assertEqual(len(result), 2)

        self.assertIn([
            (self.conv_e_to_d, self.StateD),
            (self.conv_d_to_b, self.StateB),
        ], result)

        self.assertIn([
            (self.conv_e_to_d, self.StateD),
            (self.conv_d_to_c, self.StateC),
            (self.conv_c_to_a, self.StateA),
            (self.conv_a_to_b, self.StateB),
        ], result)


class TestFindShortestPath(PathfindingTestCase):
    def test_find_shortest_path(self):
        path, cost = self.registry.find_shortest_path(self.StateE, self.StateB)

        self.assertEqual(path, [
            (self.conv_e_to_d, self.StateD),
            (self.conv_d_to_b, self.StateB),
        ])

        self.assertEqual(cost, 200)

    def test_find_shortest_path_with_cost(self):
        # Make conversion between d -> b very expensive so it takes the long way around
        self.registry._registered_converter_costs = {
            (self.StateD, self.StateB): 1000,
        }

        path, cost = self.registry.find_shortest_path(self.StateE, self.StateB)

        self.assertEqual(path, [
            (self.conv_e_to_d, self.StateD),
            (self.conv_d_to_c, self.StateC),
            (self.conv_c_to_a, self.StateA),
            (self.conv_a_to_b, self.StateB),
        ])

        self.assertEqual(cost, 400)


class TestFindOperation(RegistryTestCase):
     pass # TODO
