2. Download sample data from Sentinel Data Hub
----------------------------------------------

Option 1: Download data from Sentinel Data Hub via python package sentinelsat
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create Account (https://scihub.copernicus.eu/dhus/#/self-registration)
and change user and password below.

.. code:: ipython3

    # connect to the API
    from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
    from datetime import date
    user = 'user'
    password = 'password'
    # initialize settings
    api = SentinelAPI(user, password)

Search for available data

.. code:: ipython3

    # search by polygon (MNI test site coordinates), time, and SciHub query keywords
    footprint = geojson_to_wkt(read_geojson('coordinates_mni.geojson'))
    products = api.query(footprint,
                         date=('20210601', '20210602'),
                         platformname='Sentinel-1',
                         producttype='SLC')
    print('Following products will be downloaded')
    print(api.to_dataframe(products).title.values)
    
    print('These {} product need {} Gb of disk space'.format(len(products), api.get_products_size(products)))

**Code output:**

.. code:: ipython3

    Following products will be downloaded
    ['S1A_IW_SLC__1SDV_20210601T051818_20210601T051846_038142_048071_F417']
    These 1 product need 7.97 Gb of disk space


Start download process (**Attention: might take a while and data will
requries some free disk space)**

.. code:: ipython3

    # download all results from the search
    # files will be downloaded to specified path
    import os
    path = os.path.expanduser('~/Desktop/data')
    try:
        os.makedirs(path)
    except: FileExistsError
    api.download_all(products, path)


**Code output:**

.. code:: ipython3

    Downloading products:   100%|########| 1/1 [49:04<00:00, 2964.23s/product]
    Downloading S1A_IW_SLC__1SDV_20210601T051818_20210601T051846_038142_048071_F417.zip:   100%|########| 4.6/4.6…

    ResultTuple(downloaded={'981b798e-bcf8-48fa-acd0-4c859cf336b4': {'id': '981b798e-bcf8-48fa-acd0-4c859cf336b4', 'title': 'S1A_IW_SLC__1SDV_20210601T051818_20210601T051846_038142_048071_F417', 'size': 4643623329, 'md5': '228ed352b1411fcfc39ee6d79a2887c6', 'date': datetime.datetime(2021, 6, 1, 5, 18, 18, 742000), 'footprint': 'POLYGON((14.704199 47.602592,11.278880 48.004967,11.666771 49.677139,15.210303 49.273212,14.704199 47.602592))', 'url': "https://apihub.copernicus.eu/apihub/odata/v1/Products('981b798e-bcf8-48fa-acd0-4c859cf336b4')/$value", 'Online': True, 'Creation Date': datetime.datetime(2021, 6, 1, 8, 34, 0, 989000), 'Ingestion Date': datetime.datetime(2021, 6, 1, 8, 27, 59, 416000), 'quicklook_url': "https://apihub.copernicus.eu/apihub/odata/v1/Products('981b798e-bcf8-48fa-acd0-4c859cf336b4')/Products('Quicklook')/$value", 'path': '/home/test/Desktop/data/S1A_IW_SLC__1SDV_20210601T051818_20210601T051846_038142_048071_F417.zip', 'downloaded_bytes': 4643623329}}, retrieval_triggered={}, failed={})



Option 2: Manually search and download data from Alaska Satellite Facility (ASF)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can search for Sentinel-1 data at https://search.asf.alaska.edu/. A
NASA EOSDIS Earthdata Login account is required for downloading data and
tools from ASF. Registering for an Earthdata Login account is free
(https://urs.earthdata.nasa.gov/home). Instructions how to download data
from ASF can be found at
https://asf.alaska.edu/wp-content/uploads/2019/02/asf_datarecipe_bulk_download_from_vertex_python_script_v1.pdf.
