from tesserocr import PyTessBaseAPI, RIL, iterate_level

def tess_charconf_hocr(file, fileout, tess_profile=None):
    # Set Parameters
    parameters= {}
    if 'parameters' in tess_profile:
        for param in tess_profile['parameters']:
            if param != "":
                if "path" in param:
                    parameters["path"] = tess_profile['parameters'][param]['value']
                elif "l" in param:
                    parameters["lang"] = tess_profile['parameters'][param]['value']
                elif "oem" in param:
                    parameters["oem"] = int(tess_profile['parameters'][param]['value'])
                elif "psm" in param:
                    parameters["psm"] = int(tess_profile['parameters'][param]['value'])
    # Start api with parameters
    with PyTessBaseAPI(**parameters) as api:
        # Set necessary information
        api.SetImageFile(file)
        # Set Variable
        api.SetVariable("save_blob_choices", "T")
        if 'variables' in tess_profile:
            for var in tess_profile['variables']:
                #if tess_profile['variables'][var]['value'] == "False":
                #    api.SetVariable(var, "F")
                #elif tess_profile['variables'][var]['value'] == "True":
                #    api.SetVariable(var, "T")
                #else:
                api.SetVariable(var, str(tess_profile['variables'][var]['value']))

        api.Recognize()

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
                        idx = hocr[hocr.find(bbox):].find("'")+hocr.find(bbox)
                        hocr = hocr[:idx]+"; x_confs"+conf+hocr[idx:]
                    conf = ""
                bbinfo = r.BoundingBoxInternal(RIL.WORD)
            conf += " "+str(r.Confidence(level))
        with open(fileout+".hocr","w") as hocrfile:
            hocrfile.write(hocr)
        return 0

if __name__=="__main__":
    tess_charconf_hocr('/home/jkamlah/Coding/tesseract/testing/eurotext.tif','/home/jkamlah/Coding/tesseract/testing/eurotext.hocr')