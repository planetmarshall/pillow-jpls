import sys
from os import path
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

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as fp:
    long_description = fp.read()

setup(
    name="pillow-jpls",
    version="0.0.1",
    description="A JPEG-LS plugin for the Pillow imaging library",
    author="Andrew Marshall",
    author_email="andrew@algodynamic.com",
    url="https://github.com/planetmarshall/pillow-jpls",
    license="BSD-3-Clause",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    cmake_install_dir="pillow_jpls",
    install_requires=[
        "Pillow"
    ],
    python_requires=">=3.6"
)