from filetype.types import TYPES, Type, image

# Backport of JPEG XL support in filetype, which hasn't shipped in a release yet
# See https://github.com/h2non/filetype.py/issues/188


def _patch_filetype_with_jxl():
    """
    Patch filetype with JPEG XL support.
    """
    # TODO: Remove this patch once filetype 1.3.0 is released with JXL
    if not any(t.mime == Jxl.MIME and t.extension == Jxl.EXTENSION for t in TYPES):
        TYPES.append(Jxl())
        # Set the image.Jxl attribute to the new Jxl class so that it can be used in Willow's image format detection
        image.Jxl = Jxl


# Vendored from https://github.com/h2non/filetype.py/blob/3eae5cedad2dc65076a501a9374abafb1d700602/filetype/types/image.py#L51
class Jxl(Type):
    """
    Implements the JPEG XL image type matcher.
    """

    MIME = "image/jxl"
    EXTENSION = "jxl"

    def __init__(self):
        super().__init__(mime=Jxl.MIME, extension=Jxl.EXTENSION)

    def match(self, buf):
        return (len(buf) > 1 and buf[0] == 0xFF and buf[1] == 0x0A) or (
            len(buf) > 11
            and buf[0] == 0x00
            and buf[1] == 0x00
            and buf[2] == 0x00
            and buf[3] == 0x0C
            and buf[4] == 0x4A
            and buf[5] == 0x58
            and buf[6] == 0x4C
            and buf[7] == 0x20
            and buf[8] == 0x0D
            and buf[9] == 0x0A
            and buf[10] == 0x87
            and buf[11] == 0x0A
        )
