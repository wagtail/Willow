import os.path
from io import BytesIO
import bisect
import imghdr

import six

from willow.backends.pillow import PillowBackend
from willow.backends.wand import WandBackend
from willow.backends.opencv import OpenCVBackend


class Image(object):
    class LoaderError(RuntimeError):
        pass

    def __init__(self, initial_backend, image_format):
        self.backend = initial_backend
        self.original_format = image_format

    def __getattr__(self, attr):
        operation = self.find_operation(attr, preferred_backend=type(self.backend))

        if operation is not None:
            backend, func = operation

            def operation(*args, **kwargs):
                if backend is not type(self.backend):
                    self.switch_backend(backend)

                return func(self.backend, *args, **kwargs)

            return operation
        else:
            raise AttributeError("%r object has no attribute %r" % (
                self.__class__.__name__, attr
            ))

    def switch_backend(self, new_backend):
        if type(self.backend) is new_backend:
            return

        if hasattr(new_backend, 'from_buffer') and hasattr(self.backend, 'to_buffer'):
            buf = self.backend.to_buffer()
            self.backend = new_backend.from_buffer(buf)
            return

        if hasattr(new_backend, 'from_file') and hasattr(self.backend, 'to_file'):
            f = BytesIO()
            self.backend.to_file(f)
            self.backend = new_backend.from_file(f)
            return

        raise RuntimeError("Unable to switch backend")

    @classmethod
    def open(cls, f, initial_backend=None):
        image_format = imghdr.what(f)

        if not initial_backend:
            # Work out best initial backend based on file format
            initial_backend = cls.find_loader(image_format)

        if initial_backend:
            return cls(initial_backend.from_file(f), image_format)

    def save(self, image_format, output):
        # Get operation name
        operation_name = 'save_as_' + image_format
        return getattr(self, operation_name)(output)

    backends = []

    @classmethod
    def register_backend(cls, backend):
        if backend not in cls.backends:
            cls.backends.append(backend)

    @classmethod
    def check_backends(cls, backends):
        available_backends = []
        unavailable_backends = []

        for backend in backends:
            try:
                backend.check()
            except Exception as e:
                error = "%s: %s" % (type(e).__name__, str(e))
                unavailable_backends.append((backend, error))
            else:
                available_backends.append(backend)

        return available_backends, unavailable_backends

    @classmethod
    def find_operation(cls, operation_name, preferred_backend=None):
        # Try finding the operation in the preferred backend
        if preferred_backend is not None:
            if operation_name in preferred_backend.operations.keys():
                return preferred_backend, preferred_backend.operations[operation_name]

        # Operation doesn't exist in preferred backend, find all backends that implement it
        backends = [backend for backend in cls.backends if operation_name in backend.operations]
        if backends:
            # Now filter that list to only include backends that are available
            available_backends, unavailable_backends = cls.check_backends(backends)

            if available_backends:
                # TODO: Think of a way to select the best backend if multiple backends are found
                # Select the first available backend
                return available_backends[0], available_backends[0].operations[operation_name]

            else:
                # Some backends were found but none of them are available, raise an error
                message = '\n'.join([
                    "The operation '%s' is available in the following backends but they all returned an error:" % operation_name
                ] + [
                    "%s -- %s" % (backend.__name__, error)
                    for backend, error in unavailable_backends
                ])
                raise RuntimeError(message)

    loaders = {}

    @classmethod
    def register_loader(cls, image_format, backend, priority=0):
        # If format is a list or tuple, call this method for each one
        if isinstance(image_format, (list, tuple)):
            for ext in image_format:
                cls.register_loader(ext, backend, priority=priority)
            return

        # Register format in loaders
        if image_format not in cls.loaders:
            cls.loaders[image_format] = []

        # Add the backend
        bisect.insort_right(cls.loaders[image_format], (priority, backend))

    @classmethod
    def find_loader(cls, image_format):
        if image_format not in cls.loaders or not cls.loaders[image_format]:
            raise cls.LoaderError("Cannot find backend that can load this image file")

        # Find all backends that can load images with this format
        backends = [backend for priority, backend in cls.loaders[image_format]]

        # Now filter that list to only include backends that are available
        available_backends, unavailable_backends = cls.check_backends(backends)

        if available_backends:
            # Select the last available backend
            # The loaders list should be sorted with best backends last
            return available_backends[-1]

        else:
            # Some backends were found but none of them are available, raise an error
            message = '\n'.join([
                "This file can be loaded by the following backends but they all returned an error:"
            ] + [
                "%s -- %s" % (backend.__name__, error)
                for backend, error in unavailable_backends
            ])
            raise cls.LoaderError(message)


def setup(cls):
    # Register builtin image backends
    cls.register_backend(PillowBackend)
    cls.register_backend(WandBackend)
    cls.register_backend(OpenCVBackend)


    # Pillow is very good at loading PNG, JPEG and BMP files
    cls.register_loader(['png', 'jpeg', 'bmp'], PillowBackend, priority=100)

    # Pillow can load gifs too, but without animation
    cls.register_loader('gif', PillowBackend, priority=-100)

    # Wand can load PNG, JPEG, BMP and GIF (with animation), but doesn't work as fast as Pillow
    cls.register_loader(['png', 'jpeg', 'bmp', 'gif'], WandBackend)


setup(Image)
