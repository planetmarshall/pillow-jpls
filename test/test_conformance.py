from io import BytesIO
import os
from hashlib import md5

from PIL import Image
import pytest

import pillow_jpls # noqa # pylint: disable=unused-import

# Conformance tests from Annexe E of the `ITU Spec <https://www.itu.int/rec/T-REC-T.87/en>`_.

# We don't support
# Tests 7 and 8 are omitted as subsampling is not supported by CharLS (and is rarely used)


def _file_path(file_name):
    return os.path.realpath(os.path.join(os.path.dirname(__file__), "data", file_name))


def _encode_to_bytes(file_name, mode=None, **kwargs):
    src = Image.open(_file_path(file_name))
    if mode is not None:
        src = src.convert(mode)

    buffer = BytesIO()
    src.save(buffer, format="JPEG-LS", **kwargs)
    return buffer.getvalue()


def _decode_to_bytes(file_name, mode=None):
    image = Image.open(_file_path(file_name))
    if mode is not None:
        image = image.convert(mode)

    return image


def _load_encoded_data(file_name):
    with open(_file_path(file_name), "rb") as fp:
        return fp.read()


def _hash(data):
    return md5(data).hexdigest()


def test_01_compress_lossless_no_interleave():
    encoded_data = _encode_to_bytes("TEST8.png", interleave="none")
    expected_data = _load_encoded_data("T8C0E0.JLS")

    assert _hash(expected_data) == _hash(encoded_data)


def test_02_compress_lossless_line_interleave():
    encoded_data = _encode_to_bytes("TEST8.png", interleave="line")
    expected_data = _load_encoded_data("T8C1E0.JLS")

    assert _hash(expected_data) == _hash(encoded_data)


def test_03_compress_lossless_sample_interleave():
    encoded_data = _encode_to_bytes("TEST8.png")
    expected_data = _load_encoded_data("T8C2E0.JLS")

    assert _hash(expected_data) == _hash(encoded_data)


def test_04_compress_lossy_no_interleave():
    encoded_data = _encode_to_bytes("TEST8.png", near_lossless=3, interleave="none")
    expected_data = _load_encoded_data("T8C0E3.JLS")

    assert _hash(expected_data) == _hash(encoded_data)


def test_05_compress_lossy_line_interleave():
    encoded_data = _encode_to_bytes("TEST8.png", near_lossless=3, interleave="line")
    expected_data = _load_encoded_data("T8C1E3.JLS")

    assert _hash(expected_data) == _hash(encoded_data)


def test_06_compress_lossy_sample_interleave():
    encoded_data = _encode_to_bytes("TEST8.png", near_lossless=3)
    expected_data = _load_encoded_data("T8C2E3.JLS")

    assert _hash(expected_data) == _hash(encoded_data)


def test_09_compress_lossless_custom_threshold():
    encoded_data = _encode_to_bytes("TEST8BS2.png", t1=9, t2=9, t3=9, reset=31)
    expected_data = _load_encoded_data("T8NDE0.JLS")

    assert _hash(expected_data) == _hash(encoded_data)


def test_10_compress_lossy_custom_threshold():
    encoded_data = _encode_to_bytes("TEST8BS2.png", near_lossless=3, t1=9, t2=9, t3=9, reset=31)
    expected_data = _load_encoded_data("T8NDE3.JLS")

    assert _hash(expected_data) == _hash(encoded_data)


def test_11_compress_lossless_16():
    encoded_data = _encode_to_bytes("TEST16.png", mode="I;16", bits_per_sample=12)
    expected_data = _load_encoded_data("T16E0.JLS")

    assert _hash(expected_data) == _hash(encoded_data)


def test_12_compress_lossy_16():
    encoded_data = _encode_to_bytes("TEST16.png", mode="I;16", near_lossless=3, bits_per_sample=12)
    expected_data = _load_encoded_data("T16E3.JLS")

    assert _hash(expected_data) == _hash(encoded_data)


@pytest.mark.parametrize("encoded, decoded", [
    ("T8C0E0.JLS", "TEST8.png"),
    ("T8C1E0.JLS", "TEST8.png"),
    ("T8C2E0.JLS", "TEST8.png"),
    ("T8C0E3.JLS", "TEST8.png"),
    ("T8C1E3.JLS", "TEST8.png"),
    ("T8C2E3.JLS", "TEST8.png"),
    ("T8NDE0.JLS", "TEST8BS2.png"),
    ("T8NDE3.JLS", "TEST8BS2.png"),
    ("T16E0.JLS", "TEST16.png"),
    ("T16E3.JLS", "TEST16.png")])
def test_decompress(encoded, decoded):
    jls_decoded = _decode_to_bytes(encoded)
    raw_decoded = _decode_to_bytes(decoded)
    if raw_decoded.mode == "I":
        raw_decoded = raw_decoded.convert("I;16")

    assert _hash(raw_decoded) == _hash(jls_decoded)
