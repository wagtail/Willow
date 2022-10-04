from io import BytesIO

from willow.image import PNGImageFile
from willow.svg import SvgImage


def rasterise_to_png(image: SvgImage) -> PNGImageFile:
    from reportlab.graphics import renderPM
    from svglib.svglib import svg2rlg

    in_buf = BytesIO()
    out_buf = BytesIO()
    image.write(in_buf)
    drawing = svg2rlg(in_buf)
    renderPM.drawToFile(drawing, out_buf, fmt="PNG")
    out_buf.seek(0)
    return PNGImageFile(out_buf)


willow_operations = [(SvgImage, "rasterise_to_png", rasterise_to_png)]
