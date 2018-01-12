#!/usr/bin/env python

from setuptools import setup

requirements = [
    'nose',
    'cate'
]

setup(name='multiply-sar-pre-processing',
      version='0.1',
      description='MULTIPLY SAR Pre-Processing',
      author='MULTIPLY Team',
      packages=['multiply_sar_pre_processing'],
      entry_points={
          'console_scripts': [
              'multiply2 = sar_pre_processing.sar_pre_processing_command:main'
          ],
      },
      install_requires=requirements
      )
