from PIL.ImageFile import ImageFile


def accept(header):
    magic_number = header[:4]
    spiff_header = b"\xff\xd8\xff\xe8"
    jpeg_header = b"\xff\xd8\xff\xf7"
    return magic_number == spiff_header or magic_number == jpeg_header


class JplsImageFile(ImageFile):
    format = "JPEG-LS"
    def _open(self):
        pass