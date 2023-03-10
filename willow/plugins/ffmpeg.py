import subprocess
import os.path
from itertools import product
import json
from tempfile import NamedTemporaryFile, TemporaryDirectory

from willow.image import Image

from willow.image import (
    GIFImageFile,
    WebPImageFile,
    WebMVP9ImageFile,
    OggTheoraImageFile,
    MP4H264ImageFile,
)


def probe(file):
    with NamedTemporaryFile() as src:
        src.write(file.read())
        result = subprocess.run(["ffprobe", "-show_format", "-show_streams", "-loglevel", "quiet", "-print_format", "json", src.name], capture_output=True)
        return json.loads(result.stdout)


def transcode(source_file, output_file, output_resolution, format, codec):
    with NamedTemporaryFile() as src, TemporaryDirectory() as outdir:
        src.write(source_file.read())

        args = ["ffmpeg", "-i", src.name, "-f", format, "-codec:v", codec]

        if output_resolution:
            args += ["-s", f"{output_resolution[0]}x{output_resolution[1]}"]

        args.append(os.path.join(outdir, 'out'))

        subprocess.run(args)

        with open(os.path.join(outdir, 'out'), 'rb') as out:
            output_file.write(out.read())


class FFMpegLazyVideo(Image):
    def __init__(self, source_file, output_resolution=None):
        self.source_file = source_file
        self.output_resolution = output_resolution

    @Image.operation
    def get_size(self):
        if self.output_resolution:
            return self.output_resolution

        # Find the size from the source file
        data = probe(self.source_file.f)
        for stream in data['streams']:
            if stream['codec_type'] == 'video':
                return stream['width'], stream['height']

    @Image.operation
    def get_frame_count(self):
        # Find the frame count from the source file
        data = probe(self.source_file.f)
        for stream in data['streams']:
            if stream['codec_type'] == 'video':
                return int(stream['nb_frames'])

    @Image.operation
    def has_alpha(self):
        # Alpha not supported
        return False

    @Image.operation
    def has_animation(self):
        return True

    @Image.operation
    def resize(self, size):
        return FFMpegLazyVideo(self.source_file, size)

    @Image.operation
    def crop(self, rect):
        # Not supported, but resize the image to match the crop rect size
        left, top, right, bottom = rect
        width = right - left
        height = bottom - top
        return FFMpegLazyVideo(self.source_file, (width, height))

    @Image.operation
    def rotate(self, angle):
        # Not supported
        return self

    @Image.operation
    def set_background_color_rgb(self, color):
        # Alpha not supported
        return self

    @classmethod
    @Image.converter_from(GIFImageFile)
    @Image.converter_from(WebPImageFile)
    @Image.converter_from(WebMVP9ImageFile)
    @Image.converter_from(OggTheoraImageFile)
    @Image.converter_from(MP4H264ImageFile)
    def open(cls, file):
        return cls(file)

    @Image.operation
    def save_as_webm_vp9(self, f):
        transcode(self.source_file.f, f, self.output_resolution, 'webm', 'libvpx-vp9')
        return WebMVP9ImageFile(f)

    @Image.operation
    def save_as_ogg_theora(self, f):
        transcode(self.source_file.f, f, self.output_resolution, 'ogg', 'libtheora')
        return OggTheoraImageFile(f)

    @Image.operation
    def save_as_mp4_h264(self, f):
        transcode(self.source_file.f, f, self.output_resolution, 'mp4', 'libx264')
        return MP4H264ImageFile(f)


willow_image_classes = [FFMpegLazyVideo]
