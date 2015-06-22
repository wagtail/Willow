import imghdr

from .registry import registry
from .states import ImageState, INITIAL_STATE_CLASSES


class UnrecognisedFileError(IOError):
    pass


class Image(object):
    def __init__(self, initial_state):
        self.state = initial_state

    def __getattr__(self, attr):
        new_state_class = None

        try:
            operation = registry.get_operation(type(self.state), attr)
        except LookupError:
            try:
                operation, new_state_class = registry.find_operation(attr, with_converter_from=type(self.state))
            except LookupError:
                raise AttributeError("%r object has no attribute %r" % (
                    self.__class__.__name__, attr
                ))

        def wrapper(*args, **kwargs):
            if new_state_class:
                converter = registry.get_converter(type(self.state), new_state_class)
                self.state = converter(self.state)

            return_value = operation(self.state, *args, **kwargs)

            if isinstance(return_value, ImageState):
                self.state = return_value

            return return_value

        return wrapper

    # A couple of helpful methods

    @classmethod
    def open(cls, f):
        # Detect image format
        image_format = imghdr.what(f)

        # Find initial state
        initial_state_class = INITIAL_STATE_CLASSES.get(image_format)

        # Give error if initial state not found
        if not initial_state_class:
            if image_format:
                raise UnrecognisedFileError("Cannot load %s files" % image_format)
            else:
                raise UnrecognisedFileError("Unknown file format")

        # Instantiate initial state
        return cls(initial_state_class(f))

    def save(self, image_format, output):
        # Get operation name
        operation_name = 'save_as_' + image_format
        return getattr(self, operation_name)(output)
