###################### INFORMATION #############################
#           akf-mocrin is a "Multiple OCR Interface"
# Program:  **akf-mocrin**
# Info:     **Python 3.6**
# Author:   **Jan Kamlah**
# Date:     **12.01.2018**

########## IMPORT ##########
import configparser
import numpy as np
import argparse
import subprocess
from multiprocessing import Process
import json
import shlex
import datetime
import os
import sys
from mocrinlib.tessapi import tess_pprocess
from mocrinlib.common import create_dir, get_iopath, get_filenames
from mocrinlib.imgproc import safe_imread, get_binary

########## CMD-PARSER-SETTINGS ##########
def get_args(argv):
    """
    This function parses the command line-options
    :param:no params
    :return:the parsed cl-options
    """
    if argv:
        sys.argv.extend(argv)

    argparser = argparse.ArgumentParser()

    argparser.add_argument("--info", type=str, default="datetime", help="Text that will be tagged to the outputdirectory. Default prints datetime (year-month-day_hour%minutes).")

    argparser.add_argument("--fpathin", type=str, default="", help="Set Input Filenname/Path without config.ini")
    argparser.add_argument("--fpathout", type=str, default="", help="Set Output Filenname/Path without config.ini")
    argparser.add_argument("-c", "--cut", action='store_true', help="Cut certain areas of the image (see tess_profile['Cutter'].")
    argparser.add_argument("-f", "--fileformat", default="jpg",help="Fileformat of the images")
    argparser.add_argument("-b", "--binary", action='store_true', help="Binarize the image")
    argparser.add_argument("--no-tess", action='store_true', help="Don't perfom tessract.")
    argparser.add_argument("--no-ocropy", action='store_true', help="Don't perfom ocropy.")
    argparser.add_argument("--tess-profile", default='test', choices=["default","test",""], help="Don't perfom tessract. If the value is an empty string take name from config.ini")
    argparser.add_argument("--ocropy-profile", default='test', choices=["default","test",""], help="Don't perfom ocropy. If the value is an empty string take name from config.ini")
    argparser.add_argument("--filter", type=str, default="sauvola",choices=["sauvola","niblack","otsu","yen","triangle","isodata","minimum","li","mean"],help='Chose your favorite threshold filter: %(choices)s')
    argparser.add_argument("--threshwindow", type=int, default=31, help='Size of the window (binarization): %(default)s')
    argparser.add_argument("--threshweight", type=float, default=0.2, choices=np.arange(0, 1.0),help='Weight the effect of the standard deviation (binarization): %(default)s')
    argparser.add_argument("--threshbin", type=int, default=256,
                           help='Number of bins used to calculate histogram. This value is ignored for integer arrays.')
    argparser.add_argument("--threshhitter", type=int, default=10000,
                           help='Maximum number of iterations to smooth the histogram.')

    args = argparser.parse_args()
    return args

########## JSON_DefaultRemover ##########
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
def cut_check(args,tess_profile:dict)->int:
    """
    Checks requirements for cutting
    :param args: see 'get_args'
    :param tess_profile: see 'get_profile'
    :return:
    """
    try:
        if "--cut" in tess_profile["parameters"] and tess_profile["parameters"]["--cut"]["value"] == "True":
            args.cut = True
        if args.cut:
            args.no_ocropy = True
        else:
            del tess_profile["cutter"]
    except:
        args.cut = False
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
        profilename = config['DEFAULT']['TESSPROFILENAME']
        if args.tess_profile != "": profilename = args.tess_profile
        tess_profile_path = config['DEFAULT']['TESSPROFILEPATH'] + profilename + "_tess_profile.json"
        with open(tess_profile_path,"r") as file:
            tess_profile = json.load(file, cls=DefaultRemover)
            cut_check(args,tess_profile)
        if tess_profile == None:
            tess_profile = ""
    if not args.no_ocropy:
        profilename = config['DEFAULT']['OCROPYPROFILENAME']
        if args.ocropy_profile != "": profilename = args.ocropy_profile
        ocropy_profile_path = config['DEFAULT']['OCROPYPROFILEPATH']+profilename+"_ocropy_profile.json"
        with open(ocropy_profile_path,"r") as file:
            ocropy_profile = json.load(file,cls=DefaultRemover)
        if ocropy_profile == None:
            ocropy_profile = ""
    return (tess_profile,ocropy_profile)

def update_args(args,config):
    cli_args_profile_path = config['DEFAULT']['CLI_ARGSPATH']+config['DEFAULT']['CLI_ARGSNAME']+"_argparse_profile.json"
    with open(cli_args_profile_path, "r") as file:
        args_profile = json.load(file, cls=DefaultRemover)
        for key, value in args_profile.items():
            if key in sys.argv: continue
            if "alias" in value and value["alias"] in sys.argv: continue
            key = key.lstrip("-").replace("-","_")
            vars(args)[key] = value["value"]
    return 0

def store_settings(path_out:str,profile:dict,args,ocrname:str)->int:
    """
    Saves the used settings in the folder of the output file
    :param path_out:
    :param profile:
    :param args:
    :param ocrname:
    :return:
    """
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

