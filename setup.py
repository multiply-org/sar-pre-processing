#!/usr/bin/env python

from setuptools import setup

requirements = [
    'pytest',
    'sphinxcontrib-bibtex'
]

setup(name='multiply-sar-pre-processing',
      version='0.3',
      description='MULTIPLY SAR Pre-Processing',
      author='MULTIPLY Team',
      packages=['sar_pre_processing'],
      install_requires=requirements
)
