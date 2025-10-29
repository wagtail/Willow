import io
import os
import unittest
from unittest import mock

import filetype
from PIL import Image as PILImage
from PIL import ImageChops, ImageCms, ImageStat

from willow.image import (
    AvifImageFile,
    BadImageOperationError,
    GIFImageFile,
    IcoImageFile,
    JPEGImageFile,
    PNGImageFile,
    WebPImageFile,
)
from willow.optimizers import Cwebp, Gifsicle, Jpegoptim, Optipng, Pngquant
from willow.plugins.pillow import PillowImage, UnsupportedRotation, _PIL_Image
from willow.registry import registry

no_webp_support = not PillowImage.is_format_supported("WEBP")
no_avif_support = not PillowImage.is_format_supported("AVIF")
no_heif_support = not PillowImage.is_format_supported("HEIF")


class TestPillowOperations(unittest.TestCase):
    def setUp(self):
        with open("tests/images/transparent.png", "rb") as f:
            self.image = PillowImage.open(PNGImageFile(f))

    def test_get_size(self):
        width, height = self.image.get_size()
        self.assertEqual(width, 200)
        self.assertEqual(height, 150)

    def test_get_frame_count(self):
        frames = self.image.get_frame_count()
        self.assertEqual(frames, 1)

    def test_resize(self):
        resized_image = self.image.resize((100, 75))
        self.assertEqual(resized_image.get_size(), (100, 75))

    def test_crop(self):
        cropped_image = self.image.crop((10, 10, 100, 100))
        self.assertEqual(cropped_image.get_size(), (90, 90))

    def test_crop_out_of_bounds(self):
        # crop rectangle should be clamped to the image boundaries
        bottom_right_cropped_image = self.image.crop((150, 100, 250, 200))
        self.assertEqual(bottom_right_cropped_image.get_size(), (50, 50))

        top_left_cropped_image = self.image.crop((-50, -50, 50, 50))
        self.assertEqual(top_left_cropped_image.get_size(), (50, 50))

        # fail if the crop rectangle is entirely to the left of the image
        with self.assertRaises(BadImageOperationError):
            self.image.crop((-100, 50, -50, 100))
        # right edge of crop rectangle is exclusive, so 0 is also invalid
        with self.assertRaises(BadImageOperationError):
            self.image.crop((-50, 50, 0, 100))

        # fail if the crop rectangle is entirely above the image
        with self.assertRaises(BadImageOperationError):
            self.image.crop((50, -100, 100, -50))
        # bottom edge of crop rectangle is exclusive, so 0 is also invalid
        with self.assertRaises(BadImageOperationError):
            self.image.crop((50, -50, 100, 0))

        # fail if the crop rectangle is entirely to the right of the image
        with self.assertRaises(BadImageOperationError):
            self.image.crop((250, 50, 300, 100))
        with self.assertRaises(BadImageOperationError):
            self.image.crop((200, 50, 250, 100))

        # fail if the crop rectangle is entirely below the image
        with self.assertRaises(BadImageOperationError):
            self.image.crop((50, 200, 100, 250))
        with self.assertRaises(BadImageOperationError):
            self.image.crop((50, 150, 100, 200))

        # fail if left edge >= right edge
        with self.assertRaises(BadImageOperationError):
            self.image.crop((125, 25, 25, 125))
        with self.assertRaises(BadImageOperationError):
            self.image.crop((100, 25, 100, 125))

        # fail if bottom edge >= top edge
        with self.assertRaises(BadImageOperationError):
            self.image.crop((25, 125, 125, 25))
        with self.assertRaises(BadImageOperationError):
            self.image.crop((25, 100, 125, 100))

    def test_rotate(self):
        rotated_image = self.image.rotate(90)
        width, height = rotated_image.get_size()
        self.assertEqual((width, height), (150, 200))

    def test_rotate_without_multiple_of_90(self):
        with self.assertRaises(UnsupportedRotation):
            self.image.rotate(45)

    def test_rotate_greater_than_360(self):
        # 450 should end up the same as a 90 rotation
        rotated_image = self.image.rotate(450)
        width, height = rotated_image.get_size()
        self.assertEqual((width, height), (150, 200))

    def test_rotate_multiple_of_360(self):
        rotated_image = self.image.rotate(720)
        width, height = rotated_image.get_size()
        self.assertEqual((width, height), (200, 150))

    def test_set_background_color_rgb(self):
        red_background_image = self.image.set_background_color_rgb((255, 0, 0))
        self.assertFalse(red_background_image.has_alpha())
        self.assertEqual(red_background_image.image.getpixel((10, 10)), (255, 0, 0))

    def test_set_background_color_rgb_color_argument_check(self):
        with self.assertRaises(TypeError) as e:
            self.image.set_background_color_rgb("rgb(255, 0, 0)")

        self.assertEqual(
            str(e.exception), "the 'color' argument must be a 3-element tuple or list"
        )

    def test_transform_colorspace_to_srgb_noop(self):
        with open("tests/images/flower.jpg", "rb") as f:
            image = PillowImage.open(JPEGImageFile(f))

        transformed_image = image.transform_colorspace_to_srgb()

        # Statistics about color values should be the same - it should be a no-op after all
        stat = ImageStat.Stat(image.image)
        stat_transformed = ImageStat.Stat(transformed_image.image)
        self.assertEqual(stat.sum, stat_transformed.sum)

        self.assertEqual(transformed_image.image.mode, "RGB")

    def test_transform_colorspace_to_srgb_preserve_transparency(self):
        with open("tests/images/transparent_with_icc_profile.png", "rb") as f:
            image = PillowImage.open(PNGImageFile(f))

        # The sample image is in RGBA mode, it contains transparent pixels
        self.assertEqual(image.image.mode, "RGBA")

        transformed_image = image.transform_colorspace_to_srgb()
        # Image remains in RGBA mode
        self.assertEqual(transformed_image.image.mode, "RGBA")

        # Check that the alpha of pixel 1,1 is 0
        self.assertEqual(transformed_image.image.convert("RGBA").getpixel((1, 1))[3], 0)

    def test_transform_colorspace_to_srgb(self):
        with open("tests/images/dog_and_lake_cmyk_with_icc_profile.jpg", "rb") as f:
            image = PillowImage.open(JPEGImageFile(f))

        # The sample image should originally be in CMYK mode
        self.assertEqual(image.image.mode, "CMYK")
        self.assertIsNotNone(image.get_icc_profile())
        cms_profile = ImageCms.ImageCmsProfile(io.BytesIO(image.get_icc_profile()))

        # The original embedded profile should be called "ISO Coated v2 (built-in)"
        self.assertEqual(
            cms_profile.profile.profile_description, "ISO Coated v2 (built-in)"
        )

        image_srgb = image.transform_colorspace_to_srgb()

        # The image should now be in RGB mode as a result of the operation
        self.assertEqual(image_srgb.image.mode, "RGB")

        # We verify the result by comparing the sum of all color values in the image
        stat = ImageStat.Stat(image_srgb.image)
        expected_sum = [8617671.0, 8074576.0, 6869829.0]

        for actual, expected in zip(stat.sum, expected_sum):
            self.assertEqual(
                actual,
                expected,
                msg="The colors in the transformed image don't match with expectations. Did the sample image change or is there a bug?",
            )

        # The image should now have a embedded sRGB profile
        self.assertIsNotNone(image_srgb.get_icc_profile())
        cms_profile = ImageCms.ImageCmsProfile(io.BytesIO(image_srgb.get_icc_profile()))
        self.assertEqual(cms_profile.profile.profile_description, "sRGB built-in")

    def test_save_as_jpeg(self):
        # Remove alpha channel from image
        image = self.image.set_background_color_rgb((255, 255, 255))

        output = io.BytesIO()
        return_value = image.save_as_jpeg(output)
        output.seek(0)

        self.assertEqual(filetype.guess_extension(output), "jpg")
        self.assertIsInstance(return_value, JPEGImageFile)
        self.assertEqual(return_value.f, output)

    def test_save_as_jpeg_optimised(self):
        # Remove alpha channel from image
        image = self.image.set_background_color_rgb((255, 255, 255))

        unoptimised = image.save_as_jpeg(io.BytesIO())
        optimised = image.save_as_jpeg(io.BytesIO(), optimize=True)

        # Optimised image must be smaller than unoptimised image
        self.assertTrue(optimised.f.tell() < unoptimised.f.tell())

    def test_save_as_jpeg_progressive(self):
        # Remove alpha channel from image
        image = self.image.set_background_color_rgb((255, 255, 255))

        image = image.save_as_jpeg(io.BytesIO(), progressive=True)

        self.assertTrue(PILImage.open(image.f).info["progressive"])

    def test_save_as_jpeg_with_icc_profile(self):
        # Testing two different color profiles two cover the standard case and a special one as well
        images = ["colorchecker_sRGB.jpg", "colorchecker_ECI_RGB_v2.jpg"]
        for img_name in images:
            with open(f"tests/images/{img_name}", "rb") as f:
                image = PillowImage.open(JPEGImageFile(f))
                icc_profile = PILImage.open(f).info.get("icc_profile")
                self.assertIsNotNone(icc_profile)

                saved = image.save_as_jpeg(io.BytesIO())
                saved_icc_profile = PILImage.open(saved.f).info.get("icc_profile")
                self.assertEqual(saved_icc_profile, icc_profile)

    def test_save_as_jpeg_with_exif(self):
        with open("tests/images/colorchecker_sRGB.jpg", "rb") as f:
            image = PillowImage.open(JPEGImageFile(f))
            exif = PILImage.open(f).info.get("exif")
            self.assertIsNotNone(exif)

        saved = image.save_as_jpeg(io.BytesIO())
        saved_exif = PILImage.open(saved.f).info.get("exif")
        self.assertEqual(saved_exif, exif)

    def test_save_as_png(self):
        output = io.BytesIO()
        return_value = self.image.save_as_png(output)
        output.seek(0)

        self.assertEqual(filetype.guess_extension(output), "png")
        self.assertIsInstance(return_value, PNGImageFile)
        self.assertEqual(return_value.f, output)

    def test_save_as_png_32bits_to_16bits(self):
        """This tests checks that behavior from Pillow 11.2 and older is preserved for backwards compatibility."""
        output = io.BytesIO()
        image = PillowImage(_PIL_Image().new("I", (1, 1)))  # A 32-bit image

        return_value = image.save_as_png(output)
        output.seek(0)

        self.assertEqual(filetype.guess_extension(output), "png")
        self.assertIsInstance(return_value, PNGImageFile)
        self.assertEqual(return_value.f, output)

        # Check that the image was saved in 16-bit mode
        pillow_image = _PIL_Image().open(output)
        self.assertEqual(pillow_image.mode, "I;16")

    def test_save_as_png_optimised(self):
        unoptimised = self.image.save_as_png(io.BytesIO())
        optimised = self.image.save_as_png(io.BytesIO(), optimize=True)

        # Optimised image must be smaller than unoptimised image
        self.assertTrue(optimised.f.tell() < unoptimised.f.tell())

    def test_save_mode_cmyk_as_png(self):
        output = io.BytesIO()

        with open("tests/images/cmyk.jpg", "rb") as f:
            image = PillowImage.open(JPEGImageFile(f))

        return_value = image.save_as_png(output)
        output.seek(0)

        image = _PIL_Image().open(output)
        self.assertEqual(image.mode, "RGB")
        self.assertEqual(filetype.guess_extension(output), "png")
        self.assertIsInstance(return_value, PNGImageFile)
        self.assertEqual(return_value.f, output)

    def test_save_as_png_with_icc_profile(self):
        # Testing two different color profiles two cover the standard case and a special one as well
        images = ["colorchecker_sRGB.jpg", "colorchecker_ECI_RGB_v2.jpg"]
        for img_name in images:
            with open(f"tests/images/{img_name}", "rb") as f:
                original = PillowImage.open(JPEGImageFile(f))
                icc_profile = PILImage.open(f).info.get("icc_profile")
                self.assertIsNotNone(icc_profile)

                saved = original.save_as_png(io.BytesIO())
                saved_icc_profile = PILImage.open(saved.f).info.get("icc_profile")
                self.assertEqual(saved_icc_profile, icc_profile)

    def test_save_as_png_with_exif(self):
        with open("tests/images/colorchecker_sRGB.jpg", "rb") as f:
            original = PillowImage.open(JPEGImageFile(f))
            exif = PILImage.open(f).info.get("exif")
            self.assertIsNotNone(exif)

        saved = original.save_as_png(io.BytesIO())
        saved_exif = PILImage.open(saved.f).info.get("exif")
        self.assertEqual(saved_exif, exif)

    def test_save_as_gif(self):
        output = io.BytesIO()
        return_value = self.image.save_as_gif(output)
        output.seek(0)

        self.assertEqual(filetype.guess_extension(output), "gif")
        self.assertIsInstance(return_value, GIFImageFile)
        self.assertEqual(return_value.f, output)

    def test_save_as_gif_converts_back_to_supported_mode(self):
        output = io.BytesIO()

        with open("tests/images/transparent.gif", "rb") as f:
            image = PillowImage.open(GIFImageFile(f))
            image.image = image.image.convert("RGB")

        image.save_as_gif(output)
        output.seek(0)

        image = _PIL_Image().open(output)
        self.assertEqual(image.mode, "P")

    def test_has_alpha(self):
        has_alpha = self.image.has_alpha()
        self.assertTrue(has_alpha)

    def test_has_animation(self):
        has_animation = self.image.has_animation()
        self.assertFalse(has_animation)

    def test_transparent_gif(self):
        with open("tests/images/transparent.gif", "rb") as f:
            image = PillowImage.open(GIFImageFile(f))

        self.assertTrue(image.has_alpha())
        self.assertFalse(image.has_animation())

        # Check that the alpha of pixel 1,1 is 0
        self.assertEqual(image.image.convert("RGBA").getpixel((1, 1))[3], 0)

    def test_resize_transparent_gif(self):
        with open("tests/images/transparent.gif", "rb") as f:
            image = PillowImage.open(GIFImageFile(f))

        resized_image = image.resize((100, 75))

        self.assertTrue(resized_image.has_alpha())
        self.assertFalse(resized_image.has_animation())

        # Check that the alpha of pixel 1,1 is 0
        self.assertEqual(resized_image.image.convert("RGBA").getpixel((1, 1))[3], 0)

    def test_save_transparent_gif(self):
        with open("tests/images/transparent.gif", "rb") as f:
            image = PillowImage.open(GIFImageFile(f))

        # Save it into memory
        f = io.BytesIO()
        image.save_as_gif(f)

        # Reload it
        f.seek(0)
        image = PillowImage.open(GIFImageFile(f))

        self.assertTrue(image.has_alpha())
        self.assertFalse(image.has_animation())

        # Check that the alpha of pixel 1,1 is 0
        self.assertEqual(image.image.convert("RGBA").getpixel((1, 1))[3], 0)

    @unittest.expectedFailure  # Pillow doesn't support animation
    def test_animated_gif(self):
        with open("tests/images/newtons_cradle.gif", "rb") as f:
            image = PillowImage.open(GIFImageFile(f))

        self.assertFalse(image.has_alpha())
        self.assertTrue(image.has_animation())

    @unittest.expectedFailure  # Pillow doesn't support animation
    def test_resize_animated_gif(self):
        with open("tests/images/newtons_cradle.gif", "rb") as f:
            image = PillowImage.open(GIFImageFile(f))

        resized_image = image.resize((100, 75))

        self.assertFalse(resized_image.has_alpha())
        self.assertTrue(resized_image.has_animation())

    def test_get_pillow_image(self):
        pillow_image = self.image.get_pillow_image()

        self.assertIsInstance(pillow_image, _PIL_Image().Image)

    @unittest.skipIf(no_webp_support, "Pillow does not have WebP support")
    def test_save_as_webp(self):
        output = io.BytesIO()
        return_value = self.image.save_as_webp(output)
        output.seek(0)

        self.assertEqual(filetype.guess_extension(output), "webp")
        self.assertIsInstance(return_value, WebPImageFile)
        self.assertEqual(return_value.f, output)

    @unittest.skipIf(no_webp_support, "Pillow does not have WebP support")
    def test_open_webp(self):
        with open("tests/images/tree.webp", "rb") as f:
            image = PillowImage.open(WebPImageFile(f))

        self.assertFalse(image.has_alpha())
        self.assertFalse(image.has_animation())

    @unittest.skipIf(no_webp_support, "Pillow does not have WebP support")
    def test_open_webp_w_alpha(self):
        with open("tests/images/tux_w_alpha.webp", "rb") as f:
            image = PillowImage.open(WebPImageFile(f))

        self.assertTrue(image.has_alpha())
        self.assertFalse(image.has_animation())

    @unittest.skipIf(no_webp_support, "Pillow does not have WebP support")
    def test_save_webp_quality(self):
        high_quality = self.image.save_as_webp(io.BytesIO(), quality=90)
        low_quality = self.image.save_as_webp(io.BytesIO(), quality=30)
        self.assertLess(
            low_quality.f.tell(),
            high_quality.f.tell(),
            "Low quality WebP should be smaller than high quality WebP.",
        )

    @unittest.skipIf(no_webp_support, "Pillow does not have WebP support")
    def test_save_webp_lossless(self):
        original_image = self.image.image

        lossless_file = self.image.save_as_webp(io.BytesIO(), lossless=True)
        lossless_image = PillowImage.open(lossless_file).image

        diff = ImageChops.difference(original_image, lossless_image)
        self.assertIsNone(diff.getbbox())

    @unittest.skipIf(no_webp_support, "Pillow does not have WebP support")
    def test_save_as_webp_with_icc_profile(self):
        # Testing two different color profiles two cover the standard case and a special one as well
        images = ["colorchecker_sRGB.jpg", "colorchecker_ECI_RGB_v2.jpg"]
        for img_name in images:
            with open(f"tests/images/{img_name}", "rb") as f:
                image = PillowImage.open(JPEGImageFile(f))
                icc_profile = PILImage.open(f).info.get("icc_profile")
                self.assertIsNotNone(icc_profile)

                saved = image.save_as_webp(io.BytesIO())
                saved_icc_profile = PILImage.open(saved.f).info.get("icc_profile")
                self.assertEqual(saved_icc_profile, icc_profile)

    @unittest.skipIf(no_avif_support, "Pillow does not have AVIF support")
    def test_save_as_avif(self):
        output = io.BytesIO()
        return_value = self.image.save_as_avif(output)
        output.seek(0)

        self.assertEqual(filetype.guess_extension(output), "avif")
        self.assertIsInstance(return_value, AvifImageFile)
        self.assertEqual(return_value.f, output)

    @unittest.skipIf(no_avif_support, "Pillow does not have AVIF support")
    def test_save_as_avif_with_icc_profile(self):
        # Testing two different color profiles two cover the standard case and a special one as well
        images = ["colorchecker_sRGB.jpg", "colorchecker_ECI_RGB_v2.jpg"]
        for img_name in images:
            with open(f"tests/images/{img_name}", "rb") as f:
                image = PillowImage.open(JPEGImageFile(f))
                icc_profile = PILImage.open(f).info.get("icc_profile")
                self.assertIsNotNone(icc_profile)

                saved = image.save_as_avif(io.BytesIO())
                saved_icc_profile = PILImage.open(saved.f).info.get("icc_profile")
                self.assertEqual(saved_icc_profile, icc_profile)

    @unittest.skipIf(no_avif_support, "Pillow does not have AVIF support")
    def test_open_avif(self):
        with open("tests/images/tree.webp", "rb") as f:
            image = PillowImage.open(AvifImageFile(f))

        self.assertFalse(image.has_alpha())
        self.assertFalse(image.has_animation())

    @unittest.skipIf(no_avif_support, "Pillow does not have AVIF support")
    def test_save_avif_quality(self):
        high_quality = self.image.save_as_avif(io.BytesIO(), quality=90)
        low_quality = self.image.save_as_avif(io.BytesIO(), quality=30)
        self.assertTrue(low_quality.f.tell() < high_quality.f.tell())

    @unittest.skipIf(no_avif_support, "Pillow does not have AVIF support")
    def test_save_avif_lossless(self):
        original_image = self.image.image

        lossless_file = self.image.save_as_avif(io.BytesIO(), lossless=True)
        lossless_image = PillowImage.open(lossless_file).image

        diff = ImageChops.difference(original_image, lossless_image)
        self.assertIsNone(diff.getbbox())

    def test_save_ico(self):
        output = io.BytesIO()
        return_value = self.image.save_as_ico(output)
        output.seek(0)

        self.assertEqual(filetype.guess_extension(output), "ico")
        self.assertIsInstance(return_value, IcoImageFile)
        self.assertEqual(return_value.f, output)

    def test_open_ico(self):
        with open("tests/images/wagtail.ico", "rb") as f:
            image = PillowImage.open(IcoImageFile(f))

        self.assertTrue(image.has_alpha())
        self.assertFalse(image.has_animation())


