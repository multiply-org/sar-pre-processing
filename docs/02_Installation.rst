.. _Installation:

Installation
=============
.. note::
    The MULTIPLY platform has been developed against Python 3.6.
    It cannot be guaranteed to work with previous Python versions.

The first step is to clone the latest code and step into the check out directory::

    git clone https://github.com/multiply-org/sar-pre-processing.git
    cd sar-pre-processing

Via Conda
----------
Download and install Anaconda `link <https://www.anaconda.com/products/individual>`_ or Miniconda `link <https://docs.conda.io/en/latest/miniconda.html>`_. Installation instructions can be found `here <https://conda.io/projects/conda/en/latest/user-guide/install/index.html>`_

To install all required modules, use::

    conda env create --prefix ./env --file environment.yml
    conda activate ./env # activate the environment

To install SenSARP into an existing Python environment just for the current user, use::

    python setup.py install --user

To install for development and for the current user, use::

    python setup.py develop --user

Via virtualenv and python
--------------------------
Create a vitural environment

    python3 -m venv env
    source env/bin/activate

Install GDAL

    pip install GDAL==$(gdal-config --version)

To install SenSARP into an existing Python environment just for the current user, use::

    python setup.py install --user

To install for development and for the current user, use::

    python setup.py develop --user

Module requirements
-------------------

.. literalinclude:: ./environment.yml

Please see the `environment file <https://github.com/multiply-org/sar-pre-processing/blob/master/environment.yml>`_ for a list of dependencies.
ESA's SNAP Sentinel-1 Toolbox (Version >8.0.3) has to be installed prerequisite. The Software can be downloaded `here <http://step.esa.int/main/download/snap-download/>`_. To install the SNAP toolbox in Linux open a terminal window and use

    bash esa-snap_sentinel_unix_8_0.sh

SenSARP uses only functionalities of the Sentinel-1 Toolbox.
Currently only SNAP version 8.0 can be downloaded from the website. To update SNAP to a version >8.0.3 please start the SNAP software. You will be asked if you want to search for update. Please serach for updates and install all updates. After the updates are installed you need to restart SNAP to initialize the updates correctly.
SNAP Toolbox need libgfortran for specific operations but currently libgfortran is not installed during the installation process of SNAP therefore you might use::

    sudo apt-get install gfortran
