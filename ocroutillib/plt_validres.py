# This little script updates the textline in the gt.txt with the text from the linetxt
import glob
import os
import pyexcel as pe

class ValRes():
    def __init__(self):
        self.name = None
        self.model = None
        self.iterationen = None
        self.errors  =  None
        self.missing  =  None
        self.total  =  None
        self.err  =  None
        self.errnomiss = None


def update_traindatatext(filename):
    with open(filename) as fltxt:
        valres = None
        for ltxt in fltxt:
            if ltxt[0] == "/":
                valres = ValRes()
                valres.name = "_".join(filename.split("/")[-1].split("_")[:-2])
                valres.model = ltxt.replace("\n","").split(".")[0].split("/")[-1]
                valres.iterationen = ltxt.replace("\n", "").split(".")[0].split("-")[-1]
            if ltxt[:6] == "errors":
                valres.errors = ltxt.replace("\n","").split(" ")[-1]
            if ltxt[:7] == "missing":
                valres.missing = ltxt.replace("\n","").split(" ")[-1]
            if ltxt[:5] == "total":
                valres.total = ltxt.replace("\n","").split(" ")[-1]
            if ltxt[:4] == "err ":
                valres.err = ltxt.replace("\n","").split(" ")[-2]
            if ltxt[:9] == "errnomiss":
                valres.errnomiss = ltxt.replace("\n","").split(" ")[-2]
                sheet = pe.get_sheet(file_name="./Validierung_models.xlsx")
                sheet.row += [valres.name,valres.model,valres.iterationen, valres.errors,valres.missing, valres.total, valres.err,valres.errnomiss]
                sheet.save_as("./Validierung_models.xlsx")


if __name__=="__main__":
    for filename in glob.glob(""):
        update_traindatatext(filename)