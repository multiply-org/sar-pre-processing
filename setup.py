#!/usr/bin/env python

from setuptools import setup

requirements = [
    'pyproj',
    'pytest',
    'sphinxcontrib-bibtex'
]

__version__ = None
with open('sar_pre_processing/version.py') as f:
    exec(f.read())

setup(name='multiply-sar-pre-processing',
      version=__version__,
      description='MULTIPLY SAR Pre-Processing',
      author='MULTIPLY Team',
      packages=['sar_pre_processing'],
      install_requires=requirements
)
