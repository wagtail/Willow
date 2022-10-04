import unittest
from io import BytesIO
from itertools import product
from string import Template

from defusedxml import ElementTree

from willow.image import Image, SvgImageFile, BadImageOperationError
from willow.svg import (
    SvgWrapper,
    InvalidSvgAttribute,
    InvalidSvgSizeAttribute,
    SvgImage,
    ViewBox,
)


class SvgWrapperTestCase(unittest.TestCase):
    svg_template = Template(
        '<svg width="$width" height="$height" viewBox="$view_box" '
        'preserveAspectRatio="$preserve_aspect_ratio"></svg>'
    )

    def get_svg_wrapper(
        self,
        *,
        dpi=96,
        font_size_px=16,
        width="",
        height="",
        view_box="",
        preserve_aspect_ratio="xMidYMid meet",
    ):
        svg_raw = self.svg_template.substitute(
            {
                "width": width,
                "height": height,
                "view_box": view_box,
                "preserve_aspect_ratio": preserve_aspect_ratio,
            }
        )
        svg_buf = BytesIO(bytes(svg_raw, encoding="utf-8"))
        # ElementTree.parse returns an ElementTree,
        # ElementTree.fromstring returns an Element, a pointer to the
        # root node. SvgWrapper needs an ElementTree.
        return SvgWrapper(
            ElementTree.parse(svg_buf), dpi=dpi, font_size_px=font_size_px
        )


class SvgWrapperSizeTestCase(SvgWrapperTestCase):
    def test_size_no_unit_both_attrs(self):
        svg = self.get_svg_wrapper(width=42, height=47)
        self.assertEqual((svg.width, svg.height), (42, 47))

    def test_size_no_unit_width_only(self):
        # If only height or only width are declared, the undeclared
        # attribute takes its value from the other
        svg = self.get_svg_wrapper(width=42)
        self.assertEqual((svg.width, svg.height), (42, 42))

    def test_size_no_unit_height_only(self):
        svg = self.get_svg_wrapper(height=42)
        self.assertEqual((svg.width, svg.height), (42, 42))

    def test_size_px_unit(self):
        svg = self.get_svg_wrapper(width="42px", height="32px")
        self.assertEqual((svg.width, svg.height), (42, 32))

    def test_size_em_unit(self):
        svg = self.get_svg_wrapper(width="1em", height="2em")
        self.assertEqual((svg.width, svg.height), (16, 32))

    def test_size_ex_unit(self):
        svg = self.get_svg_wrapper(width="1ex", height="2ex")
        self.assertEqual((svg.width, svg.height), (8, 16))

    def test_size_pt_unit(self):
        svg = self.get_svg_wrapper(width="12pt", height="16pt")
        self.assertEqual(svg.width, 16)
        self.assertAlmostEqual(21.3, svg.height, places=1)

    def test_size_mm_unit(self):
        svg = self.get_svg_wrapper(width="25mm")
        self.assertAlmostEqual(svg.width, 94.5, places=1)

    def test_size_cm_unit(self):
        svg = self.get_svg_wrapper(width="2.5cm")
        self.assertAlmostEqual(svg.width, 94.5, places=1)

    def test_size_in_unit(self):
        svg = self.get_svg_wrapper(width="0.5in")
        self.assertEqual(svg.width, 48)

    def test_size_pc_unit(self):
        svg = self.get_svg_wrapper(height="2pc")
        self.assertEqual(svg.height, 32)

    def test_size_mixed_unit(self):
        svg = self.get_svg_wrapper(width="0.25in", height="0.5pc")
        self.assertEqual((svg.width, svg.height), (24, 8))

    def test_percent_fails(self):
        with self.assertRaises(InvalidSvgSizeAttribute):
            self.get_svg_wrapper(width="75%")

    def test_size_with_extra_whitespace(self):
        sizes = (" 1px", "  1px ", "1px  ")
        for size in sizes:
            with self.subTest(size=size):
                svg = self.get_svg_wrapper(width=size)
                self.assertEqual(svg.width, 1)

    def test_invalid_size_fails(self):
        bad_sizes = (
            "twenty-three-px",
            "1 2in",
        )
        for size in bad_sizes:
            with self.subTest(size=size):
                with self.assertRaises(InvalidSvgSizeAttribute):
                    self.get_svg_wrapper(width=size)

    def test_size_from_view_box(self):
        values = (
            "10 10 30 40",
            "10,10,30,40",
            "10, 10, 30, 40",
            "10, 10,30 40",
            "10, 10,30 40   ",
            " 10, 10,30 40   ",
            "   10, 10,30 40",
        )
        for view_box in values:
            svg = self.get_svg_wrapper(view_box=view_box)
            with self.subTest(view_box=view_box):
                self.assertEqual((svg.width, svg.height), (30, 40))

    def test_view_box_float_parsing(self):
        values = (
            ("0 0 0 10.0", 10.0),
            ("0 0 0 -1.0", -1.0),
            ("0 0 0 +1.0", 1.0),
            ("0 0 0 +.5", 0.5),
            ("0 0 0 -.5", -0.5),
            ("0 0 0 +.5e9", 0.5e9),
            ("0 0 0 +.5E9", 0.5e9),
            ("0 0 0 -.5e9", -0.5e9),
            ("0 0 0 -.5E9", -0.5e9),
            ("0 0 0 1.55e9", 1.55e9),
            ("0 0 0 1.55E9", 1.55e9),
            ("0 0 0 +12.55e9", 12.55e9),
            ("0 0 0 -12.55E9", -12.55e9),
            ("0 0 0 1e9", 1e9),
            ("0 0 0 1E9", 1e9),
        )
        for view_box, expected in values:
            svg = self.get_svg_wrapper(view_box=view_box)
            with self.subTest(view_box=view_box):
                self.assertEqual(svg.height, expected)

    def test_raises_negative_size(self):
        with self.assertRaises(InvalidSvgSizeAttribute):
            self.get_svg_wrapper(width="-3")

    def test_raises_zero_size(self):
        with self.assertRaises(InvalidSvgSizeAttribute):
            self.get_svg_wrapper(width="0")

    def test_parse_preserve_aspect_ratio(self):
        svg = SvgImage(self.get_svg_wrapper(preserve_aspect_ratio="none"))
        self.assertEqual(svg.image.preserve_aspect_ratio, "none")

        svg = SvgImage(self.get_svg_wrapper(preserve_aspect_ratio=""))
        self.assertEqual(svg.image.preserve_aspect_ratio, "xMidYMid meet")

        svg = SvgImage(self.get_svg_wrapper())
        self.assertEqual(svg.image.preserve_aspect_ratio, "xMidYMid meet")

        combos = list(
            product(
                ("Min", "Mid", "Max"),
                ("Min", "Mid", "Max"),
                ("", " meet", " slice"),
            )
        )
        for x, y, meet_or_slice in combos:
            preserve_aspect_ratio = f"x{x}Y{y}{meet_or_slice}"
            with self.subTest(preserve_aspect_ratio=preserve_aspect_ratio):
                svg = SvgImage(
                    self.get_svg_wrapper(preserve_aspect_ratio=preserve_aspect_ratio)
                )
                self.assertEqual(svg.image.preserve_aspect_ratio, preserve_aspect_ratio)

    def test_parse_preserve_aspect_ratio_throws(self):
        with self.assertRaises(InvalidSvgAttribute):
            SvgImage(self.get_svg_wrapper(preserve_aspect_ratio="xMidYMin foo"))

        with self.assertRaises(InvalidSvgAttribute):
            SvgImage(self.get_svg_wrapper(preserve_aspect_ratio="non"))

        with self.assertRaises(InvalidSvgAttribute):
            SvgImage(self.get_svg_wrapper(preserve_aspect_ratio="xminYMin"))

        with self.assertRaises(InvalidSvgAttribute):
            SvgImage(self.get_svg_wrapper(preserve_aspect_ratio="xMinYMa"))


