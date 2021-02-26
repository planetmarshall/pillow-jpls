from PIL.ImageFile import ImageFile

from . import _pycharls
from ._pycharls import SpiffColorSpace


def accept(header):
    magic_number = header[:4]
    spiff_header = b"\xff\xd8\xff\xe8"
    jpeg_header = b"\xff\xd8\xff\xf7"
    return magic_number == spiff_header or magic_number == jpeg_header


def _mode(num_components, bits_per_component):
    if bits_per_component > 8:
        bits_per_component = 16

    mode_table = {
        (1, 1): "1",
        (3, 8): "RGB",
        (4, 8): "RGBA",
        (1, 8): "L",
        (1, 16): "I;16"
    }
    return mode_table.get((num_components, bits_per_component))


def _metadata(header):
    meta = {
        "bits_per_sample": header.bits_per_sample,
        "component_count": header.component_count,
        "width": header.width,
        "height": header.height
    }
    if hasattr(header, "profile_id"):
        meta.update({
            "color_space": header.color_space,
            "profile_id": header.profile_id,
            "compression_type": header.compression_type,
            "resolution_units": header.resolution_units,
            "vertical_resolution": header.vertical_resolution,
            "horizontal_resolution": header.horizontal_resolution
        })
    return meta


class JplsImageFile(ImageFile):
    format = "JPEG-LS"
    format_description = "Lossless and near-lossless compression of continuous-tone still images"

    def _open(self):
        max_header_bytes = 128
        buffer = self.fp.read(max_header_bytes)
        header = _pycharls.read_header(buffer)
        mode = _mode(header.component_count, header.bits_per_sample)
        if mode is None:
            raise IOError(f"Mode not supported: components: {header.component_count}, bits: {header.bits_per_sample}")

        meta = _metadata(header)
        color_space = meta.get("color_space")
        if color_space in [SpiffColorSpace.BiLevelBlack, SpiffColorSpace.BiLevelWhite]:
            mode = "1"
        elif color_space == SpiffColorSpace.CieLab:
            mode = "LAB"
        elif color_space == SpiffColorSpace.Cmyk:
            mode = "CMYK"
        elif color_space in [SpiffColorSpace.YCbCrItuBt601Video,
                             SpiffColorSpace.YCbCrItuBt601Rgb,
                             SpiffColorSpace.YCbCrItuBt709Video]:
            mode = "YCbCr"

        self.info.update(_metadata(header))
        self._size = (header.width, header.height)
        self.mode = mode
        self.tile = [("jpeg_ls", (0, 0) + self.size, 0, (meta, ))]
