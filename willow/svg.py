import re
from collections import namedtuple
from enum import Enum

from xml.etree.ElementTree import ElementTree

from .image import Image, SVGImageFile


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

    # https://www.w3.org/Graphics/SVG/1.1/coords.html#ViewBoxAttribute
    VIEW_BOX_RE = re.compile(r"(\d+)[, ] *(\d+)[, ] *(\d+)[, ] *(\d+)")

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
        if attr := (self.root.get("width") or self.root.get("height")):
            return self._parse_size(attr)
        elif self.view_box is not None:
            return self.view_box.width

    def _get_height(self):
        if attr := (self.root.get("height") or self.root.get("width")):
            return self._parse_size(attr)
        elif self.view_box is not None:
            return self.view_box.height

    def _parse_size(self, raw_value):
        clean_value = raw_value.strip()
        match = self.UNIT_RE.search(clean_value)
        unit = clean_value[match.start() :] if match else None

        if unit == "%":
            raise InvalidSizeAttribute(
                f"Unable to handle relative size units ({raw_value})"
            )

        # TODO: better handling of invalid, not %, units

        amount_raw = clean_value[: -len(unit)] if unit else clean_value
        try:
            # Might be real number or int, may have a sign, so try to
            # cast to a float rather than (e.g.) using a complex regex.
            # https://www.w3.org/TR/2008/REC-CSS2-20080411/syndata.html#length-units
            amount = float(amount_raw)
        except ValueError as err:
            raise InvalidSizeAttribute(
                f"Unable to parse value from '{raw_value}'"
            ) from err

        if unit is None or unit == "px":
            return round(amount)
        elif unit == "em":
            return round(amount * self.font_size_px)
        elif unit == "ex":
            # This is not exactly correct, but it's the best we can do
            return round(amount * self.font_size_px / 2)
        else:
            return round(amount * self.dpi * self.COEFFICIENTS[unit])

    def _get_view_box(self):
        if attr := self.root.get("viewBox"):
            return self._parse_view_box(attr)

    def _parse_view_box(self, raw_value):
        match = self.VIEW_BOX_RE.match(raw_value.strip())
        if match is None:
            raise ViewBoxParseError(f"Unable to parse viewBox value '{raw_value}'")
        return ViewBox(*map(int, match.groups()))

    def write(self, f):
        self.dom.write(f, encoding="utf-8")
        f.seek(0)


class SVGImageOperation(str, Enum):
    CROP = "crop"
    RESIZE = "resize"


class SVGImage(Image):
    def __init__(self, dom, operations=None, dpi=96, font_size="12pt"):
        self.image = SVGWrapper(dom)
        self.operations = [] if operations is None else operations

    @classmethod
    @Image.converter_from(SVGImageFile)
    def open(cls, svg_image_file):
        return cls(svg_image_file.dom)

    @Image.operation
    def get_size(self):
        return (self.image.width, self.image.height)

    @Image.operation
    def auto_orient(self):
        return self

    @Image.operation
    def crop(self, rect):
        self.operations.append((SVGImageOperation.CROP, rect))
        # return a new instance from all of these
        return self

    @Image.operation
    def resize(self, size):
        self.operations.append((SVGImageOperation.RESIZE, size))
        return self

    @Image.operation
    def has_animation(self):
        return False

    def write(self, f):
        self.image.write(f)

    @Image.operation
    def save_as_svg(self, f):
        self.write(f)
        return SVGImageFile(f, dom=self.image.dom)


willow_image_classes = [SVGImage]
