from io import BytesIO

from PIL import Image
import numpy as np

from pillow_jpls import (
    SpiffProfileId,
    SpiffResolutionUnits,
    SpiffColorSpace,
    SpiffCompressionType
)

_rng = np.random.default_rng()


def test_encode_with_spiff_header():
    width = 42
    height = 23
    image = _rng.integers(255, size=(height, width), dtype=np.uint8)

    buffer = BytesIO()
    Image.fromarray(image).save(buffer, format="JPEG-LS")

    buffer.seek(0)
    decoded = Image.open(buffer)

    expected_header = {
        "profile_id": SpiffProfileId.NotSpecified,
        "component_count": 1,
        "height": height,
        "width": width,
        "color_space": SpiffColorSpace.Grayscale,
        "bits_per_sample": 8,
        "compression_type": SpiffCompressionType.JpegLs,
        "resolution_units": SpiffResolutionUnits.DotsPerInch,
        "vertical_resolution": 96,
        "horizontal_resolution": 96
    }

    assert decoded.info == expected_header