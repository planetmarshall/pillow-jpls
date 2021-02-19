from PIL import Image
from .jpls_image_file import JplsImageFile, accept

Image.register_open(JplsImageFile.format, JplsImageFile, accept)
Image.register_extensions(JplsImageFile.format, ["jls","jpls"])