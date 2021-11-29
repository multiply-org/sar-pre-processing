---
title: 'SenSARP: A pipeline to pre-process Sentinel-1 SLC data by using ESA SNAP Sentinel-1 Toolbox'
tags:
  - Python
  - Sentinel-1
  - SAR
  - SNAP
authors:
  - name: Thomas Weiß
    orcid: 0000-0001-5278-8379
    affiliation: 1
  - name: Tonio Fincke
    affiliation: 2
affiliations:
 - name: Department of Geography, Ludwig-Maximilians-Universität München, 80333 Munich, Germany
   index: 1
 - name: Brockmann Consult GmbH, 21029 Hamburg, Germany;
   index: 2
date: 20 April 2021
bibliography: paper.bib
---

# Summary

The Sentinel-1 mission consists of two polar-orbiting satellites acquiring Synthetic Aperture Radar data (SAR) at C-band (frequency of 5.405 GHz) with a revisit time of 6 days.
The SAR data is distributed free of charge via the Copernicus Open Access Hub (https://scihub.copernicus.eu/) by European Space Agency (ESA) and the European Commission.
Large archives are also provided by Data and Information Access Services (DIAS) which serve the purpose to facilitate the access and use of Sentinel Data.
Due to the specific imaging geometry of the radar system, the acquired radar data contains different radiometric and geometric distortions.
The radiometric quality is affected by spreading loss effect, the non-uniform antenna pattern, possible gain changes, saturation, and speckle noise.
Geometric distortions such as foreshortening, layover or shadowing effects are based on the side looking radar acquisition system.
To account for these radiometric and geometric distortions, the Sentinel-1 Level 1 data has to be corrected radiometrically and geometrically before the data can be used for further analysis or within third party applications.
Therefore, either an automatic or manual pre-processing of Sentinel-1 images is needed.

# Statement of need

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

# Method

This python package generates a file list of to be processed Sentinel-1 images (already downloaded and stored in a specific folder) based on different user defined criteria (specific year, area of interest).
Additionally, specific cases of repeatedly processed data are handled, as sometimes Sentinel-1 data were initially processed multiple times and stored under similar names on the Copernicus Open Access Hub. Also, cases where Sentinel-1 data within the user-defined area of interest might be stored in consecutive tiles are considered.

Based on the generated file list the default processing pipeline of the python package applies a pre-processing chain to Sentinel-1 Single Look Complex (SLC) time series or single images to generate radiometrically and geometrically corrected Sigma nought backscatter values.
Furthermore, if a time series is processed the images are co-registered and additional output files of multi-temporal speckle filtered data are generated.
In addition, a single speckle filter instead of a multi-temporal one is applied as well and the output will be stored as a separate layer.
To pre-process the images, the python package uses the GPT (Graph Processing Tool) of SNAP to execute different operators provided by the Sentinel-1 Toolbox.
The Sentinel Toolbox is available for download at step.esa.int, its source code is available in the senbox-org organization on GitHub.
Each of these operators performs a pre-processing step. The operators can be chained together to form a graph, which is used by the python package to run on the Sentinel-1 data using the Graph Processing Framework (GPF). The graphs are stored in xml-files. Users may change the graphs by modifying the files directly or via the Sentinel Toolbox.
User Guides to show how the GPF can be used are provided here: https://senbox.atlassian.net/wiki/spaces/SNAP/pages/70503053/Processing.

After the pre-processing the resulting radiometrically and geometrically corrected images are stored for further usage within a NetCDF4 stack file.
The processing workflow was developed and optimized to use a Sentinel-1 time series of pre-processed sigma nought backscatter values to retrieve biophysical land surface parameters by the use of radiative transfer models.
The sigma nought backscatter values provided by the default workflow of SenSARP might be used in other applications like flood risk analysis, monitoring land cover changes or monitoring global food security but it has to be mentioned that different applications have different demands and therefore, slight adjustments of the default workflow might be required.
In the future, many more new products and operational third party services based on consistent Sentinel-1 time series might be developed.

# Applications

This python package was developed within the Horizon 2020 project called MULTIscale SENTINEL land surface information retrieval Platform (MULTIPLY) (http://www.multiply-h2020.eu/, https://cordis.europa.eu/project/id/687320, https://multiply.obs-website.eu-de.otc.t-systems.com).
Furthermore, data processed by this package is used within Sentinel-Synergy-Study S3 project (https://www.researchgate.net/project/Sentinel-Synergy-Study-S3).
In addition, the python code was used to process Sentinel-1 time series images for the detection and analysis of temporary flooded vegetation [@tsyganskaya_detection_2018; @tsyganskaya_flood_2019] and for the evaluation of different radiative transfer models for microwave backscatter estimation of wheat fields [@weis_evaluation_2020].

# Other available python software packages and interfaces using ESA's SNAP software to pre-process remote sensing data

The ESA's SNAP toolbox has been written in Java. For python users the developers provide a python interface called Snappy. However, the Snappy interface is lacking in terms of installation, processing performance and usability. Hence, the remote sensing community developed different wrappers (e.g. SenSARP, snapista or pyroSAR) to use SNAP processing functionalities by utilizing the SNAP Graph Processing Tool (GPT).

## snapista

Snapista (https://snap-contrib.github.io/snapista/index.html) targets mainly experts remote sensing users with python programming skills.
It provides access to the processing operators of all toolboxes (e.g. Sentinel-1, Sentinel-2 or Sentinel-3) within SNAP.
Expert users can generate processing graphs and execute there generated graphs in a pure Pythonic way.
A guideline which processing steps are needed for different applications or which processing steps can or have to be combined are not provided yet.
As guidelines how to process different satellite data for different applications is not an easy task to do it exceeds the goal of snapista as a python wrapper for the SNAP software.
Summarizing, snapista provides access to all SNAP toolboxes (not just to Sentinel-1 Toolbox) via python. But as it provides no default processing chains, snapista will be primarily usable by expert remote sensing users.
The advantage of snapista is the accessibility of processing operators for SAR and optical data.

## pyroSAR

PyroSAR (https://pyrosar.readthedocs.io/en/latest/index.html) is a python library which provides a python wrapper to SAR pre-processing software SNAP and GAMMA [@wegnuller_sentinel-1_2016; @werner_gamma_2000].
The library provides utilities to read and store metadata information of downloaded satellite data within a database.
Furthermore, pyroSAR provides access to processing operators of SNAP and GAMMA.
A default workflow with different user options is provided to process single or time-series Sentinel-1 images.
After executing the default processing workflow radiometric and geometric corrected gamma nought backscatter data are provided in Geotiff format [@truckenbrodt_pyrosar_2019].
The processed images can also be stored within an Open Data Cube.
For expert users which might want to use a different processing workflow pyroSAR provides an option to create SNAP xml-workflows and execute them with the GPT.
Summarizing, pyroSAR provides a similar push-button option to process Sentinel-1 data with a slightly different default workflow (pyroSAR: no temporal speckle filter, gamma nought backscatter output in Geotiff format) than SenSARP (SenSARP: temporal speckle filter, sigma nought backscatter output in netCDF format).
PyroSAR, as a more complex library than SenSARP, provides on the one hand more changeable parameters within the processing workflow but on the other hand the usability for non-expert users might be narrowed compared to SenSARP.
An advantage of SenSARP, especially for non-expert users, might be the provision of background information (theory/purpose) of the different pre-processing steps within the documentation.

# Acknowledgements

The project leading to this application has received funding from the European Union’s Horizon 2020 research and innovation program under Grant Agreement No. 687320.
We would like to thank Alexander Löw and Philip Marzahn for guiding discussions that lead to this publication.
We also would like to thank Thomas Ramsauer for discussions and suggestions.
<!-- for providing comments on the manuscript -->
The author also wishes to thank the reviewers and editors for their efforts and for their helpful comments to improve this paper and the software package

# References
