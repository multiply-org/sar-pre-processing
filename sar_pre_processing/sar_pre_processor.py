"""
Wrapper module to launch preprocessor
"""

import os
import yaml
import fnmatch
# import pyproj
# import zipfile
# import shutil
# import ogr
import xml.etree.ElementTree as etree
from datetime import datetime
from file_list_sar_pre_processing import SARList
import subprocess
from netCDF4 import Dataset
from netcdf_stack import NetcdfStack

import pdb


class AttributeDict(object):
    """
    A class to convert a nested Dictionary into an object with key-values
    accessibly using attribute notation (AttributeDict.attribute) instead of
    key notation (Dict["key"]). This class recursively sets Dicts to objects,
    allowing you to recurse down nested dicts (like: AttributeDict.attr.attr)
    """

    def __init__(self, **entries):

        self.add_entries(**entries)

    def add_entries(self, **entries):
        for key, value in entries.items():
            if type(value) is dict:
                self.__dict__[key] = AttributeDict(**value)
            else:
                self.__dict__[key] = value

    # def has_entry(self, entry: str):
    #     return self._has_entry(entry, 0)

    # def _has_entry(self, entry: str, current_index: int):
    #     entry_keys = entry.split('.')
    #     if entry_keys[current_index] in self.__dict__.keys():
    #         if current_index < len(entry_keys):
    #             dict_entry = self.__dict__[entry_keys[current_index]]
    #             if type(dict_entry) is not dict:
    #                 return False
    #             return dict_entry._has_entry(entry, current_index + 1)
    #         return True
    #     return False

    def __getitem__(self, key):
        """
        Provides dict-style access to attributes
        """
        return getattr(self, key)


class PreProcessor(object):

    def __init__(self, **kwargs):
        self.config_file = kwargs.get('config', None)
        self.filelist = kwargs.get('filelist', None)
        self._check()
        self._load_config()

    def _check(self):

        assert self.config_file is not None, 'ERROR: Configuration file needs to be provided'

    def pre_process(self):

        assert False, 'Routine should be implemented in child class'

    def _load_config(self):
        """
        Load configuration from self.config.bb.pre_process()
           writes to self.config.
        """
        with open(self.config_file, 'r') as cfg:
            self.config = yaml.load(cfg)
            self.config = AttributeDict(**self.config)


