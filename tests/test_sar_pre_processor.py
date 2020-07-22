from sar_pre_processing import SARPreProcessor

"""
Testing the SAR Preprocessor
"""


def test_create_sar_pre_processor_with_vm_config():
    pre_processor = SARPreProcessor(config='./tests/test_data/vm_config.yml')
    assert pre_processor is not None


def test_create_sar_pre_processor_with_input_and_output_folder():
    pre_processor = SARPreProcessor(config='./tests/test_data/config_with_no_input_and_output_information.yml',
                                    input='./tests/test_data/', output='./tests/test_data_2/')
    assert pre_processor is not None
    pre_processor.create_processing_file_list()


# def test_select_year():
#     SAR = SARPreProcessor(config='./tests/test_config_sar_pre_processor.yml')
#     SAR.create_processing_file_list()
#     print('Start pre-processing step 1 ...')
#     SAR.pre_process_step1()
#     print('Start pre-processing step 2 ...')
#     SAR.pre_process_step2()
#     print('Start pre-processing step 3 ...')
#     SAR.pre_process_step3()
#     # SAR._select_year()


def inc(x):
    return x + 1


def test_answer():
    assert inc(3) == 4


