<img alt="MULTIPLY" align="right" src="https://raw.githubusercontent.com/multiply-org/sar-pre-processing/master/docs/images/multiply_multi_colour.png" />

# SenSARP

[![Build Status](https://www.travis-ci.com/multiply-org/sar-pre-processing.svg?branch=master)](https://travis-ci.com/McWhity/sar-pre-processing)
[![Documentation Status](https://readthedocs.org/projects/multiply-sar-pre-processing/badge/?version=master)](https://multiply-sar-pre-processing.readthedocs.io/en/master/?badge=master)

This repository contains the functionality SenSARP used within the MULTIPLY main platform.
The [SenSARP specific documentation](https://multiply-sar-pre-processing.readthedocs.io/en/master/) is hosted on ReadTheDocs. It is part of the [MULTIPLY core documentation](http://multiply.readthedocs.io/).
Please find the pdf version of the SenSARP documentation [here](https://multiply-sar-pre-processing.readthedocs.io/_/downloads/en/master/pdf/) and for the MULTIPLY platform [here](https://readthedocs.org/projects/multiply/downloads/pdf/latest/).
SenSARP is a pipeline to pre-process Sentinel-1 SLC data by using ESA SNAP Sentinel-1 Toolbox.

## Statement of need

Sentinel-1 satellites will provide continuous free available microwave remote sensing data of the entire globe at least until the end of 2030.
Furthermore, ESA is not only providing Sentinel satellite images (e.g. Sentinel-1, Sentinel-2, Sentinel-3) but they also developed free open source toolboxes (Sentinel-1, 2, 3 toolboxes) for scientific exploitation.
The toolboxes can be accessed and used via the Sentinel Application Platform (SNAP).
SNAP offers a graphical interface were expert users can develop different processing schemes and apply them on the satellite images.
Although, Sentinel-1 satellite data and a processing software are freely available, the usage of the data is mainly limited to expert users in the field of microwave remote sensing as different pre-processing steps need to be applied before using Sentinel-1 images.

SenSARP was developed to provide a push-button option to easily apply a rigid pre-processing pipeline with sensible defaults to a Sentinel-1 Level 1 SLC time series data as well as single Sentinel-1 Level 1 SLC images.
Thus, non-expert users in the field of pre-processing microwave data are able to use radiometric and geometric corrected sigma nought backscatter data for their specific applications.
Beside a rigid pre-processing pipeline, SenSARP provides filter options to retrieve only images of a specific year or images that contain a specific area of interest from a stack of downloaded Sentinel-1 data.
Furthermore, the default processing scheme of SenSARP can handle if an area of interest is contained in two tiles of the same swath (due to storage reasons data of one Sentinel-1 satellite swath is provided by ESA within different tiles).
Additionally, SenSARP checks if within a stack of Sentinel-1 images, one specific image was multiple processed by ESA and uses the newest.

For expert users, SenSARP provides the possibility to automate their pre-processing on a large scale by either modifying the default pre-processing scheme (modification of xml graph pre_processing_step1.xml) or create their own pre-processing scheme (create a new xml graph) with the graph builder of the SNAP software.
They can benefit from the filter options, the default pre-processing step 2 (co-registration of images) and the SenSARP functions to stack all processed and co-registered images within a netCDF file with additional image information e.g. satellite name, relative orbit and orbitdirection.

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
* `setup.py` - main build script, to be run with Python 3.6

## How to install

The first step is to clone the latest code and step into the check out directory::

    git clone https://github.com/multiply-org/sar-pre-processing.git
    cd sar-pre-processing

### Installation with Conda

Download and install [Anaconda](https://www.anaconda.com/products/individual) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html). Anaconda/Miniconda installation instructions can be found [Anaconda](https://conda.io/projects/conda/en/latest/user-guide/install/linux.html#install-linux-silent)

To install all required modules, use

    conda env create --prefix ./env --file environment.yml
    conda activate ./env # activate the environment

To install SenSARP into an existing Python environment, use::

    python setup.py install

To install for development, use::

    python setup.py develop

### Installation with virtualenv and python

Install system requirements

    sudo apt install python3-pip python3-tk python3-virtualenv python3-venv virtualenv

Create a virtual environment

    virtualenv -p /usr/bin/python3 env
    source env/bin/activate # activate the environment
    pip install --upgrade pip setuptools # update pip and setuptools

To install SenSARP into an existing Python environment, use::

    python setup.py install

To install for development, use::

    python setup.py develop

GDAL package needs to be installed too

    sudo apt install gdal-bin libgdal-dev

    python -m pip install pygdal=="`gdal-config --version`.*"


### Further information

Please see the [environment file](environment.yml) for a list of all installed dependencies during the installation process.
Additionally, ESA's SNAP Sentinel-1 Toolbox (Version >8.0.3) has to be installed prerequisite. The Software can be downloaded [here](http://step.esa.int/main/download/snap-download/). To install the SNAP toolbox, open a terminal window and use

    bash esa-snap_sentinel_unix_8_0.sh

SenSARP uses only functionalities of the Sentinel-1 Toolbox.
Currently, only SNAP version 8.0 can be downloaded from the website.
To update SNAP to a version >8.0.3 please start the SNAP software.
You will be asked if you want to search for update.
Please search for updates and install all updates.
After the updates are installed, you need to restart SNAP to initialize the updates correctly.
SNAP Toolbox need libgfortran for specific operations but currently libgfortran is not installed during the installation process of SNAP, therefore you might use

    sudo apt-get install gfortran

## Usage

For usage checkout the [juypter notebook](https://nbviewer.jupyter.org/github/multiply-org/sar-pre-processing/tree/master/docs/notebooks/)

## Documentation

We use [Sphinx](http://www.sphinx-doc.org/en/stable/rest.html) to generate the documentation of the MULTIPLY platform on [ReadTheDocs](https://multiply.readthedocs.io/). The SAR-Pre-Processing specific documentation is available [here](https://multiply-sar-pre-processing.readthedocs.io/en/latest/)

## Support, Contributing and testing
Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/multiply-org/sar-pre-processing/issues/new).

### Reporting bugs
If you find a bug in SenSARP, please open an new [issue](https://github.com/multiply-org/sar-pre-processing/issues/new) and tag it "bug".

### Suggesting enhancements
If you want to suggest a new feature or an improvement of a current feature, you can submit this on the [issue tracker](https://github.com/multiply-org/sar-pre-processing/issues/new) and tag it "enhancement".

### Testing

The package is currently tested for Python >= 3.6 on Unix-like systems.
To run unit tests, execute the following line from the root of the repository:

.. code:: bash

   pytest

## Authors

[Authors](AUTHORS.rst)

## License

This project is licensed under the GPLv3 License - see the [LICENSE.rst](LICENSE.rst) file for details.
