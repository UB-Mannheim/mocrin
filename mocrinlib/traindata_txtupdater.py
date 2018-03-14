# This little script updates the textline in the gt.txt with the text from the linetxt
import glob

def update_traindatatext(tddir):
    with open(tddir[:-1]+".linenr") as flnr, open(tddir[:-1]+".linetxt") as fltxt:
        for lnr, ltxt in zip(flnr, fltxt):
            with open(tddir+lnr.replace("\n","")+".gt.txt","w") as gt:
                gt.write(ltxt)

if __name__=="__main__":
    for fdir in glob.glob("/media/sf_ShareVB/many_years_firmprofiles_output/long/1957/tess/latin/cut/*/"):
        update_traindatatext(fdir)

