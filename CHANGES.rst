Change Log SenSARP
====================

[0.1] - 2021-04-20
-------------------
initial version

[0.2] - 2022-01-18 (JOSS Paper)
--------------------------------

JOSS Paper
~~~~~~~~~~~
* extensive revision

Documentation
~~~~~~~~~~~~~~
* add installation guide using virtualenv and pip
* revise introduction
* add Statement of need
* add explanations of created files and used abbreviations
* name change from "MULTIPLY SAR pre-processing" to "SenSARP"
* add notebooks (use cases)
    * default_process_single_image.ipynb
    * default_process_time_series.ipynb
    * use_user_defined_graphs.ipynb
* remove notebook running_test_application.ipynb

Software
~~~~~~~~~
* add more explanation to config file
* add more documentation to functions of class SARPreProcessor
* add functionality that to user defined xml-graphs can be used
* add functionality that a single file can be processed
* class NetcdfStackCreator was partly rewritten
* functionality of shell file (solve_projection_problem.sh) was included within python code
* bug fixes
