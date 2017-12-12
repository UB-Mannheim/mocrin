###################### INFORMATION #############################
#           akf-mocrin is a "Multiple OCR Interface"
# Program:  **akf-mocrin**
# Info:     **Python 3.6**
# Author:   **Jan Kamlah**
# Date:     **01.12.2017**

########## IMPORT ##########
import configparser
import skimage as ski
import scipy.misc as misc
import skimage.filters as imgfilter
from skimage.io import imread, imsave
import skimage.color as color
import numpy as np
import argparse
import os
import glob as glob2
import subprocess
from multiprocessing import Process
import json
import shlex
import copy
import warnings
import datetime

import sys
import os.path as path

#obsolete
#from PIL import Image
#import pytesseract
#import cv2 as cv2
#import tesserocr

########## CMD-PARSER-SETTINGS ##########
def get_args():
    """
    This function parses the cl-options
    :param:no params
    :return:the parsed cl-options
    """
    argparser = argparse.ArgumentParser()

    argparser.add_argument("--info", type=str, default="Settings", help="Text that will be tagged to the outputname")

    argparser.add_argument("-i", "--image",help="path to input image to be OCR'd")
    argparser.add_argument("-f", "--imageformat", default="jpg",help="format of the images")
    argparser.add_argument("-p", "--preprocess", type=str, default="thresh",help="type of preprocessing to be done")
    argparser.add_argument("-b", "--binary", action='store_true', help="Produce a binary")
    argparser.add_argument("--no-tess", action='store_true', help="Don't perfom tessract.")
    argparser.add_argument("--no-ocropy", action='store_false', help="Don't perfom ocropy.")
    argparser.add_argument("--tess-profile", default='test', choices=["default"], help="Don't perfom tessract.")
    argparser.add_argument("--ocropy-profile", default='test', choices=["default"], help="Don't perfom ocropy.")
    argparser.add_argument('--filter', type=str, default="sauvola",choices=["sauvola","niblack","otsu","yen","triangle","isodata","minimum","li","mean"],help='Chose your favorite threshold filter: %(choices)s')
    argparser.add_argument('--threshwindow', type=int, default=31, help='Size of the window (binarization): %(default)s')
    argparser.add_argument('--threshweight', type=float, default=0.2, choices=np.arange(0, 1.0),help='Weight the effect of the standard deviation (binarization): %(default)s')
    argparser.add_argument('--threshbin', type=int, default=256,
                           help='Number of bins used to calculate histogram. This value is ignored for integer arrays.')
    argparser.add_argument('--threshitter', type=int, default=10000,
                           help='Maximum number of iterations to smooth the histogram.')

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
                    else:
                        stop =1
        if len(delarr) == len(obj):
            del obj
            return
        for delitem in delarr:
            del obj[delitem]
        return obj

########## FUNCTIONS ##########
def store_settings(path_out,profile,args,ocrname):
    with open(path_out+ocrname+"_"+args.infotxt+"settings.txt","w") as settings:
        justnow = datetime.datetime.now()
        settings.write("-" * 200 + "\n")
        settings.write(ocrname+"-Settings for the run "+'"'+args.info+'"'+"\n"+"Timestamp:"+justnow.ctime()+"\n")
        settings.write("-" * 200 + "\n")
        settings.write("Arguments:\n")
        json.dump(vars(args), settings, sort_keys=True, indent=4)
        settings.write("\n"+"-" * 200 + "\n")
        settings.write("Profile:\n")
        json.dump(profile,settings, sort_keys=True, indent=4)
    return 0

def valid_check(file):
    try:
        image = imread("%s" % file)
    except IOError:
        print("cannot open %s" % file)
        #logging.warning("cannot open %s" % input)
        return 1
    return image

