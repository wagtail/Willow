import re
from collections import namedtuple
from fractions import Fraction
from xml.etree.ElementTree import ElementTree

from .image import BadImageOperationError, Image, SvgImageFile


class WillowSvgException(Exception):
    pass


class InvalidSizeAttribute(WillowSvgException):
    pass


class ViewBoxParseError(WillowSvgException):
    pass


ViewBox = namedtuple("ViewBox", "min_x min_y width height")


def view_box_to_attr_str(view_box):
    return f"{view_box.min_x} {view_box.min_y} {view_box.width} {view_box.height}"


UserSpaceToViewportTransform = namedtuple(
    "UserSpaceToViewportTransform",
    "scale_x scale_y translate_x translate_y",
)


class SvgWrapper:
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

        # If the root svg element has no width, height, or viewBox attributes,
        # emulate browser behaviour and set width and height to 300 and 150
        # respectively, and set the viewBox to match
        # (https://svgwg.org/specs/integration/#svg-css-sizing). This means we
        # can always crop and resize without needing to rasterise
        self.width = self._get_width() or 300
        self.height = self._get_height() or 150
        if self.view_box is None:
            self.view_box = ViewBox(0, 0, self.width, self.height)

    @property
    def root(self):
        return self.dom.getroot()

    @property
    def preserve_aspect_ratio(self):
        # Not self.root.get("preserveAspectRatio", "xMidYMid meet"), as an
        # empty string value also maps to the default
        return self.root.get("preserveAspectRatio") or "xMidYMid meet"

    def _get_width(self):
        attr_value = self.root.get("width") or self.root.get("height")
        if attr_value:
            return self._parse_size(attr_value)
        elif self.view_box is not None:
            return self.view_box.width

    def _get_height(self):
        attr_value = self.root.get("height") or self.root.get("width")
        if attr_value:
            return self._parse_size(attr_value)
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

    def set_root_attr(self, attr, value):
        self.root.set(attr, str(value))

    def set_width(self, width):
        self.set_root_attr("width", width)
        self.width = width

    def set_height(self, height):
        self.set_root_attr("height", height)
        self.height = height

    def set_view_box(self, view_box):
        self.set_root_attr("viewBox", view_box_to_attr_str(view_box))
        self.view_box = view_box

    def write(self, f):
        self.dom.write(f, encoding="utf-8")


def get_user_space_to_viewport_transform(
    svg: "SvgImage",
) -> UserSpaceToViewportTransform:
    # cairosvg used as a reference
    view_box = svg.image.view_box
    if view_box is None:
        return UserSpaceToViewportTransform(1, 1, 0, 0)

    viewport_aspect_ratio = Fraction(round(svg.image.width), round(svg.image.height))
    user_aspect_ratio = Fraction(round(view_box.width), round(view_box.height))
    if viewport_aspect_ratio == user_aspect_ratio:
        scale = svg.image.width / view_box.width
        translate = 0
        return UserSpaceToViewportTransform(scale, scale, translate, translate)

    aspect_ratio = svg.image.preserve_aspect_ratio.split()
    try:
        align, meet_or_slice = aspect_ratio
    except ValueError:
        align = aspect_ratio[0]
        meet_or_slice = None

    scale_x = svg.image.width / view_box.width
    scale_y = svg.image.height / view_box.height

    if align == "none":
        x_position = "min"
        y_position = "min"
    else:
        x_position = align[1:4].lower()
        y_position = align[5:].lower()
        choose_coefficient = max if meet_or_slice == "slice" else min
        scale_x = scale_y = choose_coefficient(scale_x, scale_y)

    # Translations to be applied after scaling user space to viewport space
    translate_x = 0
    if x_position == "mid":
        translate_x = (svg.image.width - view_box.width * scale_x) / 2
    elif x_position == "max":
        translate_x = svg.image.width - view_box.width * scale_x

    translate_y = 0
    if y_position == "mid":
        translate_y += (svg.image.height - view_box.height * scale_y) / 2
    elif y_position == "max":
        translate_y += svg.image.height - view_box.height * scale_y

    return UserSpaceToViewportTransform(scale_x, scale_y, translate_x, translate_y)


def transform_rect_to_user_space(svg: "SvgImage", rect):
    transform = get_user_space_to_viewport_transform(svg)
    left, top, right, bottom = rect
    return (
        (left - transform.translate_x) / transform.scale_x,
        (top - transform.translate_y) / transform.scale_y,
        (right - transform.translate_x) / transform.scale_x,
        (bottom - transform.translate_y) / transform.scale_y,
    )


class SvgImage(Image):
    def __init__(self, image):
        self.image: SvgWrapper = image

    @Image.operation
    def crop(self, rect, transformer=transform_rect_to_user_space):
        left, top, right, bottom = rect
        if left >= right or top >= bottom:
            raise BadImageOperationError(f"Invalid crop dimensions: {rect}")

        viewport_width = right - left
        viewport_height = bottom - top

        transformed_rect = transformer(self, rect) if callable(transformer) else rect
        left, top, right, bottom = transformed_rect

        svg_wrapper = self.image
        view_box_width = right - left
        view_box_height = bottom - top
        svg_wrapper.set_view_box(ViewBox(left, top, view_box_width, view_box_height))
        svg_wrapper.set_width(viewport_width)
        svg_wrapper.set_height(viewport_height)
        return self.__class__(image=svg_wrapper)

    @Image.operation
    def resize(self, size):
        new_width, new_height = size
        if new_width < 1 or new_height < 1:
            raise BadImageOperationError(f"Invalid resize dimensions: {size}")
        svg_wrapper = self.image
        svg_wrapper.set_width(new_width)
        svg_wrapper.set_height(new_height)
        return self.__class__(image=svg_wrapper)

    @Image.operation
    def get_size(self):
        return (self.image.width, self.image.height)

    @Image.operation
    def auto_orient(self):
        return self

    @Image.operation
    def has_animation(self):
        return False

    def write(self, f):
        self.image.write(f)
        f.seek(0)

    @Image.operation
    def save_as_svg(self, f):
        self.write(f)
        return SvgImageFile(f, dom=self.image.dom)

    @classmethod
    @Image.converter_from(SvgImageFile)
    def open(cls, svg_image_file):
        return cls(image=SvgWrapper(svg_image_file.dom))
