
from netCDF4 import Dataset, date2num
import xarray as xr
import numpy as np
import os, fnmatch
import datetime

class NetcdfStackCreator(object):
    """
    Create NetCDF stack
    """

    def __init__(self, **kwargs):
        self.input_folder = kwargs.get('input_folder', None)
        self.output_path = kwargs.get('output_path', None)
        self.output_filename = kwargs.get('output_filename', None)
        self._check()

    def _check(self):
        assert self.input_folder is not None, 'ERROR: Folder with input files need to be specified'
        assert self.output_path is not None, 'ERROR: Path of output file need to be provided'
        assert self.output_filename is not None, 'ERROR: Name of output file need to be provided'

    def create_netcdf_stack(self):
        self._create_filelist()
        self._create_empty_netcdf_file()
        self.stacking()

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
        self.filelist = sorted(self.filelist, key=lambda x:x[(length+18):(length+18+16)])

    def _create_empty_netcdf_file(self):
        """ create dummy netcdf file"""

        # create output netcdf file
        self.dataset = Dataset(os.path.join(self.output_path, self.output_filename + '.nc'), 'w', format='NETCDF4')

        # load example data for dummy creation
        data = Dataset(self.filelist[0])

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

        # create 3-D variables (localIncidenceangle ... )
        self.localIncidenceAngle = self.dataset.createVariable('localIncidenceAngle', np.float32,('time','lat','lon'), fill_value=-99999)
        self.localIncidenceAngle.units = 'degree'

        self.sigma0_vv = self.dataset.createVariable('sigma0_vv_multi', np.float32,('time','lat','lon'), fill_value=-99999)
        self.sigma0_vv.units = 'linear'
        self.sigma0_vh = self.dataset.createVariable('sigma0_vh_multi', np.float32,('time','lat','lon'), fill_value=-99999)
        self.sigma0_vh.units = 'linear'

        self.sigma0_vv_tempspeckl = self.dataset.createVariable('sigma0_vv_norm_multi', np.float32,('time','lat','lon'), fill_value=-99999)
        self.sigma0_vv_tempspeckl.units = 'linear'
        self.sigma0_vh_tempspeckl = self.dataset.createVariable('sigma0_vh_norm_multi', np.float32,('time','lat','lon'), fill_value=-99999)
        self.sigma0_vh_tempspeckl.units = 'linear'

    def stacking(self):
        """stack all file in one"""

        # 1-D Elements
        data = Dataset(self.filelist[0])
        self.latitude[:] = data.variables['lat'][:]
        self.longitude[:] = data.variables['lon'][:]

        # loop over all files in filelist
        for index, sarfile in enumerate(self.filelist):
            print()
            print("Scene", self.filelist.index(sarfile) + 1, "of", len(self.filelist))
            print(sarfile)

            # load sarfile
            data = xr.open_dataset(sarfile)

            # encoding of satellite
            if data.satellite == 'S1A':
                sat = 0
            elif data.satellite == 'S1B':
                sat = 1

            # encoding of orbitdirection
            if data.orbitdirection == 'ASCENDING':
                orbitdir = 0
            elif data.orbitdirection =='DESCENDING':
                orbitdir = 1

            # fill 1-D variable
            self.times[index] = date2num(datetime.datetime.strptime(data.date, '%Y-%m-%d %H:%M:%S'), units ='days since ' + '1970-01-01 00:00:00', calendar='gregorian')
            self.orbitdirection[index] = orbitdir
            self.orbitdirection.description = '0 = Ascending, 1 = Descending'
            self.relativeorbit[index] = int(data.relativeorbit)
            self.satellite[index] = sat
            self.satellite.description = '0 = Sentinel 1A, 1 = Sentinel 1B'

            # fill 3-D variables
            self.localIncidenceAngle[index,:,:] = data.variables['theta'][:]
            self.sigma0_vv[index,:,:] = data.variables['sigma0_vv_multi'][:]
            self.sigma0_vh[index,:,:] = data.variables['sigma0_vh_multi'][:]

            self.sigma0_vv_tempspeckl[index,:,:] = data.variables['sigma0_vv_norm_multi'][:]
            self.sigma0_vh_tempspeckl[index,:,:] = data.variables['sigma0_vh_norm_multi'][:]

        self.dataset.close()
