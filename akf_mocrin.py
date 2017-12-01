###################### INFORMATION #############################
#           akf-mocrin is a "Multiple OCR Interface"
# Program:  **akf-mocrin**
# Info:     **Python 3.6**
# Author:   **Jan Kamlah**
# Date:     **01.12.2017**

########## IMPORT ##########
import configparser
from PIL import Image
import pytesseract
import argparse
#import cv2 as cv2
import os
import glob as glob2
import subprocess
from multiprocessing import Process
import json

########## CMD-PARSER-SETTINGS ##########
def get_args():
    """
    This function parses the cl-options
    :param:no params
    :return:the parsed cl-options
    """
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", "--image",help="path to input image to be OCR'd")
    argparser.add_argument("-f", "--imageformat", default="jpg",help="format of the images")
    argparser.add_argument("-p", "--preprocess", type=str, default="thresh",help="type of preprocessing to be done")
    argparser.add_argument("--no-tess", action='store_true', help="Don't perfom tessract.")
    argparser.add_argument("--no-ocropy", action='store_false', help="Don't perfom ocropy.")
    argparser.add_argument("--tess-profile", default='test', choices=["default"], help="Don't perfom tessract.")
    argparser.add_argument("--ocropy-profile", default='default', choices=["default"], help="Don't perfom ocropy.")
    args = argparser.parse_args()
    return args

########## JSON_defaultremover ##########
class DefaultRemover(json.JSONDecoder):
    """
    Removes all Null/None and all parameters if value == default
    """
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        delarr = []
        for key, value in obj.items():
            if value == None:
                delarr.append(key)
            if key == 'value':
                if "default" in obj:
                    if obj["default"] == obj[key]:
                        del obj
                        return
        if len(delarr) == len(obj):
            del obj
            return
        for delitem in delarr:
            del obj[delitem]
        return obj

########## FUNCTIONS ##########
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
            tess_profile = json.load(file, cls=DefaultRemover)
        if tess_profile == None:
            tess_profile = ""
    if not args.no_ocropy:
        ocropy_profile_path = config['DEFAULT']['Ocropyprofile']+args.ocropy_profile+"_ocropy_profile.json"
        with open(ocropy_profile_path,"r") as file:
            ocropy_profile = json.load(file,cls=DefaultRemover)
        if ocropy_profile == None:
            ocropy_profile = ""
    return (tess_profile,ocropy_profile)

def start_tess(file,path_out, tess_profile):
    """
    Start tesseract over "pytesseract" a cli-module
    :param file: fileinputpath
    :param fop: fileoutputpath
    :param profile: contains user-specific parameters/option for tesseract
    :return:
    """
    create_dir(path_out)
    parameters = ""
    for param in tess_profile['parameters']:
        if tess_profile['parameters'][param]['value'] != "" and tess_profile['parameters'][param]['value'] != "False":
            parameters += param+" "+tess_profile['parameters'][param]['value']+" "
    parameters.strip()
    text = pytesseract.image_to_string(Image.open(file), config=parameters)
    with open(path_out + file.split('/')[-1] + '.txt', 'w') as output:
        output.write(text)
        # show the output images
        # cv2.imshow("Image", file)
        # cv2.imshow("Output", gray)
        # cv2.waitKey(0)
    print("Finished tesseract for:"+file.split('/')[-1])
    return 0

def start_ocropy(file,path_out, ocropy_profile):
    """
    Start tesseract over a cli
    :param file: fileinputpath
    :param fop: fileoutputpath
    :param profile: contains user-specific parameters/option for ocropy
    :return:
    """
    fname = file.split('/')[-1].split('.')[0]
    create_dir(path_out)
    subprocess.Popen(args=["ocropus-nlbin",file,"-o"+path_out+fname+"/"]).wait()
    subprocess.Popen(args=["ocropus-gpageseg",path_out+fname+"/????.bin.png"]).wait()
    subprocess.Popen(args=["ocropus-rpred","-Q 4",path_out+fname+"/????/??????.bin.png"]).wait()
    subprocess.Popen(args=["ocropus-hocr",path_out+fname+"/????.bin.png","-o"+path_out+"/"+file.split('/')[-1]+".html"]).wait()
    print("Finished ocropy for:" + file.split('/')[-1])
    return 0

########### MAIN ##########
def start_mocrin():
    # The filespath are stored in the config.ini file.
    # And can be changed there.
    config = configparser.ConfigParser()
    config.sections()
    config.read('config.ini')
    args = get_args()
    PATHINPUT = config['DEFAULT']['PATHINPUT']
    PATHOUTPUT = config['DEFAULT']['PATHOUTPUT']
    tess_profile, ocropy_profile = get_profiles(args, config)
    # Get all filenames and companynames
    files = glob2.glob(PATHINPUT + "**/*." + args.imageformat, recursive=True)
    for file in files:
        path_in = file.replace(PATHINPUT, "").split("/")
        path_out = PATHOUTPUT
        for pathparts in path_in[:-1]:
            path_out += pathparts + "/"
        # Start the ocr-processes ("p") asynchronously
        procs = []
        if not args.no_tess:
            p1 = Process(target=start_tess, args=[file, path_out + "tess/", tess_profile])
            print("Call tesseract!")
            p1.start()
            procs.append(p1)
        if not args.no_ocropy:
            p2 = Process(target=start_ocropy, args=[file, path_out + "ocropy/", ocropy_profile])
            print("Call ocropy!")
            p2.start()
            procs.append(p2)
        # Wait till all ocr-processes are finished
        for p in procs:
            p.join()
        print("Next image!")
    print("All images are procesed!")
    return 0

########## START ##########
if __name__ == "__main__":
    """
    Entrypoint: Searches for the files and parse them into the mainfunction (can be multiprocessed)
    """
    start_mocrin()
