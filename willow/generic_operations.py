# Generic operations are automatically registered on all image models that implement their dependencies

# Dependencies: get_size, get_frame_count
def get_pixel_count(image):
    width, height = image.get_size()
    frames = image.get_frame_count()

    return width * height * frames
