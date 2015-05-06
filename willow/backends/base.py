import six


class ImageBackendBase(type):
    def __lt__(cls, other):
        # As we insert backend classes into ordered lists, we need to define an
        # ordering for backend classes. This is used incase two priorities are
        # the same leading to the following comparison:
        # (0, BackendA) > (0, BackendB)
        # So this method is simply to prevent a crash in this situation
        return False


class ImageBackend(six.with_metaclass(ImageBackendBase)):
    @classmethod
    def operation(cls, func):
        func._willow_op_name = func.__name__
        return func

    @classmethod
    def register_operation(cls, operation_name):
        def wrapper(func):
            setattr(cls, operation_name, func)
            func._willow_op_name = operation_name
            return func

        return wrapper

    @classmethod
    def get_operations(cls):
        operations = {}
        for attr in dir(cls):
            val = getattr(cls, attr)
            if hasattr(val, '_willow_op_name'):
                operations[val._willow_op_name] = val

        return operations

    @classmethod
    def check(cls):
        pass
