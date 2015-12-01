from collections import defaultdict


class WillowRegistry(object):
    def __init__(self):
        self._registered_image_classes = set()
        self._registered_operations = defaultdict(dict)
        self._registered_converters = dict()
        self._registered_converter_costs = dict()

    def register_operation(self, image_class, operation_name, func):
        self._registered_operations[image_class][operation_name] = func

    def register_converter(self, from_image_class, to_image_class, func, cost=None):
        self._registered_converters[from_image_class, to_image_class] = func

        if cost is not None:
            self._registered_converter_costs[from_image_class, to_image_class] = cost

    def register_image_class(self, image_class):
        self._registered_image_classes.add(image_class)

        # Find and register operations/converters
        for attr in dir(image_class):
            val = getattr(image_class, attr)
            if hasattr(val, '_willow_operation'):
                self.register_operation(image_class, val.__name__, val)
            elif hasattr(val, '_willow_converter_to'):
                self.register_converter(image_class, val._willow_converter_to[0], val, cost=val._willow_converter_to[1])
            elif hasattr(val, '_willow_converter_from'):
                for converter_from, cost in val._willow_converter_from:
                    self.register_converter(converter_from, image_class, val, cost=cost)

    def register_plugin(self, plugin):
        image_classes = getattr(plugin, 'willow_image_classes', [])
        operations = getattr(plugin, 'willow_operations', [])
        converters = getattr(plugin, 'willow_converters', [])

        for image_class in image_classes:
            self.register_image_class(image_class)

        for operation in operations:
            self.register_operation(operatin[0], operation[1], operation[2])

        for converter in converters:
            self.register_converter(converter[0], converter[1], converter[2])

    def get_operation(self, image_class, operation_name):
        return self._registered_operations[image_class][operation_name]

    def operation_exists(self, operation_name):
        for image_class_operations in self._registered_operations.values():
            if operation_name in image_class_operations:
                return True

        return False

    def get_converter(self, from_image_class, to_image_class):
        return self._registered_converters[from_image_class, to_image_class]

    def get_converter_cost(self, from_image_class, to_image_class):
        return self._registered_converter_costs.get((from_image_class, to_image_class), 100)

    def get_image_classes(self, with_operation=None, with_converter_from=None, with_converter_to=None, available=None):
        image_classes = self._registered_image_classes

        if with_operation:
            image_classes = filter(lambda image_class: image_class in self._registered_operations and with_operation in self._registered_operations[image_class], image_classes)

        if with_converter_from is not None:
            image_classes = filter(lambda image_class: (with_converter_from, image_class) in self._registered_converters, image_classes)

        if with_converter_to is not None:
            image_classes = filter(lambda image_class: (image_class, with_converter_to) in self._registered_converters, image_classes)

        # Raise error if no image classes available
        if not image_classes:
            raise LookupError("Could not find image class with the '{0}' operation".format(with_operation))

        # Check each image class and remove unavailable ones
        if available:
            image_class_check_errors = {}
            available_image_classes = set()

            for image_class in image_classes:
                try:
                    image_class.check()
                except Exception as e:
                    image_class_check_errors[image_class] = e
                else:
                    available_image_classes.add(image_class)

            # Raise error if all image classes failed the check
            if not available_image_classes:
                raise LookupError('\n'.join([
                    "The operation '{0}' is available in the following image classes but they all raised errors:".format(with_operation)
                ] + [
                    "{image_class_name}: {error_message}".format(
                        image_class_name=image_class.__name__,
                        error_message=str(error)
                    )
                    for image_class, error in image_class_check_errors.items()
                ]))

            image_classes = list(available_image_classes)

        return image_classes

    # Routing

    # In some cases, it may not be possible to convert directly between two
    # image classes, so we need to use one or more intermediate classes in order
    # to get to where we want to be.

    # For example, the OpenCV plugin doesn't load JPEG images, so the image
    # needs to be loaded into either Pillow or Wand first and converted to
    # OpenCV.

    # Using a routing algorithm, we're able to work out the best path to take.

    def get_converters_from(self, from_image_class):
        """
        Yields a tuple for each image class that can be directly converted
        from the specified image classes. The tuple contains the converter
        function and the image class.

        For example:

        >>> list(registry.get_converters_from(Pillow))
        [
            (convert_pillow_to_wand, Wand),
            (save_as_jpeg, JpegFile)
            ...
        ]
        """
        for (c_from, c_to), converter in self._registered_converters.items():
            if c_from is from_image_class:
                yield converter, c_to

    def find_all_paths(self, start, end, path=[], seen_classes=set()):
        """
        Returns all paths between two image classes.

        Each path is a list of tuples representing the steps to take in order to
        convert to the new class. Each tuple contains two items: The converter
        function to call and the class that step converts to.

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

        if start in seen_classes:
            return []

        if not start in self._registered_image_classes:
            return []

        paths = []
        for converter, next_class in self.get_converters_from(start):
            if next_class not in path:
                newpaths = self.find_all_paths(
                    next_class, end,
                    path + [(converter, next_class)],
                    seen_classes.union({start}))

                paths.extend(newpaths)

        return paths

    def get_path_cost(self, start, path):
        """
        Costs up a path and returns the cost as an integer.
        """
        last_class = start
        total_cost = 0

        for converter, next_class in path:
            total_cost += self.get_converter_cost(last_class, next_class)
            last_class = next_class

        return total_cost

    def find_shortest_path(self, start, end):
        """
        Finds the shortest path between two image classes.

        This is similar to the find_all_paths function, except it only returns
        the path with the lowest cost.
        """
        current_path = None
        current_cost = None

        for path in self.find_all_paths(start, end):
            cost = self.get_path_cost(start, path)

            if current_cost is None or cost < current_cost:
                current_cost = cost
                current_path = path

        return current_path, current_cost

    def find_closest_image_class(self, start, image_classes):
        """
        Finds which of the specified image classes is the closest, based on the
        sum of the costs for the conversions needed to convert the image into it.
        """
        current_class = None
        current_path = None
        current_cost = None

        for image_class in image_classes:
            path, cost = self.find_shortest_path(start, image_class)

            if current_cost is None or cost < current_cost:
                current_class = image_class
                current_cost = cost
                current_path = path

        return current_class, current_path, current_cost

    def route_to_operation(self, from_class, operation_name):
        """
        When an operation is not available in the current image class, this
        method can be used to find the nearest class that has the opreation.

        The distance is based on the sum of all the costs for the conversions
        that are required to get to the new class.

        This function returns a tuple of four values:
         - The operation function
         - The image class needed to run the operation
         - The path to take to the new image class from the current one
         - The total cost of converting to the new image class
        """
        image_classes = self.get_image_classes(
            with_converter_from=from_class,
            with_operation=operation_name,
            available=True)

        # Choose an image class
        # image_classes will always have a value here as get_image_classes raises
        # LookupError if there are no image classes available.
        image_class, path, cost = self.find_closest_image_class(from_class, image_classes)

        return self.get_operation(image_class, operation_name), image_class, path, cost


registry = WillowRegistry()
