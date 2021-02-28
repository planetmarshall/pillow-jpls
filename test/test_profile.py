import os
from io import BytesIO

import pillow_jpls # noqa
from PIL import Image
import pytest
import numpy as np


@pytest.mark.profile
def test_roundtrip(data):
    src = Image.open(os.path.join(data, "artificial.ppm"))

    buffer = BytesIO()
    src.save(buffer, format="JPEG-LS")

    buffer.seek(0)
    dest = Image.open(buffer)

    src_data = np.array(src, dtype=np.int32)
    dest_data = np.array(dest, dtype=np.int32)

    assert np.linalg.norm(src_data.ravel() - dest_data.ravel(), ord=np.inf) == 0
