# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "instrumental_agent"
VERSION = "1.0.1"


# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = []

setup(
    name=NAME,
    version=VERSION,
    description="A wrapper for the Instrumental service.",
    author="Elijah Miller",
    author_email="elijah.miller@gmail.com",
    maintainer="Instrumental Support",
    maintainer_email="support@instrumentalapp.com",
    url="https://github.com/instrumental/instrumental-python",
    keywords=["Instrumental", "API", "Metrics", "APM"],
    classifiers=[ # see https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",

        "Environment :: Web Environment",

        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",

        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
    ],
    license="",
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    A native client library for the Instrumental service.
    """
)
