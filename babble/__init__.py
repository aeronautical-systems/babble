"""Top-level package for babble."""
import os
import site
import sys

__author__ = """Torsten Irländer"""
__email__ = "torsten.irlaender@googlemail.com"
__version__ = "0.1.0"


def get_package_root() -> str:  # pragma: no cover
    """
    returns root folder of dicop-voice package

    """
    packages = sys.path
    dir_path = [
        os.path.abspath(package) for package in packages if package.endswith("babble")
    ]
    if dir_path:
        return dir_path[0]
    else:
        packages_dir = site.getsitepackages()
        package_dir = os.path.join(packages_dir[0])
        return package_dir


PACKAGE_ROOT_DIR = get_package_root()
