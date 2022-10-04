from functools import partial

from willow.svg import (
    get_user_space_to_viewport_transform,
    transform_rect_to_user_space,
    SvgImage,
    UserSpaceToViewportTransform,
)

from .test_svg_image import SvgWrapperTestCase


class UserSpaceToViewportTransformTestCase(SvgWrapperTestCase):
    def test_get_transform_same_ratio(self):
        svg = SvgImage(
            self.get_svg_wrapper(width=100, height=100, view_box="0 0 100 100")
        )
        transform = get_user_space_to_viewport_transform(svg)
        self.assertEqual(transform, UserSpaceToViewportTransform(1, 1, 0, 0))

    def test_get_transform_equivalent_ratios(self):
        svg = SvgImage(self.get_svg_wrapper(width=90, height=30, view_box="0 0 9 3"))
        transform = get_user_space_to_viewport_transform(svg)
        self.assertEqual(transform, UserSpaceToViewportTransform(10, 10, 0, 0))

    def test_preserve_aspect_ratio_none(self):
        svg = SvgImage(
            self.get_svg_wrapper(
                width=100,
                height=100,
                view_box="0 0 50 80",
                preserve_aspect_ratio="none",
            )
        )
        transform = get_user_space_to_viewport_transform(svg)
        self.assertEqual(transform, UserSpaceToViewportTransform(2, 1.25, 0, 0))

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


class PreserveAspectRatioMeetTestCase(SvgWrapperTestCase):
    def test_portrait_view_box(self):
        # With "meet", the scaling factor will be min(scale_x,
        # scale_y). In the case of a portrait ratio view box in a
        # square viewport, this will be scale_y
        svg_wrapper = partial(
            self.get_svg_wrapper, width=100, height=100, view_box="0 0 50 80"
        )
        params = [
            ("xMinYMin meet", UserSpaceToViewportTransform(1.25, 1.25, 0, 0)),
            ("xMinYMid meet", UserSpaceToViewportTransform(1.25, 1.25, 0, 0)),
            ("xMinYMax meet", UserSpaceToViewportTransform(1.25, 1.25, 0, 0)),
            ("xMidYMin meet", UserSpaceToViewportTransform(1.25, 1.25, 18.75, 0)),
            ("xMidYMid meet", UserSpaceToViewportTransform(1.25, 1.25, 18.75, 0)),
            ("xMidYMax meet", UserSpaceToViewportTransform(1.25, 1.25, 18.75, 0)),
            ("xMaxYMin meet", UserSpaceToViewportTransform(1.25, 1.25, 37.5, 0)),
            ("xMaxYMid meet", UserSpaceToViewportTransform(1.25, 1.25, 37.5, 0)),
            ("xMaxYMax meet", UserSpaceToViewportTransform(1.25, 1.25, 37.5, 0)),
        ]
        for preserve_aspect_ratio, expected_result in params:
            with self.subTest(preserve_aspect_ratio=preserve_aspect_ratio):
                svg = SvgImage(svg_wrapper(preserve_aspect_ratio=preserve_aspect_ratio))
                self.assertEqual(
                    get_user_space_to_viewport_transform(svg), expected_result
                )

    def test_landscape_view_box(self):
        # With a landscape orientation view box, we will use scale_x
        # as the scaling factor
        svg_wrapper = partial(
            self.get_svg_wrapper, width=100, height=100, view_box="0 0 80 50"
        )
        params = [
            ("xMinYMin meet", UserSpaceToViewportTransform(1.25, 1.25, 0, 0)),
            ("xMidYMin meet", UserSpaceToViewportTransform(1.25, 1.25, 0, 0)),
            ("xMaxYMin meet", UserSpaceToViewportTransform(1.25, 1.25, 0, 0)),
            ("xMinYMid meet", UserSpaceToViewportTransform(1.25, 1.25, 0, 18.75)),
            ("xMidYMid meet", UserSpaceToViewportTransform(1.25, 1.25, 0, 18.75)),
            ("xMaxYMid meet", UserSpaceToViewportTransform(1.25, 1.25, 0, 18.75)),
            ("xMinYMax meet", UserSpaceToViewportTransform(1.25, 1.25, 0, 37.5)),
            ("xMidYMax meet", UserSpaceToViewportTransform(1.25, 1.25, 0, 37.5)),
            ("xMaxYMax meet", UserSpaceToViewportTransform(1.25, 1.25, 0, 37.5)),
        ]
        for preserve_aspect_ratio, expected_result in params:
            with self.subTest(preserve_aspect_ratio=preserve_aspect_ratio):
                svg = SvgImage(svg_wrapper(preserve_aspect_ratio=preserve_aspect_ratio))
                self.assertEqual(
                    get_user_space_to_viewport_transform(svg), expected_result
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
            ("xMinYMin slice", UserSpaceToViewportTransform(2.5, 2.5, 0, 0)),
            ("xMidYMin slice", UserSpaceToViewportTransform(2.5, 2.5, 0, 0)),
            ("xMaxYMin slice", UserSpaceToViewportTransform(2.5, 2.5, 0, 0)),
            ("xMinYMid slice", UserSpaceToViewportTransform(2.5, 2.5, 0, -50)),
            ("xMidYMid slice", UserSpaceToViewportTransform(2.5, 2.5, 0, -50)),
            ("xMaxYMid slice", UserSpaceToViewportTransform(2.5, 2.5, 0, -50)),
            ("xMinYMax slice", UserSpaceToViewportTransform(2.5, 2.5, 0, -100)),
            ("xMidYMax slice", UserSpaceToViewportTransform(2.5, 2.5, 0, -100)),
            ("xMaxYMax slice", UserSpaceToViewportTransform(2.5, 2.5, 0, -100)),
        ]
        for preserve_aspect_ratio, expected_result in params:
            with self.subTest(preserve_aspect_ratio=preserve_aspect_ratio):
                svg = SvgImage(svg_wrapper(preserve_aspect_ratio=preserve_aspect_ratio))
                self.assertEqual(
                    get_user_space_to_viewport_transform(svg), expected_result
                )

    def test_landscape_view_box(self):
        # With a landscape orientation view box, we will use scale_y
        # as the scaling factor
        svg_wrapper = partial(
            self.get_svg_wrapper, width=100, height=100, view_box="0 0 80 40"
        )
        params = [
            ("xMinYMin slice", UserSpaceToViewportTransform(2.5, 2.5, 0, 0)),
            ("xMinYMid slice", UserSpaceToViewportTransform(2.5, 2.5, 0, 0)),
            ("xMinYMax slice", UserSpaceToViewportTransform(2.5, 2.5, 0, 0)),
            ("xMidYMin slice", UserSpaceToViewportTransform(2.5, 2.5, -50, 0)),
            ("xMidYMid slice", UserSpaceToViewportTransform(2.5, 2.5, -50, 0)),
            ("xMidYMax slice", UserSpaceToViewportTransform(2.5, 2.5, -50, 0)),
            ("xMaxYMin slice", UserSpaceToViewportTransform(2.5, 2.5, -100, 0)),
            ("xMaxYMid slice", UserSpaceToViewportTransform(2.5, 2.5, -100, 0)),
            ("xMaxYMax slice", UserSpaceToViewportTransform(2.5, 2.5, -100, 0)),
        ]
        for preserve_aspect_ratio, expected_result in params:
            with self.subTest(preserve_aspect_ratio=preserve_aspect_ratio):
                svg = SvgImage(svg_wrapper(preserve_aspect_ratio=preserve_aspect_ratio))
                self.assertEqual(
                    get_user_space_to_viewport_transform(svg), expected_result
                )
