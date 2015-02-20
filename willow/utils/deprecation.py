from functools import wraps
import warnings


class RemovedInWillow03Warning(DeprecationWarning):
    pass


def deprecated_resize_parameters(resize):
    @wraps(resize)
    def wrapper(backend, *args):
        if len(args) == 1:
            size = args[0]
        elif len(args) == 2:
            size = (args[0], args[1])

            warnings.warn(
                "Passing width and height to Image.resize() in separate arguments is now deprecated. "
                "Change image.resize(width, height) to image.resize((width,height))",
                RemovedInWillow03Warning)
        else:
            raise TypeError("resize() takes exactly 1 argument (%d given)" % len(args))

        return resize(backend, size)

    return wrapper


def deprecated_crop_parameters(crop):
    @wraps(crop)
    def wrapper(backend, *args):
        if len(args) == 1:
            rect = args[0]
        elif len(args) == 4:
            rect = (args[0], args[1], args[2], args[3])

            warnings.warn(
                "Passing left, top, right and bottom to Image.crop() in separate arguments is now deprecated. "
                "Change image.crop(left, top, right, bottom) to image.crop((left, top, right, bottom))",
                RemovedInWillow03Warning)
        else:
            raise TypeError("crop() takes exactly 1 argument (%d given)" % len(args))

        return crop(backend, rect)

    return wrapper