class SvgImageTestCase(SvgWrapperTestCase):
    def test_resize(self):
        f = BytesIO(b'<svg width="42" height="42" viewBox="0 0 42 42"></svg>')
        svg_image_file = Image.open(f)
        resized = svg_image_file.resize((10, 10))
        self.assertEqual(resized.get_size(), (10, 10))
        self.assertIsInstance(resized, SvgImage)

        # Check the underlying etree has been updated
        self.assertEqual(resized.image.root.get("width"), "10")
        self.assertEqual(resized.image.root.get("height"), "10")

    def test_resize_throws(self):
        f = BytesIO(b'<svg width="42" height="42" viewBox="0 0 42 42"></svg>')
        svg_image_file = Image.open(f)

        with self.assertRaises(BadImageOperationError):
            svg_image_file.resize((0, 10))

        with self.assertRaises(BadImageOperationError):
            svg_image_file.resize((10, 0))

    def test_crop(self):
        f = BytesIO(b'<svg width="42" height="42" viewBox="0 0 42 42"></svg>')
        svg_image_file = Image.open(f)
        cropped = svg_image_file.crop((5, 5, 15, 15))
        self.assertEqual(cropped.get_size(), (10, 10))
        self.assertEqual(cropped.image.view_box, ViewBox(5, 5, 10, 10))

        # Check the underlying etree has been updated
        self.assertEqual(float(cropped.image.root.get("width")), 10)
        self.assertEqual(float(cropped.image.root.get("height")), 10)
        self.assertEqual(
            [float(x) for x in cropped.image.root.get("viewBox").split()],
            [5, 5, 10, 10],
        )

    def test_crop_with_transform(self):
        # user coordinates scaled by 2 and translated 50 units south
        svg = SvgImage(
            self.get_svg_wrapper(
                width=50,
                height=100,
                view_box="0 0 25 25",
                preserve_aspect_ratio="xMidYMax meet",
            )
        )

        cropped = svg.crop((10, 10, 20, 20))
        self.assertEqual(cropped.get_size(), (10, 10))
        self.assertEqual(cropped.image.view_box, ViewBox(5, -20, 5, 5))
        self.assertEqual(float(cropped.image.root.get("width")), 10)
        self.assertEqual(float(cropped.image.root.get("height")), 10)

    def test_crop_throws(self):
        f = BytesIO(b'<svg width="42" height="42" viewBox="0 0 42 42"></svg>')
        svg_image_file = Image.open(f)

        with self.assertRaises(BadImageOperationError):
            # left > right
            svg_image_file.crop((10, 0, 0, 10))

        with self.assertRaises(BadImageOperationError):
            # left == right
            svg_image_file.crop((10, 0, 10, 10))

        with self.assertRaises(BadImageOperationError):
            # top > bottom
            svg_image_file.crop((0, 10, 10, 0))

        with self.assertRaises(BadImageOperationError):
            # top == bottom
            svg_image_file.crop((0, 10, 10, 10))

    def test_save_as_svg(self):
        f = BytesIO(b'<svg width="13" height="13" viewBox="0 0 13 13"></svg>')
        svg_image_file = Image.open(f)
        svg = SvgImage(image=SvgWrapper(svg_image_file.dom))
        written = svg.save_as_svg(BytesIO())
        self.assertIsInstance(written, SvgImageFile)
        self.assertEqual(written.dom.getroot().get("width"), "13")
        self.assertEqual(written.dom.getroot().get("height"), "13")