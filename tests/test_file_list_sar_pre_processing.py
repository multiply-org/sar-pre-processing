from sar_pre_processing.file_list_sar_pre_processing import SARList

def test__create_filelist():
    initialize_SARList = SARList(config='./tests/test_config_sar_pre_processor.yml')
    filelist = initialize_SARList._create_filelist(input_folder='./tests/test_data_2',expression='*.zip')
    assert len(filelist) == 8

def test__decomposition_filename():
    initialize_SARList = SARList(config='./tests/test_config_sar_pre_processor.yml')
    filepath, filename, fileshortname, extension = initialize_SARList._decomposition_filename('/path/filename.txt')
    assert filepath == '/path'
    assert filename == 'filename.txt'
    assert fileshortname == 'filename'
    assert extension == '.txt'

def test__select_year():
    initialize_SARList = SARList(config='./tests/test_config_sar_pre_processor.yml')
    filelist_all = initialize_SARList._create_filelist(input_folder='./tests/test_data_2',expression='*.zip')
    filelist_2020 = initialize_SARList._select_year(filelist_all,'2020')
    assert len(filelist_2020) == 4

def test__contain_area_of_interest():
    initialize_SARList = SARList(config='./tests/test_config_sar_pre_processor.yml')
    filelist_all = initialize_SARList._create_filelist('./tests/test_data_2','*.zip')
    location = [11.6, 48.4, 11.9, 48.1]
    output_folder = './tests/test_data_2'
    filelist_end = initialize_SARList._contain_area_of_interest(filelist_all,location,output_folder)
    assert len(filelist_end) == 7

    filelist_2017 = initialize_SARList._select_year(filelist_all,'2017')
    filelist_end = initialize_SARList._contain_area_of_interest(filelist_2017,location,output_folder)
    assert len(filelist_end) == 0

def test__double_processed():
    initialize_SARList = SARList(config='./tests/test_config_sar_pre_processor.yml')
    filelist = initialize_SARList._create_filelist('./tests/test_data_2','*.zip')
    filelist_2016 = initialize_SARList._select_year(filelist,'2016')
    filelist_end = initialize_SARList._double_processed(filelist_2016)
    assert len(filelist_end) == 1
    assert filelist_end[0] == './tests/test_data_2/S1A_IW_SLC__1SDV_20160204T051740_20160204T051807_009792_00E52E_A9B0.zip'

def test__border_control():
    initialize_SARList = SARList(config='./tests/test_config_sar_pre_processor.yml')
    filelist = initialize_SARList._create_filelist('./tests/test_data_2','*.zip')
    filelist_2020 = initialize_SARList._select_year(filelist,'2020')
    filelist_new, filelist_border_control = initialize_SARList._border_control(filelist_2020)
    assert len(filelist_border_control) == 2
    assert filelist_border_control[0] == './tests/test_data_2/S1A_IW_SLC__1SDV_20200110T165907_20200110T165934_030741_03864C_88B8.zip'
    assert filelist_border_control[1] == './tests/test_data_2/S1A_IW_SLC__1SDV_20200110T165932_20200110T170000_030741_03864C_E827.zip'

