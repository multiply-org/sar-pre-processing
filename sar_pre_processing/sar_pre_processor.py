"""
Wrapper module to launch preprocessor
"""

import logging
import os
import pkg_resources
import yaml
import fnmatch
import xml.etree.ElementTree as ETree
from datetime import datetime
from .attribute_dict import AttributeDict
from .file_list_sar_pre_processing import SARList
import subprocess
from netCDF4 import Dataset
from typing import List, Optional
from .netcdf_stack import NetcdfStackCreator
import math
import numpy as np

logging.getLogger().setLevel(logging.INFO)
# Set up logging
component_progress_logger = logging.getLogger('ComponentProgress')
component_progress_logger.setLevel(logging.INFO)
component_progress_formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
component_progress_logging_handler = logging.StreamHandler()
component_progress_logging_handler.setLevel(logging.INFO)
component_progress_logging_handler.setFormatter(component_progress_formatter)
component_progress_logger.addHandler(component_progress_logging_handler)


class PreProcessor(object):

    def __init__(self, **kwargs):
        self.config_file = kwargs.get('config', None)
        self.filelist = kwargs.get('filelist', None)
        self.use_user_defined_graphs = kwargs.get('use_user_defined_graphs', 'no')
        self._check()
        self._load_config()
        if kwargs.get('input', None) is not None:
            self.config.input_folder = kwargs.get('input', None)
        if kwargs.get('output', None) is not None:
            self.config.output_folder = kwargs.get('output', None)

    def _check(self):
        assert self.config_file is not None, 'ERROR: Configuration file needs to be provided'

    @staticmethod
    def pre_process():
        assert False, 'Routine should be implemented in child class'

    def _load_config(self):
        """
        Load configuration and writes to self.config.
        """
        with open(self.config_file, 'r') as cfg:
            self.config = yaml.safe_load(cfg)
            if 'SAR' in self.config:
                self.config = AttributeDict(**self.config['SAR'])
            else:
                self.config = AttributeDict(**self.config)


