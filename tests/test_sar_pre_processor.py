from sar_pre_processing import SARPreProcessor

"""
Testing the SAR Preprocessor
"""


def test_select_year():
    SAR = SARPreProcessor(config='./tests/test_config_sar_pre_processor.yml')
    SAR.create_processing_file_list()
    print('Start pre-processing step 1 ...')
    SAR.pre_process_step1()
    print('Start pre-processing step 2 ...')
    SAR.pre_process_step2()
    print('Start pre-processing step 3 ...')
    SAR.pre_process_step3()
    # SAR._select_year()


from sar_pre_processing import sar_pre_processor


def inc(x):
    return x + 1

def test_answer():
    assert inc(3) == 4


