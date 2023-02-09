from functools import partial

from willow.svg import (
    get_viewport_to_user_space_transform,
    transform_rect_to_user_space,
    SvgImage,
    ViewportToUserSpaceTransform,
)

from .test_svg_image import SvgWrapperTestCase


class ViewportToUserSpaceTransformTestCase(SvgWrapperTestCase):
    def test_get_transform_same_ratio(self):
        svg = SvgImage(
            self.get_svg_wrapper(width=100, height=100, view_box="0 0 100 100")
        )
        transform = get_viewport_to_user_space_transform(svg)
        self.assertEqual(transform, ViewportToUserSpaceTransform(1, 1, 0, 0))

    def test_get_transform_equivalent_ratios(self):
        svg = SvgImage(self.get_svg_wrapper(width=90, height=30, view_box="0 0 9 3"))
        transform = get_viewport_to_user_space_transform(svg)
        self.assertEqual(transform, ViewportToUserSpaceTransform(10, 10, 0, 0))

    def test_get_transform_equivalent_ratios_floats(self):
        svg = SvgImage(
            self.get_svg_wrapper(width=95, height=35, view_box="0 0 9.5 3.5")
        )
        transform = get_viewport_to_user_space_transform(svg)
        self.assertEqual(transform, ViewportToUserSpaceTransform(10, 10, 0, 0))

    def test_preserve_aspect_ratio_none(self):
        svg = SvgImage(
            self.get_svg_wrapper(
                width=100,
                height=100,
                view_box="0 0 50 80",
                preserve_aspect_ratio="none",
            )
        )
        transform = get_viewport_to_user_space_transform(svg)
        self.assertEqual(transform, ViewportToUserSpaceTransform(2, 1.25, 0, 0))

    def test_transform_rect_to_user_space_translate_x(self):
        svg_wrapper = partial(
            self.get_svg_wrapper, width=100, height=50, view_box="0 0 25 25"
        )
        params = [
            # transform = (2, 2, 0, 0)
            ("xMinYMid meet", (10, 10, 20, 20), (5, 5, 10, 10)),
            # transform = (2, 2, 25, 0)
            ("xMidYMid meet", (10, 10, 20, 20), (-7.5, 5, -2.5, 10)),
            # transform = (2, 2, 50, 0)
            ("xMaxYMid meet", (10, 10, 20, 20), (-20, 5, -15, 10)),
        ]
        for preserve_aspect_ratio, rect, expected_result in params:
            with self.subTest(preserve_aspect_ratio=preserve_aspect_ratio, rect=rect):
                svg = SvgImage(svg_wrapper(preserve_aspect_ratio=preserve_aspect_ratio))
                self.assertEqual(
                    transform_rect_to_user_space(svg, rect), expected_result
                )

    def test_transform_rect_to_user_space_translate_y(self):
        svg_wrapper = partial(
            self.get_svg_wrapper, width=50, height=100, view_box="0 0 25 25"
        )
        params = [
            # transform = (2, 2, 0, 0)
            ("xMidYMin meet", (10, 10, 20, 20), (5, 5, 10, 10)),
            # transform = (2, 2, 0, 25)
            ("xMidYMid meet", (10, 10, 20, 20), (5, -7.5, 10, -2.5)),
            # transform = (2, 2, 0, 50)
            ("xMidYMax meet", (10, 10, 20, 20), (5, -20, 10, -15)),
        ]
        for preserve_aspect_ratio, rect, expected_result in params:
            with self.subTest(preserve_aspect_ratio=preserve_aspect_ratio, rect=rect):
                svg = SvgImage(svg_wrapper(preserve_aspect_ratio=preserve_aspect_ratio))
                self.assertEqual(
                    transform_rect_to_user_space(svg, rect), expected_result
                )

    def test_complex_user_space_origin_transform(self):
        svg = SvgImage(
            self.get_svg_wrapper(
                width=100,
                height=100,
                view_box="-50 -50 100 100",
                preserve_aspect_ratio="none",
            )
        )
        self.assertEqual(
            transform_rect_to_user_space(svg, (0, 0, 50, 50)),
            (-50, -50, 0, 0),
        )

        svg = SvgImage(
            self.get_svg_wrapper(
                width=200,
                height=200,
                view_box="-50 -50 100 100",
                preserve_aspect_ratio="none",
            )
        )
        self.assertEqual(
            transform_rect_to_user_space(svg, (0, 0, 50, 50)),
            (-25, -25, 0, 0),
        )