class TestPillowImageWithOptimizers(unittest.TestCase):
    def setUp(self):
        with mock.patch.dict(os.environ, {"WILLOW_OPTIMIZERS": "true"}):
            registry.register_optimizer(Cwebp)
            registry.register_optimizer(Gifsicle)
            registry.register_optimizer(Jpegoptim)
            registry.register_optimizer(Optipng)
            registry.register_optimizer(Pngquant)

    def tearDown(self):
        # reset the registry as we get the global state
        registry._registered_optimizers = []

    @unittest.skipIf(not Jpegoptim.check_library(), "jpegoptim not installed")
    def test_save_as_jpeg(self):
        with open("tests/images/flower.jpg", "rb") as f:
            original_size = os.fstat(f.fileno()).st_size
            image = PillowImage.open(JPEGImageFile(f))

        return_value = image.save_as_jpeg(io.BytesIO())
        self.assertTrue(original_size > return_value.f.seek(0, io.SEEK_END))

        with mock.patch("willow.plugins.pillow.PillowImage.optimize") as mock_optimize:
            image.save_as_jpeg(io.BytesIO(), apply_optimizers=False)
            mock_optimize.assert_not_called()

    @unittest.skipIf(
        not (Pngquant.check_library() and Optipng.check_library()),
        "optipng or pngquant not installed",
    )
    def test_save_as_png(self):
        with open("tests/images/transparent.png", "rb") as f:
            original_size = os.fstat(f.fileno()).st_size
            image = PillowImage.open(PNGImageFile(f))

        return_value = image.save_as_png(io.BytesIO())
        self.assertTrue(original_size > return_value.f.seek(0, io.SEEK_END))

        with mock.patch("willow.plugins.pillow.PillowImage.optimize") as mock_optimize:
            image.save_as_png(io.BytesIO(), apply_optimizers=False)
            mock_optimize.assert_not_called()

    @unittest.skipIf(not Gifsicle.check_library(), "gifsicle not installed")
    def test_save_as_gif(self):
        with open("tests/images/transparent.gif", "rb") as f:
            original_size = os.fstat(f.fileno()).st_size
            image = PillowImage.open(GIFImageFile(f))

        return_value = image.save_as_gif(io.BytesIO())
        self.assertTrue(original_size < return_value.f.seek(0, io.SEEK_END))

        with mock.patch("willow.plugins.pillow.PillowImage.optimize") as mock_optimize:
            image.save_as_gif(io.BytesIO(), apply_optimizers=False)
            mock_optimize.assert_not_called()

    @unittest.skipIf(
        no_webp_support or not Cwebp.check_library(),
        "webp not supported or cwebp not installed",
    )
    def test_save_as_webp(self):
        with open("tests/images/tree.webp", "rb") as f:
            original_size = os.fstat(f.fileno()).st_size
            image = PillowImage.open(WebPImageFile(f))

        return_value = image.save_as_gif(io.BytesIO())
        self.assertTrue(original_size < return_value.f.seek(0, io.SEEK_END))

        with mock.patch("willow.plugins.pillow.PillowImage.optimize") as mock_optimize:
            image.save_as_webp(io.BytesIO(), apply_optimizers=False)
            mock_optimize.assert_not_called()