class SARPreProcessor(PreProcessor):

    def __init__(self, **kwargs):
        super(SARPreProcessor, self).__init__(**kwargs)

        # Check if output folder is specified
        assert self.config.output_folder is not None, 'ERROR: output folder needs to be specified'

        # Initialize output folder for different preprocessing steps
        self.config.output_folder_step1 = os.path.join(self.config.output_folder, 'step1')
        self.config.output_folder_step2 = os.path.join(self.config.output_folder, 'step2')
        self.config.output_folder_step3 = os.path.join(self.config.output_folder, 'step3')

        # Initialize name of necessary xml-graphs for preprocessing
        self._configure_config_graph('pre_process_step1', 'pre_process_step1.xml')
        self._configure_config_graph('pre_process_step1_border', 'pre_process_step1_border.xml')
        self._configure_config_graph('pre_process_step2', 'pre_process_step2.xml')
        self._configure_config_graph('pre_process_step3', 'pre_process_step3.xml')
        self._configure_config_graph('pre_process_step3_single_file', 'pre_process_step3_single_file.xml')

        # Initialize name addition for output files
        self.name_addition_step1 = '_GC_RC_No_Su'
        self.name_addition_step2 = '_Co'
        self.name_addition_step3 = '_speckle'

        # Check if path of SNAP's graph-processing-tool is specified
        if not self.config.has_entry('gpt'):
            # test that gpt is available as parameter
            try:
                return_code = subprocess.call("gpt Subset -h")
                if return_code > 0:
                    raise UserWarning('ERROR: path for SNAPs graph-processing-tool is not specified correctly')
            except FileNotFoundError:
                raise UserWarning('ERROR: path for SNAPs graph-processing-tool is not specified correctly')

    def _configure_config_graph(self, key_name: str, default_name: str):
        """
        put location of processing xml graphs within config
        check if user has specified personal xml graphs otherwise use default ones
        """
        if self.config.use_user_defined_graphs == 'yes':
            if self.config.has_entry(key_name):
                if not os.path.exists(self.config[key_name]):
                    if self.config.has_entry('xml_graph_path'):
                        graph_path = os.path.join(self.config.xml_graph_path, self.config[key_name])
                        if not os.path.exists(graph_path):
                            raise UserWarning(f'Could not determine location of user defined {self.config[key_name]}.')
                        self.config.add_entry(key_name, graph_path)
                    else:
                        raise UserWarning(f'Could not determine location of {self.config[key_name]}.')
        else:
            default_graph = pkg_resources.resource_filename('sar_pre_processing.default_graphs', default_name)
            self.config.add_entry(key_name, default_graph)

    @staticmethod
    def _create_file_list(input_folder, expression):
        """
        Create list containing all files in input_folder (without subfolder)
        that contain the provided expression within the filename
        """
        file_list = []
        for root, dirnames, filenames in os.walk(input_folder):
            for filename in fnmatch.filter(filenames, expression):
                file_list.append(os.path.join(root, filename))
            break
        return file_list

    @staticmethod
    def _decompose_filename(file):
        """
        Decomposition of filename including path in
        path, filename, fileshortname and extension
        """
        (filepath, filename) = os.path.split(file)
        (fileshortname, extension) = os.path.splitext(filename)
        return filepath, filename, fileshortname, extension

    @staticmethod
    def _get_area(lat_min, lat_max, lon_min, lon_max):
        """
        Change input coordinates for subset operator"
        """
        assert lat_min <= lat_max, 'ERROR: invalid lat'
        assert lon_min <= lon_max, 'ERROR: invalid lon'
        return '%.14f %.14f,%.14f %.14f,%.14f %.14f,%.14f %.14f,%.14f %.14f' % \
               (lon_min, lat_min, lon_min, lat_max, lon_max, lat_max, lon_max, lat_min, lon_min, lat_min)

    def create_processing_file_list(self):
        """
        create a list with all to be processed file names
        """
        self.file_list = SARList(config=self.config).create_list()
        return self.file_list

    def pre_process_step1(self):
        """
        Pre-process S1 SLC data with SNAP's GPT

        1) apply precise orbit file
        2) thermal noise removal
        3) calibration
        4) TOPSAR-Deburst
        5) Geometric Terrain Correction
        6) Radiometric Correction (after kellndorfer et al.)
        7) backscatter normalisation on specified angle in config file (based on Lambert's Law) (optional)

        """

        # Check if input folder is specified
        assert self.config.input_folder is not None, 'ERROR: input folder not specified'
        assert os.path.exists(self.config.input_folder)

        # Check if output folder for step1 is specified, create one if non existing
        assert self.config.output_folder_step1 is not None, 'ERROR: output folder for step1 needs to be specified'
        if not os.path.exists(self.config.output_folder_step1):
            os.makedirs(self.config.output_folder_step1)

        # Check if XML file for pre-processing is specified
        assert self.config.pre_process_step1 is not None, \
            'ERROR: path of XML file for pre-processing step 1 is not not specified'

        area = None
        try:
            if self.config.region.subset == 'yes':
                lower_right_y = self.config.region['lr']['lat']
                upper_left_y = self.config.region['ul']['lat']
                upper_left_x = self.config.region['ul']['lon']
                lower_right_x = self.config.region['lr']['lon']
                area = self._get_area(lower_right_y, upper_left_y, upper_left_x, lower_right_x)
                logging.info('area of interest specified')
            else:
                logging.info('area of interest not specified, whole images will be processed')
        except AttributeError:
            logging.info('area of interest not specified, whole images will be processed')

        # loop to process all files stored in input directory
        try:
            normalisation_angle = self.config.normalisation_angle
            if normalisation_angle is None:
                normalisation_angle = '35'
                logging.info('normalisation angle not specified, default value of 35 is used for processing')
        except AttributeError:
            normalisation_angle = '35'
            logging.info('normalisation angle not specified, default value of 35 is used for processing')
        total_num_files = len(self.file_list[0]) + len(self.file_list[1])
        for i, file in enumerate(self.file_list[0]):
            component_progress_logger.info(f'{int((i / total_num_files) * 100)}')
            self._gpt_step1(file, None, area, normalisation_angle, self.config.pre_process_step1)

        for i, file in enumerate(self.file_list[1][::2]):
            component_progress_logger.info(f'{int(((len(self.file_list[0]) + i) / total_num_files) * 100)}')
            file_list2 = self.file_list[1][1::2]
            if i < len(file_list2):
                file2 = file_list2[i]
                self._gpt_step1(file, file2, area, normalisation_angle, self.config.pre_process_step1_border)

    def _gpt_step1(self, file: str, file2: str, area: str, normalisation_angle: str, script_path: str):
        """
        run preprocessing step1
        """
        # Divide filename
        filepath, filename, fileshortname, extension = self._decompose_filename(file)

        # Call SNAP routine, xml file
        logging.info(f'Process {filename} with SNAP.')
        output_file = os.path.join(self.config.output_folder_step1,
                                   fileshortname + self.name_addition_step1 + '.dim')
        area_part = ''
        if area is not None:
            area_part = '-Parea="POLYGON ((' + area + '))" '
        file2_part = ''
        if file2 is not None:
            file2_part = ' -Pinput2="' + file2 + '"'
        if self.use_user_defined_graphs == 'yes':
            call = '"' + self.config.gpt + '" "' + script_path + \
               '" -Pinput="' + file + '"' + file2_part + ' -Poutput="' + output_file + \
               '" ' + area_part + '-c 2G -x'
        else:
            call = '"' + self.config.gpt + '" "' + script_path + \
               '" -Pinput="' + file + '"' + file2_part + ' -Poutput="' + output_file + \
               '" -Pangle="' + normalisation_angle + '" ' + area_part + '-c 2G -x'
        return_code = subprocess.call(call, shell=True)
        logging.info(return_code)

    def pre_process_step2(self):
        """
        pre_process_step1 has to be done first

        Pre-process S1 SLC data with SNAP's GPT

        1) co-register pre-processed data

        !!! all files will get metadata of the master image !!!
        That is how SNAP does it! Metadata will be corrected within
        netcdf output files at the end of the preprocessing chain
        (def add_netcdf_information)
        """
        # Check if XML file for pre-processing step 2 is specified
        assert self.config.pre_process_step2 is not None, \
            'ERROR: path of XML file for pre-processing step 2 is not not specified'

        # Check if output folder of pre_process_step1 exists
        assert os.path.exists(self.config.output_folder_step1), \
            'ERROR: output folder of pre-processing step1 not found'

        # Check if output folder for step2 is specified, create if non existing
        assert self.config.output_folder_step2 is not None, 'ERROR: output folder for step2 needs to be specified'
        if not os.path.exists(self.config.output_folder_step2):
            os.makedirs(self.config.output_folder_step2)

        # Create file_list with all to be processed images
        if self.file_list is None:
            file_list = self._create_file_list(self.config.output_folder_step1, '*.dim')
            file_list.sort()
            logging.info('no file list specified, therefore all images in output folder step1 will be processed')
        else:
            file_list = []
            for list in self.file_list:
                for file in list:
                    filepath, filename, file_short_name, extension = self._decompose_filename(file)
                    new_file_name = os.path.join(
                        self.config.output_folder_step1, file_short_name + self.name_addition_step1 + '.dim')
                    if os.path.exists(new_file_name) is True:
                        file_list.append(new_file_name)
                    else:
                        logging.info(f'skip processing for {file}. File does not exist')
            file_list.sort()

        if len(file_list) == 0:
            logging.info('No valid files found for pre-processing step 2.')
            return

        if len(file_list) == 1:
            self.config.single_file = 'yes'
            logging.info('Single image, no co-register of images necessary')
            return

        if len(file_list) > 1:
            self.config.single_file = 'no'

        # Set Master image for co-registration
        master = file_list[0]

        # loop to co-register all found images to master image
        for i, file in enumerate(file_list):
            component_progress_logger.info(f'{int((i / len(file_list)) * 100)}')
            logging.info(f'Scene {file_list.index(file) + 1} of {len(file_list)}')

            # Divide filename
            filepath, filename, file_short_name, extension = self._decompose_filename(file)

            # Call SNAP routine, xml file
            logging.info(f'Process {filename} with SNAP.')
            output_file = os.path.join(
                self.config.output_folder_step2, file_short_name + self.name_addition_step2 + '.dim')

            if self.use_user_defined_graphs == 'yes':
                file_format = 'NetCDF4-CF'
            else:
                file_format = 'BEAM-DIMAP'

            call = '"' + self.config.gpt + '" "' + self.config.pre_process_step2 + \
                   '" -Pinput="' + master + '" -Pinput2="' + file + '" -Poutput="' + output_file + '" -Pfile_format="' + file_format + '" -c 2G -x'
            return_code = subprocess.call(call, shell=True)
            logging.info(return_code)
            logging.info(datetime.now())

    def pre_process_step3(self):
        """
        pre_process_step1 and 2 has to be done first

        Pre-process S1 SLC data with SNAP's GPT

        1) apply multi-temporal speckle filter / single speckle filter

        """
        # Check if output folder of pre_process_step1 exists
        assert os.path.exists(self.config.output_folder_step2), 'ERROR: output folder of pre-processing step2 not found'

        # Check if output folder for step3 is specified, create if non existing
        assert self.config.output_folder_step3 is not None, 'ERROR: output folder for step3 needs to be specified'
        if not os.path.exists(self.config.output_folder_step3):
            os.makedirs(self.config.output_folder_step3)

        if self.use_user_defined_graphs == 'yes':
            logging.info('combination of default multi temporal speckle filter and user defined graphs is not supported yet')
            return

        if (self.config.speckle_filter.multi_temporal.apply == 'yes') and (self.config.single_file == 'no'):
            # Check if XML file for pre-processing step 3 is specified
            assert self.config.pre_process_step3 is not None, \
                'ERROR: path of XML file for pre-processing step 3 is not not specified'

            # Create filelist with all to be processed images
            if self.file_list is None:
                file_list = self._create_file_list(self.config.output_folder_step2, '*.dim')
                logging.info('no file list specified, therefore all images in output folder step2 will be processed')
            else:
                file_list = []
                for list in self.file_list:
                    for file in list:
                        file_path, filename, file_short_name, extension = self._decompose_filename(file)
                        new_file_name = os.path.join(self.config.output_folder_step2, file_short_name +
                                                     self.name_addition_step1 + self.name_addition_step2 + '.dim')
                        if os.path.exists(new_file_name) is True:
                            file_list.append(new_file_name)
                        else:
                            logging.info(f'skip processing for {file}. File {new_file_name} does not exist.')

            # Sort file list by date (hard coded position in filename!)
            file_path, filename, file_short_name, extension = self._decompose_filename(file_list[0])
            file_list.sort(key=lambda x: x[len(file_path) + 18:len(file_path) + 33])
            file_list_old = file_list


            # loop to apply multi-temporal filtering
            # vv and vh polarisation are separated
            for i, file in enumerate(file_list):
                component_progress_logger.info(f'{int((i / len(file_list)) * 100)}')
                files_temporal_filter = int(self.config.speckle_filter.multi_temporal.files)
                if len(file_list) <= files_temporal_filter:
                    processing_file_list = file_list[0:files_temporal_filter]
                elif i < math.floor(files_temporal_filter / 2):
                    processing_file_list = file_list[0:files_temporal_filter]
                elif i <= len(file_list) - math.ceil(files_temporal_filter / 2):
                    processing_file_list = file_list[i - math.floor(files_temporal_filter / 2):i + math.ceil(
                        files_temporal_filter / 2)]
                else:
                    processing_file_list = file_list[i - math.floor(files_temporal_filter / 2) - (
                            math.ceil(files_temporal_filter / 2) - (len(file_list) - i)):len(file_list)]
                file_path, filename, file_short_name, extension = self._decompose_filename(file)
                a, a, b, a = self._decompose_filename(self._create_file_list(
                    os.path.join(file_path, file_short_name + '.data'), '*_slv1_*.img')[0])
                a, a, c, a = self._decompose_filename(self._create_file_list(
                    os.path.join(file_path, file_short_name + '.data'), '*_slv2_*.img')[0])
                a, a, d, a = self._decompose_filename(self._create_file_list(
                    os.path.join(file_path, file_short_name + '.data'), '*_slv3_*.img')[0])
                a, a, e, a = self._decompose_filename(self._create_file_list(
                    os.path.join(file_path, file_short_name + '.data'), '*_slv4_*.img')[0])
                list_bands_single_speckle_filter = ','.join([b, c, d, e])

                name_change_vv_single = d
                name_change_vh_single = e
                name_change_vv_norm_single = b
                name_change_vh_norm_single = c

                list_bands_vv_multi = []
                list_bands_vh_multi = []

                list_bands_vv_norm_multi = []
                list_bands_vh_norm_multi = []

                for processing_file in processing_file_list:
                    file_path, filename, file_short_name, extension = self._decompose_filename(processing_file)

                    # get filename from folder (think about better way!)
                    a, a, band_vv_name_multi, a = self._decompose_filename(self._create_file_list(
                        os.path.join(file_path, file_short_name + '.data'), '*_slv3_*.img')[0])
                    a, a, band_vh_name_multi, a = self._decompose_filename(self._create_file_list(
                        os.path.join(file_path, file_short_name + '.data'), '*_slv4_*.img')[0])
                    a, a, band_vv_name_norm_multi, a = self._decompose_filename(self._create_file_list(
                        os.path.join(file_path, file_short_name + '.data'), '*_slv1_*.img')[0])
                    a, a, band_vh_name_norm_multi, a = self._decompose_filename(self._create_file_list(
                        os.path.join(file_path, file_short_name + '.data'), '*_slv2_*.img')[0])
                    list_bands_vv_multi.append(band_vv_name_multi)
                    list_bands_vh_multi.append(band_vh_name_multi)

                    list_bands_vv_norm_multi.append(band_vv_name_norm_multi)
                    list_bands_vh_norm_multi.append(band_vh_name_norm_multi)

                # Divide filename of file of interest
                file_path, filename, file_short_name, extension = self._decompose_filename(file)

                output_file = os.path.join(
                    self.config.output_folder_step3, file_short_name + self.name_addition_step3 + '.nc')

                date = datetime.strptime(file_short_name[17:25], '%Y%m%d')
                date = date.strftime('%d%b%Y')

                theta = 'localIncidenceAngle_slv10_' + date

                processing_file_list = ','.join(processing_file_list)
                list_bands_vv_multi = ','.join(list_bands_vv_multi)
                list_bands_vh_multi = ','.join(list_bands_vh_multi)
                list_bands_vv_norm_multi = ','.join(list_bands_vv_norm_multi)
                list_bands_vh_norm_multi = ','.join(list_bands_vh_norm_multi)

                call = '"' + self.config.gpt + '" "' + self.config.pre_process_step3 + \
                       '" -Pinput="' + processing_file_list + '" -Pinput2="' + file + \
                       '" -Poutput="' + output_file + '" -Ptheta="' + theta + \
                       '" -Plist_bands_vv_multi="' + list_bands_vv_multi + \
                       '" -Plist_bands_vh_multi="' + list_bands_vh_multi + \
                       '" -Plist_bands_vv_norm_multi="' + list_bands_vv_norm_multi + \
                       '" -Plist_bands_vh_norm_multi="' + list_bands_vh_norm_multi + '" -Pdate="' + date + \
                       '" -Pname_change_vv_single="' + name_change_vv_single + \
                       '" -Pname_change_vh_single="' + name_change_vh_single + \
                       '" -Pname_change_vv_norm_single="' + name_change_vv_norm_single + \
                       '" -Pname_change_vh_norm_single="' + name_change_vh_norm_single + \
                       '" -Plist_bands_single_speckle_filter="' + list_bands_single_speckle_filter + '" -c 2G -x'
                return_code = subprocess.call(call, shell=True)
                logging.info(return_code)
                logging.info(datetime.now())


        elif self.config.single_file == 'yes':
            if self.config.speckle_filter.multi_temporal.apply == 'yes':
                self.config.speckle_filter.multi_temporal.apply = 'no'
                logging.info('multi temporal filter cannot applied to a single image, just single speckle filter is applied')

            # Check if XML file for pre-processing step 3 is specified
            assert self.config.pre_process_step3_single_file is not None, \
                'ERROR: path of XML file for pre-processing step 3 is not not specified'

            # Create filelist with all to be processed images
            if self.file_list is None:
                file_list = self._create_file_list(self.config.output_folder_step1, '*.dim')
                logging.info('no file list specified, therefore all images in output folder step1 will be processed')
            else:
                file_list = []
                for list in self.file_list:
                    for file in list:
                        file_path, filename, file_short_name, extension = self._decompose_filename(file)
                        new_file_name = os.path.join(self.config.output_folder_step1, file_short_name +
                                                     self.name_addition_step1 + '.dim')
                        if os.path.exists(new_file_name) is True:
                            file_list.append(new_file_name)
                        else:
                            logging.info(f'skip processing for {file}. File {new_file_name} does not exist.')

            # Sort file list by date (hard coded position in filename!)
            file_path, filename, file_short_name, extension = self._decompose_filename(file_list[0])
            file_list.sort(key=lambda x: x[len(file_path) + 18:len(file_path) + 33])
            file_list_old = file_list

            # loop to apply multi-temporal filtering
            # vv and vh polarisation are separated
            for i, file in enumerate(file_list):
                component_progress_logger.info(f'{int((i / len(file_list)) * 100)}')

                a, a, b, a = self._decompose_filename(self._create_file_list(
                    os.path.join(file_path, file_short_name + '.data'), '*vv_kelln_norm*.img')[0])
                a, a, c, a = self._decompose_filename(self._create_file_list(
                    os.path.join(file_path, file_short_name + '.data'), '*vh_kelln_norm*.img')[0])
                a, a, d, a = self._decompose_filename(self._create_file_list(
                    os.path.join(file_path, file_short_name + '.data'), '*_vv_kelln.img')[0])
                a, a, e, a = self._decompose_filename(self._create_file_list(
                    os.path.join(file_path, file_short_name + '.data'), '*_vh_kelln.img')[0])
                list_bands_single_speckle_filter = ','.join([b, c, d, e])

                name_change_vv_single = d
                name_change_vh_single = e
                name_change_vv_norm_single = b
                name_change_vh_norm_single = c

                # Divide filename of file of interest
                file_path, filename, file_short_name, extension = self._decompose_filename(file)

                output_file = os.path.join(
                    self.config.output_folder_step3, file_short_name + self.name_addition_step3 + '.nc')

                date = datetime.strptime(file_short_name[17:25], '%Y%m%d')
                date = date.strftime('%d%b%Y')

                theta = 'localIncidenceAngle'

                call = '"' + self.config.gpt + '" "' + self.config.pre_process_step3_single_file + \
                       '" -Pinput2="' + file + \
                       '" -Poutput="' + output_file + '" -Ptheta="' + theta + \
                       '" -Pname_change_vv_single="' + name_change_vv_single + \
                       '" -Pname_change_vh_single="' + name_change_vh_single + \
                       '" -Pname_change_vv_norm_single="' + name_change_vv_norm_single + \
                       '" -Pname_change_vh_norm_single="' + name_change_vh_norm_single + \
                       '" -Plist_bands_single_speckle_filter="' + list_bands_single_speckle_filter + '" -c 2G -x'
                return_code = subprocess.call(call, shell=True)
                logging.info(return_code)
                logging.info(datetime.now())

        elif self.config.speckle_filter.multi_temporal.apply == 'no':
            # Check if XML file for pre-processing step 3 is specified
            assert self.config.pre_process_step3_single_file is not None, \
                'ERROR: path of XML file for pre-processing step 3 is not not specified'

            # Create filelist with all to be processed images
            if self.file_list is None:
                file_list = self._create_file_list(self.config.output_folder_step2, '*.dim')
                logging.info('no file list specified, therefore all images in output folder step2 will be processed')
            else:
                file_list = []
                for list in self.file_list:
                    for file in list:
                        file_path, filename, file_short_name, extension = self._decompose_filename(file)
                        new_file_name = os.path.join(self.config.output_folder_step2, file_short_name +
                                                     self.name_addition_step1 + self.name_addition_step2 + '.dim')
                        if os.path.exists(new_file_name) is True:
                            file_list.append(new_file_name)
                        else:
                            logging.info(f'skip processing for {file}. File {new_file_name} does not exist.')

            # Sort file list by date (hard coded position in filename!)
            file_path, filename, file_short_name, extension = self._decompose_filename(file_list[0])
            file_list.sort(key=lambda x: x[len(file_path) + 18:len(file_path) + 33])
            file_list_old = file_list


            # loop to apply multi-temporal filtering
            # vv and vh polarisation are separated
            for i, file in enumerate(file_list):
                component_progress_logger.info(f'{int((i / len(file_list)) * 100)}')
                files_temporal_filter = int(self.config.speckle_filter.multi_temporal.files)
                if len(file_list) <= files_temporal_filter:
                    processing_file_list = file_list[0:files_temporal_filter]
                elif i < math.floor(files_temporal_filter / 2):
                    processing_file_list = file_list[0:files_temporal_filter]
                elif i <= len(file_list) - math.ceil(files_temporal_filter / 2):
                    processing_file_list = file_list[i - math.floor(files_temporal_filter / 2):i + math.ceil(
                        files_temporal_filter / 2)]
                else:
                    processing_file_list = file_list[i - math.floor(files_temporal_filter / 2) - (
                            math.ceil(files_temporal_filter / 2) - (len(file_list) - i)):len(file_list)]
                file_path, filename, file_short_name, extension = self._decompose_filename(file)
                a, a, b, a = self._decompose_filename(self._create_file_list(
                    os.path.join(file_path, file_short_name + '.data'), '*_slv1_*.img')[0])
                a, a, c, a = self._decompose_filename(self._create_file_list(
                    os.path.join(file_path, file_short_name + '.data'), '*_slv2_*.img')[0])
                a, a, d, a = self._decompose_filename(self._create_file_list(
                    os.path.join(file_path, file_short_name + '.data'), '*_slv3_*.img')[0])
                a, a, e, a = self._decompose_filename(self._create_file_list(
                    os.path.join(file_path, file_short_name + '.data'), '*_slv4_*.img')[0])
                list_bands_single_speckle_filter = ','.join([b, c, d, e])

                name_change_vv_single = d
                name_change_vh_single = e
                name_change_vv_norm_single = b
                name_change_vh_norm_single = c

                # Divide filename of file of interest
                file_path, filename, file_short_name, extension = self._decompose_filename(file)

                output_file = os.path.join(
                    self.config.output_folder_step3, file_short_name + self.name_addition_step3 + '.nc')

                date = datetime.strptime(file_short_name[17:25], '%Y%m%d')
                date = date.strftime('%d%b%Y')

                theta = 'localIncidenceAngle_slv10_' + date

                call = '"' + self.config.gpt + '" "' + self.config.pre_process_step3_single_file + \
                       '" -Pinput2="' + file + \
                       '" -Poutput="' + output_file + '" -Ptheta="' + theta + \
                       '" -Pname_change_vv_single="' + name_change_vv_single + \
                       '" -Pname_change_vh_single="' + name_change_vh_single + \
                       '" -Pname_change_vv_norm_single="' + name_change_vv_norm_single + \
                       '" -Pname_change_vh_norm_single="' + name_change_vh_norm_single + \
                       '" -Plist_bands_single_speckle_filter="' + list_bands_single_speckle_filter + '" -c 2G -x'
                return_code = subprocess.call(call, shell=True)
                logging.info(return_code)
                logging.info(datetime.now())

    def solve_projection_problem(self):
        """
        solve projection problem of created NetCDF file
        """
        sh_file = pkg_resources.resource_filename('sar_pre_processing', 'solve_projection_problem.sh')
        subprocess.call(sh_file + ' ' + self.config.output_folder_step3, shell=True)

    def add_netcdf_information(self):
        """
        Add information from original S1 SLC image to processed NetCDF file.
        - update date information (wrong date information were stored due to coregistration process)
        - orbitdirection (ASCENDING, DESCENDING)
        - relative orbit
        - Satellite (S1A, S1B)
        - Frequency
        """
        # input folder
        input_folder = self.config.output_folder_step3
        expression = '*.nc'
        file_list = self._create_file_list(input_folder, expression)

        # for loop through all measurement points
        for file in file_list:
            # Divide filename
            file_path, filename, file_short_name, extension = self._decompose_filename(file)
            file_path2 = self.config.output_folder_step1

            # extract date from filename
            start_date = datetime.strptime(file_short_name[17:32], '%Y%m%dT%H%M%S')
            stop_date = datetime.strptime(file_short_name[33:48], '%Y%m%dT%H%M%S')

            data_set = Dataset(file, 'r+', format="NETCDF4")

            # update date information
            try:
                data_set.delncattr('start_date')
                data_set.delncattr('stop_date')
            except RuntimeError:
                pass
            data_set.setncattr_string('date', str(start_date))

            # extract orbit direction from metadata
            metadata = ETree.parse(os.path.join(file_path2, filename[0:79] + '.dim'))
            for i in metadata.findall('Dataset_Sources'):
                for ii in i.findall('MDElem'):
                    for iii in ii.findall('MDElem'):
                        for iiii in iii.findall('MDATTR'):
                            r = iiii.get('name')
                            if r == 'PASS':
                                orbit_dir = iiii.text
                                data_set.setncattr_string('orbitdirection', orbit_dir)
                            continue

            # extract orbit from metadata
            metadata = ETree.parse(os.path.join(file_path2, filename[0:79] + '.dim'))
            for i in metadata.findall('Dataset_Sources'):
                for ii in i.findall('MDElem'):
                    for iii in ii.findall('MDElem'):
                        for iiii in iii.findall('MDATTR'):
                            r = iiii.get('name')
                            if r == 'REL_ORBIT':
                                relorbit = iiii.text
                                data_set.setncattr_string('relativeorbit', relorbit)

            # extract frequency from metadata
            metadata = ETree.parse(os.path.join(file_path2, filename[0:79] + '.dim'))
            for i in metadata.findall('Dataset_Sources'):
                for ii in i.findall('MDElem'):
                    for iii in ii.findall('MDElem'):
                        for iiii in iii.findall('MDATTR'):
                            r = iiii.get('name')
                            if r == 'radar_frequency':
                                frequency = float(iiii.text) / 1000.
                                data_set.setncattr_string('frequency', str(frequency))

            # extract satellite name from name tag
            if file_short_name[0:3] == 'S1A':
                data_set.setncattr_string('satellite', 'S1A')
            elif file_short_name[0:3] == 'S1B':
                data_set.setncattr_string('satellite', 'S1B')

            try:
                crs_var = data_set.createVariable('crs', np.int32, ())
                crs_var.standard_name = 'crs'
                crs_var.grid_mapping_name = 'latitude_longitude'
                crs_var.crs_wkt = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'
            except RuntimeError:
                pass

            for x in data_set.variables.keys():
                if x == 'lat' or x == 'lon' or x == 'crs':
                    pass
                else:
                    data_set[x].grid_mapping = 'crs'

            data_set.close()


    def create_netcdf_stack(self, filename: Optional[str] = None):
        """
        create one NetCDF stack file from output of step3
        Orbitdirection: '0 = Ascending, 1 = Descending'
        Satellite: '0 = Sentinel 1A, 1 = Sentinel 1B'
        """

        if self.use_user_defined_graphs == 'yes':
            if filename is None:
                filename = self.config.output_folder_step2.rsplit('/', 2)[1]
            stack_creator = NetcdfStackCreator(input_folder=self.config.output_folder_step2, output_path=self.config.output_folder_step2.rsplit('/', 1)[0], output_filename=filename, temporal_filter=self.config.speckle_filter.multi_temporal.apply)
        else:
            if filename is None:
                filename = self.config.output_folder_step3.rsplit('/', 2)[1]
            stack_creator = NetcdfStackCreator(input_folder=self.config.output_folder_step3, output_path=self.config.output_folder_step3.rsplit('/', 1)[0], output_filename=filename, temporal_filter=self.config.speckle_filter.multi_temporal.apply)
        stack_creator.create_netcdf_stack()

