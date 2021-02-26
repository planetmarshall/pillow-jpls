from PIL.ImageFile import PyDecoder

from . import _pycharls
from ._pycharls import SpiffColorSpace


class JplsImageDecoder(PyDecoder):
    def __init__(self, mode, *args):
        super().__init__(mode, *args)
        self._pulls_fd = True  # we decode the entire image in one shot
        self.color_space = args[0].get("color_space")

    def decode(self, buffer):
        buffer = self.fd.read()
        errcode = 0
        try:
            decoded = _pycharls.decode(buffer)
            raw_mode = None
            if self.color_space in [SpiffColorSpace.BiLevelWhite, SpiffColorSpace.BiLevelBlack]:
                raw_mode = "1;8"
            self.set_as_raw(bytes(decoded), rawmode=raw_mode)
        except RuntimeError:
            errcode = -2

        return -1, errcode
