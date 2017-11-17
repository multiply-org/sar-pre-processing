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

    def __getitem__(self, key):
        """
        Provides dict-style access to attributes
        """
        return getattr(self, key)


class PreProcessor(object):

    def __init__(self, **kwargs):
        self.config = kwargs.get('config', None)
        self._check()
        self._get_config()

        # self.gpt = self.config.gpt

    def _check(self):
        assert self.config is not None, 'ERROR: configuration needs to be provided'

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

        # Check if path of SNAP's graph-processing-tool is specified
        assert self.config.gpt is not None, 'ERROR: path for SNAPs graph-processing-tool is not not specified'

        # Check if path of path to XML files is specified
        assert self.config.xml_graph.path is not None, 'ERROR: path of XML files for processing is not not specified'


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
        # print "Number of found files:", len(filelist)
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

    def _select_year(self, filelist, year):
        """
        Select all S1 data in input_folder of a specific year
        """
        # position of year in filename is hard coded!!!

        filelist_new = []
        for file in filelist:
            filepath, filename, fileshortname, extension = self._decomposition_filename(
                file)
            if filename[17:21] == str(self.config.year):
                filelist_new.append(file)
            else:
                pass

        print('Number of found files for year %s:' %year, len(filelist_new))
        return filelist_new

    def _check_location(self, file, location, output_folder):
        """
        Checks of the area of interest defined by location is contained in file
        file is a map projected jpeg, the xml file containing the projection
        needs to be in the same location as sarfile

        THIS VERSION FINALLY WITH INTERSECT OF POLYGONS OGR
        """

        filepath, filename, fileshortname, extension = self._decomposition_filename(file)

        # # Various file paths and names:
        # (sarfilepath, sarfilename) = os.path.split(sarfile)
        # (sarfileshortname, extension) = os.path.splitext(sarfilename)

        # Get metadata
        # Path to product.xml-file within zipped S1 image
        xml_file = fileshortname + '.SAFE/preview/map-overlay.kml'

        # Path to product.xml file once extracted
        xml_file_extracted = os.path.join(output_folder, xml_file)

        # Extract the zipfile
        try:
            zfile = zipfile.ZipFile(file, 'r')
            zfile.extract(xml_file, output_folder)
            zfile.close()
        except:
            print('zipfile cannot open')
            contained = False
            return contained

        # Parse the xml file
        tree = etree.parse(xml_file_extracted)
        root = tree.getroot()

        # Access corners for Sentinel-1
        # Get bounding box
        for tiepoint in root.iter('{http://www.google.com/kml/ext/2.2}LatLonQuad'):
            child_list = tiepoint.getchildren()
        bounding_box = child_list[0].text
        bounding_box_list = bounding_box.split(' ')
        # WKT requires that last point = first point in polygon, add first point
        wkt_image1 = 'POLYGON((' + bounding_box + ' ' + bounding_box_list[0] + '))'
        # WKT requires other use of comma and spaces in coordinate list
        wkt_image2 = wkt_image1.replace(' ', ';')
        wkt_image3 = wkt_image2.replace(',', ' ')
        wkt_image = wkt_image3.replace(';', ',')

        # Define projections
        datasetEPSG = pyproj.Proj('+init=EPSG:4326')
        locationEPSG = pyproj.Proj('+init=EPSG:4326')

        # Transform coordinates of location into file coordinates
        upper_left_x,  upper_left_y = pyproj.transform(locationEPSG, datasetEPSG, location[0], location[1])
        lower_right_x, lower_right_y = pyproj.transform(locationEPSG, datasetEPSG, location[2], location[3])
        wkt_location = 'POLYGON((' + str(upper_left_x) + ' ' + str(upper_left_y) + ',' + str(upper_left_x) + ' ' + str(lower_right_y) + ',' + str(lower_right_x) + ' ' + str(lower_right_y) + ',' + str(lower_right_x) + ' ' + str(upper_left_y) + ',' + str(upper_left_x) + ' ' + str(upper_left_y) + '))'

        # Use ogr to check if polygon contained
        poly_location = ogr.CreateGeometryFromWkt(wkt_location)
        poly_image = ogr.CreateGeometryFromWkt(wkt_image)
        contained = poly_location.Intersect(poly_image)
        # print contained
        shutil.rmtree(os.path.join(output_folder, fileshortname + '.SAFE'))
        return contained

    def _contain_area_of_interest(self, filelist, location, output_folder):
        """
        Check if all files in input_folder contain area of interest
        """
        filelist_new = []
        for file in filelist:
            contained = self._check_location(file, location, output_folder)
            if contained is False:
                continue
            filelist_new.append(file)
        print('Number of found files containing area of interest: %s' % (len(filelist_new)))
        return filelist_new

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
        input_folder = self.config.input_folder
        assert input_folder is not None, 'ERROR: input folder not specified'
        assert os.path.exists(input_folder)

        # Check if output folder is specified, if not existing create new folder
        output_folder = self.config.output_folder.step1
        assert output_folder is not None, 'ERROR: output folder needs to be specified'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Check if XML file for pre-processing is specified
        assert self.config.xml_graph.pre_process_step1 is not None, 'ERROR: path of XML file for pre-processing step 1 is not not specified'

        # Check if normalisation angle is specified
        assert self.config.normalisation_angle is not None, 'ERROR: normalisation angle not specified in configuration file'

        # Name addition for processed data
        xml_addition = 'GC_RC_No_Su'

        lower_right_y = self.config.region['lr']['lat']
        upper_left_y = self.config.region['ul']['lat']
        upper_left_x = self.config.region['ul']['lon']
        lower_right_x = self.config.region['lr']['lon']
        # todo: how is it with coordinates that go across the datum line ??

        # Coordinates for subset area
        area = self._get_area(lower_right_y, upper_left_y, upper_left_x, lower_right_x)

        # list with all zip files found in input_folder
        filelist = self._create_filelist(input_folder, '*.zip')

        # If Year is specified in config-file pre-processing will be only done for specified year
        try:
            filelist = self._select_year(filelist, self.config.year)
            filelist.sort()
        except AttributeError:
            pass

        # Coordinates for location check
        location = [upper_left_x, upper_left_y, lower_right_x, lower_right_y]

        # list with all zip files that contain area of interest
        filelist = self._contain_area_of_interest(filelist, location, self.config.input_folder)

        # loop to process all files stored in input directory
        for file in filelist:

            print('Scene', filelist.index(file) + 1, 'of', len(filelist))

            # Divide filename
            filepath, filename, fileshortname, extension = self._decomposition_filename(file)

            # Call SNAP routine, xml file
            print('Process ', filename, ' with SNAP.')

            outputfile = os.path.join(output_folder, fileshortname + '_' + xml_addition + '.dim')

            os.system(self.config.gpt + ' ' + os.path.join(self.config.xml_graph.path, self.config.xml_graph.pre_process_step1) + ' -Pinput="' + file + '" -Poutput="' + outputfile + '" -Pangle="' + str(self.config.normalisation_angle) + '" -Parea="POLYGON ((' + area + '))"')

        pdb.set_trace()

    def pre_process_step2(self, **kwargs):

        """
        pre_process_step1 has to be done first

        Pre-process S1 SLC data with SNAP's GPT

        1) co-register pre-processed data

        !!! all files will get metadata of the master image !!! Problem?

        """

        # Name addition for processed data
        xml_addition = 'Co'

        # Check if XML file for pre-processing step 2 is specified
        assert self.config.xml_graph.pre_process_step2 is not None, 'ERROR: path of XML file for pre-processing step 2 is not not specified'

        # Check if output folder for pre_process_step1 is specified
        assert self.config.output_folder.step1 is not None, 'ERROR: output folder of pre-processing step 1 needs to be specified'
        assert os.path.exists(self.config.output_folder.step1)

        # Create new output folder for co-registered data if not existing
        if not os.path.exists(self.config.output_folder.step2):
            os.makedirs(self.config.output_folder.step2)

        # list with all dim files found in output-folder of pre_process_step1
        filelist = self._create_filelist(self.config.output_folder.step1, '*.dim')
        filelist.sort()

        # Set Master image for co-registration
        master = filelist[0]

        # loop to co-register all found images to master image
        for file in filelist:

            print('Scene', filelist.index(file) + 1, 'of', len(filelist))

            # Divide filename
            filepath, filename, fileshortname, extension = self._decomposition_filename(file)

            # Call SNAP routine, xml file
            print('Process ', filename, ' with SNAP.')

            outputfile = os.path.join(self.config.output_folder.step2,fileshortname + '_' + xml_addition + '.dim')

            os.system(self.config.gpt + ' ' + os.path.join(self.config.xml_graph.path, self.config.xml_graph.pre_process_step2) + ' -Pinput="' + master + '" -Pinput2="' + file + '" -Poutput="' + outputfile  + '"')


    def pre_process_step3(self, **kwargs):

        """
        pre_process_step1 and 2 has to be done first

        Pre-process S1 SLC data with SNAP's GPT

        1) apply multi-temporal speckle filter

        """

        # Name addition for processed data
        xml_addition = 'Co'

        # Check if XML file for pre-processing step 3 is specified
        assert self.config.xml_graph.pre_process_step3 is not None, 'ERROR: path of XML file for pre-processing step 3 is not not specified'

        # Check if output folder for pre_process_step2 is specified
        assert self.config.output_folder.step2 is not None, 'ERROR: output folder of pre-processing step 1 needs to be specified'
        assert os.path.exists(self.config.output_folder.step2)

        # Create new output folder for multi-temporal speckle filter data if not existing
        if not os.path.exists(self.config.output_folder.step3):
            os.makedirs(self.config.output_folder.step3)

        # list with all dim files found in output-folder of pre_process_step2
        filelist = self._create_filelist(self.config.output_folder.step2, '*.dim')
        filelist.sort()

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

            outputfile = os.path.join(self.config.output_folder.step3, fileshortname + '_' + xml_addition + '.dim')

            date = datetime.strptime(fileshortname[17:25], '%Y%m%d')
            date = date.strftime('%d%b%Y')

            processing_filelist = ','.join(processing_filelist)
            list_bands_vv = ','.join(list_bands_vv)
            list_bands_vh = ','.join(list_bands_vh)

            os.system(self.config.gpt + ' ' + os.path.join(self.config.xml_graph.path, self.config.xml_graph.pre_process_step3) + ' -Pinput="' + processing_filelist + '" -Pinput2="' + file  + '" -Poutput="' + outputfile + '" -Plist_bands_vv="' + list_bands_vv + '" -Plist_bands_vh="' + list_bands_vh + '" -Pdate="' + date + '"')









        # o.k., now the rest of the preprocessor can be added here
        # to keep things most flexible it would be good to have that in
        # a separate class

        return 'some data'
