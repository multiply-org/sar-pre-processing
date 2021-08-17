<img alt="MULTIPLY" align="right" src="https://raw.githubusercontent.com/multiply-org/sar-pre-processing/master/docs/images/multiply_multi_colour.png" />

# SenSARP

[![Build Status](https://www.travis-ci.com/multiply-org/sar-pre-processing.svg?branch=master)](https://travis-ci.com/McWhity/sar-pre-processing)
[![Documentation Status](https://readthedocs.org/projects/multiply-sar-pre-processing/badge/?version=master)](https://multiply-sar-pre-processing.readthedocs.io/en/master/?badge=master)

This repository contains the functionality for Sentinel-1 SAR-Pre.Processing of the MULTIPLY main platform.
The [SenSARP specific documentation](https://multiply-sar-pre-processing.readthedocs.io/en/master/) is hosted on ReadTheDocs. It is part of the [MULTIPLY core documentation](http://multiply.readthedocs.io/).
Please find the pdf version of the SenSARP documentation [here](https://multiply-sar-pre-processing.readthedocs.io/_/downloads/en/master/pdf/) and for the MULTIPLY platform [here](https://readthedocs.org/projects/multiply/downloads/pdf/latest/).

## Content of this repository

* `docs/` - The auto generated documentation
* `recipe/` Conda installation recipe
* `sar_pre_processing/` - The main sar pre processing software package
* `test/` - The test package.
* `AUTHORS.rst` - Author information.
* `CHANGES.md` - Package change log.
* `LICENSE.rst` - License of software in repository.
* `README.md` - Readme.
* `environmental.yml` - Requirements.
* `sar_pre_processing_CLI.txt` - Renaming package to SenSARP
* `setup.py` - main build script, to be run with Python 3.6

## How to install

The first step is to clone the latest code and step into the check out directory:

    $ git clone https://github.com/multiply-org/sar-pre-processing.git
    $ cd sar-pre-processing

The MULTIPLY platform has been developed against Python 3.6.
It cannot be guaranteed to work with previous Python versions.

MULTIPLY SAR-pre-processing can be run from sources directly.
To install all required modules, use

    $ conda env create --prefix ./env --file environment.yml
    $ conda activate ./env # activate the environment

To install MULTIPLY SAR-pre-processing into an existing Python environment just for the current user, use

    $ python setup.py install --user

To install for development and for the current user, use

    $ python setup.py develop --user

## Module requirements

Please see the [environment file](environment.yml) for a list of dependencies.
ESA's SNAP Sentinel-1 Toolbox has to be installed prerequisite. The Software can be downloaded [here](http://step.esa.int/main/download/snap-download/).
enSARP uses only functionalities of the Sentinel-1 Toolbox.
Currently only SNAP version 8.0 can be downloaded from the website. To update SNAP to a version >8.0.3 please start the SNAP software.
You will be asked if you want to search for update.
After the updates are installed you need to restart SNAP to initialize the installed updates.
SNAP Toolbox need libgfortran for specific operations but currently libgfortran is not installed during the installation process of SNAP (Linux version) therefore you might use

    $ sudo apt-get install gfortran

## Usage

For usage checkout the [juypter notebook](https://nbviewer.jupyter.org/github/multiply-org/sar-pre-processing/tree/master/docs/notebooks/)

## Documentation

We use [Sphinx](http://www.sphinx-doc.org/en/stable/rest.html) to generate the documentation of the MULTIPLY platform on [ReadTheDocs](https://multiply.readthedocs.io/). The SAR-Pre-Processing specific documentation is available [here](https://multiply-sar-pre-processing.readthedocs.io/en/latest/)

## Contribution and Development

You are very welcome to contribute to MULTIPLY SAR-Pre-Processing. To do so, please first make a fork into your own repository and then create a Pull Request.

### Reporting issues and feedback

If you encounter any bugs with the tool, please file a [new issue](https://github.com/multiply-org/sar-pre-processing/issues/new).

## Authors

[Authors](AUTHORS.rst)

## License

This project is licensed under the GPLv3 License - see the [LICENSE.rst](LICENSE.rst) file for details.
