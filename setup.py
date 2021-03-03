#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages

from __future__ import absolute_import
from __future__ import print_function

import io

from os.path import dirname
from os.path import join


__version__ = None
with open('sar_pre_processing/version.py') as f:
    exec(f.read())

def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as fh:
        return fh.read()


setup(name='multiply-sar-pre-processing',
      version=__version__,
      description='MULTIPLY SAR Pre-Processing',
      long_description=read('README.md'),
      license='GNU license',
      author='MULTIPLY Team',
      author_email='weiss.thomas@lmu.de',
      url='https://github.com/multiply-org/sar-pre-processing',
      packages=find_packages('sar_pre_processing'),
      package_dir={'': 'sar_pre_processing'},
      # packages=['sar_pre_processing', 'sar_pre_processing.default_graphs'],
      package_data={'sar_pre_processing.default_graphs': ['pre_process_step1.xml', 'pre_process_step1_border.xml',
                                                          'pre_process_step2.xml', 'pre_process_step3.xml'],
                    'sar_pre_processing': ['solve_projection_problem.sh']
    },
      include_package_data=True,
)
