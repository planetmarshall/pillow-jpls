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
    author_email="andrew@algodynamic.com",
    url="https://github.com/planetmarshall/pillow-jpls",
    license="BSD-3-Clause",
    packages=find_packages(),
    cmake_install_dir="pillow_jpls",
    install_requires=[
        "Pillow"
    ],
    python_requires=">=3.6"
)