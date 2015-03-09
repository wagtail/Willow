from __future__ import division


class Transform(object):
    def __init__(self, width, height, scale_x=1.0, scale_y=1.0, offset_x=0.0, offset_y=0.0):
        self._width = width
        self._height = height
        self._scale_x = scale_x
        self._scale_y = scale_y
        self._offset_x = offset_x
        self._offset_y = offset_y

    def _clone(self):
        return type(self)(
            self._width, self._height,
            self._scale_x, self._scale_y,
            self._offset_x, self._offset_y
        )

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

    def get_size(self):
        return self._width, self._height

    def get_matrix(self):
        return [
            self._scale_x, 0,
            0, self._scale_y,
            self._offset_x, self._offset_y,
        ]

    def _apply_size(self, width, height):
        self._width = width
        self._height = height

    def _apply_scale(self, x, y):
        self._scale_x *= x
        self._scale_y *= y

    def _apply_offset(self, x, y):
        self._offset_x += self._scale_x * x
        self._offset_y += x + self._scale_y * y
