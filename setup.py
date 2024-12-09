import sys
from setuptools import setup

# Check Python version
if sys.version_info < (3, 11):
    print(
        "Warning: Your Python version is {}. This package is compatible "
        "with Python 3.7 but is recommended to be used with Python 3.11 or higher.".format(
            sys.version
        )
    )

setup()