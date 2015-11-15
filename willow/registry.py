from collections import defaultdict


class WillowRegistry(object):
    def __init__(self):
        self._registered_state_classes = set()
        self._registered_operations = defaultdict(dict)
        self._registered_converters = dict()
        self._registered_converter_costs = dict()

    def register_operation(self, state_class, operation_name, func):
        self._registered_operations[state_class][operation_name] = func

    def register_converter(self, from_state_class, to_state_class, func, cost=None):
        self._registered_converters[from_state_class, to_state_class] = func

        if cost is not None:
            self._registered_converter_costs[from_state_class, to_state_class] = cost

    def register_state_class(self, state_class):
        self._registered_state_classes.add(state_class)

        # Find and register operations/converters
        for attr in dir(state_class):
            val = getattr(state_class, attr)
            if hasattr(val, '_willow_operation'):
                self.register_operation(state_class, val.__name__, val)
            elif hasattr(val, '_willow_converter_to'):
                self.register_converter(state_class, val._willow_converter_to[0], val, cost=val._willow_converter_to[1])
            elif hasattr(val, '_willow_converter_from'):
                for converter_from, cost in val._willow_converter_from:
                    self.register_converter(converter_from, state_class, val, cost=cost)

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

    def get_converter_cost(self, from_state_class, to_state_class):
        return self._registered_converter_costs.get((from_state_class, to_state_class), 100)

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

    # Routing

    # In some cases, it may not be possible to convert directly between two
    # states, so we need to use one or more intermediate states in order to
    # get to where we want to be.

    # For example, the OpenCV plugin doesn't load JPEG images, so the image
    # needs to be loaded into either Pillow or Wand first and converted to
    # OpenCV.

    # Using a routing algorithm, we're able to work out the best path to take.

    def get_converters_from(self, from_state_class):
        """
        Yields a tuple for each state class a state can be directly converted
        to. The tuple contains the converter function and the state class.

        For example:

        >>> list(registry.get_converters_from(Pillow))
        [
            (convert_pillow_to_wand(), Wand),
            (save_as_jpeg(), JpegFile)
            ...
        ]
        """
        for (c_from, c_to), converter in self._registered_converters.items():
            if c_from is from_state_class:
                yield converter, c_to

    def find_all_paths(self, start, end, path=[], seen_states=set()):
        """
        Returns all paths between two states.

        Each path is a list of tuples representing the step to take in order to
        convert to the new state. The tuples contain two items, The converter
        function to call and the state class that step converts to.

        The order of the paths returned is undefined.

        For example:

        >>> registry.find_all_paths(JpegFile, OpenCV)
        [
            [
                (load_jpeg_into_pillow, Pillow),
                (convert_pillow_to_opencv, OpenCV)
            ],
            [
                (load_jpeg_into_wand, Wand),
                (convert_wand_to_opencv, OpenCV)
            ]
        ]
        """
        # Implementation based on https://www.python.org/doc/essays/graphs/
        if start == end:
            return [path]

        if start in seen_states:
            return []

        if not start in self._registered_state_classes:
            return []

        paths = []
        for converter, next_state in self.get_converters_from(start):
            if next_state not in path:
                newpaths = self.find_all_paths(
                    next_state, end,
                    path + [(converter, next_state)],
                    seen_states.union({start}))

                paths.extend(newpaths)

        return paths

    def get_path_cost(self, start_state, path):
        """
        Costs up a path and returns it as an integer.
        """
        last_state = start_state
        total_cost = 0

        for converter, next_state in path:
            total_cost += self.get_converter_cost(last_state, next_state)
            last_state = next_state

        return total_cost

    def find_shortest_path(self, start, end):
        """
        Finds the shortest path between two states.

        This is similar to the find_all_paths function, except it costs up each
        path and only returns the one with the lowest cost.
        """
        current_path = None
        current_cost = None

        for path in self.find_all_paths(start, end):
            cost = self.get_path_cost(start, path)

            if current_cost is None or cost < current_cost:
                current_cost = cost
                current_path = path

        return current_path, current_cost

    def find_closest_state_class(self, start, state_classes):
        """
        Finds which of the specified states is the closest, based on the sum of
        the costs of the converters needed to convert the image into the final
        state.
        """
        current_state = None
        current_path = None
        current_cost = None

        for state in state_classes:
            path, cost = self.find_shortest_path(start, state)

            if current_cost is None or cost < current_cost:
                current_state = state
                current_cost = cost
                current_path = path

        return current_state, current_path, current_cost

    def route_to_operation(self, from_state, operation_name):
        """
        When an operation is not available in the current state. This method
        can be used to find the nearest state that has the opreation.

        The distance is based on the sum of all the conversions that are
        required to get to the new state.

        This function returns a single converter function and the end state
        class. When this converter function is called, it would perform all the
        steps to convert the image into the final state class.
        """
        state_classes = self.get_state_classes(
            with_converter_from=from_state,
            with_operation=operation_name,
            available=True)

        # Choose a state class
        # state_classes will always have a value here as get_state_classes raises
        # LookupError if there are no state classes available.
        state_class, path, cost = self.find_closest_state_class(from_state, state_classes)

        return self.get_operation(state_class, operation_name), state_class, path, cost


registry = WillowRegistry()
