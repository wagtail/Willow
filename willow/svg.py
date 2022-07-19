import re
from collections import namedtuple
from enum import Enum

from xml.etree.ElementTree import ElementTree

from .image import Image, SVGImageFile, BadImageOperationError


class WillowSVGException(Exception):
    pass


class InvalidSizeAttribute(WillowSVGException):
    pass


class ViewBoxParseError(WillowSVGException):
    pass


ViewBox = namedtuple("ViewBox", "min_x min_y width height")


class SVGWrapper:
    # https://developer.mozilla.org/en-US/docs/Web/SVG/Content_type#length
    UNIT_RE = re.compile(r"(?:em|ex|px|in|cm|mm|pt|pc|%)$")

    # https://developer.mozilla.org/en-US/docs/Web/SVG/Content_type#number
    NUMBER_PATTERN = r"(\d+(?:[Ee]\d+)?|[+-]?\d*\.\d+(?:[Ee]\d+)?)"

    # https://www.w3.org/Graphics/SVG/1.1/coords.html#ViewBoxAttribute
    VIEW_BOX_RE = re.compile(
        f"{NUMBER_PATTERN}[, ] *{NUMBER_PATTERN}[, ] *"
        f"{NUMBER_PATTERN}[, ] *{NUMBER_PATTERN}$"
    )

    # Borrowed from cairosvg
    COEFFICIENTS = {
        "mm": 1 / 25.4,
        "cm": 1 / 2.54,
        "in": 1,
        "pt": 1 / 72.0,
        "pc": 1 / 6.0,
    }

    def __init__(self, dom: ElementTree, dpi=96, font_size_px=16):
        self.dom = dom
        self.dpi = dpi
        self.font_size_px = font_size_px
        self.view_box = self._get_view_box()
        self.width = self._get_width()
        self.height = self._get_height()

    @property
    def root(self):
        return self.dom.getroot()

    def _get_width(self):
        attr_value = self.root.get("width") or self.root.get("height")
        if attr_value:
            return self._parse_size(attr_value)
        elif self.view_box is not None:
            return self.view_box.width
        return 1

    def _get_height(self):
        attr_value = self.root.get("height") or self.root.get("width")
        if attr_value:
            return self._parse_size(attr_value)
        elif self.view_box is not None:
            return self.view_box.height
        return 1

    def _parse_size(self, raw_value):
        clean_value = raw_value.strip()
        match = self.UNIT_RE.search(clean_value)
        unit = clean_value[match.start() :] if match else None

        if unit == "%":
            raise InvalidSizeAttribute(
                f"Unable to handle relative size units ({raw_value})"
            )

        amount_raw = clean_value[: -len(unit)] if unit else clean_value
        try:
            amount = float(amount_raw)
        except ValueError as err:
            raise InvalidSizeAttribute(
                f"Unable to parse value from '{raw_value}'"
            ) from err
        if amount <= 0:
            raise InvalidSizeAttribute(f"Negative or 0 sizes are invalid ({amount})")

        if unit is None or unit == "px":
            return amount
        elif unit == "em":
            return amount * self.font_size_px
        elif unit == "ex":
            # This is not exactly correct, but it's the best we can do
            return amount * self.font_size_px / 2
        else:
            return amount * self.dpi * self.COEFFICIENTS[unit]

    def _get_view_box(self):
        attr_value = self.root.get("viewBox")
        if attr_value:
            return self._parse_view_box(attr_value)

    def _parse_view_box(self, raw_value):
        match = self.VIEW_BOX_RE.match(raw_value.strip())
        if match is None:
            raise ViewBoxParseError(f"Unable to parse viewBox value '{raw_value}'")
        return ViewBox(*map(float, match.groups()))

    def write(self, f):
        self.dom.write(f, encoding="utf-8")


class SVGImageTransform(str, Enum):
    CROP = "crop"
    RESIZE = "resize"


class SVGImage(Image):
    def __init__(self, image, operations=None):
        self.image = image
        self.operations = [] if operations is None else operations

    @classmethod
    @Image.converter_from(SVGImageFile)
    def open(cls, svg_image_file):
        svg_wrapper = SVGWrapper(svg_image_file.dom)
        return cls(image=svg_wrapper)

    @Image.operation
    def get_size(self):
        return (self.image.width, self.image.height)

    @Image.operation
    def auto_orient(self):
        return self

    @Image.operation
    def crop(self, rect):
        # Validate the rect here rather than when we actually apply
        # the crop during rasterisation to give immediate feedback
        left, top, right, bottom = rect
        width, height = self.get_size()
        if (
            left >= right
            or left >= width
            or right <= 0
            or top >= bottom
            or top >= height
            or bottom <= 0
        ):
            raise BadImageOperationError("Invalid crop dimensions: %r" % (rect,))

        return self.__class__(
            self.image, [*self.operations, (SVGImageTransform.CROP, rect)]
        )

    @Image.operation
    def resize(self, size):
        return self.__class__(
            self.image, [*self.operations, (SVGImageTransform.RESIZE, size)]
        )

    @Image.operation
    def has_animation(self):
        return False

    def write(self, f):
        self.image.write(f)
        f.seek(0)

    @Image.operation
    def save_as_svg(self, f):
        self.write(f)
        return SVGImageFile(f, dom=self.image.dom)
