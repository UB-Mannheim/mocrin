###################### INFORMATION #############################
#           Dont ask! It is the Ocronator..!
# Program:  **Ocronator**
# Info:     **Python 3.6**
# Author:   **Jan Kamlah**
# Date:     **30.11.2017**

######### IMPORT ############
import configparser
from PIL import Image
import pytesseract
import argparse
import cv2 as cv2
import os
import glob as glob2
import subprocess
from multiprocessing import Process
import json

####################### CMD-PARSER-SETTINGS ########################
def get_args():
    """
    This function parses the cl-options
    :param:no params
    :return:the parsed cl-options
    """
    parser = argparse.ArgumentParser()
    #args.add_argument("-i", "--image", required=True,help="path to input image to be OCR'd")
    #args.add_argument("-p", "--preprocess", type=str, default="thresh",help="type of preprocessing to be done")
    parser.add_argument("--no-tess", action='store_true', help="Don't perfom tessract.")
    parser.add_argument("--no-ocropy", action='store_false', help="Don't perfom ocropy.")
    parser.add_argument("--tess-profile", default='default', choices=["default"], help="Don't perfom tessract.")
    parser.add_argument("--ocropy-profile", default='default', choices=["default"], help="Don't perfom ocropy.")
    args = parser.parse_args()
    return args

######### FUNCTIONS ############
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

def get_profiles(args,config):
    """
    This function loads the json-profiles for tesseract and ocropy,
    which contains user-specific parameters and options.
    :param args:
    :param config:
    :return: json-profiles (dictionaries) for tesseract and ocropy
    """
    tess_profile, ocropy_profile = {}, {}
    if not args.no_tess:
        tess_profile_path = config['DEFAULT']['Tessprofile'] + args.tess_profile + "_tess_profile.json"
        with open(tess_profile_path,"r") as file:
            tess_profile = json.load(file)
    if not args.no_ocropy:
        ocropy_profile_path = config['DEFAULT']['Ocropyprofile']+args.ocropy_profile+"_ocropy_profile.json"
        with open(ocropy_profile_path,"r") as file:
            ocropy_profile = json.load(file)
    return (tess_profile,ocropy_profile)

def start_tess(file,fop, profile):
    """
    Start tesseract over "pytesseract" a cli-module
    :param file: fileinputpath
    :param fop: fileoutputpath
    :param profile: contains user-specific parameters/option for tesseract
    :return:
    """
    create_dir(fop)
    # load the image as a PIL/Pillow image, apply OCR, and then delete
    # the temporary file
    parameters = ""
    for param in profile['parameters']:
        if profile['parameters'][param]['value'] != "" and profile['parameters'][param]['value'] != "False":
            parameters += param+" "+profile['parameters'][param]['value']+" "
    parameters.strip()
    text = pytesseract.image_to_string(Image.open(file), config=parameters)
    with open(fop + file.split('/')[-1] + '.txt', 'w') as output:
        output.write(text)
        # show the output images
        # cv2.imshow("Image", file)
        # cv2.imshow("Output", gray)
        # cv2.waitKey(0)
    return 0

def start_ocropy(file,fop, profile):
    """
    Start tesseract over a cli
    :param file: fileinputpath
    :param fop: fileoutputpath
    :param profile: contains user-specific parameters/option for ocropy
    :return:
    """
    fname = file.split('/')[-1].split('.')[0]
    create_dir(fop)
    subprocess.Popen(args=["ocropus-nlbin",file,"-o"+fop+fname+"/"]).wait()
    subprocess.Popen(args=["ocropus-gpageseg",fop+fname+"/????.bin.png"]).wait()
    subprocess.Popen(args=["ocropus-rpred","-Q 4",fop+fname+"/????/??????.bin.png"]).wait()
    subprocess.Popen(args=["ocropus-hocr",fop+fname+"/????.bin.png","-o"+fop+"/"+file.split('/')[-1]+".html"]).wait()
    return 0


################ START ################
if __name__ == "__main__":
    """
    Entrypoint: Searches for the files and parse them into the mainfunction (can be multiprocessed)
    """
    # The filespath are stored in the config.ini file.
    # And can be changed there.
    config = configparser.ConfigParser()
    config.sections()
    config.read('config.ini')
    args = get_args()
    pathx = config['DEFAULT']['allpath']
    pathxoutput = config['DEFAULT']['allpath_output']
    tess_profile, ocropy_profile = get_profiles(args, config)
    for filen in ['short','long']:
        for i in [1957,1961,1965,1969,1973,1976]:
            path = pathx+filen+"/"+str(i)+"/*"
            pathoutput = pathxoutput + filen + "/" + str(i) + "/"
            # Get all filenames and companynames
            files = glob2.glob(path)
            for idx, file in enumerate(files):
                procs = []
                if not args.no_tess:
                    p1 = Process(target=start_tess, args=[file, pathoutput + "tess/",tess_profile])
                    print("Starts with Tesseract!")
                    p1.start()
                    procs.append(p1)
                if not args.no_ocropy:
                    p2 = Process(target=start_ocropy, args=[file, pathoutput + "ocropy/",ocropy_profile])
                    print("Starts with Ocropus!")
                    p2.start()
                    procs.append(p2)
                for p in procs:
                    p.join()
                print("Next image!")
                #start_tess(file,pathoutput+ "tess/"))
                #start_ocropy(file,pathoutput+ "ocropy/")
    print("FINISHED!")