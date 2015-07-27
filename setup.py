#!/usr/bin/env python

import re
import codecs
import os

# Prevent spurious errors during `python setup.py test`, a la
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html:
try:
    import multiprocessing
except ImportError:
    pass


from setuptools import setup


def read(*parts):
    return codecs.open(os.path.join(os.path.dirname(__file__), *parts)).read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


setup(
    name='popcoder',
    entry_points={
        'console_scripts': ['crontabber = crontabber.main:main']
    },
    version=find_version('popcoder', '__init__.py'),
    url='https://github.com/mozilla/popcoder',
    author='Mike Nolan',
    author_email='me@michael-nolan.com',
    description=(
        'Python library for transcoding popcorn code into flat video files'
    ),
    license='Mozilla Public License 2.0 (MPL 2.0)',
    long_description=read('README.rst'),
    packages=['popcoder', 'popcoder.tests'],
    include_package_data=True,
    install_requires=[],
    zip_safe=False,
    classifiers=[
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    test_suite='popcoder.tests',
    tests_require=['mock'],
)