class PreserveAspectRatioMeetTestCase(SvgWrapperTestCase):
    def test_portrait_view_box(self):
        # With "meet", the scaling factor will be min(scale_x,
        # scale_y). In the case of a portrait ratio view box in a
        # square viewport, this will be scale_y
        svg_wrapper = partial(
            self.get_svg_wrapper, width=100, height=100, view_box="0 0 50 80"
        )
        params = [
            ("xMinYMin meet", ViewportToUserSpaceTransform(1.25, 1.25, 0, 0)),
            ("xMinYMid meet", ViewportToUserSpaceTransform(1.25, 1.25, 0, 0)),
            ("xMinYMax meet", ViewportToUserSpaceTransform(1.25, 1.25, 0, 0)),
            ("xMidYMin meet", ViewportToUserSpaceTransform(1.25, 1.25, 18.75, 0)),
            ("xMidYMid meet", ViewportToUserSpaceTransform(1.25, 1.25, 18.75, 0)),
            ("xMidYMax meet", ViewportToUserSpaceTransform(1.25, 1.25, 18.75, 0)),
            ("xMaxYMin meet", ViewportToUserSpaceTransform(1.25, 1.25, 37.5, 0)),
            ("xMaxYMid meet", ViewportToUserSpaceTransform(1.25, 1.25, 37.5, 0)),
            ("xMaxYMax meet", ViewportToUserSpaceTransform(1.25, 1.25, 37.5, 0)),
        ]
        for preserve_aspect_ratio, expected_result in params:
            with self.subTest(preserve_aspect_ratio=preserve_aspect_ratio):
                svg = SvgImage(svg_wrapper(preserve_aspect_ratio=preserve_aspect_ratio))
                self.assertEqual(
                    get_viewport_to_user_space_transform(svg), expected_result
                )

    def test_landscape_view_box(self):
        # With a landscape orientation view box, we will use scale_x
        # as the scaling factor
        svg_wrapper = partial(
            self.get_svg_wrapper, width=100, height=100, view_box="0 0 80 50"
        )
        params = [
            ("xMinYMin meet", ViewportToUserSpaceTransform(1.25, 1.25, 0, 0)),
            ("xMidYMin meet", ViewportToUserSpaceTransform(1.25, 1.25, 0, 0)),
            ("xMaxYMin meet", ViewportToUserSpaceTransform(1.25, 1.25, 0, 0)),
            ("xMinYMid meet", ViewportToUserSpaceTransform(1.25, 1.25, 0, 18.75)),
            ("xMidYMid meet", ViewportToUserSpaceTransform(1.25, 1.25, 0, 18.75)),
            ("xMaxYMid meet", ViewportToUserSpaceTransform(1.25, 1.25, 0, 18.75)),
            ("xMinYMax meet", ViewportToUserSpaceTransform(1.25, 1.25, 0, 37.5)),
            ("xMidYMax meet", ViewportToUserSpaceTransform(1.25, 1.25, 0, 37.5)),
            ("xMaxYMax meet", ViewportToUserSpaceTransform(1.25, 1.25, 0, 37.5)),
        ]
        for preserve_aspect_ratio, expected_result in params:
            with self.subTest(preserve_aspect_ratio=preserve_aspect_ratio):
                svg = SvgImage(svg_wrapper(preserve_aspect_ratio=preserve_aspect_ratio))
                self.assertEqual(
                    get_viewport_to_user_space_transform(svg), expected_result
                )


class PreserveAspectRatioSliceTestCase(SvgWrapperTestCase):
    def test_portrait_view_box(self):
        # With "slice", the scaling factor will be max(scale_x,
        # scale_y). In the case of a portrait ratio view box in a
        # square viewport, this will be scale_x
        svg_wrapper = partial(
            self.get_svg_wrapper, width=100, height=100, view_box="0 0 40 80"
        )
        params = [
            ("xMinYMin slice", ViewportToUserSpaceTransform(2.5, 2.5, 0, 0)),
            ("xMidYMin slice", ViewportToUserSpaceTransform(2.5, 2.5, 0, 0)),
            ("xMaxYMin slice", ViewportToUserSpaceTransform(2.5, 2.5, 0, 0)),
            ("xMinYMid slice", ViewportToUserSpaceTransform(2.5, 2.5, 0, -50)),
            ("xMidYMid slice", ViewportToUserSpaceTransform(2.5, 2.5, 0, -50)),
            ("xMaxYMid slice", ViewportToUserSpaceTransform(2.5, 2.5, 0, -50)),
            ("xMinYMax slice", ViewportToUserSpaceTransform(2.5, 2.5, 0, -100)),
            ("xMidYMax slice", ViewportToUserSpaceTransform(2.5, 2.5, 0, -100)),
            ("xMaxYMax slice", ViewportToUserSpaceTransform(2.5, 2.5, 0, -100)),
        ]
        for preserve_aspect_ratio, expected_result in params:
            with self.subTest(preserve_aspect_ratio=preserve_aspect_ratio):
                svg = SvgImage(svg_wrapper(preserve_aspect_ratio=preserve_aspect_ratio))
                self.assertEqual(
                    get_viewport_to_user_space_transform(svg), expected_result
                )

    def test_landscape_view_box(self):
        # With a landscape orientation view box, we will use scale_y
        # as the scaling factor
        svg_wrapper = partial(
            self.get_svg_wrapper, width=100, height=100, view_box="0 0 80 40"
        )
        params = [
            ("xMinYMin slice", ViewportToUserSpaceTransform(2.5, 2.5, 0, 0)),
            ("xMinYMid slice", ViewportToUserSpaceTransform(2.5, 2.5, 0, 0)),
            ("xMinYMax slice", ViewportToUserSpaceTransform(2.5, 2.5, 0, 0)),
            ("xMidYMin slice", ViewportToUserSpaceTransform(2.5, 2.5, -50, 0)),
            ("xMidYMid slice", ViewportToUserSpaceTransform(2.5, 2.5, -50, 0)),
            ("xMidYMax slice", ViewportToUserSpaceTransform(2.5, 2.5, -50, 0)),
            ("xMaxYMin slice", ViewportToUserSpaceTransform(2.5, 2.5, -100, 0)),
            ("xMaxYMid slice", ViewportToUserSpaceTransform(2.5, 2.5, -100, 0)),
            ("xMaxYMax slice", ViewportToUserSpaceTransform(2.5, 2.5, -100, 0)),
        ]
        for preserve_aspect_ratio, expected_result in params:
            with self.subTest(preserve_aspect_ratio=preserve_aspect_ratio):
                svg = SvgImage(svg_wrapper(preserve_aspect_ratio=preserve_aspect_ratio))
                self.assertEqual(
                    get_viewport_to_user_space_transform(svg), expected_result
                )
