from PIL import Image

import _pycharls

_mode_table = {
    'RGB': (8, 3)
}


def save(image: Image, fp, file_name):
    if image.mode not in _mode_table:
        raise SyntaxError(f"Image mode {image.mode} not supported")

    bits_per_sample, component_count = _mode_table[image.mode]
    frame_info = _pycharls.FrameInfo()
    frame_info.width = image.width
    frame_info.height = image.height
    frame_info.component_count = component_count
    frame_info.bits_per_sample = bits_per_sample
    encoded_bytes = _pycharls.encode_from_interleaved_samples(image.tobytes(), frame_info)
    fp.write(bytes(encoded_bytes))

