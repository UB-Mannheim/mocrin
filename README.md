![ocromore](docs/img/mocrin_logo.png)
========================
![license](https://img.shields.io/badge/license-Apache%20License%202.0-blue.svg)

Overview
--------
Coordinates multiple ocr-engine to create a uniform workflow and folder structure.

`mocrin` is a command line driven processing tool for multiple ocr-engine.  
The main purpose is to handle multiple ocr-engine with one interface for 
a cleaner and uniform workflow. Another purpose is to serve as part of an self-configuration
process to extract the best settings for different ocr-engines. 
Just now you can store multiple configuration files for the ocr-engines.
It can also be used to cut out areas from image with user-set characteristics, which
can be further used as training datasets for NN-models.

First the program parses the different ocr-outputfiles to a sqlite-database.
The purpose of this database is to serve as an exchange and store platform using 
pandas as handler. Combining pandas and the dataframe-objectifier offers a 
wide-range of performant use-cases like msa. 
To evaluate the results you can either use the common standard
isri tool to generate a accuracy report or do visual comparision with diff-tools (default "meld").

Note that the automatic processing will sometimes need some manual adjustments.

#### Current State
✓  Talk to tesseract  
✓  Talk to ocropus    
✓  Talk to abbyy 
✓  Configuration files (for the whole process and every single ocr-engine) 
✓  Implement cut method 
✓  Create uniform output structure  
✓  Create hocr-output   
✓  Create logs with settings information   
  
✘  Store results in database/hocr-files  
✘  Plot results in different ways (with matplotlib)

##### Output fileformats
✓  hocr (with confidences)   
✓  abbyy-xml (with confidences "ASCII")
 
Installation
------------
#### Requirements

   ##### Install:
   
   - linux distribution:    
     - [Ubuntu][ubuntu-link]
     - ...
   - [Python 3.6][python-link]
   
   ##### Alternative docker (for windows recommended):
   
   Build:  
   
   - docker build -t mocrin .
   
   Run:  
   
   - docker run -it -v `PWD`:/home/developer/coding/mocrin mocrin 
   - then run cli commands (see example)
   
   To run the scripts for visual results in your OS:  
   (not available in the docker-image) 
     
   - install Python and Requirements   

   ##### Info
   The project was written in PyCharm 2017.3 (CE)>,   
   so if you are a developer it's recommended to use it. 

   Python 3.6.3 (default, Oct  6 2017, 08:44:35)   
   [GCC 5.4.0 20160609] on linux  
   Tested on: Ubuntu17.10
    
   [ubuntu-link]: https://www.ubuntu.com/
   [python-link]: https://www.anaconda.com/download/
    
#### Building instructions

    Dependencies can be installed into a Python Virtual Environment:

        $ virtualenv mocrin_venv/
        $ source mocrin_venv/bin/activate
        $ pip install -r requirements.txt

Process steps
----------
#### Overview
Will follow soon.

Running
-------
#### Example
First of all you have to adjust the config-files.
There are two main config-files in "./profiles/":
   + cli_args 
        + path to ocr ocr-files (e.g. hocr)
        + parameter for parsing hocr to db
            + naming etc.
   + ocropy 
      + path to db
      + parameter for combining the information from the ocr-files
   + tess 
        + path to db
        + parameter for combining the information from the ocr-files
        
The parameter to perform the examples are set as default.  
So you can just run the following commands.

At the current stage it is recommended to use PyCharm to perform the next steps.
        
Parse files to db and do preprocessing:

    # All parameters can set in the to_db_reader config
    # set HOCR2SQL parse files to db 
    # set POS parameter, to set the naming of db and tables 
    # set PREPROCSSING (It is recommended to perform the preprocessing steps directly after parsing  
    # but it is not necassary)
    
    $ python3 ./plt_charinfo.py
    
Combine files and generate a accuracy report:

    # All parameters can set in the voter config
    # set DO_MSA_BEST to perform msa (not Textdistance) method
    # set DO_ISRI_VAL to generate a accuracy report
    
    $ python3 ./main_msa_ndist_charconf.py
    
To perform a visual comparision:

    $ python3 ./result_visualization.py

The result are stored in ./Testfiles/tableparser_output/

Further Information
-------------------
Will follow soon.

Originally written by Jan Kamlah.
