###################### INFORMATION #############################
#           Module for talking to the tesseract api through tesserocr

########## IMPORT ##########
import os
import glob

########## COMMON FUNCTIONS ##########
def create_dir(newdir:str)->int:
    """
    Creates a new directory
    :param_newdir: Directory which should be created
    :return: None
    """
    if not os.path.isdir(newdir):
        try:
            os.makedirs(newdir)
            print(newdir)
        except IOError:
            print("cannot create %s directoy" % newdir)
    return 0

def get_iopath(fpathin,fpathout,config):
    """
    Get input and ouput path from config
    :param fpathin:
    :param fpathout:
    :param config:
    :return:
    """
    PATHINPUT = config['DEFAULT']['PATHINPUT']
    if fpathin != "":
        PATHINPUT = fpathin
    PATHOUTPUT = config['DEFAULT']['PATHOUTPUT']
    if fpathout != "":
        PATHINPUT = fpathout
    return PATHINPUT, PATHOUTPUT

def get_filenames(fileformat,PATHINPUT:str):
    """
    Get all filenames and companynames (iglob-iterator)
    """
    files = []
    if os.path.isdir(PATHINPUT):
        files = glob.iglob(PATHINPUT + "**/*." + fileformat, recursive=True)
    elif os.path.isfile(PATHINPUT):
        files = [PATHINPUT]
    else:
        print("Input informations are not correct.")
    return files

