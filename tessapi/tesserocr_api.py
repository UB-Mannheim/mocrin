from tesserocr import PyTessBaseAPI, RIL, iterate_level
import string as string
from skimage.io import imread, imsave
import os
import re

def get_param(tess_profile):
    # This func extends the hocr-file of tesseract with charconfs
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

def set_vars(api, file, tess_profile):
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

def extended_hocr(file, fileout, tess_profile=None):
    parameters = get_param(tess_profile)
    with PyTessBaseAPI(**parameters) as api:
        set_vars(api, file, tess_profile)
        ri = api.GetIterator()
        hocr = api.GetHOCRText(0)
        level = RIL.SYMBOL
        bbinfo = tuple()
        conf = ""
        for r in iterate_level(ri, level):
            if bbinfo != r.BoundingBoxInternal(RIL.WORD):
                if bbinfo != ():
                    bbox = "bbox " + " ".join(map(str, bbinfo))
                    if bbox in hocr:
                        idx = hocr.find(bbox)
                        endtxt = hocr[idx:].find("/div") + idx
                        shocr = hocr[:endtxt]
                        found = True
                        while found:
                            idx_next = shocr.find(bbox, idx+1)
                            if idx_next != -1:
                                idx = idx_next
                            else:
                                found = False
                        idx = hocr[idx:].find("'") + idx
                        hocr = hocr[:idx]+"; x_confs"+conf+hocr[idx:]
                    conf = ""
                bbinfo = r.BoundingBoxInternal(RIL.WORD)
            conf += " "+str(r.Confidence(level))
    with open(fileout+".hocr","w") as hocrfile:
        hocrfile.write(hocr)
    return 0

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

def cutter(file, fileout, tess_profile):
    try:
        cutter = tess_profile["cutter"]
        # Init the api
        parameters = get_param(tess_profile)
        with PyTessBaseAPI(**parameters) as api:
            set_vars(api, file, tess_profile)
            ri = api.GetIterator()
            # The char method is not quite correct,
            # it seems that charbboxes get calculated after recognition, which leads sometimes to false cutouts.
            leveldict = {"char":RIL.SYMBOL,"word":RIL.WORD,"line":RIL.TEXTLINE}
            level = leveldict[cutter["level"]]
            expr_finder = init_expr_finder(cutter)
            img = imread(file)
            count = 0
            for r in iterate_level(ri, level):
                symbol = r.GetUTF8Text(level)  # r == ri
                conf = r.Confidence(level)
                expr_result = expr_finder(cutter,symbol)
                if expr_result["char"] or expr_result["word"] or expr_result["grp"]:
                    if cutter["min_conf"] < conf < cutter["max_conf"]:
                        symbol = re.sub('[^0-9a-zA-Z]+', '_', symbol)
                        count += 1
                        bbox = r.BoundingBoxInternal(level)
                        pad = get_pad(bbox, cutter["pad"], cutter["padprc"])
                        cutarea = img[bbox[1] - pad[0]:bbox[3] + pad[0], bbox[0] - pad[1]:bbox[2] + pad[1], :]
                        cutdir = "/".join(fileout.split("/")[:-1]) + "/cut/" + symbol + "/"
                        create_dir(cutdir)
                        imsave(cutdir + '{:06d}'.format(count) + "_" + symbol + "_" + '{:.3f}'.format(conf).replace(".",
                                                                                                                    "-") + "_" +
                               fileout.split("/")[-1] + "." + file.split(".")[-1], cutarea)
    except:
        print("Some nasty things while cutting happens.")
    return 0

def init_expr_finder(cutter):
    expr = {}
    expr["res"] = {"char": False, "word": False, "grp": False}
    expr["op"] = {"and": all, "or": any}
    expr["filter"] = get_filter(cutter)

    def find_expr(cutter,symbol):
        try:
            filterres =[]
            for filter in expr["filter"]:
                filterres.append(expr["op"][cutter["filterop"]]([True if s in symbol else False for s in filter]))
            result = expr["op"][cutter["grpop"]](filterres)
            #if cutter["filterop"] == "or":
            #    expr_res["char"] = any([True if s in expr["char"] else False for s in symbol])
            #    if cutter["level"] != "char":
            #        expr_res["word"] = any([True if s in symbol else False for s in expr["word"]])
            #        expr_res["grp"] = all([True if s in expr["grp"] else False for s in symbol])
            #else:
            #    expr_res["char"] = all([True if s in symbol else False for s in expr["char"]])
            #    if cutter["level"] != "char":
            #        expr_res["word"] = all([True if s in symbol else False for s in expr["word"]])
            #        if expr["char"]:
            #            expr_res["word"] = expr_res["word"]*expr_res["char"]
            #            expr_res["char"] = expr_res["word"]
            #        expr_res["grp"] = any([True if s in expr["grp"] else False for s in symbol])
        except:
            print("Something nasty happens while finding x, so it got skipped!")
        return result

    return find_expr

def get_filter(cutter):
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

