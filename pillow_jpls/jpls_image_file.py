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


class JplsImageFile(ImageFile):
    format = "JPEG-LS"
    format_description = "Lossless and near-lossless compression of continuous-tone still images"

    def _open(self):
        max_header_bytes = 32
        buffer = self.fp.read(max_header_bytes)
        header = _pycharls.read_header(buffer)
        mode = _mode(header["component_count"], header["bits_per_sample"])
        if mode is None:
            raise IOError(
                "Mode not supported: components: {component_count}, bits: {bits_per_component}".format(**header))

        self.info.update(header)
        self._size = (header["width"], header["height"])
        self.mode = mode
        self.tile = [ ("jpeg_ls", (0, 0) + self.size, 0, (self.mode, 0)) ]