class SARPreProcessor(PreProcessor):

    def __init__(self, **kwargs):
        super(SARPreProcessor, self).__init__(**kwargs)

        # Check if output folder is specified
        assert self.config.output_folder is not None, 'ERROR: output folder needs to be specified'

        # Initialise output folder for different preprocessing steps
        # (can be put in the YAML config file if needed)
        self.config.output_folder_step1 = os.path.join(
            self.config.output_folder, 'step1')
        self.config.output_folder_step2 = os.path.join(
            self.config.output_folder, 'step2')
        self.config.output_folder_step3 = os.path.join(
            self.config.output_folder, 'step3')

        # Initialise name of necessary xml-graphs for preprocessing
        # (can be put in the YAML config file if needed)
        self.config.xml_graph_pre_process_step1 = 'pre_process_step1.xml'
        self.config.xml_graph_pre_process_step1_border = 'pre_process_step1_border.xml'
        self.config.xml_graph_pre_process_step2 = 'pre_process_step2.xml'
        self.config.xml_graph_pre_process_step3 = 'pre_process_step3.xml'

        # Initialise name addition for output files
        self.name_addition_step1 = '_GC_RC_No_Su'
        self.name_addition_step2 = '_Co'
        self.name_addition_step3 = '_speckle'

        # Check if path of SNAP's graph-processing-tool is specified
        assert self.config.gpt is not None, 'ERROR: path for SNAPs graph-processing-tool is not not specified'

        # Check if path of path to XML files is specified
        # if not self.config.has_entry('xml_graph_path') is None:
        #     self.config.xml_graph_path = '.\\xml_files'
        # assert self.config.xml_graph.path is not None, 'ERROR: path of XML files for processing is not not specified'

        # pass

        # TODO PUT THE GRAPH DIRECTORIES AND NAMES IN A SEPARATE CONFIG !!!

        # # xml-processing graph
        # self.xmlgraphpath = '/media/tweiss/Work/python_code/MULTIPLY/pre_processing_Sentinel_1/xml_files/'
        # # the XML config files should gfo somewhere in a specific directory in the multiply-core repo
        # self.xmlgraph = 'preprocess_v01.xml'

    # todo discuss if input/output specification part of processing or part of
    # instantiation of the object itself

    def _create_filelist(self, input_folder, expression):
        """
        Create list containing all files in input_folder (without subfolder) that contain the provided expression within the filename
        """
        filelist = []
        for root, dirnames, filenames in os.walk(input_folder):
            for filename in fnmatch.filter(filenames, expression):
                filelist.append(os.path.join(root, filename))
            break
        # print('Number of found files:', len(filelist))
        return filelist

    def _decomposition_filename(self, file):
        """
        Decomposition of filename including path in
        path, filename, fileshortname and extension
        """
        (filepath, filename) = os.path.split(file)
        (fileshortname, extension) = os.path.splitext(filename)
        return filepath, filename, fileshortname, extension

    def _get_area(self, lat_min, lat_max, lon_min, lon_max):
        """
        Change input coordinates for subset operator"
        """

        assert lat_min <= lat_max, 'ERROR: invalid lat'
        assert lon_min <= lon_max, 'ERROR: invalid lon'
        return '%.14f %.14f,%.14f %.14f,%.14f %.14f,%.14f %.14f,%.14f %.14f' % (lon_min, lat_min, lon_min, lat_max, lon_max, lat_max, lon_max, lat_min, lon_min, lat_min)

    def pre_process_step1(self, **kwargs):
        """
        Pre-process S1 SLC data with SNAP's GPT

        1) apply precise orbit file
        2) thermal noise removal
        3) calibration
        4) TOPSAR-Deburst
        5) Geometric Terrain Correction
        6) Radiometric Correction (after kellndorfer et al.)
        7) backscatter normalisation on specified angle in config file (based on Lambert's Law)

        """

        # create filelist
        self.file_list = SARList(config=self.config_file).create_list()

        # Check if input folder is specified
        assert self.config.input_folder is not None, 'ERROR: input folder not specified'
        assert os.path.exists(self.config.input_folder)

        # Check if output folder for step1 is specified, if not existing create
        # new folder
        assert self.config.output_folder_step1 is not None, 'ERROR: output folder for step1 needs to be specified'
        if not os.path.exists(self.config.output_folder_step1):
            os.makedirs(self.config.output_folder_step1)

        # Check if XML file for pre-processing is specified
        assert self.config.xml_graph_pre_process_step1 is not None, \
            'ERROR: path of XML file for pre-processing step 1 is not not specified'

        if self.config.subset == 'yes':
            try:
                lower_right_y = self.config.region['lr']['lat']
                upper_left_y = self.config.region['ul']['lat']
                upper_left_x = self.config.region['ul']['lon']
                lower_right_x = self.config.region['lr']['lon']
                # todo: how is it with coordinates that go across the datum
                # line ??

                # Coordinates for subset area
                area = self._get_area(
                    lower_right_y, upper_left_y, upper_left_x, lower_right_x)
                process_all = 'no'
            except AttributeError:
                print('area of interest not specified, whole images will be processed')
                process_all = 'yes'
        elif self.config.subset == 'no':
            process_all = 'yes'
        else:
            raise ValueError('subset has to be set to "yes" or "no"')

        # loop to process all files stored in input directory
        for file in self.file_list[0]:

            print('Scene ', self.file_list[0].index(
                file) + 1, ' of ', len(self.file_list[0]))

            # Divide filename
            filepath, filename, fileshortname, extension = self._decomposition_filename(
                file)

            # Call SNAP routine, xml file
            print('Process ', filename, ' with SNAP.')

            outputfile = os.path.join(
                self.config.output_folder_step1, fileshortname + self.name_addition_step1 + '.dim')

            try:
                normalisation_angle = self.config.normalisation_angle
                if normalisation_angle is None:
                    normalisation_angle = 35
                    print(
                        'normalisaton angle not specified, default value of 35 is used for processing')
            except AttributeError:
                normalisation_angle = 35
                print(
                    'normalisaton angle not specified, default value of 35 is used for processing')

            if process_all == 'no':
                # pdb.set_trace()
                subprocess.call(self.config.gpt + ' ' + os.path.join(self.config.xml_graph_path, self.config.xml_graph_pre_process_step1) + ' -Pinput="' +
                                file + '" -Poutput="' + outputfile + '" -Pangle="' + str(normalisation_angle) + '" -Parea="POLYGON ((' + area + '))" -c 2G -x', shell=True)
            else:
                subprocess.call(self.config.gpt + ' ' + os.path.join(self.config.xml_graph_path, self.config.xml_graph_pre_process_step1) +
                                ' -Pinput="' + file + '" -Poutput="' + outputfile + '" -Pangle="' + str(normalisation_angle) + '" -c 2G -x', shell=True)

        # pdb.set_trace()
        for i, file in enumerate(self.file_list[1][::2]):
            file_list2 = self.file_list[1][1::2]
            file2 = file_list2[i]

            # Divide filename
            filepath, filename, fileshortname, extension = self._decomposition_filename(
                file)

            outputfile = os.path.join(
                self.config.output_folder_step1, fileshortname + self.name_addition_step1 + '.dim')

            try:
                normalisation_angle = self.config.normalisation_angle
                if normalisation_angle is None:
                    normalisation_angle = 35
                    print('normalisaton angle not specified, default value of 35 is used for processing')
            except AttributeError:
                normalisation_angle = 35
                print('normalisaton angle not specified, default value of 35 is used for processing')
            # pdb.set_trace()
            if process_all == 'no':
                subprocess.call(self.config.gpt + ' ' + os.path.join(self.config.xml_graph_path, self.config.xml_graph_pre_process_step1_border) + ' -Pinput="' +
                                file + '" -Pinput2="' + file2 + '" -Poutput="' + outputfile + '" -Pangle="' + str(normalisation_angle) + '" -Parea="POLYGON ((' + area + '))" -c 2G -x', shell=True)
            else:
                subprocess.call(self.config.gpt + ' ' + os.path.join(self.config.xml_graph_path, self.config.xml_graph_pre_process_step1_border) +
                                ' -Pinput="' + file + '" -Pinput2="' + file2 + '" -Poutput="' + outputfile + '" -Pangle="' + str(normalisation_angle) + '" -c 2G -x', shell=True)

    def pre_process_step2(self, **kwargs):
        """
        pre_process_step1 has to be done first

        Pre-process S1 SLC data with SNAP's GPT

        1) co-register pre-processed data

        !!! all files will get metadata of the master image !!! Problem?

        """

        # Check if XML file for pre-processing step 2 is specified
        assert self.config.xml_graph_pre_process_step2 is not None, 'ERROR: path of XML file for pre-processing step 2 is not not specified'

        # Check if output folder of pre_process_step1 exists
        assert os.path.exists(
            self.config.output_folder_step1), 'ERROR: output folder of pre-processing step1 not found'

        # Check if output folder for step2 is specified, if not existing create
        # new folder
        assert self.config.output_folder_step2 is not None, 'ERROR: output folder for step2 needs to be specified'
        if not os.path.exists(self.config.output_folder_step2):
            os.makedirs(self.config.output_folder_step2)

        # Create filelist with all to be processed images
        if self.filelist is None:
            print(
                'no filelist specified therefore all images in output folder step1 will be processed')
            filelist = self._create_filelist(
                self.config.output_folder_step1, '*.dim')
            filelist.sort()
        else:
            filelist = []
            for file in self.filelist:
                filepath, filename, fileshortname, extension = self._decomposition_filename(
                    file)
                new_file_name = os.path.join(
                    self.config.output_folder_step1, fileshortname + self.name_addition_step1 + '.dim')

                if os.path.exists(new_file_name) is True:
                    filelist.append(new_file_name)
                else:
                    print('skip processing for %s. File does not exists' % file)
            filelist.sort()

        # Set Master image for co-registration
        master = filelist[0]

        # loop to co-register all found images to master image
        for file in filelist:
            print('Scene', filelist.index(file) + 1, 'of', len(filelist))

            # Divide filename
            filepath, filename, fileshortname, extension = self._decomposition_filename(
                file)

            # Call SNAP routine, xml file
            print('Process ', filename, ' with SNAP.')

            outputfile = os.path.join(
                self.config.output_folder_step2, fileshortname + self.name_addition_step2 + '.dim')

            os.system(self.config.gpt + ' ' + os.path.join(self.config.xml_graph_path, self.config.xml_graph_pre_process_step2) +
                      ' -Pinput="' + master + '" -Pinput2="' + file + '" -Poutput="' + outputfile + '"')
            print(datetime.now())

    def pre_process_step3(self, **kwargs):
        """
        pre_process_step1 and 2 has to be done first

        Pre-process S1 SLC data with SNAP's GPT

        1) apply multi-temporal speckle filter

        """

        # Check if output folder of pre_process_step1 exists
        assert os.path.exists(
            self.config.output_folder_step2), 'ERROR: output folder of pre-processing step2 not found'

        # Check if output folder for step3 is specified, if not existing create
        # new folder
        assert self.config.output_folder_step3 is not None, 'ERROR: output folder for step3 needs to be specified'
        if not os.path.exists(self.config.output_folder_step3):
            os.makedirs(self.config.output_folder_step3)

        # list with all dim files found in output-folder of pre_process_step2
        filelist = self._create_filelist(os.path.join(
            self.config.output_folder, 'step2'), '*.dim')
        filelist.sort()

        # Create filelist with all to be processed images
        if self.filelist is None:
            print(
                'no filelist specified therefore all images in output folder step2 will be processed')
            filelist = self._create_filelist(
                self.config.output_folder_step2, '*.dim')
        else:
            filelist = []
            for file in self.filelist:
                filepath, filename, fileshortname, extension = self._decomposition_filename(
                    file)
                new_file_name = os.path.join(
                    self.config.output_folder_step2, fileshortname + self.name_addition_step1 + self.name_addition_step2 + '.dim')

                if os.path.exists(new_file_name) is True:
                    filelist.append(new_file_name)
                else:
                    print('skip processing for %s. File does not exists' % file)

        # Sort filelist by date (hard coded position in filename!!!)
        filepath, filename, fileshortname, extension = self._decomposition_filename(filelist[0])
        filelist.sort(key=lambda x: x[len(filepath) + 18:len(filepath) + 33])
        filelist_old = filelist


        for i in ['S1A', 'S1B']:

            filelist = [k for k in filelist_old if i in k]

            if self.config.speckle_filter.multi_temporal.apply == 'yes':

                # Check if XML file for pre-processing step 3 is specified
                assert self.config.xml_graph_pre_process_step3 is not None, 'ERROR: path of XML file for pre-processing step 3 is not not specified'

                new_filelist = []

                # loop to apply multi-temporal filtering
                # right now 15 scenes if possible 7 before and 7 after multi-temporal filtered scene, vv and vh polarisation are separated
                # use the speckle filter algorithm metadata? metadata for date
                # might be wrong!!!

                for i, file in enumerate(filelist):


                    # apply speckle filter on 15 scenes if possible 7 before and 7 after the scene of interest
                    # what happens if there are less then 15 scenes available
                    if i < 2:
                        processing_filelist = filelist[0:5]
                    else:
                        if i <= len(filelist) - 3:
                            processing_filelist = filelist[i - 2:i + 3]
                        else:
                            processing_filelist = filelist[
                                i - 2 - (3 - (len(filelist) - i)):len(filelist)]

                    filepath, filename, fileshortname, extension = self._decomposition_filename(
                        file)

                    a, a, b, a = self._decomposition_filename(self._create_filelist(
                        os.path.join(filepath, fileshortname + '.data'), '*_slv1_*.img')[0])
                    a, a, c, a = self._decomposition_filename(self._create_filelist(
                        os.path.join(filepath, fileshortname + '.data'), '*_slv2_*.img')[0])
                    a, a, d, a = self._decomposition_filename(self._create_filelist(
                        os.path.join(filepath, fileshortname + '.data'), '*_slv3_*.img')[0])
                    a, a, e, a = self._decomposition_filename(self._create_filelist(
                        os.path.join(filepath, fileshortname + '.data'), '*_slv4_*.img')[0])
                    list_bands_single_speckle_filter = ','.join([b, c, d, e])

                    name_change_vv_single = d
                    name_change_vh_single = e
                    name_change_vv_norm_single = b
                    name_change_vh_norm_single = c

                    # pdb.set_trace()

                    list_bands_vv_multi = []
                    list_bands_vh_multi = []

                    list_bands_vv_norm_multi = []
                    list_bands_vh_norm_multi = []

                    for processing_file in processing_filelist:
                        filepath, filename, fileshortname, extension = self._decomposition_filename(
                            processing_file)

                        # get filename from folder
                        # think about better way !!!!
                        a, a, band_vv_name_multi, a = self._decomposition_filename(self._create_filelist(
                            os.path.join(filepath, fileshortname + '.data'), '*_slv3_*.img')[0])
                        a, a, band_vh_name_multi, a = self._decomposition_filename(self._create_filelist(
                            os.path.join(filepath, fileshortname + '.data'), '*_slv4_*.img')[0])
                        a, a, band_vv_name_norm_multi, a = self._decomposition_filename(self._create_filelist(
                            os.path.join(filepath, fileshortname + '.data'), '*_slv1_*.img')[0])
                        a, a, band_vh_name_norm_multi, a = self._decomposition_filename(self._create_filelist(
                            os.path.join(filepath, fileshortname + '.data'), '*_slv2_*.img')[0])

                        list_bands_vv_multi.append(band_vv_name_multi)
                        list_bands_vh_multi.append(band_vh_name_multi)

                        list_bands_vv_norm_multi.append(band_vv_name_norm_multi)
                        list_bands_vh_norm_multi.append(band_vh_name_norm_multi)

                    # Divide filename of file of interest
                    filepath, filename, fileshortname, extension = self._decomposition_filename(
                        file)

                    outputfile = os.path.join(
                        self.config.output_folder_step3, fileshortname + self.name_addition_step3 + '.nc')

                    date = datetime.strptime(fileshortname[17:25], '%Y%m%d')
                    date = date.strftime('%d%b%Y')

                    theta = 'localIncidenceAngle_slv10_' + date

                    processing_filelist = ','.join(processing_filelist)
                    list_bands_vv_multi = ','.join(list_bands_vv_multi)
                    list_bands_vh_multi = ','.join(list_bands_vh_multi)
                    list_bands_vv_norm_multi = ','.join(list_bands_vv_norm_multi)
                    list_bands_vh_norm_multi = ','.join(list_bands_vh_norm_multi)

                    # pdb.set_trace()
                    os.system(self.config.gpt + ' ' + os.path.join(self.config.xml_graph_path, self.config.xml_graph_pre_process_step3) + ' -Pinput="' + processing_filelist + '" -Pinput2="' + file + '" -Poutput="' + outputfile + '" -Ptheta="' + theta + '" -Plist_bands_vv_multi="' + list_bands_vv_multi + '" -Plist_bands_vh_multi="' + list_bands_vh_multi + '" -Plist_bands_vv_norm_multi="' + list_bands_vv_norm_multi + '" -Plist_bands_vh_norm_multi="' + list_bands_vh_norm_multi + '" -Pdate="' + date + '" -Pname_change_vv_single="' + name_change_vv_single + '" -Pname_change_vh_single="' + name_change_vh_single + '" -Pname_change_vv_norm_single="' + name_change_vv_norm_single + '" -Pname_change_vh_norm_single="' + name_change_vh_norm_single + '" -Plist_bands_single_speckle_filter="' + list_bands_single_speckle_filter + '"')
                    print(datetime.now())


    def netcdf_information(self, **kwargs):

        # input folder
        input_folder = self.config.output_folder_step3
        expression = '*.nc'

        filelist = self._create_filelist(input_folder, expression)

        # for loop though all measurement points
        for file in filelist:

            # Divide filename
            filepath, filename, fileshortname, extension = self._decomposition_filename(
                    file)

            filepath2 = self.config.output_folder_step1

            # extract orbitdirection from metadata
            metadata = etree.parse(os.path.join(filepath2,filename[0:79]+'.dim'))
            for i in metadata.findall('Dataset_Sources'):
                for ii in i.findall('MDElem'):
                    for iii in ii.findall('MDElem'):
                        for iiii in iii.findall('MDATTR'):
                            r = iiii.get('name')
                            if r == 'PASS':
                                orbitdir = iiii.text
                                if orbitdir == 'ASCENDING':
                                    orbitdir = 'ASCENDING'
                                elif orbitdir =='DESCENDING':
                                    orbitdir = 'DESCENDING'
                                else:
                                    pass
                            continue

            # extract orbit from metadata
            metadata = etree.parse(os.path.join(filepath2,filename[0:79]+'.dim'))
            for i in metadata.findall('Dataset_Sources'):
                for ii in i.findall('MDElem'):
                    for iii in ii.findall('MDElem'):
                        for iiii in iii.findall('MDATTR'):
                            r = iiii.get('name')
                            if r == 'REL_ORBIT':
                                relorbit = iiii.text


            # extract satellite name from name tag
            if fileshortname[0:3] == 'S1A':
                sat = 'S1A'
            elif fileshortname[0:3] == 'S1B':
                sat = 'S1B'
            else:
                pass

            dset = Dataset(file, 'r+', format="NETCDF4")

            orbitdirection = dset.setncattr_string('orbitdirection', orbitdir)
            relativeorbit = dset.setncattr_string('relativeorbit', relorbit)
            satellite = dset.setncattr_string('satellite', sat)

"""run script"""

if __name__ == "__main__":
    processing = SARPreProcessor(config='sample_config_file.yml')
    # processing.pre_process_step1()
    # processing.pre_process_step2()
    # processing.pre_process_step3()
    # subprocess.call(os.path.join(os.getcwd(),'projection_problem.sh ' + processing.config.output_folder_step3), shell=True)
    # processing.netcdf_information()
    NetcdfStack(input_folder=processing.config.output_folder_step3, output_path=processing.config.output_folder_step3.rsplit('/', 1)[0] , output_filename=processing.config.output_folder_step3.rsplit('/', 2)[1])

    print('finished')











# filtertype = self.config.speckle_filter.multi_temporal.filter
# filtersizex = self.config.speckle_filter.multi_temporal.filtersizex
# filtersizey = self.config.speckle_filter.multi_temporal.filtersizey
# windowsize = self.config.speckle_filter.multi_temporal.windowsize
# targetwindowsize = self.config.speckle_filter.multi_temporal.targetwindowsize
