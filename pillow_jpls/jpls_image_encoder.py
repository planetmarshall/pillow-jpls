from PIL import Image

from . import _pycharls
from ._pycharls import (
    SpiffProfileId,
    SpiffCompressionType,
    SpiffColorSpace,
    SpiffResolutionUnits,
    SpiffHeader
)


_mode_table = {
    "1": (1, 8, SpiffColorSpace.BiLevelBlack),
    "L": (1, 8, SpiffColorSpace.Grayscale),
    "P": (1, 8, SpiffColorSpace.Grayscale),
    "RGB": (3, 8, SpiffColorSpace.Rgb),
    "RGBA": (4, 8, SpiffColorSpace.Rgb),
    "LAB": (3, 8, SpiffColorSpace.CieLab),
    "CMYK": (4, 8, SpiffColorSpace.Cmyk),
    "YCbCr": (3, 8, SpiffColorSpace.YCbCrItuBt601Video),
    "I;16": (1, 16, SpiffColorSpace.Grayscale),
    "RGB;16": (3, 16, SpiffColorSpace.Rgb),
}


def modes_to_str():
    return ", ".join(_mode_table.keys())


def _spiff_header(image: Image, spiff_header):
    component_count, bits_per_sample, default_color_space = _mode_table[image.mode]
    spiff = SpiffHeader()
    spiff.profile_id = spiff_header.get("profile_id", SpiffProfileId.NotSpecified)
    spiff.component_count = component_count
    spiff.height = image.height
    spiff.width = image.width
    spiff.color_space = spiff_header.get("color_space", default_color_space)
    spiff.bits_per_sample = max(bits_per_sample, 2)
    spiff.compression_type = SpiffCompressionType.JpegLs
    spiff.resolution_units = spiff_header.get("resolution_units", SpiffResolutionUnits.DotsPerInch)
    spiff.vertical_resolution = spiff_header.get("vertical_resolution", 96)
    spiff.horizontal_resolution = spiff_header.get("horizontal_resolution", 96)
    return spiff


def save(image: Image, fp, file_name):
    if image.mode not in _mode_table:
        raise SyntaxError(
            f"Image mode {image.mode} not supported. Convert to one of the supported modes: {modes_to_str()}.")

    component_count, bits_per_sample, _ = _mode_table[image.mode]
    frame_info = _pycharls.FrameInfo()
    frame_info.width = image.width
    frame_info.height = image.height
    frame_info.component_count = component_count
    frame_info.bits_per_sample = max(image.encoderinfo.get("bits_per_sample", bits_per_sample), 2)

    spiff_header = image.encoderinfo.get("spiff", {})
    header = None
    if spiff_header is not None:
        header = _spiff_header(image, spiff_header)
        header.bits_per_sample = frame_info.bits_per_sample

    image.encoderinfo["spiff"] = header
    if image.mode == "1":
        image.encoderinfo["maxval"] = 1
        # bitmap images are stored in a compressed representation if you use tobytes()
        data = bytes(image.getdata())
    else:
        data = image.tobytes()

    fp.write(_pycharls.encode(data, frame_info, **image.encoderinfo))
