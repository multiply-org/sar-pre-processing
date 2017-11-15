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


    def pre_process(self, **kwargs):

        """
        Keyword parameters
        ----------
        input : str
            name of directory where the downloaded SAR data is
            located
        output : str
            name of directory where to put results
        """

        # Check if input folder is specified
        input_folder = self.config.input_folder
        assert input_folder is not None, 'ERROR: input folder not specified'
        assert os.path.exists(input_folder)

        # Check if output folder is specified, if not existing create new folder
        output_folder = self.config.output_folder
        assert output_folder is not None, 'ERROR: output folder needs to be specified'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Check if path of SNAP's graph-processing-tool is specified
        assert self.config.gpt is not None, 'ERROR: path for SNAPs graph-processing-tool is not not specified'

        # Check if path of XML files is specified
        assert self.config.xml_graph.path is not None, 'ERROR: path of XML files for processing is not not specified'

        # Check if XML file for pre-processing is specified
        assert self.config.xml_graph.pre_processing is not None, 'ERROR: path of XML files for processing is not not specified'

        # Check if XML file for pre-processing is specified
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
        filelist = self._contain_area_of_interest(filelist, location, self.config.output_folder)

        # loop to process all files stored in input directory
        for file in filelist:

            print('Scene', filelist.index(file) + 1, 'of', len(filelist))

            # Divide filename
            filepath, filename, fileshortname, extension = self._decomposition_filename(file)

            # Call SNAP routine, xml file
            print('Process ', filename, ' with SNAP.')

            outputfile = os.path.join(output_folder, fileshortname + '_' + xml_addition + '.dim')

            os.system(self.config.gpt + ' ' + os.path.join(self.config.xml_graph.path, self.config.xml_graph.pre_processing) + ' -Pinput="' + file + '" -Poutput="' + outputfile + '" -Pangle="' + str(self.config.normalisation_angle) + '" -Parea="POLYGON ((' + area + '))"')

        pdb.set_trace()









        # o.k., now the rest of the preprocessor can be added here
        # to keep things most flexible it would be good to have that in
        # a separate class

        return 'some data'
