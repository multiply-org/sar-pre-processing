#!/usr/bin/env python

from setuptools import setup
import os

# removed dependencies to prevent multiple installations
requirements = [
       'netCDF4',
       'PyYAML',
       'pyproj',
       'pytest',
       'gdal==3.0.2',
       'xarray',
       'sphinxcontrib-bibtex'
]

__version__ = None
with open('sar_pre_processing/version.py') as f:
    exec(f.read())

setup(name='multiply-sar-pre-processing',
      version=__version__,
      description='MULTIPLY SAR Pre-Processing',
      author='MULTIPLY Team',
      packages=['sar_pre_processing', 'sar_pre_processing.default_graphs'],
      install_requires=requirements,
      package_data={'sar_pre_processing.default_graphs': ['pre_process_step1.xml', 'pre_process_step1_border.xml',
                                                          'pre_process_step2.xml', 'pre_process_step3.xml'],
                    'sar_pre_processing': ['solve_projection_problem.sh']
    },
      include_package_data=True,
)
