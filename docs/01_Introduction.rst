.. _Introduction:

Introduction
============
The two Sentinel-1 satellites 1A and 1B are one of the first satellites which are providing free microwave
data in high temporal and spatial resolution. Within the MULTIPLY project we developed a pre-
processing chain to process time-series of Sentinel-1 data for quantitative analysis of vegetation and
soil parameters over agricultural fields. Therefore, geometric and radiometric corrections
as well as (multi-temporal) speckle filter is applied. The whole pre-processing of Sentinel-1
Level-1 Single Look Complex (SLC) data is accomplished by ESA’s SNAP S1TBX software (version 7.0.3).
The SNAP toolbox can be downloaded from http://step.esa.int/main/download/snap-download/. To automatically
apply different pre-processing steps on Sentinel-1 data a python script, which uses the Graph Processing Tool (GPT)
of the S1TBX, was developed. All codes, xml-graphs etc are stored in a GitHub repository accessible
under https://github.com/multiply-org/sar-pre-processing.

Getting Started
^^^^^^^^^^^^^^^
Please find instructions on how to download and install the prior engine in the :ref:`Installation` section.

Testing and Contribution
^^^^^^^^^^^^^^^^^^^^^^^^^
You are welcome to test and contribute to the MULTIPLY SAR pre processing. Please use `GitHub <https://github.com/McWhity/sar-pre-processing>`_ for that matter.
