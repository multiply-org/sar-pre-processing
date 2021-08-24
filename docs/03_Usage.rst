Usage
======

Requirements
--------------

- Installation of SenSARP
- Installation of ESA's SNAP Toolbox version >8.0.3
    - Currently only SNAP version 8.0 can be downloaded from the `ESA website <https://step.esa.int/main/download/snap-download/>`_. To update SNAP to a version >8.0.3 please start the SNAP software. You will be asked if you want to search for update. After the updates are installed you need to restart SNAP to initialize the installed updates.
    - SNAP Toolbox need libgfortran for specific operations but currently libgfortran is not installed during the installation process of SNAP therefore you might use::

        sudo apt-get install gfortran

- Sentinel-1 SLC data
    - Instruction how to download Sentinel 1 data are given in :ref:`Download_S1_data`.

.. _Download_S1_data:

Download Sentinel-1 data
--------------------------

Option 1: Download data from Sentinel Data Hub via python package sentinelsat
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create Account (`<https://scihub.copernicus.eu/dhus/#/self-registration>`_) and change user and password below::

    # connect to the API
    from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
    from datetime import date
    user = 'username'
    password = 'password'
    # initialize settings
    api = SentinelAPI(user, password)

Search for available data::

    # search by polygon (MNI test site coordinates), time, and SciHub query keywords
    footprint = geojson_to_wkt(read_geojson('coordinates_mni.geojson'))
    products = api.query(footprint,
                         date=('20210601', '20210615'),
                         platformname='Sentinel-1',
                         producttype='SLC')
    print('Following products will be downloaded')
    print(api.to_dataframe(products).title.values)

    print('These {} product need {} Gb of disk space'.format(len(products), api.get_products_size(products)))

Start download process (Attention: might take a while and data will requries some free disk space)::

    # download all results from the search
    # files will be downloaded to specified path
    import os
    path = "/path/to/data/"
    try:
        os.makedirs(path)
    except: FileExistsError
    api.download_all(products, path)


Option 2: Download data from NASA Earth Data Search
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can search for Sentinel-1 data `here <https://search.earthdata.nasa.gov/search>`_.
Instructions how to search and download data from NASA Earth Data can be found `here <https://earthdata.nasa.gov/faq/earthdata-search-faq>`_.

Examples
----------

Apply default pre-processing chain of SenSARP to a time-series
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set paths for

- input_folder (path to stored Sentinel-1 SLC data (zip files) e.g. “~/Downloads”)
- output_folder (path where processed data will be stored e.g. “~/output”)
- gpt_loction (gpt is located in the bin folder of your SNAP installation)::

    import os
    input_folder = os.path.expanduser(path)
    output_folder = os.path.expanduser(path)
    gpt_location = os.path.expanduser('~/snap/bin/gpt')

Create config file with information about input, output and gpt location::

    import yaml

    with open('sample_config_file.yaml') as stream:
       data = yaml.safe_load(stream)

    data['input_folder'] = input_folder
    data['output_folder'] = output_folder
    data['gpt'] = gpt_location

    with open('test_config_file.yaml', 'wb') as stream:
       yaml.safe_dump(data, stream, default_flow_style=False,
                      explicit_start=True, allow_unicode=True, encoding='utf-8')

Set optional config options (More information about configuration file is given in ......)::

    with open('test_config_file.yaml') as stream:
       data = yaml.safe_load(stream)

    # Filter option
    ## Filter via year of interest
    data['year'] = '2021'

    ## Define region of interest
    data['region']['lr']['lat'] = 48.2 # lower right latitude
    data['region']['lr']['lon'] = 11.9 # lower right longitude
    data['region']['ul']['lat'] = 48.4 # upper left latitude
    data['region']['ul']['lon'] = 11.6 # upper left longitude
    data['region']['subset'] = 'yes'

    ## Define multi-temporal filtering properties
    data['speckle_filter']['multi_temporal']['apply'] = 'yes'
    data['speckle_filter']['multi_temporal']['files'] = '5' # Number of files used for multi temporal filtering

    ## Define incidence angle for normalization
    data['normalization_angle'] = '35'

    with open('test_config_file.yaml', 'wb') as stream:
       yaml.safe_dump(data, stream, default_flow_style=False,
                      explicit_start=True, allow_unicode=True, encoding='utf-8')

Start default pre-processing chain of SenSARP::

    from sar_pre_processing.sar_pre_processor import *
    import warnings
    warnings.filterwarnings("ignore")

    processing = SARPreProcessor(config='test_config_file.yaml')
    processing.create_processing_file_list()
    print('start step 1')
    processing.pre_process_step1()
    print('start step 2')
    processing.pre_process_step2()
    print('start step 3')
    processing.pre_process_step3()
    print('start add netcdf information')
    processing.add_netcdf_information()
    print('start create netcdf stack')
    processing.create_netcdf_stack()

