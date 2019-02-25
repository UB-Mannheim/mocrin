![mocrin](docs/img/mocrin_logo.png "mocrin")
========================
![license](https://img.shields.io/badge/license-Apache%20License%202.0-blue.svg)

Overview
--------
**Mocrin** coordinates multiple ocr-engine to create a 
uniform workflow and folder structure.
It is part of the [Aktienführer-Datenarchiv work process][akf-link],
but can also be used independently.

![mocrin_process](docs/img/mocrin_process.png "Workflow diagram")

`Mocrin` is a command line driven processing tool for multiple ocr-engine.  
The main purpose is to handle multiple ocr-engine with one interface for 
a cleaner and uniform workflow. Another purpose is to serve as part of an self-configuration
process to extract the best settings for different ocr-engines. 
Just now you can store multiple configuration files for the ocr-engines.
It can also be used to cut out areas from image with user-set characteristics, which
can be further used as training datasets for NN-models.

`Ocromore` further parse the different ocr-outputfiles to a sqlite-database.
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

##### Output fileformats
✓  hocr (with confidences)   
✓  abbyy-xml (with confidences "ASCII")
 
Installation
------------
#### Requirements

   ##### Install:
   
   - linux distribution:    
     - [Ubuntu][ubuntu-link]
     - etc.
   - [Python 3.6][python-link]
   
   ##### Alternative docker (for windows recommended):
   
   Build:  
   
    docker build -t mocrin .
   
   Run: 
    
    docker run -it -v 'PWD':/home/developer/coding/mocrin mocrin 
   
   Then run cli commands (see example)
   
   To run the scripts for visual results in your OS:  
   (not available in the docker-image) 
     
   - install Python and Requirements   

   ##### Info
   The project was written in PyCharm 2017.3 (CE)>,   
   so if you are a developer it's recommended to use it. 

   Python 3.6.3 (default, Oct  6 2017, 08:44:35)   
   GCC 5.4.0 20160609 on linux  
   Tested on: Ubuntu17.10
    
#### Building instructions

    Dependencies can be installed into a Python Virtual Environment:

        $ virtualenv mocrin_venv/
        $ source mocrin_venv/bin/activate
        $ pip install -r requirements.txt

Process steps
----------
#### Overview
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
 
Running
-------
#### Example
       
Parse OCR with multiple Engines and store the result in a unified folder structure:

    # All parameters can set in the configs
    # Config files are stored in the profiles folder.
    
    $ python3 ./mocrin.py
    
The result are stored in ./Testfiles/tableparser_output/

Copyright and License
--------

Copyright (c) 2017 Universitätsbibliothek Mannheim

Author: [Jan Kamlah](https://github.com/jkamlah) 

**mocrin** is Free Software. You may use it under the terms of the Apache 2.0 License.
See [LICENSE](./LICENSE) for details.


Acknowledgements
-------

The tools are depending on some third party libraries:
 *  [tesserocr][tesserocr-link] - Wrapper for Tesseract-API (MIT-License)


[ubuntu-link]: https://www.ubuntu.com/ "ubuntu"
[python-link]: https://www.anaconda.com/download/ "anaconda"
[akf-link]: https://github.com/UB-Mannheim/Aktienfuehrer-Datenarchiv-Tools "Aktienfuehrer-Datenarchiv-Tools"
[tesserocr-link]: https://github.com/sirfz/tesserocr "Tesserocr"