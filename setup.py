import sys
from setuptools import find_packages

try:
    from skbuild import setup
except ImportError:
    print(
        "Please update pip, you need pip 10 or greater,\n"
        " or you need to install the PEP 518 requirements in pyproject.toml yourself",
        file=sys.stderr,
    )
    raise

setup(
    name="pillow-jpls",
    version="0.0.1",
    description="A JPEG-LS plugin for the Pillow imaging library",
    author="Andrew Marshall",
    license="Apache-2.0",
    packages=find_packages(),
    install_requires=[
        "Pillow"
    ]
)