def charcutter(file, fileout, ri, cutter, level):
    if chararr == [""]:chararr=[]
    img = imread(file)
    group = []
    if cutter["group"]["value"] != "":
        grouparr = cutter["group"]["value"].split("|")
        for groupval in grouparr:
            group+= getattr(string, groupval)
    count = 0
    for r in iterate_level(ri, level):
        symbol = r.GetUTF8Text(level)  # r == ri
        conf = r.Confidence(level)
        if symbol in chararr or symbol in group:
            if int(cutter["min_conf"]["value"]) < conf < int(cutter["max_conf"]["value"]):
                symbol = re.sub('[^0-9a-zA-Z]+', '_', symbol)
                count += 1
                bbox = r.BoundingBoxInternal(level)
                pad = get_pad(bbox,int(cutter["pad"]["value"]),float(cutter["padprc"]["value"]))
                cutarea = img[bbox[1]-pad[0]:bbox[3]+pad[0], bbox[0]-pad[1]:bbox[2]+pad[1], :]
                cutdir = "/".join(fileout.split("/")[:-1])+"/cut/"+symbol+"/"
                create_dir(cutdir)
                imsave(cutdir+'{:06d}'.format(count)+"_"+symbol+"_"+'{:.3f}'.format(conf).replace(".","-")+"_"+fileout.split("/")[-1] +"."+file.split(".")[-1],cutarea)
                #imgbin = r.GetBinaryImage(RIL.WORD)
                #imsave(cutdir +"bin_"+'{:06d}'.format(count) + "_" +symbol + "_" + '{:.3f}'.format(conf).replace(".", "-") + "_" +  fileout.split("/")[-1] + "." + file.split(".")[-1], imgbin)
    return 0

def wordcutter(file, fileout, ri, cutter, level):
    chararr = cutter["char"]["value"].replace(" ", "").split("|")
    if chararr == [""]:chararr=[]
    wordarr = cutter["word"]["value"].split("|")
    if wordarr == [""]: wordarr = []
    img = imread(file)
    group = []
    if cutter["group"]["value"] != "":
        grouparr = cutter["group"]["value"].split("|")
        for groupval in grouparr:
            group += list(getattr(string, groupval))
    count = 0
    setmax=False
    if cutter["wordmaxlen"]["value"] == "-1":setmax = True
    for r in iterate_level(ri, level):
        symbol = r.GetUTF8Text(level)  # r == ri
        conf = r.Confidence(level)
        if setmax:cutter["wordmaxlen"]["value"] = len(symbol)
        if int(cutter["min_conf"]["value"]) < conf < int(cutter["max_conf"]["value"]):
            if int(cutter["wordminlen"]["value"]) < len(symbol) <= int(cutter["wordmaxlen"]["value"]):
                fchar, fword, fgroup = find_x(cutter, symbol, chararr, wordarr, group)
                if fchar or fword or fgroup:
                    symbol = symbol.replace(string.punctuation, "_")
                    symbol = re.sub('[^0-9a-zA-Z]+', '', symbol)
                    if symbol == "":symbol = "_"
                    count += 1
                    bbox = r.BoundingBoxInternal(level)
                    pad = get_pad(bbox, int(cutter["pad"]["value"]), float(cutter["padprc"]["value"]))
                    cutarea = img[bbox[1] - pad[0]:bbox[3] + pad[0], bbox[0] - pad[1]:bbox[2] + pad[1], :]
                    cutdir = "/".join(fileout.split("/")[:-1]) + "/cut/" + symbol + "/"
                    create_dir(cutdir)
                    imsave(cutdir + '{:06d}'.format(count) + "_" + symbol + "_" + '{:.3f}'.format(conf).replace(".",
                                                                                                                "-") + "_" +
                           fileout.split("/")[-1] + "." + file.split(".")[-1], cutarea)
    return 0

def linecutter(file, fileout, ri, cutter, level):
    chararr = cutter["char"]["value"].replace(" ", "").split("|")
    if chararr == [""]: chararr = []
    wordarr = cutter["word"]["value"].split("|")
    if wordarr == [""]: wordarr = []
    img = imread(file)
    group = []
    if cutter["group"]["value"] != "":
        grouparr = cutter["group"]["value"].split("|")
        for groupval in grouparr:
            group += list(getattr(string, groupval))
    count = 0
    setmax = False
    if cutter["wordmaxlen"]["value"] == "-1": setmax = True
    for r in iterate_level(ri, level):
        symbol = r.GetUTF8Text(level)  # r == ri
        conf = r.Confidence(level)
        print(symbol)
        if setmax: cutter["wordmaxlen"]["value"] = len(symbol)
        if int(cutter["min_conf"]["value"]) < conf < int(cutter["max_conf"]["value"]):
            if int(cutter["wordminlen"]["value"]) < len(symbol) <= int(cutter["wordmaxlen"]["value"]):
                # Find the char, word or/and groups
                fchar, fword, fgroup = find_x(cutter,symbol,chararr,wordarr,group)
                if fchar or fword or fgroup:
                    symbol = symbol.replace(" ","_").replace(string.punctuation, "_")
                    symbol = re.sub('[^0-9a-zA-Z_]+', '', symbol)
                    if symbol == "": symbol = "_"
                    count += 1
                    bbox = r.BoundingBoxInternal(level)
                    pad = get_pad(bbox, int(cutter["pad"]["value"]), float(cutter["padprc"]["value"]))
                    cutarea = img[bbox[1] - pad[0]:bbox[3] + pad[0], bbox[0] - pad[1]:bbox[2] + pad[1], :]
                    cutdir = "/".join(fileout.split("/")[:-1]) + "/cut/" + symbol + "/"
                    create_dir(cutdir)
                    imsave(cutdir + '{:06d}'.format(count) + "_" + symbol + "_" + '{:.3f}'.format(conf).replace(".",
                                                                                                                "-") + "_" +
                           fileout.split("/")[-1] + "." + file.split(".")[-1], cutarea)
    return 0

def get_pad(bbox,padval=0, padprc=0.0):
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

def tess_pprocess(file, fileout,cut, tess_profile=None):
    if cut and tess_profile != None:
        cutter(file, fileout, tess_profile)
    else:
        extended_hocr(file, fileout, tess_profile)
    return 0

if __name__=="__main__":
    extended_hocr('/home/jkamlah/Coding/tesseract/testing/eurotext.tif','/home/jkamlah/Coding/tesseract/testing/eurotext.hocr')