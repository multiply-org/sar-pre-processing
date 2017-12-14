"""
Wrapper module to launch preprocessor
"""

import os
import yaml
import fnmatch
import pyproj
import zipfile
import shutil
import ogr
import xml.etree.ElementTree as etree
from datetime import datetime
from file_list_sar_pre_processing import SARList

import pdb

filelist = SARList(config='sample_config_file.yml').create_list()

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

    def __getitem__(self, key):
        """
        Provides dict-style access to attributes
        """
        return getattr(self, key)


class PreProcessor(object):

    def __init__(self, **kwargs):
        self.config = kwargs.get('config', None)
        self.filelist = kwargs.get('filelist', None)
        self._check()
        self._get_config()

    def _check(self):
        assert self.config is not None, 'ERROR: Configuration file needs to be provided'

    def pre_process(self):
        assert False, 'Routine should be implemented in child class'

    def _get_config(self):
        """
        Load configuration from self.config.bb.pre_process()
           writes to self.config.
        """
        with open(self.config, 'r') as cfg:
            self.config = yaml.load(cfg)
            self.config = AttributeDict(**self.config)


class SARPreProcessor(PreProcessor):

    def __init__(self, **kwargs):
        super(SARPreProcessor, self).__init__(**kwargs)

        # Check if output folder is specified
        assert self.config.output_folder is not None, 'ERROR: output folder needs to be specified'

        # Initialise output folder for different preprocessing steps
        # (can be put in the YAML config file if needed)
        self.config.output_folder_step1 = os.path.join(self.config.output_folder, 'step1')
        self.config.output_folder_step2 = os.path.join(self.config.output_folder, 'step2')
        self.config.output_folder_step3 = os.path.join(self.config.output_folder, 'step3')

        # Initialise name of necessary xml-graphs for preprocessing
        # (can be put in the YAML config file if needed)
        self.config.xml_graph_pre_process_step1 = 'pre_process_step1.xml'
        self.config.xml_graph_pre_process_step2 = 'pre_process_step2.xml'
        self.config.xml_graph_pre_process_step3 = 'pre_process_step3.xml'

        # Initialise name addition for output files
        self.name_addition_step1 = '_GC_RC_No_Su'
        self.name_addition_step2 = '_Co'
        self.name_addition_step3 = '_speckle'


        # Check if path of SNAP's graph-processing-tool is specified
        assert self.config.gpt is not None, 'ERROR: path for SNAPs graph-processing-tool is not not specified'

        # Check if path of path to XML files is specified
        assert self.config.xml_graph_path is not None, 'ERROR: path of XML files for processing is not not specified'

        pass

        # TODO PUT THE GRAPH DIRECTORIES AND NAMES IN A SEPARATE CONFIG !!!

        # # xml-processing graph
        # self.xmlgraphpath = '/media/tweiss/Work/python_code/MULTIPLY/pre_processing_Sentinel_1/xml_files/'
        # # the XML config files should gfo somewhere in a specific directory in the multiply-core repo
        # self.xmlgraph = 'preprocess_v01.xml'

    # todo discuss if input/output specification part of processing or part of instantiation of the object itself

    def _create_filelist(self, input_folder, expression):
        """
        Create list containing all files in input_folder (without subfolder) that contain the provided expression within the filename
        """
        filelist = []
        for root, dirnames, filenames in os.walk(input_folder):
            for filename in fnmatch.filter(filenames, expression):
                filelist.append(os.path.join(root, filename))
            break
        print('Number of found files:', len(filelist))
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

        # Check if input folder is specified
        assert self.config.input_folder is not None, 'ERROR: input folder not specified'
        assert os.path.exists(self.config.input_folder)

        # Check if output folder for step1 is specified, if not existing create new folder
        assert self.config.output_folder_step1 is not None, 'ERROR: output folder for step1 needs to be specified'
        if not os.path.exists(self.config.output_folder_step1):
            os.makedirs(self.config.output_folder_step1)

        # Check if XML file for pre-processing is specified
        assert self.config.xml_graph_pre_process_step1 is not None, 'ERROR: path of XML file for pre-processing step 1 is not not specified'

        try:
            lower_right_y = self.config.region['lr']['lat']
            upper_left_y = self.config.region['ul']['lat']
            upper_left_x = self.config.region['ul']['lon']
            lower_right_x = self.config.region['lr']['lon']
            # todo: how is it with coordinates that go across the datum line ??

            # Coordinates for subset area
            area = self._get_area(lower_right_y, upper_left_y, upper_left_x, lower_right_x)
            process_all = 'no'
        except AttributeError:
            print('area of interest not specified, whole images will be processed')
            process_all = 'yes'

        if self.filelist is None:
            print('no filelist specified therefore all images in input folder will be processed')
            self.filelist = self._create_filelist(self.config.input_folder, '*.zip')
            filelist.sort()
        else:
            for file in self.filelist:
                if os.path.exists(file) is True:
            else:
                print('skip processing for %s. File does not exists' % file)



        # loop to process all files stored in input directory
        for file in self.filelist:

            print('Scene', self.filelist.index(file) + 1, 'of', len(self.filelist))

            # Divide filename
            filepath, filename, fileshortname, extension = self._decomposition_filename(file)

            # Call SNAP routine, xml file
            print('Process ', filename, ' with SNAP.')

            outputfile = os.path.join(self.config.output_folder_step1, fileshortname + self.name_addition_step1 + '.dim')

            try:
                normalisation_angle = self.config.normalisation_angle
                if normalisation_angle is None:
                    normalisation_angle = 35
                    print('normalisaton angle not specified, default value of 35 is used for processing')
            except AttributeError:
                normalisation_angle = 35
                print('normalisaton angle not specified, default value of 35 is used for processing')

            if process_all == 'no':
                os.system(self.config.gpt + ' ' + os.path.join(self.config.xml_graph_path, self.config.xml_graph_pre_process_step1) + ' -Pinput="' + file + '" -Poutput="' + outputfile + '" -Pangle="' + str(normalisation_angle) + '" -Parea="POLYGON ((' + area + '))"')
            else:
                os.system(self.config.gpt + ' ' + os.path.join(self.config.xml_graph_path, self.config.xml_graph_pre_process_step1) + ' -Pinput="' + file + '" -Poutput="' + outputfile + '" -Pangle="' + str(normalisation_angle) + '"')

        pdb.set_trace()

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
        assert os.path.exists(self.config.output_folder_step1), 'ERROR: output folder of pre-processing step1 not found'

        # Check if output folder for step2 is specified, if not existing create new folder
        assert self.config.output_folder_step2 is not None, 'ERROR: output folder for step2 needs to be specified'
        if not os.path.exists(self.config.output_folder_step2):
            os.makedirs(self.config.output_folder_step2)

        # Create filelist with all to be processed images
        if self.filelist is None:
            print('no filelist specified therefore all images in output folder step1 will be processed')
            filelist = self._create_filelist(self.config.output_folder_step1, '*.dim')
            filelist.sort()
        else:
            filelist = []
            for file in self.filelist:
                filepath, filename, fileshortname, extension = self._decomposition_filename(file)
                new_file_name = os.path.join(self.config.output_folder_step1, fileshortname + self.name_addition_step1 + '.dim')

                if os.path.exists(new_file_name) is True:
                    filelist.append(new_file_name)
                else:
                    print('skip processing for %s. File does not exists' % file)
            filelist.sort()

        # Set Master image for co-registration
        master = filelist[0]
        pdb.set_trace()
        # loop to co-register all found images to master image
        for file in filelist:
            print('Scene', filelist.index(file) + 1, 'of', len(filelist))

            # Divide filename
            filepath, filename, fileshortname, extension = self._decomposition_filename(file)

            # Call SNAP routine, xml file
            print('Process ', filename, ' with SNAP.')

            outputfile = os.path.join(self.config.output_folder_step2, fileshortname + self.name_addition_step2 + '.dim')

            os.system(self.config.gpt + ' ' + os.path.join(self.config.xml_graph_path, self.config.xml_graph_pre_process_step2) + ' -Pinput="' + master + '" -Pinput2="' + file + '" -Poutput="' + outputfile  + '"')


    def pre_process_step3(self, **kwargs):

        """
        pre_process_step1 and 2 has to be done first

        Pre-process S1 SLC data with SNAP's GPT

        1) apply multi-temporal speckle filter

        """

        # Check if XML file for pre-processing step 3 is specified
        assert self.config.xml_graph_pre_process_step3 is not None, 'ERROR: path of XML file for pre-processing step 3 is not not specified'

        # Check if output folder of pre_process_step1 exists
        assert os.path.exists(self.config.output_folder_step2), 'ERROR: output folder of pre-processing step2 not found'

        # Check if output folder for step2 is specified, if not existing create new folder
        assert self.config.output_folder_step3 is not None, 'ERROR: output folder for step3 needs to be specified'
        if not os.path.exists(self.config.output_folder_step3):
            os.makedirs(self.config.output_folder_step3)

        # list with all dim files found in output-folder of pre_process_step2
        filelist = self._create_filelist(os.path.join(self.config.output_folder, 'step2'), '*.dim')
        filelist.sort()

        # Create filelist with all to be processed images
        if self.filelist is None:
            print('no filelist specified therefore all images in output folder step2 will be processed')
            filelist = self._create_filelist(self.config.output_folder_step2, '*.dim')
        else:
            filelist = []
            for file in self.filelist:
                filepath, filename, fileshortname, extension = self._decomposition_filename(file)
                new_file_name = os.path.join(self.config.output_folder_step2, fileshortname + self.name_addition_step1 + self.name_addition_step2 + '.dim')

                if os.path.exists(new_file_name) is True:
                    filelist.append(new_file_name)
                else:
                    print('skip processing for %s. File does not exists' % file)

        # Sort filelist by date (hard coded position in filename!!!)
        filepath, filename, fileshortname, extension = self._decomposition_filename(filelist[0])
        filelist.sort(key=lambda x: x[len(filepath)+18:len(filepath)+33])

        new_filelist = []

        # loop to apply multi-temporal filtering
        # right now 15 scenes if possible 7 before and 7 after multi-temporal filtered scene, vv and vh polarisation are separated
        # use the speckle filter algorithm metadata? metadata for date might be wrong!!!

        for i, file in enumerate(filelist):

            # apply speckle filter on 15 scenes if possible 7 before and 7 after the scene of interest
            # what happens if there are less then 15 scenes available
            if i < 7:
                processing_filelist = filelist[0:15]
            else:
                if i <= len(filelist)-8:
                    processing_filelist = filelist[i-7:i+8]
                else:
                    processing_filelist = filelist[i-7-(8-(len(filelist)-i)):len(filelist)]

            list_bands_vv = []
            list_bands_vh = []

            for processing_file in processing_filelist:
                filepath, filename, fileshortname, extension = self._decomposition_filename(processing_file)

                self._create_filelist(os.path.join(filepath,fileshortname+'.data'), '*_slv1_*.img')

                # get filename from folder
                # think about better way !!!!
                a, a, band_vv_name, a = self._decomposition_filename(self._create_filelist(os.path.join(filepath,fileshortname+'.data'), '*_slv1_*.img')[0])
                a, a, band_vh_name, a = self._decomposition_filename(self._create_filelist(os.path.join(filepath,fileshortname+'.data'), '*_slv2_*.img')[0])

                list_bands_vv.append(band_vv_name)
                list_bands_vh.append(band_vh_name)

            # Divide filename of file of interest
            filepath, filename, fileshortname, extension = self._decomposition_filename(file)

            outputfile = os.path.join(self.config.output_folder_step3, fileshortname + self.name_addition_step3 + '.nc')

            date = datetime.strptime(fileshortname[17:25], '%Y%m%d')
            date = date.strftime('%d%b%Y')

            processing_filelist = ','.join(processing_filelist)
            list_bands_vv = ','.join(list_bands_vv)
            list_bands_vh = ','.join(list_bands_vh)

            os.system(self.config.gpt + ' ' + os.path.join(self.config.xml_graph_path, self.config.xml_graph_pre_process_step3) + ' -Pinput="' + processing_filelist + '" -Pinput2="' + file  + '" -Poutput="' + outputfile + '" -Plist_bands_vv="' + list_bands_vv + '" -Plist_bands_vh="' + list_bands_vh + '" -Pdate="' + date + '"')





        # o.k., now the rest of the preprocessor can be added here
        # to keep things most flexible it would be good to have that in
        # a separate class

        return 'some data'
