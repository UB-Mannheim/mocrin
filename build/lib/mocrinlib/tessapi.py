###################### INFORMATION #############################
#           Module for talking to the tesseract api through tesserocr (please use tesserocr from git.com/ub-mannheim)

########## IMPORT ##########
from tesserocr import PyTessBaseAPI, RIL, iterate_level
import string as string
from skimage.io import imread, imsave
import re
from mocrinlib.common import create_dir
from mocrinlib.imgproc import safe_imread
import lxml.etree as ET
from io import StringIO

########## EXTENDED HOCR FUNCTION ##########
def extend_hocr(file:str, fileout:str, tess_profile:dict=None):
    """
    Prodcues an extended hocr-file with char_confidences
    :param file:
    :param fileout:
    :param tess_profile:
    :return:
    """
    parameters = get_param(tess_profile)
    with PyTessBaseAPI(**parameters) as api:
        set_vars(api, file, tess_profile)
        ri = api.GetIterator()
        # TODO: Need to fix header ...
        #lang = api.GetInitLanguagesAsString()
        version = api.Version()
        hocrparse = ET.parse(StringIO(
f'''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<title>OCR Results</title>
<meta http-equiv="content-type" content="text/html; charset=utf-8" />
<meta name='ocr-system' content='tesseract {version}' />
<meta name='ocr-capabilities' content='ocr_page ocr_carea ocr_par ocr_line ocrx_word'/>
</head>
</html>'''))
        hocrroot = hocrparse.getroot()
        hocrtess = ET.fromstring(api.GetHOCRText(0))
        hocrtess.set("title", "image "+file+"; bbox"+hocrtess.get("title").split("bbox")[-1])
        allwordinfo = hocrtess.findall('.//div/p/span/span')
        level = RIL.SYMBOL
        bbinfo = tuple()
        conf = ""
        for r in iterate_level(ri, level):
            if bbinfo != r.BoundingBoxInternal(RIL.WORD):
                if bbinfo != ():
                    bbox = "bbox " + " ".join(map(str, bbinfo))
                    for wordinfo in allwordinfo:
                        if bbox in wordinfo.get("title"):
                            wordinfo.set("title", wordinfo.get("title")+";x_confs"+conf)
                            allwordinfo.remove(wordinfo)
                            break
                    conf = ""
                bbinfo = r.BoundingBoxInternal(RIL.WORD)
            conf += " "+str(r.Confidence(level))
    bbox = "bbox " + " ".join(map(str, bbinfo))
    for wordinfo in allwordinfo:
        if bbox in wordinfo.get("title"):
            wordinfo.set("title", wordinfo.get("title") + ";x_confs" + conf)
    hocrbody = ET.SubElement(hocrroot, "body")
    hocrbody.append(hocrtess)
    hocrparse.write(fileout+".hocr", xml_declaration=True,encoding='UTF-8')
    return 0

def get_param(tess_profile:dict):
    """
    Read the parameters for the api func call
    :param tess_profile:
    :return:
    """
    # Set Parameters
    parameters = {}
    if 'parameters' in tess_profile:
        for param in tess_profile['parameters']:
            if param != "":
                if "tessdata-dir" in param:
                    parameters["path"] = tess_profile['parameters'][param]['value']
                elif "l" in param:
                    parameters["lang"] = tess_profile['parameters'][param]['value']
                elif "oem" in param:
                    parameters["oem"] = int(tess_profile['parameters'][param]['value'])
                elif "psm" in param:
                    parameters["psm"] = int(tess_profile['parameters'][param]['value'])
    return parameters

def set_vars(api, file:str, tess_profile:dict):
    """
    Reads the user-specific variables from the tess_profile
    :param api:
    :param file:
    :param tess_profile:
    :return:
    """
    # Set necessary information
    api.SetImageFile(file)
    # Set Variable
    api.SetVariable("save_blob_choices", "T")
    if 'variables' in tess_profile:
        for var in tess_profile['variables']:
            # TODO: test it!
            # if tess_profile['variables'][var]['value'] == "False":
            #    api.SetVariable(var, "F")
            # elif tess_profile['variables'][var]['value'] == "True":
            #    api.SetVariable(var, "T")
            # else:
            api.SetVariable(var, str(tess_profile['variables'][var]['value']))
    api.Recognize()
    return 0

