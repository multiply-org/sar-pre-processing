"""
Testing the SAR Preprocessor
"""

from multiply_sar_pre_processing.sar_pre_processor import SARPreProcessor
import unittest
import tempfile
import datetime
from multiply_dummy.configuration import Configuration
from multiply_dummy.state import TargetState


class SARTest(unittest.TestCase):
    def setUp(self):
        self.d_in = tempfile.mkdtemp()

        t1 = datetime.datetime(2000,1,1)
        t2 = datetime.datetime(2002,12,31)


        tstate = TargetState(state={'lai':True, 'sm':False}) 

        r = {}
        r.update({'lr' : {'lat': 45., 'lon' : 11.2}})
        r.update({'ul' : {'lat': 47., 'lon' : 10.2}})
        self.c = Configuration(region=r, time_start=t1, time_stop=t2, tstate=tstate)


    def tearDown(self):
        pass


    def test_init(self):
        S = SARPreProcessor(config=self.c)
        S.pre_process(input=self.d_in, output=tempfile.mkdtemp())
