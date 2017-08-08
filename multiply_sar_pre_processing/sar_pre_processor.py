"""
Wrapper module to launch preprocessor
"""

import os


class PreProcessor(object):

    def __init__(self, **kwargs):
        self.config = kwargs.get('config', None)
        self._check()

        self.gpt = self.config.gpt

    def _check(self):
        assert self.config is not None, 'ERROR: configuration needs to be provided'

    def pre_process(self):
        assert False, 'Routine should be implemented in child class'


class SARPreProcessor(PreProcessor):

    def __init__(self, **kwargs):
        super(SARPreProcessor, self).__init__(**kwargs)

        # TODO PUT THE GRAPH DIRECTORIES AND NAMES IN A SEPARATE CONFIG !!!

        # xml-processing graph
        self.xmlgraphpath = '/media/tweiss/Work/python_code/MULTIPLY/pre_processing_Sentinel_1/xml_files/'
        # the XML config files should gfo somewhere in a specific directory in the multiply-core repo
        self.xmlgraph = 'preprocess_v01.xml'

    # todo discuss if input/output specification part of processing or part of instantiation of the object itself
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
        input_folder = kwargs.get('input', None)
        assert input_folder is not None, 'ERROR: input folder not specified'
        assert os.path.exists(input_folder)

        output_folder = kwargs.get('output', None)
        assert output_folder is not None, 'ERROR: output folder needs to be specified'
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Name addition for processed data
        xml_addition = 'subset'
        
        lower_right_y = self.config.region['lr']['lat']
        upper_left_y = self.config.region['ul']['lat']
        upper_left_x = self.config.region['ul']['lon']
        lower_right_x = self.config.region['lr']['lon']
        # todo: how is it with coordinates that go across the datum line ??

        # Coordinates for subset area
        area = self.get_area(lower_right_y, upper_left_y, upper_left_x, lower_right_x)

        # o.k., now the rest of the preprocessor can be added here
        # to keep things most flexible it would be good to have that in 
        # a separate class
        
        return 'some data'

    def get_area(self, lat_min, lat_max, lon_min, lon_max):
        """
        Change input coordinates for subset operator
        """
        assert lat_min <= lat_max, 'ERROR: invalid lat'
        assert lon_min <= lon_max, 'ERROR: invalid lon'
        return '%.14f %.14f,%.14f %.14f,%.14f %.14f,%.14f %.14f,%.14f %.14f' % (lon_min, lat_min, lon_min, lat_max,
                                                                                lon_max, lat_max, lon_max, lat_min,
                                                                                lon_min, lat_min)
