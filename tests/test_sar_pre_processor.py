"""
Testing the SAR Preprocessor
"""

import sys
import os

sys.path.append(os.path.dirname(sys.path[0]))

from sar_pre_processing import sar_pre_processor


def inc(x):
    return x + 1

def test_answer():
    assert inc(3) == 4


