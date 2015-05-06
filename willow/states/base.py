class ImageState(object):
    @staticmethod
    def operation(func):
        func._willow_operation = True
        return func

    @staticmethod
    def converter_to(state_class):
        def wrapper(func):
            func._willow_converter_to = state_class
            return func

        return wrapper

    @staticmethod
    def converter_from(state_class):
        def wrapper(func):
            if not hasattr(func, '_willow_converter_from'):
                func._willow_converter_from = []
            func._willow_converter_from.append(state_class)
            return func

        return wrapper
