# This little script updates the textline in the gt.txt with the text from the linetxt
import glob
import os

def update_traindatatext(tddir):
    with open(tddir[:-1]+".linenr") as flnr, open(tddir[:-1]+".linetxt") as fltxt:
        for lnr, ltxt in zip(flnr, fltxt):
            if ltxt == "\n" and lnr == "\n": continue
            if ltxt == "\n":
                for files in glob.glob(tddir+lnr.replace("\n","")):
                    os.remove(files)
            with open(tddir+lnr.replace("\n","")+".gt.txt","w") as gt:
                gt.write(ltxt.strip())
                #gt.write(ltxt.strip())

if __name__=="__main__":
    for fdir in glob.glob(""):
        update_traindatatext(fdir)

