.. _Installation:

Installation
=============
.. note::
    The MULTIPLY platform has been developed against Python 3.6.
    It cannot be guaranteed to work with previous Python versions.

The first step is to clone the latest code and step into the check out directory::

    git clone https://github.com/multiply-org/sar-pre-processing.git
    cd sar-pre-processing

SenSARP can be run from sources directly.
To install all required modules, use::

    conda env create --prefix ./env --file environment.yml
    conda activate ./env # activate the environment

To install SenSARP into an existing Python environment just for the current user, use::

    python setup.py install --user

To install for development and for the current user, use::

    python setup.py develop --user


Module requirements
-------------------

.. literalinclude:: ./environment.yml

Please see the `environment file <https://github.com/multiply-org/sar-pre-processing/blob/master/environment.yml>`_ for a list of dependencies.
ESA's SNAP Sentinel-1 Toolbox has to be installed prerequisite. The Software can be downloaded
`here <http://step.esa.int/main/download/snap-download/>`_
- SNAP Toolbox need libgfortran for specific operations but currently libgfortran is not installed during the installation process of SNAP therefore you might use::

    sudo apt-get install gfortran
