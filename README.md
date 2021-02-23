JPEG-LS plugin for Python Pillow
================================

![Build status](https://github.com/planetmarshall/pillow-jpls/actions/workflows/scikit_build.yml/badge.svg?branch=pillow-jpls)


A plugin for the Python [Pillow](https://pillow.readthedocs.io/en/stable/) imaging library for the
JPEG-LS codec,
based on the [Charls](https://github.com/team-charls/charls) JPEG-LS implemetation. 
Python bindings implemented using [pybind11](https://pybind11.readthedocs.io/en/stable/).

Usage
-----

```
pip install .
```

### With PIL
```.py
import pillow_jpls
from PIL import Image
from io import BytesIO

img = Image.open("mandrill.jls")
img.save("mandrill_copy.jls)

# Saving to a buffer
buffer = BytesIO()
img.save(buffer, "JPEG-LS")
```

### With scikit-image

[scikit-image](https://scikit-image.org/) uses PIL as one of its backends, so usage is transparent

```.py
import pillow_jpls
import skimage
import numpy as np

img = skimage.imread("mandrill.jls")
data = (np.random.rand(4, 3) * 4095).astype(np.uint16)
skimage.imsave("random.jls", plugin="pil", plugin_args={"bits_per_component": 12})
```

### Options

The encoder supports the following options. See the specification for details, and the tests for 
example usage.

* `near_lossless` : `0` is lossless - the default.
* `interleave` : one of `none`, `line` or `sample` 
* `bits_per_component` : override the number of bits encoded per component, otherwise taken from the image format
* `maxval`: override the maximum value of any component, otherwise taken from `bits_per_component`
* `t1`
* `t2`
* `t3`
* `reset`

Build
-----

The build is driven by [PEP 517](https://www.python.org/dev/peps/pep-0517/) 
and [Scikit Build](https://scikit-build.readthedocs.io/en/latest/). 
[cibuildwheel](https://github.com/joerick/cibuildwheel) is used to generate packages using Github Actions.

```
pip install pep517
python -m pep517.build --binary .
```

Tests
-----

A suite of tests covering the applicable conformance tests from the specification is provided.
You will need [git-lfs](https://git-lfs.github.com/) to clone the data.

```
pip install pytest .
pytest -v test
```


References
----------

* [JPEG-LS on Wikipedia](https://en.wikipedia.org/wiki/Lossless_JPEG#JPEG-LS)
* [The ITU T.87 Specification](https://www.itu.int/rec/T-REC-T.87-199806-I/en)
