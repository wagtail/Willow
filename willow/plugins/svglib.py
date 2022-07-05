from io import BytesIO

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from willow.image import PNGImageFile
from willow.svg import SVGImage, SVGImageOperation


def rasterise_to_png(image):
    in_buf = BytesIO()
    image.write(in_buf)
    drawing = svg2rlg(in_buf)

    for op, args in image.operations:
        if op == SVGImageOperation.RESIZE:
            width, height = image.get_size()
            new_width, new_height = args
            sx = new_width / width
            sy = new_height / height
            drawing.scale(sx, sy)
            drawing.width = new_width
            drawing.height = new_height

    out_buf = BytesIO()
    renderPM.drawToFile(drawing, out_buf, fmt="PNG")
    out_buf.seek(0)
    return PNGImageFile(out_buf)


willow_operations = [(SVGImage, "rasterise_to_png", rasterise_to_png)]
