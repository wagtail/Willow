from collections import defaultdict


class WillowRegistry(object):
    def __init__(self):
        self._registered_state_classes = set()
        self._registered_operations = defaultdict(dict)
        self._registered_converters = dict()

    def register_operation(self, state_class, operation_name, func):
        self._registered_operations[state_class][operation_name] = func

    def register_converter(self, from_state_class, to_state_class, func):
        self._registered_converters[from_state_class, to_state_class] = func

    def register_state_class(self, state_class):
        self._registered_state_classes.add(state_class)

        # Find and register operations/converters
        for attr in dir(state_class):
            val = getattr(state_class, attr)
            if hasattr(val, '_willow_operation'):
                self.register_operation(state_class, val.__name__, val)
            elif hasattr(val, '_willow_converter_to'):
                self.register_converter(state_class, val._willow_converter_to, val)
            elif hasattr(val, '_willow_converter_from'):
                for converter_from in val._willow_converter_from:
                    self.register_converter(converter_from, state_class, val)

    def register_plugin(self, plugin):
        state_classes = getattr(plugin, 'willow_state_classes', [])
        operations = getattr(plugin, 'willow_operations', [])
        converters = getattr(plugin, 'willow_converters', [])

        for state_class in state_classes:
            self.register_state_class(state_class)

        for operation in operations:
            self.register_operation(operatin[0], operation[1], operation[2])

        for converter in converters:
            self.register_converter(converter[0], converter[1], converter[2])

    def get_operation(self, state_class, operation_name):
        return self._registered_operations[state_class][operation_name]

    def operation_exists(self, operation_name):
        for state_class_operations in self._registered_operations.values():
            if operation_name in state_class_operations:
                return True

        return False

    def get_converter(self, from_state_class, to_state_class):
        return self._registered_converters[from_state_class, to_state_class]

    def get_state_classes(self, with_operation=None, with_converter_from=None, with_converter_to=None, available=None):
        state_classes = self._registered_state_classes

        if with_operation:
            state_classes = filter(lambda state: state in self._registered_operations and operation_name in self._registered_operations[state], state_classes)

        if with_converter_from is not None:
            state_classes = filter(lambda state: (with_converter_from, state) in self._registered_converters, state_classes)

        if with_converter_to is not None:
            state_classes = filter(lambda state: (state, with_converter_to) in self._registered_converters, state_classes)

        # Raise error if no state classes available
        if not state_classes:
            raise LookupError("Could not find state class with the '{0}' operation".format(operation_name))

        # Check each state class and remove unavailable ones
        if available:
            state_class_check_errors = {}
            available_state_classes = set()

            for state_class in state_classes:
                try:
                    state_class.check()
                except Exception as e:
                    state_class_check_errors[state_class] = e
                else:
                    available_state_classes.add(state_class)

            # Raise error if all state classes failed the check
            if not available_state_classes:
                raise LookupError('\n'.join([
                    "The operation '{0}' is available in the following states but they all raised errors:".format(operation_name)
                ] + [
                    "{state_class_name}: {error_message}".format(
                        state_class_name=state_class.__name__,
                        error_message=str(error)
                    )
                    for state_class, error in state_class_check_errors.items()
                ]))

            state_classes = list(available_state_classes)

        return state_classes

    def route_to_operation(self, operation_name, with_converter_from=None):
        state_classes = self.get_state_classes(
            with_operation=operation_name,
            with_converter_from=with_converter_from,
            available=True)

        # Choose a state class
        state_class = list(state_classes)[0]

        return self.get_operation(state_class, operation_name), state_class


registry = WillowRegistry()
