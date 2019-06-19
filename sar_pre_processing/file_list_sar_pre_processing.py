"""
Create List of SAR data which will be processed by sar_pre_processer module
"""

import os
import yaml
import fnmatch
import pyproj
import zipfile
import shutil
# import ogr
import xml.etree.ElementTree as etree
from datetime import datetime
from osgeo import ogr

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

class SARList(object):

    def __init__(self, **kwargs):
        self.config = kwargs.get('config', None)
        self._load_config()
        self._check()

    def _check(self):
        assert self.config is not None, 'ERROR: Configuration file needs to be provided'
        assert self.config.input_folder is not None, 'ERROR: Input folder needs to be provided'

    def _load_config(self):
        """
        Load configuration and writes to self.config
        """
        with open(self.config, 'r') as cfg:
            self.config = yaml.safe_load(cfg)
            self.config = AttributeDict(**self.config)

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

    def _double_processed(self, filelist):
        """
        Check if two file names have the exact same time stamp (double processed data by ESA) and choose newest one

        input: file list with double processed data
        output: file list without double processed data
        """
        filelist.sort()
        filelist_new = []
        filelist_double_processed = []
        for file in filelist:
            index = filelist.index(file)
            filepath, filename, fileshortname, extension = self._decomposition_filename(
                file)

            try:
                filepath1, filename1, fileshortname1, extension1 = self._decomposition_filename(filelist[index+1])
            except IndexError:
                filename1 = ''
                pass

            try:
                if index == 0:
                    filename2 = ''
                else:
                    filepath2, filename2, fileshortname2, extension2 = self._decomposition_filename(filelist[index-1])
            except IndexError:
                filename2 = ''
                pass

            if filename[0:62] == filename1[0:62] or filename[0:62] == filename2[0:62]:
                filelist_double_processed.append(file)
            else:
                filelist_new.append(file)
        print('Number of found files that were double processed: %s' % (len(filelist_double_processed)/2.))

        filelist_end = self._check_timestamp(filelist_double_processed)
        filelist_end = filelist_end + filelist_new
        filelist_end.sort()

        return filelist_end

    def _check_processing_timestamp(self, file, file1):
        """
        check processing time stamp of input files and return file with newer time stamp
        """

        filepath, filename, fileshortname, extension = self._decomposition_filename(file)
        filepath1, filename1, fileshortname1, extension1 = self._decomposition_filename(
            file1)

        if fileshortname[0:62] == fileshortname1[0:62]:
            pass
        else:
            return

        # Get metadata
        # Path to product.safe-file within zipped Sentinel image
        xml_file = fileshortname + '.SAFE/manifest.safe'
        xml_file1 = fileshortname1 + '.SAFE/manifest.safe'

        # Extract the zipfile
        try:
            zfile = zipfile.ZipFile(file, 'r')
            zfile.extract(xml_file, filepath)
            zfile.close()
            zfile = zipfile.ZipFile(file1, 'r')
            zfile.extract(xml_file1, filepath)
            zfile.close()
        except:
            print('zipfile cannot open !!!!')
            contained = False
            return contained

        # Path to product.xml
        xml_file_extracted = os.path.join(filepath, xml_file)
        xml_file_extracted1 = os.path.join(filepath, xml_file1)

        # Parse the xml file
        tree = etree.parse(xml_file_extracted)
        root = tree.getroot()
        processing_timestamp = root.find(
            './/{http://www.esa.int/safe/sentinel-1.0}processing')
        timestamp = processing_timestamp.items()[0][1]

        tree1 = etree.parse(xml_file_extracted1)
        root1 = tree1.getroot()
        processing_timestamp1 = root1.find(
            './/{http://www.esa.int/safe/sentinel-1.0}processing')
        timestamp1 = processing_timestamp1.items()[0][1]

        shutil.rmtree(os.path.join(filepath, fileshortname + '.SAFE'))
        shutil.rmtree(os.path.join(filepath, fileshortname1 + '.SAFE'))

        if timestamp > timestamp1:
            return file
        else:
            return file1

    def _check_timestamp(self, filelist):
        """
        Sort out the newest of the double processed files
        """

        filelist_new = []
        for file in filelist:
            index = filelist.index(file)
            try:
                file1 = filelist[index+1]
            except IndexError:
                continue

            file_timestamp = self._check_processing_timestamp(file, file1)
            if file_timestamp is None:
                pass
            else:
                filelist_new.append(file_timestamp)
        return filelist_new

    def _border_control(self, filelist):
        """
        ?????
        """
        filelist.sort()
        filelist_new = []
        filelist_border_control = []
        for file in filelist:
            index = filelist.index(file)
            filepath, filename, fileshortname, extension = self._decomposition_filename(
                file)

            try:
                filepath1, filename1, fileshortname1, extension1 = self._decomposition_filename(filelist[index+1])
            except IndexError:
                filename1 = ''
                pass

            try:
                if index == 0:
                    filename2 = ''
                else:
                    filepath2, filename2, fileshortname2, extension2 = self._decomposition_filename(filelist[index-1])
            except IndexError:
                filename2 = ''
                pass

            if filename[0:25] == filename1[0:25] or filename[0:25] == filename2[0:25]:
                filelist_border_control.append(file)
            else:
                filelist_new.append(file)
        print('Number of found files with border issues: %s' % (len(filelist_border_control)))

        # pdb.set_trace()
        # filelist_end = self._check_timestamp(filelist_double_processed)
        # filelist_end = filelist_end + filelist_new
        # filelist_end.sort()

        return filelist_new, filelist_border_control

    def create_list(self, **kwargs):

        # list with all zip files found in input_folder
        filelist = self._create_filelist(self.config.input_folder, '*.zip')

        # If Year is specified in config-file pre-processing will be only done for specified year
        try:
            filelist = self._select_year(filelist, self.config.year)
            filelist.sort()
        except AttributeError:
            print('year not specified')
            pass

        # list with all zip files that contain area of interest
        try:
            lower_right_y = self.config.region['lr']['lat']
            upper_left_y = self.config.region['ul']['lat']
            upper_left_x = self.config.region['ul']['lon']
            lower_right_x = self.config.region['lr']['lon']
            # todo: how is it with coordinates that go across the datum line ??

            location = [upper_left_x, upper_left_y, lower_right_x, lower_right_y]
            filelist = self._contain_area_of_interest(filelist, location, self.config.input_folder)
        except AttributeError:
            print('area of interest not specified')

        # check for double processed data by ESA and choose newest one
        filelist = self._double_processed(filelist)

        filelist = self._border_control(filelist)

        # print('Number of files that will be processed: %s' % len(filelist[0]+len(filelist[1])))


        return filelist

