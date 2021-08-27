.. _Introduction:

Introduction
============
The Sentinel-1 mission consists of two polar-orbiting satellites acquiring Synthetic Aperture Radar data (SAR) at C-band (frequency of 5.405 GHz) with a revisit time of 6 days.
The SAR data is distributed free of charge via the Copernicus Open Access Hub (https://scihub.copernicus.eu/) by European Space Agency (ESA) and the European Commission.
Large archives are also provided by Data and Information Access Services (DIAS) which serve the purpose to facilitate the access and use of Sentinel Data.
Due to the specific imaging geometry of the radar system the acquired radar data contains different radiometric and geometric distortions.
The radiometric quality is affected by spreading loss effect, the non-uniform antenna pattern, possible gain changes, saturation, and speckle noise.
Geometric distortions such as foreshortening, layover or shadowing effects are based on the side looking radar acquisition system.
To account for these radiometric and geometric distortions the Sentinel-1 Level 1 data has to be corrected radiometrically and geometrically before the data can be used for further analysis or within third party applications.
Therefore, either an automatic or manual pre-processing of Sentinel-1 images is needed.

Statement of need
=================
Sentinel-1 satellites will provide continuous free available microwave remote sensing data of the entire globe at least until the end of 2030.
Furthermore, ESA is not only providing Sentinel satellite images (e.g. Sentinel-1, Sentinel-2, Sentinel-3) but they also developed free open source toolboxes (Sentinel-1, 2, 3 toolboxes) for scientific exploitation.
The toolboxes can be accessed and used via the Sentinel Application Platform (SNAP).
SNAP offers a graphical interface were expert users can develop different processing schemes and apply them on the satellite images.
Although, Sentinel-1 satellite data and a processing software are freely available, the usage of the data is mainly limited to expert users in the field of microwave remote sensing as different pre-processing steps need to be applied before using Sentinel-1 images.

SenSARP was developed to provide a push-button option to easily apply a rigid pre-processing pipeline with sensible defaults to a Sentinel-1 Level 1 SLC time series data as well as single Sentinel-1 Level 1 SLC images.
Thus, non-expert users in the field of pre-processing microwave data are able to use radiometric and geometric corrected sigma nought backscatter data for their specific applications.
Beside a rigid pre-processing pipeline SenSARP provides filter options to retrieve only images of a specific year or images that contain a specific area of interest from a stack of downloaded Sentinel-1 data.
Furthermore, the default processing scheme of SenSARP can handle if an area of interest is contained in two tiles of the same swath (due to storage reasons data of one Sentinel-1 satellite swath is provided by ESA within different tiles).
Additionally, SenSARP checks if within a stack of Sentinel-1 images one specific image was multiple processed by ESA and uses the newest.

For expert users SenSARP provides the possibility to automate their pre-processing on a large scale by either modifying the default pre-processing scheme (modification of xml graph pre_processing_step1.xml) or create their own pre-processing scheme (create a new xml graph) with the graph builder of the SNAP software.
They can benefit from the filter options, the default pre-processing step 2 (co-registration of images) and the SenSARP functions to stack all processed and co-registered images within a netCDF file with additional image information e.g. satellite name, relative orbit and orbitdirection.


Getting Started
================
Please find instructions on how to download and install SenSARP in the :ref:`Installation` section.

Testing and Contribution
=========================
You are welcome to test and contribute to SenSARP. Please use `GitHub <https://github.com/multiply-org/sar-pre-processing>`_ for that matter.
