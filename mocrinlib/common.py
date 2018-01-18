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

def get_iopath(args,config):
    PATHINPUT = config['DEFAULT']['PATHINPUT']
    if args.file != "":
        PATHINPUT = args.file
    PATHOUTPUT = config['DEFAULT']['PATHOUTPUT']
    return PATHINPUT, PATHOUTPUT

def get_filenames(args,PATHINPUT:str):
    # Get all filenames and companynames (iglob-iterator)
    files = []
    if os.path.isdir(PATHINPUT):
        files = glob.iglob(PATHINPUT + "**/*." + args.fileformat, recursive=True)
    elif os.path.isfile(PATHINPUT):
        files = [PATHINPUT]
    else:
        print("Input informations are not correct.")
    return files

