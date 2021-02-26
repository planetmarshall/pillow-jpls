from io import BytesIO
import os

from PIL import Image
import pytest
import numpy as np

import pillow_jpls # noqa # pylint: disable=unused-import

# Conformance tests from Annexe E of the `ITU Spec <https://www.itu.int/rec/T-REC-T.87/en>`_.
# Tests 7 and 8 are omitted as subsampling is not supported by CharLS (and is rarely used)


def _encode_to_array(file_name, mode=None, **kwargs):
    src = Image.open(file_name)
    if mode is not None:
        src = src.convert(mode)

    buffer = BytesIO()
    src.save(buffer, format="JPEG-LS", spiff=None, **kwargs)
    return np.frombuffer(buffer.getvalue(), dtype=np.uint8).astype(np.int32)


def _decode_to_array(file_name, mode=None):
    image = Image.open(file_name)
    if image.mode == "I":
        image.convert("I;16")
    elif mode is not None:
        image = image.convert(mode)

    return np.array(image, dtype=np.int32)


def _load_encoded_data(file_name):
    with open(file_name, "rb") as fp:
        return np.frombuffer(fp.read(), dtype=np.uint8).astype(dtype=np.int32)


def assert_array_equal(expected: np.ndarray, actual: np.ndarray, epsilon=0):
    assert np.linalg.norm(expected.ravel() - actual.ravel(), ord=np.inf) <= epsilon


def test_01_compress_lossless_no_interleave(data):
    encoded_data = _encode_to_array(os.path.join(data, "TEST8.png"), interleave="none")
    expected_data = _load_encoded_data(os.path.join(data, "T8C0E0.JLS"))

    assert_array_equal(expected_data, encoded_data)


def test_02_compress_lossless_line_interleave(data):
    encoded_data = _encode_to_array(os.path.join(data, "TEST8.png"), interleave="line")
    expected_data = _load_encoded_data(os.path.join(data, "T8C1E0.JLS"))

    assert_array_equal(expected_data, encoded_data)


def test_03_compress_lossless_sample_interleave(data):
    encoded_data = _encode_to_array(os.path.join(data, "TEST8.png"))
    expected_data = _load_encoded_data(os.path.join(data, "T8C2E0.JLS"))

    assert_array_equal(expected_data, encoded_data)


def test_04_compress_lossy_no_interleave(data):
    encoded_data = _encode_to_array(os.path.join(data, "TEST8.png"), near_lossless=3, interleave="none")
    expected_data = _load_encoded_data(os.path.join(data, "T8C0E3.JLS"))

    assert_array_equal(expected_data, encoded_data)


def test_05_compress_lossy_line_interleave(data):
    encoded_data = _encode_to_array(os.path.join(data, "TEST8.png"), near_lossless=3, interleave="line")
    expected_data = _load_encoded_data(os.path.join(data, "T8C1E3.JLS"))

    assert_array_equal(expected_data, encoded_data)


def test_06_compress_lossy_sample_interleave(data):
    encoded_data = _encode_to_array(os.path.join(data, "TEST8.png"), near_lossless=3)
    expected_data = _load_encoded_data(os.path.join(data, "T8C2E3.JLS"))

    assert_array_equal(expected_data, encoded_data)


def test_09_compress_lossless_custom_threshold(data):
    encoded_data = _encode_to_array(os.path.join(data, "TEST8BS2.png"), t1=9, t2=9, t3=9, reset=31)
    expected_data = _load_encoded_data(os.path.join(data, "T8NDE0.JLS"))

    assert_array_equal(expected_data, encoded_data)


def test_10_compress_lossy_custom_threshold(data):
    encoded_data = _encode_to_array(os.path.join(data, "TEST8BS2.png"), near_lossless=3, t1=9, t2=9, t3=9, reset=31)
    expected_data = _load_encoded_data(os.path.join(data, "T8NDE3.JLS"))

    assert_array_equal(expected_data, encoded_data)


def test_11_compress_lossless_16(data):
    encoded_data = _encode_to_array(os.path.join(data, "TEST16.png"), mode="I;16", bits_per_sample=12)
    expected_data = _load_encoded_data(os.path.join(data, "T16E0.JLS"))

    assert_array_equal(expected_data, encoded_data)


def test_12_compress_lossy_16(data):
    encoded_data = _encode_to_array(os.path.join(data, "TEST16.png"), mode="I;16", near_lossless=3, bits_per_sample=12)
    expected_data = _load_encoded_data(os.path.join(data, "T16E3.JLS"))

    assert_array_equal(expected_data, encoded_data)


@pytest.mark.parametrize("encoded, decoded, epsilon", [
    ("T8C0E0.JLS", "TEST8.png", 0),
    ("T8C1E0.JLS", "TEST8.png", 0),
    ("T8C2E0.JLS", "TEST8.png", 0),
    ("T8C0E3.JLS", "TEST8.png", 3),
    ("T8C1E3.JLS", "TEST8.png", 3),
    ("T8C2E3.JLS", "TEST8.png", 3),
    ("T8NDE0.JLS", "TEST8BS2.png", 0),
    ("T8NDE3.JLS", "TEST8BS2.png", 3),
    ("T16E0.JLS", "TEST16.png", 0),
    ("T16E3.JLS", "TEST16.png", 3)])
def test_decompress(data, encoded, decoded, epsilon):
    jls_decoded = _decode_to_array(os.path.join(data, encoded))
    raw_decoded = _decode_to_array(os.path.join(data, decoded))

    assert_array_equal(raw_decoded, jls_decoded, epsilon=epsilon)
