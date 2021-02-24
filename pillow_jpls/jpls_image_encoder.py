from PIL import Image

from . import _pycharls


_mode_table = {
    'RGB': (3, 8),
    'L': (1, 8),
    'I;16': (1, 16)
}


def modes_to_str():
    return ", ".join(_mode_table.keys())


def save(image: Image, fp, file_name):
    if image.mode not in _mode_table:
        raise SyntaxError(
            f"Image mode {image.mode} not supported. Convert to one of the supported modes: {modes_to_str()}.")

    component_count, bits_per_sample = _mode_table[image.mode]
    frame_info = _pycharls.FrameInfo()
    frame_info.width = image.width
    frame_info.height = image.height
    frame_info.component_count = component_count
    frame_info.bits_per_sample = image.encoderinfo.get("bits_per_sample", bits_per_sample)
    encoded_bytes = _pycharls.encode(image.tobytes(), frame_info, image.encoderinfo)
    fp.write(bytes(encoded_bytes))
