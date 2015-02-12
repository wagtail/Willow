from __future__ import division


class Transform(object):
    def __init__(self, width, height, matrix=None):
        self._width = width
        self._height = height
        self._matrix = matrix or [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]

    def _clone(self):
        return type(self)(self._width, self._height, list(self._matrix))

    def resize(self, width, height):
        new = self._clone()
        new._apply_size(width, height)
        new._apply_scale(self._width / width, self._height / height)
        return new

    def crop(self, top, left, right, bottom):
        new = self._clone()
        new._apply_size(right - left, bottom - top)
        new._apply_offset(left, top)
        return new

    def scale(self, x, y):
        new = self._clone()
        new._apply_scale(x, y)
        return new

    def offset(self, x, y):
        new = self._clone()
        new._apply_offset(x, y)
        return new

    def atob(self, x, y):
        pass

    def btoa(self, x, y):
        pass

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def size(self):
        return self._width, self._height

    def _apply_size(self, width, height):
        self._width = width
        self._height = height

    def _apply_scale(self, x, y):
        self._matrix[0] *= x
        self._matrix[1] *= x
        self._matrix[2] *= y
        self._matrix[3] *= y

    def _apply_offset(self, x, y):
        self._matrix[4] += self._matrix[0] * x + self._matrix[2] * y
        self._matrix[5] += self._matrix[1] * x + self._matrix[3] * y
