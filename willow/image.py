import imghdr
import warnings

from .registry import registry
from .states import ImageState, INITIAL_STATE_CLASSES
from .utils.deprecation import RemovedInWillow05Warning


class UnrecognisedFileError(IOError):
    pass


class Image(object):
    def __init__(self, initial_state):
        self.state = initial_state

    def __getattr__(self, attr):
        # Raise error if attr is not an operation
        if not registry.operation_exists(attr):
            raise AttributeError("%r object has no attribute %r" % (
                self.__class__.__name__, attr
            ))

        try:
            operation = registry.get_operation(type(self.state), attr)
            new_state_class = None
        except LookupError:
            operation, new_state_class, conversion_path, conversion_cost = registry.route_to_operation(type(self.state), attr)

        def wrapper(*args, **kwargs):
            if new_state_class:
                for converter, new_state in conversion_path:
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
        image = cls(initial_state_class(f))
        image._original_format = image_format
        return image

    @property
    def original_format(self):
        warnings.warn(
            "Image.original_format has been deprecated and will be removed in a future release.",
            RemovedInWillow05Warning)
        return getattr(self, '_original_format', None)

    def save(self, image_format, output):
        # Get operation name
        operation_name = 'save_as_' + image_format
        return getattr(self, operation_name)(output)
