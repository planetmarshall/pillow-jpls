import sys
from os import path
from setuptools import find_packages
import re


_semver_regex = r"""(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)"""
_project_regex = r"^project\(.*$"

try:
    from skbuild import setup
except ImportError:
    print(
        "Please update pip, you need pip 10 or greater,\n"
        " or you need to install the PEP 518 requirements in pyproject.toml yourself",
        file=sys.stderr,
    )
    raise


def _current_directory():
    return path.abspath(path.dirname(__file__))


def _long_description():
    with open(path.join(_current_directory(), 'README.md'), encoding='utf-8') as fp:
        return fp.read()


def _version():
    with open(path.join(_current_directory(), 'CMakeLists.txt'), encoding='utf-8') as fp:
        text = fp.read()
        project_line = re.search(_project_regex, text, re.MULTILINE | re.IGNORECASE)
        semver = re.search(_semver_regex, project_line.group())
        return "{major}.{minor}.{patch}".format(**semver.groupdict())


setup(
    name="pillow-jpls",
    version=_version(),
    description="A JPEG-LS plugin for the Pillow imaging library",
    author="Andrew Marshall",
    author_email="andrew@algodynamic.com",
    url="https://github.com/planetmarshall/pillow-jpls",
    license="BSD-3-Clause",
    long_description=_long_description(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    cmake_install_dir="pillow_jpls",
    install_requires=[
        "Pillow"
    ],
    python_requires=">=3.6"
)