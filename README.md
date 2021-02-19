JPEG-LS plugin for Python Pillow
================================

[Build status](https://github.com/planetmarshall/pillow-jpls/actions/workflows/scikit_build/badge.svg)


A plugin for the Python [Pillow](https://pillow.readthedocs.io/en/stable/) imaging library for the
JPEG-LS codec,
based on the [Charls](https://github.com/team-charls/charls) JPEG-LS implemetation. 
Python bindings implemented using [pybind11](https://pybind11.readthedocs.io/en/stable/).

Build
-----

The build is driven by [PEP 517](https://www.python.org/dev/peps/pep-0517/) 
and [Scikit Build](https://scikit-build.readthedocs.io/en/latest/). 
[cibuildwheel](https://github.com/joerick/cibuildwheel) is used to generate packages using Github Actions.

```
pip install pep517
python -m pep517.build --binary .
```

or

```
pip install .
```

References
----------

* [JPEG-LS on Wikipedia](https://en.wikipedia.org/wiki/Lossless_JPEG#JPEG-LS)
* [The ITU T.87 Specification](https://www.itu.int/rec/T-REC-T.87-199806-I/en)
