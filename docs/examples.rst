3. Examples
------------
Example 1: Use default processing graph to pre-process single SAR image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set paths for
    - input_folder (path to stored Sentinel-1 SLC data (zip files) e.g. “~/Downloads”)
    - output_folder (path where processed data will be stored e.g. “~/output”)
    - gpt_loction (gpt is located in the bin folder of your SNAP installation)’

.. code:: ipython3

    input_folder = path
    output_folder = path
    gpt_location = os.path.expanduser('~/snap/bin/gpt')

Create config file with information about input folder, output folder
and gpt path

.. code:: ipython3

    import yaml
    
    with open('sample_config_file.yaml') as stream:
       data = yaml.safe_load(stream)
    
    data['input_folder'] = input_folder
    data['output_folder'] = output_folder
    data['gpt'] = gpt_location
    
    with open('test_config_file.yaml', 'wb') as stream:
       yaml.safe_dump(data, stream, default_flow_style=False, 
                      explicit_start=True, allow_unicode=True, encoding='utf-8')

Optional config options for subsetting

.. code:: ipython3

    with open('test_config_file.yaml') as stream:
       data = yaml.safe_load(stream)
    
    ## Define region of interest
    data['region']['lr']['lat'] = 48.2 # lower right latitude
    data['region']['lr']['lon'] = 11.9 # lower right longitude
    data['region']['ul']['lat'] = 48.4 # upper left latitude
    data['region']['ul']['lon'] = 11.6 # upper left longitude
    data['region']['subset'] = 'yes'
    
    with open('test_config_file.yaml', 'wb') as stream:
       yaml.safe_dump(data, stream, default_flow_style=False, 
                      explicit_start=True, allow_unicode=True, encoding='utf-8')

Start pre-processing steps

.. code:: ipython3

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


**Code output:**

.. code:: ipython3

    INFO:root:Found files within input folder: 1
    INFO:root:year not specified
    INFO:root:area of interest not specified
    INFO:root:Number of found files that were double processed: 0.0
    INFO:root:Number of found files with border issues: 0
    INFO:root:area of interest specified
    INFO:root:normalisation angle not specified, default value of 35 is used for processing
    INFO:ComponentProgress:0
    INFO:ComponentProgress:0
    INFO:root:Process S1A_IW_SLC__1SDV_20210601T051818_20210601T051846_038142_048071_F417.zip with SNAP.

    start step 1

    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start

    ...12%...24%..34%...46%...58%..68%...80%... done.

    INFO:root:0
    INFO:root:Single image, no co-register of images necessary
    INFO:root:multi temporal filter cannot applied to a single image, just single speckle filter is applied
    INFO:ComponentProgress:0
    INFO:ComponentProgress:0

    start step 2
    start step 3

    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start

    ...12%...24%.

    21174 [main] INFO serverStartup - Nc4Iosp: NetCDF-4 C library loaded (jna_path='/home/test/.snap/auxdata/netcdf_natives/8.0.5/amd64', libname='netcdf').
    21194 [main] INFO serverStartup - NetcdfLoader: set log level: old=0 new=0
    21197 [main] INFO serverStartup - Nc4Iosp: set log level: old=0 new=0

    ..36%...48%...60%...72%...84%..

    INFO:root:0
    INFO:root:2021-08-24 22:12:32.731281

     done.
    start add netcdf information

    INFO:root:Number of scenes found for processing: 1

    start create netcdf stack
    
    Scene 1 of 1
    /home/test/Desktop/data/step3/S1A_IW_SLC__1SDV_20210601T051818_20210601T051846_038142_048071_F417_GC_RC_No_Su_speckle.nc



Example 2: Use default processing graph to pre-process a time series of SAR images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set paths for
    - input_folder (path to stored Sentinel-1 SLC data (zip files) e.g. “~/Downloads”)
    - output_folder (path where processed data will be stored e.g. “~/output”)
    - gpt_loction (gpt is located in the bin folder of your SNAP installation)’

.. code:: ipython3

    input_folder = path
    output_folder = path
    gpt_location = os.path.expanduser('~/snap/bin/gpt')

