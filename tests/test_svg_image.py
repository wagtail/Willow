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

    def test_relative_size_uses_view_box(self):
        cases = [
            ({"width": "100%", "height": "100%", "view_box": "0 0 42 42"}, (42, 42)),
            ({"width": "200%", "height": "200%", "view_box": "0 0 42 42"}, (42, 42)),
            ({"width": "1.5%", "height": "3.2%", "view_box": "0 0 42 42"}, (42, 42)),
        ]
        for attrs, expected in cases:
            with self.subTest(attrs=attrs, expected=expected):
                svg_wrapper = self.get_svg_wrapper(**attrs)
                self.assertEqual((svg_wrapper.width, svg_wrapper.height), expected)

    def test_relative_size_uses_other_absolute_size(self):
        cases = [
            ({"width": "100%", "height": "100", "view_box": "0 0 42 42"}, (100, 100)),
            ({"width": "100", "height": "100%", "view_box": "0 0 42 42"}, (100, 100)),
            ({"width": "300%", "height": "100", "view_box": "0 0 42 42"}, (100, 100)),
            ({"width": "100", "height": "300%", "view_box": "0 0 42 42"}, (100, 100)),
            (
                {"width": "100%", "height": "200em", "view_box": "0 0 42 42"},
                (3200, 3200),
            ),
            (
                {"width": "200em", "height": "100%", "view_box": "0 0 42 42"},
                (3200, 3200),
            ),
        ]
        for attrs, expected in cases:
            with self.subTest(attrs=attrs, expected=expected):
                svg_wrapper = self.get_svg_wrapper(**attrs)
                self.assertEqual((svg_wrapper.width, svg_wrapper.height), expected)

    def test_relative_size_no_view_box_uses_defaults(self):
        cases = [
            {"width": "100%", "height": "", "view_box": ""},
            {"width": "", "height": "100%", "view_box": ""},
            {"width": "100%", "height": "100%", "view_box": ""},
        ]
        for attrs in cases:
            with self.subTest(attrs=attrs):
                svg_wrapper = self.get_svg_wrapper(**attrs)
                self.assertEqual((svg_wrapper.width, svg_wrapper.height), (300, 150))


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

    def test_get_frame_count(self):
        svg = SvgImage(self.get_svg_wrapper())
        self.assertEqual(svg.get_frame_count(), 1)

    def test_crop_preserves_original_image(self):
        """
        Cropping should create a new image, leaving the original untouched.
        """
        f = BytesIO(b'<svg width="42" height="42" viewBox="0 0 42 42"></svg>')
        svg_image_file = Image.open(f)
        svg = SvgImage.open(svg_image_file)
        svg.crop((0, 0, 10, 10))
        self.assertEqual(svg.image.view_box, ViewBox(0, 0, 42, 42))

    def test_resize_preserves_original_image(self):
        f = BytesIO(b'<svg width="42" height="42" viewBox="0 0 42 42"></svg>')
        svg_image_file = Image.open(f)
        svg = SvgImage.open(svg_image_file)
        svg.resize((21, 21))
        self.assertEqual(svg.get_size(), (42, 42))


class SvgViewBoxTestCase(unittest.TestCase):
    def test_view_box_re(self):
        params = [
            ("0 0 1 1", ViewBox(0, 0, 1, 1)),
            (" 0 0 1 1 ", ViewBox(0, 0, 1, 1)),
            ("-0 +0 -1 +1", ViewBox(0, 0, -1, 1)),
            ("+0 -0 +1 -1", ViewBox(0, 0, 1, -1)),
            ("-0,+0,-1,+1", ViewBox(0, 0, -1, 1)),
            ("+0,-0,+1,-1", ViewBox(0, 0, 1, -1)),
            ("-0,   +0, -1   +1", ViewBox(0, 0, -1, 1)),
            ("+0,   -0, +1     -1", ViewBox(0, 0, 1, -1)),
            ("150 150 200 200", ViewBox(150, 150, 200, 200)),
            (
                "150.1 150.12 200.123 200.1234",
                ViewBox(150.1, 150.12, 200.123, 200.1234),
            ),
            ("150.0,150.0,200.0,200.0", ViewBox(150, 150, 200, 200)),
            ("150.0, 150.0, 200.0, 200.0", ViewBox(150, 150, 200, 200)),
            ("150.0,  150.0,   200.0  200.0", ViewBox(150, 150, 200, 200)),
            ("-350 360.1 464 81.9", ViewBox(-350, 360.1, 464, 81.9)),
            ("0 0 1e2 12.13e3", ViewBox(0, 0, 100, 12130)),
            ("-0 -0 -1e2 -12.13e3", ViewBox(0, 0, -100, -12130)),
            ("0 0 .5 .5", ViewBox(0, 0, 0.5, 0.5)),
            ("0 0 .5e1 .5e1", ViewBox(0, 0, 5, 5)),
            ("0 0 .5e0 .5e0", ViewBox(0, 0, 0.5, 0.5)),
            ("0 0 -.5e1 +.5e1", ViewBox(0, 0, -5, 5)),
            ("0 0 -.0e1 +.0e1", ViewBox(0, 0, 0, 0)),
            ("0 0,-.0e1,+.0e1", ViewBox(0, 0, 0, 0)),
            (".1,0,0,0", ViewBox(0.1, 0, 0, 0)),
            ("+.1,0,0,0", ViewBox(0.1, 0, 0, 0)),
            ("-.1,0,0,0", ViewBox(-0.1, 0, 0, 0)),
        ]
        for value, expected in params:
            with self.subTest(value=value, expected=expected):
                self.assertEqual(SvgWrapper._parse_view_box(value), expected)