def get_binary(args, image, file,binpath):
    if not os.path.exists(binpath + file.split('/')[-1]):
        create_dir(binpath)
        uintimage = get_uintimg(image)
        if args.filter == "sauvola":
            thresh = imgfilter.threshold_sauvola(uintimage, args.threshwindow, args.threshweight)
            binary = image > thresh
        elif args.filter == "niblack":
            thresh = imgfilter.threshold_niblack(uintimage, args.threshwindow, args.threshweight)
            binary = thresh
        elif args.filter == "otsu":
            thresh = imgfilter.threshold_otsu(uintimage, args.threshbin)
            binary = image <= thresh
        elif args.filter == "yen":
            thresh = imgfilter.threshold_yen(uintimage, args.threshbin)
            binary = image <= thresh
        elif args.filter == "triangle":
            thresh = imgfilter.threshold_triangle(uintimage, args.threshbin)
            binary = image > thresh
        elif args.filter == "isodata":
            thresh = imgfilter.threshold_isodata(uintimage, args.threshbin)
            binary = image > thresh
        elif args.filter == "minimum":
            thresh = imgfilter.threshold_minimum(uintimage, args.threshbin, args.threshitter)
            binary = image > thresh
        elif args.filter == "li":
            thresh = imgfilter.threshold_li(uintimage)
            binary = image > thresh
        elif args.filter == "mean":
            thresh = imgfilter.threshold_mean(uintimage)
            binary = image > thresh
        else:
            binary = uintimage
            #if args.filter == "testall":
        #    thresh = imgfilter.try_all_threshold(uintimage)
        #binary = uintimage > thresh
        #binary = 1 - binary  # inverse binary
        with warnings.catch_warnings():
            # Transform rotate convert the img to float and save convert it back
            warnings.simplefilter("ignore")
            misc.imsave(binpath+file.split('/')[-1],binary)
    return binpath+file.split('/')[-1]

def get_uintimg(image):
    if len(image.shape) > 2:
        uintimage = color.rgb2gray(copy.deepcopy(image))
    else:
        uintimage = copy.deepcopy(image)
    if uintimage.dtype == "float64":
        with warnings.catch_warnings():
            # Transform rotate convert the img to float and save convert it back
            warnings.simplefilter("ignore")
            uintimage = ski.img_as_uint(uintimage, force_copy=True)
    return uintimage

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

def start_tess(file,path_out, tess_profile,args):
    """
    Start tesseract over "pytesseract" a cli-module
    :param file: fileinputpath
    :param fop: fileoutputpath
    :param profile: contains user-specific parameters/option for tesseract
    :return:
    """

    create_dir(path_out)
    if args.idx == 0:
        store_settings(path_out,tess_profile,args, "Tesseract")
    path_out+= args.infotxt
    parameters = ""
    for param in tess_profile['parameters']:
        if tess_profile['parameters'][param]['value'] != "" and tess_profile['parameters'][param]['value'] != "False":
            parameters += param+" "+tess_profile['parameters'][param]['value']+" "
    if "variables" in tess_profile:
        for var in tess_profile['variables']:
            parameters += "-c "+var + "=" + tess_profile['variables'][var]['value'] + " "
    parameters.strip()
    parameters = shlex.split(parameters)
    file_out = path_out + file.split('/')[-1]
    subprocess.Popen(args=['tesseract',file,file_out]+parameters).wait()
    print("Finished tesseract for:"+file.split('/')[-1])
    return 0

