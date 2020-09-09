---
title: 'sar-pre-processing: A Python package for pre-processing Sentinel-1 SLC data with ESAs SNAP Toolbox'
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
date: 02 September 2020
bibliography: paper.bib
---

# Summary

The Sentinel-1 mission consists of two polar-orbiting satellites acquiring Synthetic Aperture Radar data (SAR) at C-band (frequency of 5.405 GHz) with a revisit time of 6 days. The SAR data distributed as Ground Range Detected (GRD) or Single Look Complex (SLC) is distributed free of charge via the Copernicus Open Access Hub by ESA and the European Commission. For further analysis or usage within third party applications the provided Sentinel-1 Level 1 SLC data has to be radiometric and geometric corrected. Therefore, either a semi-automatic or manual pre processing of Sentinel-1 images is needed.

This python package generates are file list of to be processed Sentinel-1 images (already downloaded and stored in a specific folder) based on different user defined criteria (specific year, area of interest). Additionally, specific cases of double processed data (sometimes Sentinel-1 images were initially processed multiple times and stored under similar names within Copernicus Open Access Hub) and border issues due to user defined area of interest (due to storages reasons Sentinel-1 data of the area of interest might be stored within different consecutive images) are handled.
Based on the generated file list the python packages applies a pre processing chain to Sentinel-1 SLC time series data to generate radiometric and geometric corrected Sigma nought backscatter values. Furthermore, the time series images are co-registered and additional output files of single and/or multi-temporal speckle filtered data are generated. To pre process the images the python packages uses the framework of ESA's SNAP Toolbox (current version 7.0.3). The individual processing steps are defined within default xml-files (user defined xml-files can be generated e.g. with the SNAP Toolbox and used within the python package). After the pre processing the generated radiometric and geometric corrected images are stored for further usage within a NetCDF4 stack file.
Among other applications the processed images can be and are used for flood risk analysis, monitoring land cover changes, monitoring global food security or estimation of land surface parameters. In the future many more new products and operational third party services based on consistent Sentinel-1 time series might be developed.

This python package was developed within the Horizon 2020 project called MULTIscale SENTINEL land surface information retrieval Platform (MULTIPLY) [@noauthor_multiscale_nodate, @noauthor_multiply_nodate]. Furthermore, data processed by this package is used within Sentinel-Synergy-Study S3 project [@noauthor_sentinel-synergy-study_nodate]. In addition, the python code was used to process Sentinel-1 time series images for analysis on detection of temporary flooded vegetation [@tsyganskaya_detection_2018, @tsyganskaya_flood_2019].

# Acknowledgements

The project leading to this application has received funding from the European Union’s Horizon 2020 research and innovation program under Grant Agreement No. 687320.

# References
