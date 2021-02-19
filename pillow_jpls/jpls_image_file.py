from PIL.ImageFile import ImageFile


def accept(prefix):
    pass


class JplsImageFile(ImageFile):
    format = "JPEG-LS"
    def _open(self):
        pass