def start_ocropy(file,path_out, ocropy_profile,args):
    """
    Start tesseract over a cli
    :param file: fileinputpath
    :param fop: fileoutputpath
    :param profile: contains user-specific parameters/option for ocropy
    :return:
    """
    fname = file.split('/')[-1].split('.')[0]
    create_dir(path_out)
    if args.idx == 0:
        store_settings(path_out,ocropy_profile,args, "Ocropy")
    parameters = get_ocropy_param(ocropy_profile)
    subprocess.Popen(args=["ocropus-nlbin",file,"-o"+path_out+args.infotxt+fname+"/"]+parameters["ocropus-nlbin"]).wait()
    subprocess.Popen(args=["ocropus-gpageseg",path_out+args.infotxt+fname+"/????.bin.png","-n","--maxlines","2000"]+parameters["ocropus-gpageseg"]).wait()
    subprocess.Popen(args=["ocropus-rpred","-Q 4",path_out+args.infotxt+fname+"/????/??????.bin.png"]+parameters["ocropus-rpred"]).wait()
    subprocess.Popen(args=["ocropus-hocr",path_out+args.infotxt+fname+"/????.bin.png","-o"+path_out+"/"+fname.split('/')[-1]+".hocr"]+parameters["ocropus-hocr"]).wait()
    print("Finished ocropy for:" + file.split('/')[-1])
    return 0

def get_ocropy_param(ocropy_profile):
    parameters = {}
    for funcall in ["ocropus-nlbin","ocropus-gpageseg","ocropus-rpred","ocropus-hocr"]:
        if funcall in ocropy_profile['parameters']:
            parameters[funcall] = ""
            for param in ocropy_profile['parameters'][funcall]:
                if param == "files":
                    continue
                if "-" not in param:
                    for next_param in ocropy_profile['parameters'][funcall][param]:
                        if next_param == "files":
                            continue
                        if ocropy_profile['parameters'][funcall][param][next_param]['value'] != "" and \
                                ocropy_profile['parameters'][funcall][param][next_param]['value'] != "False":
                            if "action" in ocropy_profile['parameters'][funcall][param][next_param]:
                                parameters[funcall] += next_param + " "
                            else:
                                parameters[funcall] += next_param + " " + ocropy_profile['parameters'][funcall][param][next_param][
                                    'value'] + " "
                else:
                    if ocropy_profile['parameters'][funcall][param]['value'] != "" and ocropy_profile['parameters'][funcall][param]['value'] != "False":
                        if "action" in ocropy_profile['parameters'][funcall][param]:
                            parameters[funcall] += param + " "
                        else:
                            parameters[funcall] += param+" "+ocropy_profile['parameters'][funcall][param]['value']+" "
            #if len(parameters[funcall]) == 0:
            #    del parameters[funcall]
            #    continue
            parameters[funcall].strip()
            parameters[funcall] = shlex.split(parameters[funcall])

    return parameters

########### MAIN ##########
def start_mocrin():
    # The filespath are stored in the config.ini file.
    # And can be changed there.
    config = configparser.ConfigParser()
    config.sections()
    config.read('config.ini')
    args = get_args()
    args.infofolder = ""
    args.infotxt = ""
    if args.info != "":
        args.infofolder = args.info+"/"
        args.infotxt = args.info+"_"
    PATHINPUT = config['DEFAULT']['PATHINPUT']
    PATHOUTPUT = config['DEFAULT']['PATHOUTPUT']
    tess_profile, ocropy_profile = get_profiles(args, config)
    # Get all filenames and companynames
    files = glob2.glob(PATHINPUT + "**/*." + args.imageformat, recursive=True)
    for idx,file in enumerate(files):
        args.idx = idx
        path_in = file.replace(PATHINPUT, "").split("/")
        path_out = PATHOUTPUT
        for pathparts in path_in[:-1]:
            path_out += pathparts + "/"

        # Check if the file is a valid image for the ocr
        image = valid_check(file)

        # Produce a binary image, could improve the results of the ocr?
        if args.binary:
            file = get_binary(args, image, file,path_out+'bin/')

        # Start the ocr-processes ("p") asynchronously
        procs = []

        if not args.no_tess:
            p1 = Process(target=start_tess, args=[file, path_out + "tess/"+args.infofolder, tess_profile,args])
            print("Call tesseract!")
            p1.start()
            procs.append(p1)
        if not args.no_ocropy:
            p2 = Process(target=start_ocropy, args=[file, path_out + "ocropy/"+args.infofolder, ocropy_profile,args])
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
