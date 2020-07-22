

from sar_pre_processing.sar_pre_processor import *
import warnings
warnings.filterwarnings("ignore")

processing = SARPreProcessor(config='sar_pre_processing/sample_config_file.yml')
processing.create_processing_file_list()
processing.pre_process_step1()
processing.pre_process_step2()
processing.pre_process_step3()
processing.solve_projection_problem()
processing.add_netcdf_information()
processing.create_netcdf_stack()