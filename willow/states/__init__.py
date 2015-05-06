from collections import defaultdict


class StatesRegistry(object):
    _registered_states = set()
    _registered_operations = defaultdict(dict)
    _registered_converters = dict()

    def register_operation(self, state_class, operation_name, func):
        self._registered_operations[state_class][operation_name] = func

    def register_converter(self, from_state_class, to_state_class, func):
        if isinstance(from_state_class, list):
            for state_class in from_state_class:
                self.register_converter(state_class, to_state_class, func)
            return

        self._registered_converters[from_state_class, to_state_class] = func

    def register_state(self, state_class):
        self._registered_states.add(state_class)

        # Find and register operations/converters
        for attr in dir(state_class):
            val = getattr(state_class, attr)
            if hasattr(val, '_willow_operation'):
                self.register_operation(state_class, val._willow_operation, val)
            elif hasattr(val, '_willow_converter_to'):
                self.register_converter(state_class, val._willow_converter_to, val)
            elif hasattr(val, '_willow_converter_from'):
                self.register_converter(val._willow_converter_from, state_class, val)


registry = StatesRegistry()
register_state = registry.register_state
register_operation = registry.register_operation
register_converter = registry.register_converter
