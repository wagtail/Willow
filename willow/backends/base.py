import six


class ImageBackendBase(type):
    def __init__(cls, name, bases, dct):
        super(ImageBackendBase, cls).__init__(name, bases, dct)

        # Make sure all backends have their own operations attribute
        cls.operations = {}

    def __lt__(cls, other):
        # As we insert backend classes into ordered lists, we need to define an
        # ordering for backend classes. This is used incase two priorities are
        # the same leading to the following comparison:
        # (0, BackendA) > (0, BackendB)
        # So this method is simply to prevent a crash in this situation
        return False


class ImageBackend(six.with_metaclass(ImageBackendBase)):
    @classmethod
    def register_operation(cls, operation_name):
        def wrapper(func):
            cls.operations[operation_name] = func

            return func

        return wrapper

    @classmethod
    def check(cls):
        pass
