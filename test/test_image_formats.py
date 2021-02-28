from io import BytesIO

from PIL import Image
import numpy as np
import pytest

from pillow_jpls import (
    SpiffProfileId,
    SpiffResolutionUnits,
    SpiffColorSpace,
    SpiffCompressionType
)

_rng = np.random.default_rng()


def test_bilevel_image():
    width = 300
    height = 200
    data = _rng.integers(2, size=(height, width), dtype=np.uint8)
    buffer = BytesIO()
    Image.fromarray(data * 255, mode="L").convert("1").save(buffer, format="JPEG-LS")

    buffer.seek(0)
    decoded_data = np.array(Image.open(buffer)).astype(np.uint8)

    assert np.linalg.norm(decoded_data - data, ord=np.inf) == 0


@pytest.mark.parametrize("shape, bits, maxval, dtype, mode, colorspace",[
    ((42, 23), 8, 255, np.uint8, "L", SpiffColorSpace.Grayscale),
    ((18, 6), 8, 255, np.uint8, "P", SpiffColorSpace.Grayscale),
    ((8, 7, 3), 8, 255, np.uint8, "RGB", SpiffColorSpace.Rgb),
    ((365, 7, 4), 8, 255, np.uint8, "RGBA", SpiffColorSpace.Rgb),
    ((12, 47, 3), 8, 255, np.uint8, "LAB", SpiffColorSpace.CieLab),
    ((12, 507, 4), 8, 255, np.uint8, "CMYK", SpiffColorSpace.Cmyk),
    ((19, 87, 3), 8, 255, np.uint8, "YCbCr", SpiffColorSpace.YCbCrItuBt601Video),
    ((52, 13), 16, 65535, np.uint16, "I;16", SpiffColorSpace.Grayscale),
    ((3, 4), 12, 4095, np.uint16, "I;16", SpiffColorSpace.Grayscale)
])
def test_encode_with_spiff_header(shape, bits, maxval, dtype, mode, colorspace):
    width = shape[1]
    height = shape[0]
    component_count = 1 if len(shape) == 2 else shape[-1]
    data = _rng.integers(maxval + 1, size=shape, dtype=dtype)

    buffer = BytesIO()
    Image.fromarray(data, mode).save(buffer, format="JPEG-LS", bits_per_sample=bits)

    buffer.seek(0)
    decoded_image = Image.open(buffer)
    decoded_data = np.array(decoded_image, dtype=dtype)

    expected_header = {
        "profile_id": SpiffProfileId.NotSpecified,
        "component_count": component_count,
        "width": width,
        "height": height,
        "color_space": colorspace,
        "bits_per_sample": max(bits, 2),
        "compression_type": SpiffCompressionType.JpegLs,
        "resolution_units": SpiffResolutionUnits.DotsPerInch,
        "vertical_resolution": 96,
        "horizontal_resolution": 96
    }

    assert decoded_image.info == expected_header
    assert np.linalg.norm(data.ravel() - decoded_data.ravel(), ord=np.inf) == 0
