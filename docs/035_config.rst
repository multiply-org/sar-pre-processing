5. Configuration file
----------------------

.. code-block:: yaml

    # Sample config file
    #====================
    ## Necessary parameters
    #-----------------------
    ### Input folder with SAR data (zip format)
    input_folder: '/media/tweiss/Daten/test_mysentinelapi' # values: string

    ### Output folder to store the pre-processed data
    output_folder: '/media/tweiss/Daten/test_mysentinelapi' # values: string

    ### Location of SNAP's graph-processing-tool
    gpt: /home/tweiss/snap/bin/gpt

    ## Optional parameters
    #-----------------------
    ### Year of interest
    #~~~~~~~~~~~~~~~~~~~~
    year: 2021 # values: integer

    ### Area of interest
    #~~~~~~~~~~~~~~~~~~~
    region:
      subset: 'yes' # values: 'no' or 'yes'
      ul:
        lat: 48.40 # values: float
        lon: 11.60 # values: float
      lr:
        lat: 48.10 # values: float
        lon: 11.90 # values: float

    ### Used parameters of multi-temporal speckle filter
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    speckle_filter:
      multi_temporal:
        apply: 'yes' # values: 'no' or 'yes'
        files: '5' # values: integer

    ### Used parameter of incidence normalization (default angle is 35°)
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    normalisation_angle: 35 # values: float

    ### Single file processing
    #~~~~~~~~~~~~~~~~~~~~~~~~~
    single_file: 'yes' # values: 'no' or 'yes'

    ### Usage of user defined xml graphs
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #### Specification is user defined xml graph should be used
    use_user_definde_graphs: 'no' # values: 'no' or 'yes'

    #### Location of user defined xml files for processing
    xml_graph_path: /media/tweiss/Work/GIT/GitHub/multiply-org/sar-pre-processing/sar_pre_processing/user_defined_graphs

    ##### file names of user defined xml graphs
    pre_process_step1: expert_user.xml