########## CUTTER FUNCTION ##########
def cutter(file:str, fileout:str, tess_profile:dict):
    """
    Cuts areas (char, word, line) which contains user-specific expression
    :param file: inputfile
    :param fileout: output filename
    :param tess_profile: profile containing user-specific informations and options
    :return:
    """
    try:
        cutter = tess_profile["cutter"]
        # Init the api
        parameters = get_param(tess_profile)
        with PyTessBaseAPI(**parameters) as api:
            set_vars(api, file, tess_profile)
            ri = api.GetIterator()
            # The char method is not quite correct,
            # it seems that charbboxes get calculated after recognition, which leads sometimes to false cutouts.
            level = {"char":RIL.SYMBOL,"word":RIL.WORD,"line":RIL.TEXTLINE}.get(cutter["level"], "char")
            expr_finder = init_expr_finder(cutter)
            img = safe_imread(file)
            count = 0
            for r in iterate_level(ri, level):
                symbol = r.GetUTF8Text(level)  # r == ri
                conf = r.Confidence(level)
                if cutter["regex"] == "":
                    expr_result = expr_finder(cutter,symbol)
                else:
                    expr_result = re.search(cutter["regex"],symbol)
                if expr_result:
                    if cutter["min_conf"] < conf < cutter["max_conf"]:
                        origsymbol = symbol[:]
                        symbol = re.sub('[^0-9a-zA-Z]+', '_', symbol)
                        count += 1
                        bbox = r.BoundingBoxInternal(level)
                        pad = get_pad(bbox, cutter["pad"], cutter["padprc"])
                        cutarea = img[bbox[1] - pad[0]:bbox[3] + pad[0], bbox[0] - pad[1]:bbox[2] + pad[1], :]
                        cutdir = "/".join(fileout.split("/")[:-1]) + "/cut/" + symbol + "/"
                        create_dir(cutdir)
                        fprefix = '{:06d}'.format(count) + "_" + symbol + "_" + '{:.3f}'.format(conf).replace(".", "-")
                        imsave(cutdir +  "_" + fprefix + fileout.split("/")[-1] + "." + file.split(".")[-1], cutarea)
                        with open("/".join(fileout.split("/")[:-1])+"/cutinfo.txt","a") as cutinfo:
                            cutinfo.write('{:06d}'.format(count)+"\t"+origsymbol+"\t"+'{:.3f}'.format(conf))
    except:
        print("Some nasty things while cutting happens.")
    return 0

def init_expr_finder(cutter:dict):
    """
    Initialize the callback func with expr-dict, 'op' - 'filteroperator' and 'filter' - 'user given filter characters'
    :param cutter: dict containg information for cutting. Here are used 'filterop(erator)' and 'gr(ou)pop(erator)'.
    :return:
    """
    expr = {}
    expr["op"] = {"and": all, "or": any}
    expr["filter"] = get_filter(cutter)

    def find_expr(cutter:dict,symbol:str)->bool:
        # searches the symbol for the filterexpr with given filteroperator
        try:
            filterres =[]
            for filter in expr["filter"]:
                filterres.append(expr["op"].get(cutter["filterop"],"and")([True if s in symbol else False for s in filter]))
            result = expr["op"].get(cutter["grpop"],"and")(filterres)
        except:
            print("Something nasty happens while finding expressions!")
            result = False
        return result

    return find_expr

def get_filter(cutter:dict)->list:
    """
    Sets up the filtergroups which are divided by '||' and
    :param cutter:
    :return:
    """
    filterarrgrps = cutter["filter"].split("||")
    filter = []
    for filterarrgrp in filterarrgrps:
        # do set for unique values
        filter.append(set(filterarrgrp.split("|")))
    for exgrp in filter:
        for starex in ("*ascii_letters","*ascii_lowercase","*ascii_uppercase","*digits","*punctuation"):
            if starex in exgrp:
                exgrp.discard(starex)
                exgrp.update(set(getattr(string, starex[1:])))
    return filter

def get_pad(bbox,padval:int=0, padprc:float=0.0)->tuple:
    """
    Calculates the padding values for cutting
    :param bbox: boundingbox information
    :param padval: padding value (pixel)
    :param padprc: padding value (percantage)
    :return:
    """
    pad = [0,0]
    try:
        if padval != 0:
            pad = pad+padval
        if padprc != 0.0:
            pad[0] = int((pad[0]+abs(bbox[3]-bbox[1]))*padprc)
            pad[1] = int((pad[0]+abs(bbox[2]-bbox[0]))*padprc)
    except:
        print("Padding values are incorrect.")
    return tuple(pad)

########## MAIN FUNCTION ##########
def tess_pprocess(file:str,fileout:str,cut:bool, tess_profile:dict=None)->int:
    """
    Starts either the cutting or the extended_hocr process
    :param file: inputfile
    :param fileout: outputfile name
    :param cut: flag for cutting options
    :param tess_profile: containing user-specfic information and options
    :return: None
    """
    if cut and tess_profile != None:
        print("Start cut")
        cutter(file, fileout, tess_profile)
    else:
        print("Start hocr")
        extend_hocr(file, fileout, tess_profile)
    return 0

########## ENTRYPOINT ##########
if __name__=="__main__":
    extend_hocr('/home/jkamlah/Coding/tesseract/testing/eurotext.tif','/home/jkamlah/Coding/tesseract/testing/eurotext.hocr')