Apply default pre-processing chain of SenSARP to one single image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set paths for

- input_folder (path to stored Sentinel-1 SLC data (zip files) e.g. “~/Downloads”)
- output_folder (path where processed data will be stored e.g. “~/output”)
- gpt_loction (gpt is located in the bin folder of your SNAP installation)::

    import os
    input_folder = os.path.expanduser(path)
    output_folder = os.path.expanduser(path)
    gpt_location = os.path.expanduser('~/snap/bin/gpt')

Create config file with information about input, output and gpt location::

    import yaml

    with open('sample_config_file.yaml') as stream:
       data = yaml.safe_load(stream)

    data['input_folder'] = input_folder
    data['output_folder'] = output_folder
    data['gpt'] = gpt_location

    with open('test_config_file.yaml', 'wb') as stream:
       yaml.safe_dump(data, stream, default_flow_style=False,
                      explicit_start=True, allow_unicode=True, encoding='utf-8')

Set optional config options (More information about configuration file is given in ......)::

    with open('test_config_file.yaml') as stream:
       data = yaml.safe_load(stream)

    # Filter option
    ## Filter via year of interest
    data['year'] = '2021'

    ## Define region of interest
    data['region']['lr']['lat'] = 48.2 # lower right latitude
    data['region']['lr']['lon'] = 11.9 # lower right longitude
    data['region']['ul']['lat'] = 48.4 # upper left latitude
    data['region']['ul']['lon'] = 11.6 # upper left longitude
    data['region']['subset'] = 'yes'

    ## Define incidence angle for normalization
    data['normalization_angle'] = '35'

    with open('test_config_file.yaml', 'wb') as stream:
       yaml.safe_dump(data, stream, default_flow_style=False,
                      explicit_start=True, allow_unicode=True, encoding='utf-8')

Start default pre-processing chain of SenSARP::

    from sar_pre_processing.sar_pre_processor import *
    import warnings
    warnings.filterwarnings("ignore")

    processing = SARPreProcessor(config='test_config_file.yaml')
    processing.create_processing_file_list()
    print('start step 1')
    processing.pre_process_step1()
    print('start step 2')
    processing.pre_process_step2()
    print('start step 3')
    processing.pre_process_step3()
    print('start add netcdf information')
    processing.add_netcdf_information()
    print('start create netcdf stack')
    processing.create_netcdf_stack()

Apply expert user defined pre-processing chain
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set paths for

- input_folder (path to stored Sentinel-1 SLC data (zip files) e.g. “~/Downloads”)
- output_folder (path where processed data will be stored e.g. “~/output”)
- gpt_loction (gpt is located in the bin folder of your SNAP installation)::

    import os
    input_folder = os.path.expanduser(path)
    output_folder = os.path.expanduser(path)
    gpt_location = os.path.expanduser('~/snap/bin/gpt')

Create config file with information about input, output and gpt location::

    import yaml

    with open('sample_config_file.yaml') as stream:
       data = yaml.safe_load(stream)

    data['input_folder'] = input_folder
    data['output_folder'] = output_folder
    data['gpt'] = gpt_location

    with open('test_config_file.yaml', 'wb') as stream:
       yaml.safe_dump(data, stream, default_flow_style=False,
                      explicit_start=True, allow_unicode=True, encoding='utf-8')

Set optional config options (More information about configuration file is given in ......)::

    with open('test_config_file.yaml') as stream:
       data = yaml.safe_load(stream)

    # Filter option
    ## Filter via year of interest
    data['year'] = '2021'

    ## Define region of interest
    data['region']['lr']['lat'] = 48.2 # lower right latitude
    data['region']['lr']['lon'] = 11.9 # lower right longitude
    data['region']['ul']['lat'] = 48.4 # upper left latitude
    data['region']['ul']['lon'] = 11.6 # upper left longitude
    data['region']['subset'] = 'yes'

    ## Define incidence angle for normalization
    data['normalization_angle'] = '35'

    with open('test_config_file.yaml', 'wb') as stream:
       yaml.safe_dump(data, stream, default_flow_style=False,
                      explicit_start=True, allow_unicode=True, encoding='utf-8')

Start default pre-processing chain of SenSARP::

    from sar_pre_processing.sar_pre_processor import *
    import warnings
    warnings.filterwarnings("ignore")

    processing = SARPreProcessor(config='test_config_file.yaml')
    processing.create_processing_file_list()
    print('start step 1')
    processing.pre_process_step1()
    print('start step 2')
    processing.pre_process_step2()
    print('start step 3')
    processing.pre_process_step3()
    print('start add netcdf information')
    processing.add_netcdf_information()
    print('start create netcdf stack')
    processing.create_netcdf_stack()



Example configuration file of SenSARP
-------------------------------------------------