class TestPillowCMYKImageAutomaticSRGBTransformOnSave(unittest.TestCase):
    """Test that CMYK images with a color profile are converted to sRGB when saved as anything other than JPEG."""

    EXPECTED_PROFILE_DESCRIPTION = "sRGB built-in"

    def setUp(self):
        with open("tests/images/dog_and_lake_cmyk_with_icc_profile.jpg", "rb") as f:
            self.image = PillowImage.open(JPEGImageFile(f))

            self.assertEqual(self.image.image.mode, "CMYK")

    def test_save_as_jpeg(self):
        output = io.BytesIO()
        self.image.transform_colorspace_to_srgb = mock.Mock(
            wraps=self.image.transform_colorspace_to_srgb
        )
        return_value = self.image.save_as_jpeg(output)

        image = PillowImage.open(return_value)

        # JPEG is special. It is the only format that Pillow supports saving in CMYK mode.
        # Thus we don't need to convert the image to sRGB.
        self.assertEqual(image.image.mode, "CMYK")
        self.image.transform_colorspace_to_srgb.assert_not_called()

        # The JPEG should have the original ICC profile embedded
        self.assertEqual(image.get_icc_profile(), self.image.get_icc_profile())

    @unittest.skipIf(no_webp_support, "Pillow does not have WebP support")
    def test_save_as_webp(self):
        self.image.transform_colorspace_to_srgb = mock.Mock(
            wraps=self.image.transform_colorspace_to_srgb
        )
        return_value = self.image.save_as_webp(io.BytesIO())

        image = PillowImage.open(return_value)
        self.image.transform_colorspace_to_srgb.assert_called_once()
        self.assertEqual(image.image.mode, "RGB")

        # The expected ICC profile should be embedded
        cms_profile = ImageCms.ImageCmsProfile(io.BytesIO(image.get_icc_profile()))
        self.assertEqual(
            cms_profile.profile.profile_description, self.EXPECTED_PROFILE_DESCRIPTION
        )

    @unittest.skipIf(no_avif_support, "Pillow does not have AVIF support")
    def test_save_as_avif(self):
        self.image.transform_colorspace_to_srgb = mock.Mock(
            wraps=self.image.transform_colorspace_to_srgb
        )
        return_value = self.image.save_as_avif(io.BytesIO())

        image = PillowImage.open(return_value)

        self.image.transform_colorspace_to_srgb.assert_called_once()
        self.assertEqual(image.image.mode, "RGB")

        # The expected ICC profile should be embedded
        cms_profile = ImageCms.ImageCmsProfile(io.BytesIO(image.get_icc_profile()))
        self.assertEqual(
            cms_profile.profile.profile_description, self.EXPECTED_PROFILE_DESCRIPTION
        )

    @unittest.skipIf(no_heif_support, "Pillow does not have HEIC support")
    def test_save_as_heic(self):
        self.image.transform_colorspace_to_srgb = mock.Mock(
            wraps=self.image.transform_colorspace_to_srgb
        )
        return_value = self.image.save_as_heic(io.BytesIO())

        image = PillowImage.open(return_value)

        self.image.transform_colorspace_to_srgb.assert_called_once()
        self.assertEqual(image.image.mode, "RGB")

        # The expected ICC profile should be embedded
        cms_profile = ImageCms.ImageCmsProfile(io.BytesIO(image.get_icc_profile()))
        self.assertEqual(
            cms_profile.profile.profile_description, self.EXPECTED_PROFILE_DESCRIPTION
        )

    def test_save_as_png(self):
        self.image.transform_colorspace_to_srgb = mock.Mock(
            wraps=self.image.transform_colorspace_to_srgb
        )
        return_value = self.image.save_as_png(io.BytesIO())
        image = PillowImage.open(return_value)

        self.image.transform_colorspace_to_srgb.assert_called_once()
        self.assertEqual(image.image.mode, "RGB")

        # The expected ICC profile should be embedded
        cms_profile = ImageCms.ImageCmsProfile(io.BytesIO(image.get_icc_profile()))
        self.assertEqual(
            cms_profile.profile.profile_description, self.EXPECTED_PROFILE_DESCRIPTION
        )


