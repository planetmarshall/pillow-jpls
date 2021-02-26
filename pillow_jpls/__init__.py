from PIL import Image
from .jpls_image_file import JplsImageFile, accept
from .jpls_image_encoder import save
from .jpls_image_decoder import JplsImageDecoder

from ._pycharls import ( # noqa
    SpiffProfileId,
    SpiffResolutionUnits,
    SpiffColorSpace,
    SpiffCompressionType
)

Image.register_open(JplsImageFile.format, JplsImageFile, accept)
Image.register_extensions(JplsImageFile.format, [".jls", ".jpls"])
Image.register_save(JplsImageFile.format, save)
Image.register_decoder("jpeg_ls", JplsImageDecoder)
Image.register_mime(JplsImageFile.format, "image/jls")
