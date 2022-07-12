import unittest
from io import BytesIO
from string import Template

from defusedxml import ElementTree
from willow.svg import SVGWrapper, InvalidSizeAttribute


class SVGWrapperSizeTestCase(unittest.TestCase):
    svg_template = Template(
        '<svg width="$width" height="$height" viewBox="$view_box"></svg>'
    )

    @classmethod
    def setUpClass(cls):
        cls.epsilon = 0.2

    def get_svg_wrapper(
        self, *, dpi=96, font_size_px=16, width="", height="", view_box=""
    ):
        svg_raw = self.svg_template.substitute(
            {"width": width, "height": height, "view_box": view_box}
        )
        svg_buf = BytesIO(bytes(svg_raw, encoding="utf-8"))
        # ElementTree.parse returns an ElementTree,
        # ElementTree.fromstring returns an Element, a pointer to the
        # root node. SVGWrapper needs an ElementTree.
        return SVGWrapper(
            ElementTree.parse(svg_buf), dpi=dpi, font_size_px=font_size_px
        )

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
        self.assertLess(abs(21.5 - svg.height), self.epsilon)

    def test_size_mm_unit(self):
        svg = self.get_svg_wrapper(width="25mm")
        self.assertLess(abs(94.5 - svg.width), self.epsilon)

    def test_size_cm_unit(self):
        svg = self.get_svg_wrapper(width="2.5cm")
        self.assertLess(abs(94.5 - svg.width), self.epsilon)

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
        with self.assertRaises(InvalidSizeAttribute):
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
                with self.assertRaises(InvalidSizeAttribute):
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
