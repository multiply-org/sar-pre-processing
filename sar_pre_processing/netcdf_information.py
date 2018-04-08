

from netCDF4 import Dataset, num2date, date2num
import xarray as xr
import numpy as np
import os, fnmatch
import xml.etree.ElementTree as etree
from datetime import datetime, date
import pandas as pd

import pdb




input_folder = '/media/nas_data/Thomas/S1_LMU_site_2017/step3'
expression = '*.nc'
filelist = []
for root, dirnames, filenames in os.walk(input_folder):
    for filename in fnmatch.filter(filenames, expression):
        filelist.append(os.path.join(root, filename))
    break


# for loop though all measurement points
for file in filelist:

    (sarfilepath, sarfilename) = os.path.split(file)
    (sarfileshortname, extension)  = os.path.splitext(sarfilename)

    sarfilepath2 = '/media/nas_data/Thomas/S1_LMU_site_2017/step1/'
    # extract orbitdirection from metadata
    metadata = etree.parse(sarfilepath2+sarfilename[0:79]+'.dim')
    for i in metadata.findall('Dataset_Sources'):
        for ii in i.findall('MDElem'):
            for iii in ii.findall('MDElem'):
                for iiii in iii.findall('MDATTR'):
                    r = iiii.get('name')
                    if r == 'PASS':
                        orbitdir = iiii.text
                        if orbitdir == 'ASCENDING':
                            orbitdir = 'ASCENDING'
                            print(orbitdir)
                        elif orbitdir =='DESCENDING':
                            orbitdir = 'DESCENDING'
                            print(orbitdir)
                        else:
                            pass
                    continue

    # extract orbit from metadata
    metadata = etree.parse(sarfilepath2+sarfilename[0:79]+'.dim')
    for i in metadata.findall('Dataset_Sources'):
        for ii in i.findall('MDElem'):
            for iii in ii.findall('MDElem'):
                for iiii in iii.findall('MDATTR'):
                    r = iiii.get('name')
                    if r == 'REL_ORBIT':
                        relorbit = iiii.text


    # extract satellite name from name tag
    if sarfileshortname[0:3] == 'S1A':
        sat = 'S1A'
    elif sarfileshortname[0:3] == 'S1B':
        sat = 'S1B'
    else:
        pass

    dset = Dataset(file, 'r+', format="NETCDF4")

    orbitdirection = dset.setncattr_string('orbitdirection', orbitdir)
    relativeorbit = dset.setncattr_string('relativeorbit', relorbit)
    satellite = dset.setncattr_string('satellite', sat)



    dset.close()


