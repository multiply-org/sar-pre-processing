
from netCDF4 import Dataset, date2num
import xarray as xr
import numpy as np
import os, fnmatch
import xml.etree.ElementTree as etree
from datetime import datetime, date
from dateutil import parser

import pdb

class NetcdfStack(object):

    def __init__(self, **kwargs):
        self.input_folder = kwargs.get('input_folder', None)
        self.output_path = kwargs.get('output_path', None)
        self.output_filename = kwargs.get('output_filename', None)
        self._check()
        self._create_filelist()
        self._create_empty_netcdf_file()
        self.stacking()

    def _check(self):
        assert self.input_folder is not None, 'ERROR: Folder with input files need to be specified'
        assert self.output_path is not None, 'ERROR: Path of output file need to be provided'
        assert self.output_filename is not None, 'ERROR: Name of output file need to be provided'

    def _create_filelist(self):
        """create a list containing all file in specified input folder"""

        # Create list containing all files to be processed
        self.filelist = []
        for root, dirnames, filenames in os.walk(self.input_folder):
            for filename in fnmatch.filter(filenames, '*.nc'):
                self.filelist.append(os.path.join(root, filename))
        print("Number of scenes found for processing:", len(self.filelist))

        # sort filelist by time (ascending)
        length = len(self.input_folder)
        self.filelist = sorted(self.filelist, key=lambda x:x[(length+18):104])

    def _create_empty_netcdf_file(self):
        """ create dummy netcdf file"""

        # create output netcdf file
        self.dataset = Dataset(os.path.join(self.output_path, self.output_filename + '.nc'), 'w', format='NETCDF4')

        # load example data for dummy creation
        data = Dataset(self.filelist[0])
        (sarfilenamepath, sarfilename) = os.path.split(self.filelist[0])
        (sarfileshortname, extension)  = os.path.splitext(sarfilename)

        # create dimensions
        self.lat = self.dataset.createDimension('lat', len(data.variables['lat'][:]))
        self.lon = self.dataset.createDimension('lon', len(data.variables['lon'][:]))
        self.time = self.dataset.createDimension('time', None)

        # create 1-D variables  (time, orbitdirection, relativorbit, satellite, latitude, longitude)
        self.times = self.dataset.createVariable('time', np.float32, ('time'))
        self.times.calendar = 'gregorian'
        self.times.units = 'days since ' + '1970-01-01 00:00:00'
        self.orbitdirection = self.dataset.createVariable('orbitdirection', np.float32, ('time'))
        self.relativeorbit = self.dataset.createVariable('relorbit', np.float32, ('time'))
        self.satellite = self.dataset.createVariable('satellite', np.float32, ('time'))
        self.latitude = self.dataset.createVariable('lat', np.float32, ('lat'))
        self.longitude = self.dataset.createVariable('lon', np.float32, ('lon'))

        # create 3-D variables (localIncidenceangle, projectedLocalIncidenceAngle, incidenceAngleFromEllipsoid, ... )
        self.localIncidenceAngle = self.dataset.createVariable('localIncidenceAngle', np.float32,('time','lat','lon'), fill_value=-99999)
        self.localIncidenceAngle.units = 'degree'
        # self.projectedLocalIncidenceAngle = self.dataset.createVariable('projectedLocalIncidenceAngle', np.float32,('time','lat','lon'), fill_value=-99999)
        # self.projectedLocalIncidenceAngle.units = 'degree'
        # self.incidenceAngleFromEllipsoid = self.dataset.createVariable('incidenceAngleFromEllipsoid', np.float32,('time','lat','lon'), fill_value=-99999)
        # self.incidenceAngleFromEllipsoid.units = 'degree'

        self.sigma0_vv_db = self.dataset.createVariable('sigma0_vv_multi_db', np.float32,('time','lat','lon'), fill_value=-99999)
        self.sigma0_vv_db.units = 'dB'
        self.sigma0_vh_db = self.dataset.createVariable('sigma0_vh_multi_db', np.float32,('time','lat','lon'), fill_value=-99999)
        self.sigma0_vh_db.units = 'dB'

        self.sigma0_vv_tempspeckl_db = self.dataset.createVariable('sigma0_vv_norm_multi_db', np.float32,('time','lat','lon'), fill_value=-99999)
        self.sigma0_vv_tempspeckl_db.units = 'dB'
        self.sigma0_vh_tempspeckl_db = self.dataset.createVariable('sigma0_vh_norm_multi_db', np.float32,('time','lat','lon'), fill_value=-99999)
        self.sigma0_vh_tempspeckl_db.units = 'dB'

    def stacking(self):
        """stack all file in one"""

        # 1-D Elements
        data = Dataset(self.filelist[0])
        self.latitude[:] = data.variables['lat'][:]
        self.longitude[:] = data.variables['lon'][:]

        # loop over all files in filelist
        y=0

        for sarfile in self.filelist:
            index = self.filelist.index(sarfile)-y
            print()
            print("Scene", self.filelist.index(sarfile) + 1, "of", len(self.filelist))
            print(sarfile)
            (sarfilepath, sarfilename) = os.path.split(sarfile)
            (sarfileshortname, extension) = os.path.splitext(sarfilename)

            # extract date from name tag
            date = parser.parse(sarfileshortname.split('_')[5])
            date_file_tag = date.strftime('%d%b%Y')

            # extract orbitdirection from metadata
            metadata = etree.parse(sarfilepath[0:-1]+'1/'+sarfilename[0:-14]+'.dim')
            for i in metadata.findall('Dataset_Sources'):
                for ii in i.findall('MDElem'):
                    for iii in ii.findall('MDElem'):
                        for iiii in iii.findall('MDATTR'):
                            r = iiii.get('name')
                            if r == 'PASS':
                                orbitdir = iiii.text
                                if orbitdir == 'ASCENDING':
                                    orbitdir = 0
                                elif orbitdir =='DESCENDING':
                                    orbitdir = 1
                                else:
                                    pass
                            continue

            # extract orbit from metadata
            metadata = etree.parse(sarfilepath[0:-1]+'1/'+sarfilename[0:-14]+'.dim')
            for i in metadata.findall('Dataset_Sources'):
                for ii in i.findall('MDElem'):
                    for iii in ii.findall('MDElem'):
                        for iiii in iii.findall('MDATTR'):
                            r = iiii.get('name')
                            if r == 'REL_ORBIT':
                                relorbit = iiii.text

            # extract satellite name from name tag
            if sarfileshortname[0:3] == 'S1A':
                sat = 0
            elif sarfileshortname[0:3] == 'S1B':
                sat = 1
            else:
                pass

            # load sarfile
            data = xr.open_dataset(sarfile)

            # get time stamp
            timestamp = (parser.parse(sarfileshortname.split('_')[5]))

            # fill 1-D variable
            self.times[index] = date2num(timestamp, units ='days since ' + '1970-01-01 00:00:00', calendar='gregorian')
            self.orbitdirection[index] = orbitdir
            self.orbitdirection.description = '0 = Ascending, 1 = Descending'
            self.relativeorbit[index] = relorbit
            self.satellite[index] = sat
            self.satellite.description = '0 = Sentinel 1A, 1 = Sentinel 1B'

            # fill 3-D variables
            self.localIncidenceAngle[index,:,:] = data.variables['theta'][:]
            # self.projectedLocalIncidenceAngle[index,:,:] = data.variables['projectedLocalIncidenceAngle_slv9_' + date_file_tag][:]
            # self.incidenceAngleFromEllipsoid[index,:,:] = data.variables['incidenceAngleFromEllipsoid_slv10_' + date_file_tag][:]

            self.sigma0_vv_db[index,:,:] = data.variables['sigma0_vv_multi'][:]
            self.sigma0_vh_db[index,:,:] = data.variables['sigma0_vh_multi'][:]

            self.sigma0_vv_tempspeckl_db[index,:,:] = data.variables['sigma0_vv_norm_multi'][:]
            self.sigma0_vh_tempspeckl_db[index,:,:] = data.variables['sigma0_vh_norm_multi'][:]

        self.dataset.close()



# pdb.set_trace()



# # create 2-D variables
# latitude = dataset.createVariable('latitude', np.float32,('lon','lat'), fill_value=-99999)
# longitude = dataset.createVariable('longitude', np.float32,('lon','lat'), fill_value=-99999)
# elevation = dataset.createVariable('elevation', np.float32,('lon','lat'), fill_value=-99999)
# pdb.set_trace()
# # fill 2-D variables
# latitude[:,:] = data.variables['latitude_slv6_' + date_file_tag][:]
# latitude.units = 'degree_north'
# longitude[:,:] = data.variables['longitude_slv7_' +date_file_tag][:]
# longitude.units = 'degree_east'
# elevation[:,:] = data.variables['elevation_slv5_' +date_file_tag][:]
# elevation.units = 'meters'
# pdb.set_trace()