class TestPillowImageOrientation(unittest.TestCase):
    def assert_orientation_landscape_image_is_correct(self, image):
        # Check that the image is the correct size (and not rotated)
        self.assertEqual(image.get_size(), (600, 450))

        # Check that the red flower is in the bottom left
        # The JPEGs have compressed slightly differently so the colours won't be spot on
        colour = image.image.convert("RGB").getpixel((155, 282))
        self.assertAlmostEqual(colour[0], 217, delta=25)
        self.assertAlmostEqual(colour[1], 38, delta=25)
        self.assertAlmostEqual(colour[2], 46, delta=25)

        # Check that the water is at the bottom
        colour = image.image.convert("RGB").getpixel((377, 434))
        self.assertAlmostEqual(colour[0], 85, delta=25)
        self.assertAlmostEqual(colour[1], 93, delta=25)
        self.assertAlmostEqual(colour[2], 65, delta=25)

    def assert_exif_orientation_equals_value(self, image, value):
        exif = image.image.getexif()
        self.assertIsNotNone(exif)
        self.assertEqual(exif.get(0x0112, 1), value)  # 0x0112 = Orientation

    def test_jpeg_with_orientation_1(self):
        with open("tests/images/orientation/landscape_1.jpg", "rb") as f:
            image = PillowImage.open(JPEGImageFile(f))
            self.assert_exif_orientation_equals_value(image, 1)

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)
        self.assert_exif_orientation_equals_value(image, 1)

    def test_jpeg_with_orientation_2(self):
        with open("tests/images/orientation/landscape_2.jpg", "rb") as f:
            image = PillowImage.open(JPEGImageFile(f))
            self.assert_exif_orientation_equals_value(image, 2)

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)
        self.assert_exif_orientation_equals_value(image, 1)

    def test_jpeg_with_orientation_3(self):
        with open("tests/images/orientation/landscape_3.jpg", "rb") as f:
            image = PillowImage.open(JPEGImageFile(f))
            self.assert_exif_orientation_equals_value(image, 3)

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)
        self.assert_exif_orientation_equals_value(image, 1)

    def test_jpeg_with_orientation_4(self):
        with open("tests/images/orientation/landscape_4.jpg", "rb") as f:
            image = PillowImage.open(JPEGImageFile(f))
            self.assert_exif_orientation_equals_value(image, 4)

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)
        self.assert_exif_orientation_equals_value(image, 1)

    def test_jpeg_with_orientation_5(self):
        with open("tests/images/orientation/landscape_5.jpg", "rb") as f:
            image = PillowImage.open(JPEGImageFile(f))
            self.assert_exif_orientation_equals_value(image, 5)

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)
        self.assert_exif_orientation_equals_value(image, 1)

    def test_jpeg_with_orientation_6(self):
        with open("tests/images/orientation/landscape_6.jpg", "rb") as f:
            image = PillowImage.open(JPEGImageFile(f))
            self.assert_exif_orientation_equals_value(image, 6)

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)
        self.assert_exif_orientation_equals_value(image, 1)

    def test_jpeg_with_orientation_7(self):
        with open("tests/images/orientation/landscape_7.jpg", "rb") as f:
            image = PillowImage.open(JPEGImageFile(f))
            self.assert_exif_orientation_equals_value(image, 7)

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)
        self.assert_exif_orientation_equals_value(image, 1)

    def test_jpeg_with_orientation_8(self):
        with open("tests/images/orientation/landscape_8.jpg", "rb") as f:
            image = PillowImage.open(JPEGImageFile(f))
            self.assert_exif_orientation_equals_value(image, 8)

        image = image.auto_orient()

        self.assert_orientation_landscape_image_is_correct(image)
        self.assert_exif_orientation_equals_value(image, 1)
