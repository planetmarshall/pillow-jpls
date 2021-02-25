from PIL.ImageFile import ImageFile

from . import _pycharls


def accept(header):
    magic_number = header[:4]
    spiff_header = b"\xff\xd8\xff\xe8"
    jpeg_header = b"\xff\xd8\xff\xf7"
    return magic_number == spiff_header or magic_number == jpeg_header


def _mode(num_components, bits_per_component):
    if bits_per_component > 8:
        bits_per_component = 16

    mode_table = {
        (3, 8): 'RGB',
        (1, 8): 'L',
        (1, 16): 'I;16'
    }
    return mode_table.get((num_components, bits_per_component))


def _header_attributes(header):
    attributes = {
        "bits_per_sample": header.bits_per_sample,
        "component_count": header.component_count,
        "width": header.width,
        "height": header.height
    }
    if hasattr(header, "profile_id"):
        attributes.update({
            "color_space": header.color_space,
            "profile_id": header.profile_id,
            "compression_type": header.compression_type,
            "resolution_units": header.resolution_units,
            "vertical_resolution": header.vertical_resolution,
            "horizontal_resolution": header.horizontal_resolution
        })
    return attributes


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

        self.info.update(_header_attributes(header))
        self._size = (header.width, header.height)
        self.mode = mode
        self.tile = [("jpeg_ls", (0, 0) + self.size, 0, (self.mode, 0))]