Create config file with information about input, output and gpt location

.. code:: ipython3

    import yaml

    with open('sample_config_file.yaml') as stream:
       data = yaml.safe_load(stream)

    data['input_folder'] = input_folder
    data['output_folder'] = output_folder
    data['gpt'] = gpt_location

    with open('test_config_file.yaml', 'wb') as stream:
       yaml.safe_dump(data, stream, default_flow_style=False,
                      explicit_start=True, allow_unicode=True, encoding='utf-8')

Optional config options which might be useful

.. code:: ipython3

    with open('test_config_file.yaml') as stream:
       data = yaml.safe_load(stream)

    # Filter option
    ## Filter via year of interes
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

Start pre-processing steps

.. code:: ipython3

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


**Code output:**

.. code:: ipython3

    INFO:root:Found files within input folder: 8
    INFO:root:Number of found files for year 2021: 8
    INFO:root:area of interest not specified
    INFO:root:Number of found files that were double processed: 0.0
    INFO:root:Number of found files with border issues: 4
    INFO:root:area of interest specified
    INFO:root:normalisation angle not specified, default value of 35 is used for processing
    INFO:ComponentProgress:0
    INFO:ComponentProgress:0
    INFO:root:Process S1A_IW_SLC__1SDV_20210601T051818_20210601T051846_038142_048071_F417.zip with SNAP.

    start step 1

    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start

    ...12%...24%..34%...46%...58%..68%...80%... done.

    INFO:root:0
    INFO:ComponentProgress:12
    INFO:ComponentProgress:12
    INFO:root:Process S1A_IW_SLC__1SDV_20210602T170732_20210602T170759_038164_048116_EF11.zip with SNAP.
    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start

    ...11%...21%...32%...43%...53%...64%...75%...85%.. done.

    INFO:root:0
    INFO:ComponentProgress:25
    INFO:ComponentProgress:25
    INFO:root:Process S1A_IW_SLC__1SDV_20210606T052628_20210606T052655_038215_04828D_89C3.zip with SNAP.
    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start

    ...10%...21%...31%...42%...52%...63%...74%...84%.. done.

    INFO:root:0
    INFO:ComponentProgress:37
    INFO:ComponentProgress:37
    INFO:root:Process S1B_IW_SLC__1SDV_20210607T051737_20210607T051804_027246_034125_2C2A.zip with SNAP.
    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start

    ...12%...24%..34%...46%...58%..68%...80%... done.

    INFO:root:0
    INFO:ComponentProgress:50
    INFO:ComponentProgress:50
    INFO:root:Process S1A_IW_SLC__1SDV_20210609T165916_20210609T165943_038266_0483FE_CD3F.zip with SNAP.
    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start

    ...10%...20%...30%....42%...52%...62%...72%...82%... done.

    INFO:root:0
    INFO:ComponentProgress:62
    INFO:ComponentProgress:62
    INFO:root:Process S1B_IW_SLC__1SDV_20210603T165832_20210603T165900_027195_033F94_5E37.zip with SNAP.
    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start

    ...10%...21%...31%...41%...52%...63%...74%...84%.. done.

    INFO:root:0
    INFO:root:skip processing for /home/test/Desktop/data/S1A_IW_SLC__1SDV_20210609T165941_20210609T170008_038266_0483FE_08A0.zip. File does not exist
    INFO:root:skip processing for /home/test/Desktop/data/S1B_IW_SLC__1SDV_20210603T165857_20210603T165924_027195_033F94_E158.zip. File does not exist
    INFO:ComponentProgress:0
    INFO:ComponentProgress:0
    INFO:root:Scene 1 of 6
    INFO:root:Process S1A_IW_SLC__1SDV_20210601T051818_20210601T051846_038142_048071_F417_GC_RC_No_Su.dim with SNAP.

    start step 2

    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start

    ...12%...25%..35%..45%...57%..67%..77%...89% done.

    -- org.jblas INFO Deleting /tmp/jblas894490658805952774/libgfortran-4.so
    -- org.jblas INFO Deleting /tmp/jblas894490658805952774/libquadmath-0.so
    -- org.jblas INFO Deleting /tmp/jblas894490658805952774/libjblas.so
    -- org.jblas INFO Deleting /tmp/jblas894490658805952774/libjblas_arch_flavor.so
    -- org.jblas INFO Deleting /tmp/jblas894490658805952774
    INFO:root:0
    INFO:root:2021-08-25 10:02:08.004106
    INFO:ComponentProgress:16
    INFO:ComponentProgress:16
    INFO:root:Scene 2 of 6
    INFO:root:Process S1A_IW_SLC__1SDV_20210602T170732_20210602T170759_038164_048116_EF11_GC_RC_No_Su.dim with SNAP.
    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403

    ...12%...25%..35%..45%...57%..67%..77%...89% done.

    -- org.jblas INFO Deleting /tmp/jblas1208556710770333014/libgfortran-4.so
    -- org.jblas INFO Deleting /tmp/jblas1208556710770333014/libquadmath-0.so
    -- org.jblas INFO Deleting /tmp/jblas1208556710770333014/libjblas.so
    -- org.jblas INFO Deleting /tmp/jblas1208556710770333014/libjblas_arch_flavor.so
    -- org.jblas INFO Deleting /tmp/jblas1208556710770333014
    INFO:root:0
    INFO:root:2021-08-25 10:03:03.158585
    INFO:ComponentProgress:33
    INFO:ComponentProgress:33
    INFO:root:Scene 3 of 6
    INFO:root:Process S1A_IW_SLC__1SDV_20210606T052628_20210606T052655_038215_04828D_89C3_GC_RC_No_Su.dim with SNAP.
    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start

    ...12%...25%..35%..45%...57%..67%..77%...89% done.

    -- org.jblas INFO Deleting /tmp/jblas4664425677947938341/libgfortran-4.so
    -- org.jblas INFO Deleting /tmp/jblas4664425677947938341/libquadmath-0.so
    -- org.jblas INFO Deleting /tmp/jblas4664425677947938341/libjblas.so
    -- org.jblas INFO Deleting /tmp/jblas4664425677947938341/libjblas_arch_flavor.so
    -- org.jblas INFO Deleting /tmp/jblas4664425677947938341
    INFO:root:0
    INFO:root:2021-08-25 10:03:44.964480
    INFO:ComponentProgress:50
    INFO:ComponentProgress:50
    INFO:root:Scene 4 of 6
    INFO:root:Process S1A_IW_SLC__1SDV_20210609T165916_20210609T165943_038266_0483FE_CD3F_GC_RC_No_Su.dim with SNAP.
    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start

    ...12%...25%..35%..45%...57%..67%..77%...89% done.

    -- org.jblas INFO Deleting /tmp/jblas2700153776847850762/libgfortran-4.so
    -- org.jblas INFO Deleting /tmp/jblas2700153776847850762/libquadmath-0.so
    -- org.jblas INFO Deleting /tmp/jblas2700153776847850762/libjblas.so
    -- org.jblas INFO Deleting /tmp/jblas2700153776847850762/libjblas_arch_flavor.so
    -- org.jblas INFO Deleting /tmp/jblas2700153776847850762
    INFO:root:0
    INFO:root:2021-08-25 10:04:29.912825
    INFO:ComponentProgress:66
    INFO:ComponentProgress:66
    INFO:root:Scene 5 of 6
    INFO:root:Process S1B_IW_SLC__1SDV_20210603T165832_20210603T165900_027195_033F94_5E37_GC_RC_No_Su.dim with SNAP.
    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403

    ...12%...25%..35%..45%...57%..67%..77%...89% done.

    -- org.jblas INFO Deleting /tmp/jblas193598082844173125/libgfortran-4.so
    -- org.jblas INFO Deleting /tmp/jblas193598082844173125/libquadmath-0.so
    -- org.jblas INFO Deleting /tmp/jblas193598082844173125/libjblas.so
    -- org.jblas INFO Deleting /tmp/jblas193598082844173125/libjblas_arch_flavor.so
    -- org.jblas INFO Deleting /tmp/jblas193598082844173125
    INFO:root:0
    INFO:root:2021-08-25 10:05:18.856109
    INFO:ComponentProgress:83
    INFO:ComponentProgress:83
    INFO:root:Scene 6 of 6
    INFO:root:Process S1B_IW_SLC__1SDV_20210607T051737_20210607T051804_027246_034125_2C2A_GC_RC_No_Su.dim with SNAP.
    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403
    INFO: org.esa.snap.core.datamodel.Product: raster width 2404 not equal to 2403

    ...12%...25%..35%..45%...57%..67%..77%...89% done.

    -- org.jblas INFO Deleting /tmp/jblas3143016119804068644/libgfortran-4.so
    -- org.jblas INFO Deleting /tmp/jblas3143016119804068644/libquadmath-0.so
    -- org.jblas INFO Deleting /tmp/jblas3143016119804068644/libjblas.so
    -- org.jblas INFO Deleting /tmp/jblas3143016119804068644/libjblas_arch_flavor.so
    -- org.jblas INFO Deleting /tmp/jblas3143016119804068644
    INFO:root:0
    INFO:root:2021-08-25 10:06:09.093124
    INFO:root:skip processing for /home/test/Desktop/data/S1A_IW_SLC__1SDV_20210609T165941_20210609T170008_038266_0483FE_08A0.zip. File /home/test/Desktop/data/step2/S1A_IW_SLC__1SDV_20210609T165941_20210609T170008_038266_0483FE_08A0_GC_RC_No_Su_Co.dim does not exist.
    INFO:root:skip processing for /home/test/Desktop/data/S1B_IW_SLC__1SDV_20210603T165857_20210603T165924_027195_033F94_E158.zip. File /home/test/Desktop/data/step2/S1B_IW_SLC__1SDV_20210603T165857_20210603T165924_027195_033F94_E158_GC_RC_No_Su_Co.dim does not exist.
    INFO:ComponentProgress:0
    INFO:ComponentProgress:0

    start step 3

    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start


    ...10%....22%....34%....45%...

    11330 [main] INFO serverStartup - Nc4Iosp: NetCDF-4 C library loaded (jna_path='/home/test/.snap/auxdata/netcdf_natives/8.0.5/amd64', libname='netcdf').
    11345 [main] INFO serverStartup - NetcdfLoader: set log level: old=0 new=0
    11345 [main] INFO serverStartup - Nc4Iosp: set log level: old=0 new=0

    55%....67%....79%....90% done.

    INFO:root:0
    INFO:root:2021-08-25 10:07:46.994092
    INFO:ComponentProgress:16
    INFO:ComponentProgress:16
    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start

    ...10%....22%....34%....45%...

    10805 [main] INFO serverStartup - Nc4Iosp: NetCDF-4 C library loaded (jna_path='/home/test/.snap/auxdata/netcdf_natives/8.0.5/amd64', libname='netcdf').
    10823 [main] INFO serverStartup - NetcdfLoader: set log level: old=0 new=0
    10824 [main] INFO serverStartup - Nc4Iosp: set log level: old=0 new=0

    55%....67%....79%....90% done.

    INFO:root:0
    INFO:root:2021-08-25 10:09:19.785908
    INFO:ComponentProgress:33
    INFO:ComponentProgress:33
    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start

    ...10%....22%....34%....45%...

    10397 [main] INFO serverStartup - Nc4Iosp: NetCDF-4 C library loaded (jna_path='/home/test/.snap/auxdata/netcdf_natives/8.0.5/amd64', libname='netcdf').
    10407 [main] INFO serverStartup - NetcdfLoader: set log level: old=0 new=0
    10415 [main] INFO serverStartup - Nc4Iosp: set log level: old=0 new=0

    55%....67%....79%....90% done.

    INFO:root:0
    INFO:root:2021-08-25 10:10:52.726901
    INFO:ComponentProgress:50
    INFO:ComponentProgress:50
    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start

    ...10%....22%....34%....45%...

    9730 [main] INFO serverStartup - Nc4Iosp: NetCDF-4 C library loaded (jna_path='/home/test/.snap/auxdata/netcdf_natives/8.0.5/amd64', libname='netcdf').
    9734 [main] INFO serverStartup - NetcdfLoader: set log level: old=0 new=0
    9746 [main] INFO serverStartup - Nc4Iosp: set log level: old=0 new=0

    55%....67%....79%....90% done.

    INFO:root:0
    INFO:root:2021-08-25 10:12:26.159929
    INFO:ComponentProgress:66
    INFO:ComponentProgress:66
    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start

    ...10%....22%....34%....45%...

    10364 [main] INFO serverStartup - Nc4Iosp: NetCDF-4 C library loaded (jna_path='/home/test/.snap/auxdata/netcdf_natives/8.0.5/amd64', libname='netcdf').
    10381 [main] INFO serverStartup - NetcdfLoader: set log level: old=0 new=0
    10381 [main] INFO serverStartup - Nc4Iosp: set log level: old=0 new=0

    55%....67%....79%....90% done.

    INFO:root:0
    INFO:root:2021-08-25 10:13:57.298459
    INFO:ComponentProgress:83
    INFO:ComponentProgress:83
    INFO: org.esa.snap.core.gpf.operators.tooladapter.ToolAdapterIO: Initializing external tool adapters
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Incompatible GDAL 3.3.1 found on system. Internal GDAL 3.0.0 from distribution will be used.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.
    INFO: org.esa.snap.core.util.EngineVersionCheckActivator: Please check regularly for new updates for the best SNAP experience.
    INFO: org.esa.s2tbx.dataio.gdal.GDALVersion: Internal GDAL 3.0.0 set to be used by SNAP.

    Executing processing graph

    INFO: org.hsqldb.persist.Logger: dataFileCache open start

    ...10%....22%....34%....45%...

    10293 [main] INFO serverStartup - Nc4Iosp: NetCDF-4 C library loaded (jna_path='/home/test/.snap/auxdata/netcdf_natives/8.0.5/amd64', libname='netcdf').
    10303 [main] INFO serverStartup - NetcdfLoader: set log level: old=0 new=0
    10309 [main] INFO serverStartup - Nc4Iosp: set log level: old=0 new=0

    55%....67%....79%....90% done.

    INFO:root:0
    INFO:root:2021-08-25 10:15:30.980602

    start add netcdf information


    INFO:root:Number of scenes found for processing: 7

    start create netcdf stack

    Scene 1 of 7
    /home/test/Desktop/data/step3/S1A_IW_SLC__1SDV_20210601T051818_20210601T051846_038142_048071_F417_GC_RC_No_Su_Co_speckle.nc

    Scene 2 of 7
    /home/test/Desktop/data/step3/S1A_IW_SLC__1SDV_20210601T051818_20210601T051846_038142_048071_F417_GC_RC_No_Su_speckle.nc

    Scene 3 of 7
    /home/test/Desktop/data/step3/S1A_IW_SLC__1SDV_20210602T170732_20210602T170759_038164_048116_EF11_GC_RC_No_Su_Co_speckle.nc

    Scene 4 of 7
    /home/test/Desktop/data/step3/S1B_IW_SLC__1SDV_20210603T165832_20210603T165900_027195_033F94_5E37_GC_RC_No_Su_Co_speckle.nc

    Scene 5 of 7
    /home/test/Desktop/data/step3/S1A_IW_SLC__1SDV_20210606T052628_20210606T052655_038215_04828D_89C3_GC_RC_No_Su_Co_speckle.nc

    Scene 6 of 7
    /home/test/Desktop/data/step3/S1B_IW_SLC__1SDV_20210607T051737_20210607T051804_027246_034125_2C2A_GC_RC_No_Su_Co_speckle.nc

    Scene 7 of 7
    /home/test/Desktop/data/step3/S1A_IW_SLC__1SDV_20210609T165916_20210609T165943_038266_0483FE_CD3F_GC_RC_No_Su_Co_speckle.nc
