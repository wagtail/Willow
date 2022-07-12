from functools import reduce
from io import BytesIO

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from reportlab.graphics.shapes import Drawing
from willow.image import PNGImageFile
from willow.svg import SVGImage, SVGImageTransform


def crop_drawing(drawing, rect):
    # svglib/reportlab have no explicit crop operation, emulate it by
    # translating the graphic and putting it into a new container
    # (reportlab.graphics Drawing) of the required size
    left, top, right, bottom = rect

    # Translate the inner object here rather than the outer Drawing,
    # otherwise the translation won't be scaled in subsequent scale
    # operations
    group = drawing.contents[0]
    group.translate(-left, -top)
    new_container = Drawing(width=right - left, height=bottom - top)
    new_container.add(group)
    return new_container


def resize_drawing(drawing, size):
    new_width, new_height = size
    scale_x = new_width / drawing.width
    scale_y = new_height / drawing.height
    drawing.scale(scale_x, scale_y)
    drawing.width = new_width
    drawing.height = new_height
    return drawing


def transform(drawing, operation):
    op, args = operation
    if op == SVGImageTransform.CROP:
        transformer = crop_drawing
    else:
        transformer = resize_drawing
    return transformer(drawing, args)


def rasterise_to_png(image):
    in_buf = BytesIO()
    image.write(in_buf)

    drawing = svg2rlg(in_buf)
    drawing = reduce(transform, image.operations, drawing)

    out_buf = BytesIO()
    renderPM.drawToFile(drawing, out_buf, fmt="PNG")
    out_buf.seek(0)
    return PNGImageFile(out_buf)


willow_operations = [(SVGImage, "rasterise_to_png", rasterise_to_png)]
