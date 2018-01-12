###################### INFORMATION #############################
#           akf-mocrin is a "Multiple OCR Interface"
# Program:  **akf-mocrin**
# Info:     **Python 3.6**
# Author:   **Jan Kamlah**
# Date:     **01.12.2017**

########## IMPORT ##########
import configparser
import numpy as np
import argparse
import glob as glob2
import subprocess
from multiprocessing import Process
import json
import shlex
import datetime
from mocrinlib.tessapi import tess_pprocess
from mocrinlib.common import create_dir
from mocrinlib.imgproc import safe_imread, get_binary

########## CMD-PARSER-SETTINGS ##########
def get_args():
    """
    This function parses the command line-options
    :param:no params
    :return:the parsed cl-options
    """
    argparser = argparse.ArgumentParser()

    argparser.add_argument("--info", type=str, default="sauvola", help="Text that will be tagged to the outputdirectory. Default prints datetime.")

    argparser.add_argument("-i", "--image",help="path to input image to be OCR'd")
    argparser.add_argument("-c", "--cut", action='store_true', help="Cut certain areas of the image (see tess_profile['Cutter'].")
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

########## COMMON FUNCTIONS ##########
def cut_check(args,tess_profile):
    """
    Checks requirements for cutting
    :param args: see 'get_args'
    :param tess_profile: see 'get_profile'
    :return:
    """
    try:
        if tess_profile["cutter"] and tess_profile["parameters"]["--cut"]["value"] == "True":
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
        tess_profile_path = config['DEFAULT']['Tessprofile'] + args.tess_profile + "_tess_profile.json"
        with open(tess_profile_path,"r") as file:
            tess_profile = json.load(file, cls=DefaultRemover)
            cut_check(args,tess_profile)
        if tess_profile == None:
            tess_profile = ""
    if not args.no_ocropy:
        ocropy_profile_path = config['DEFAULT']['Ocropyprofile']+args.ocropy_profile+"_ocropy_profile.json"
        with open(ocropy_profile_path,"r") as file:
            ocropy_profile = json.load(file,cls=DefaultRemover)
        if ocropy_profile == None:
            ocropy_profile = ""
    return (tess_profile,ocropy_profile)

def store_settings(path_out,profile,args,ocrname):
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
    # with tesserocr obsolete
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
    # gets all user-specific parameters from the ocropy-profile
    parameters = get_ocropy_param(ocropy_profile)
    subprocess.Popen(args=["ocropus-nlbin",file,"-o"+path_out+args.infotxt+fname+"/"]+parameters["ocropus-nlbin"]).wait()
    subprocess.Popen(args=["ocropus-gpageseg",path_out+args.infotxt+fname+"/????.bin.png","-n","--maxlines","2000"]+parameters["ocropus-gpageseg"]).wait()
    subprocess.Popen(args=["ocropus-rpred",path_out+args.infotxt+fname+"/????/??????.bin.png"]+parameters["ocropus-rpred"]).wait()
    subprocess.Popen(args=["ocropus-hocr",path_out+args.infotxt+fname+"/????.bin.png","-o"+path_out+"/"+fname.split('/')[-1]+".hocr"]+parameters["ocropus-hocr"]).wait()
    print("Finished ocropy for: " + file.split('/')[-1])
    return 0

def get_ocropy_param(ocropy_profile):
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
    """
    The filespath are stored in the config.ini file.
    And can be changed there.
    """
    config = configparser.ConfigParser()
    config.sections()
    config.read('config.ini')
    args = get_args()
    args.infofolder = ""
    args.infotxt = ""
    if args.info != "":
        args.infotxt = ""
        if args.info == "datetime":
            args.infofolder = datetime.datetime.now().strftime("%Y-%m-%d_%Hh%Mmin")+"/"
        else:
            args.infofolder = args.info+"/"
            args.infotxt = args.info+"_"

    PATHINPUT = config['DEFAULT']['PATHINPUT']
    PATHOUTPUT = config['DEFAULT']['PATHOUTPUT']
    tess_profile, ocropy_profile = get_profiles(args, config)
    # Get all filenames and companynames (iglob-iterator)
    files = glob2.iglob(PATHINPUT + "**/*." + args.imageformat, recursive=True)

    for idx,file in enumerate(files):
        args.idx = idx
        path_in = file.replace(PATHINPUT, "").split("/")
        path_out = PATHOUTPUT
        for pathparts in path_in[:-1]:
            path_out += pathparts + "/"

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
