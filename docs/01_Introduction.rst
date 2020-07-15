.. _Introduction:

Introduction
============

The two Sentinel-1 satellites 1A and 1B are one of the first satellites which are providing free microwave
data in high temporal and spatial resolution. Within the MULTIPLY project we developed a pre-
processing chain to process time-series of Sentinel-1 data for quantitative analysis of vegetation and
soil parameters over agricultural fields. Therefore, geometric and radiometric corrections
as well as (multi-temporal) speckle filter is applied. The whole pre-processing chain for Sentinel-1
Level-1 Single Look Complex (SLC) data is accomplished by ESA’s SNAP S1TBX software (version 7.0.3).
The SNAP toolbox can be downloaded from http://step.esa.int/main/download/snap-download/. However, to automatically
apply different pre-processing steps on Sentinel-1 data a python script, which uses the Graph Processing Tool (GPT)
of the S1TBX, was developed provided. All codes, xml-graphs etc are stored in a GitHub repository accessible
under https://github.com/multiply-org/sar-pre-processing.

This is the documentation of python package Multiply-sar-pre-processing and is structured in following sections:

.. toctree::
   :maxdepth: 1

* :ref:`Introduction`
* :ref:`Installation`
* :ref:`ProcessingChain`
* :ref:`Technicaldocumantation`

Indices and tables
-------------------

* :ref:`genindex`
* :ref:`modindex`

Credits
-------------
The project leading to this application has received funding from the
European Union’s Horizon 2020 research and innovation program
under grant agreement No 687320.



