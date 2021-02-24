from PIL.ImageFile import PyDecoder


from . import _pycharls

class JplsImageDecoder(PyDecoder):
    def __init__(self, mode, *args):
        super().__init__(mode, *args)
        self._pulls_fd = True # we decode the entire image in one shot

    def decode(self, buffer):
        buffer = self.fd.read()
        return -1
