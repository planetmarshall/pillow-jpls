import pillow_jpls

from PIL import Image

# Conformance tests from Annexe E of the `ITU Spec <https://www.itu.int/rec/T-REC-T.87/en>`_.
# Tests 7 and 8 are omitted as subsampling is not supported by CharLS (and is rarely used)


def test_01_compress_lossless_no_interleave():
    assert 0


def test_02_compress_lossless_line_interleave():
    assert 0


def test_03_compress_lossless_sample_interleave():
    assert 0


def test_04_compress_lossy_no_interleave():
    assert 0


def test_05_compress_lossy_line_interleave():
    assert 0


def test_06_compress_lossy_sample_interleave():
    assert 0


def test_09_compress_lossless_custom_threshold():
    assert 0


def test_10_compress_lossy_custom_threshold():
    assert 0


def test_11_compress_lossless_16():
    assert 0


def test_12_compress_lossless_16():
    assert 0