########## TESSERACT FUNCTIONS ##########
def start_tess(file:str,path_out:str, tess_profile:dict,args)->int:
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
    # with tesserocr obsolete ||
    # use if tesserocr should not be installed -> than cut and extended hocr cant be used
    # all dependencies have to be removed (tessapi..)
    # maybe OCR-D can build another useful api, if so please replace
        #parameters = ""
        #for param in tess_profile['parameters']:
        #    if tess_profile['parameters'][param]['value'] != "" and tess_profile['parameters'][param]['value'] != "False":
        #        parameters += param+""+tess_profile['parameters'][param]['value']+" "
        #if "variables" in tess_profile:
        #    for var in tess_profile['variables']:
        #        parameters += "-c "+var + "=" + tess_profile['variables'][var]['value'] + " "
        #        parameters += "-c " + var + "=" + tess_profile['variables'][var]['value'] + " "
        #parameters += "-c tessedit_debug_quality_metrics=1 -c tessedit_write_params_to_file=/home/PARAMS.txt"
        #parameters.strip()
        #parameters = shlex.split(parameters)
        #subprocess.Popen(args=['tesseract',file,file_out]+parameters).wait()
    file_out = path_out + file.split('/')[-1]
    tess_pprocess(file, file_out, args.cut, tess_profile)
    print("Finished tesseract for: "+file.split('/')[-1])
    return 0

########## OCROPY FUNCTIONS ##########
def start_ocropy(file:str,path_out:str, ocropy_profile:dict,args)->int:
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
    # gets all user-specific parameters from the ocropy-profile
    parameters = get_ocropy_param(ocropy_profile)
    subprocess.Popen(args=["ocropus-nlbin",file,"-o"+path_out+args.infotxt+fname+"/"]+parameters["ocropus-nlbin"]).wait()
    subprocess.Popen(args=["ocropus-gpageseg",path_out+args.infotxt+fname+"/????.bin.png","-n","--maxlines","2000"]+parameters["ocropus-gpageseg"]).wait()
    subprocess.Popen(args=["ocropus-rpred",path_out+args.infotxt+fname+"/????/??????.bin.png"]+parameters["ocropus-rpred"]).wait()
    subprocess.Popen(args=["ocropus-hocr",path_out+args.infotxt+fname+"/????.bin.png","-o"+path_out+"/"+file.split('/')[-1]+".hocr"]+parameters["ocropus-hocr"]).wait()
    print("Finished ocropy for: " + file.split('/')[-1])
    return 0

def get_ocropy_param(ocropy_profile:dict)->dict:
    """
    Get all user-specific parameters from the ocropy-profile,
    but only for "ocropus-nlbin","ocropus-gpageseg","ocropus-rpred","ocropus-hocr".
    :param ocropy_profile:
    :return: dict with parameters and values which are different to the default values
    """
    parameters = {}
    # only search for specific func parameters
    for funcall in ["ocropus-nlbin","ocropus-gpageseg","ocropus-rpred","ocropus-hocr"]:
        if funcall in ocropy_profile['parameters']:
            parameters[funcall] = ""
            for param in ocropy_profile['parameters'][funcall]:
                # ignore 'files' param
                if param == "files":
                    continue
                # Go one level deeper if necessary
                if "-" not in param:
                    for next_param in ocropy_profile['parameters'][funcall][param]:
                        if next_param == "files":
                            continue
                        if ocropy_profile['parameters'][funcall][param][next_param]['value'] != "" and \
                                ocropy_profile['parameters'][funcall][param][next_param]['value'] != False:
                            if "action" in ocropy_profile['parameters'][funcall][param][next_param]:
                                parameters[funcall] += next_param + " "
                            else:
                                parameters[funcall] += next_param + " " + ocropy_profile['parameters'][funcall][param][next_param][
                                    'value'] + " "
                else:
                    if ocropy_profile['parameters'][funcall][param]['value'] != "" and ocropy_profile['parameters'][funcall][param]['value'] != False:
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

########### MAIN FUNCTION ##########
def start_mocrin(*argv)->int:
    """
    The filespath are stored in the config.ini file.
    And can be changed there.
    :param *argv: argument vector with arguments parsed by function call not commandline
    """
    config = configparser.ConfigParser()
    config.sections()
    config.read('config.ini')
    args = get_args(argv)
    update_args(args,config)
    args.infofolder = ""
    args.infotxt = ""
    if args.info != "":
        args.infotxt = ""
        if args.info == "datetime":
            args.infofolder = datetime.datetime.now().strftime("%Y-%m-%d_T%HH%MM")+"/"
        else:
            args.infofolder = args.info+"/"
            args.infotxt = args.info+"_"
    PATHINPUT, PATHOUTPUT = get_iopath(args.fpathin,args.fpathout,config)
    files = get_filenames(args.fileformat,PATHINPUT)
    tess_profile, ocropy_profile = get_profiles(args, config)

    for idx,file in enumerate(files):
        args.idx = idx
        path_out = PATHOUTPUT+os.path.dirname(file).replace(PATHINPUT[:-1],"")

        # Safe image read function
        image = safe_imread(file)

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
