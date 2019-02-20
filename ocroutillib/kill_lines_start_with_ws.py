# This little script updates the textline in the gt.txt with the text from the linetxt
import glob
import os

def clean_emptylines(filename):
    with open(filename) as fltxt:
        for ltxt in fltxt:
            if ltxt[0] != " ":
                with open("./corrected.txt","a") as gt:
                    gt.write(ltxt.strip())
                    gt.write("\n")

if __name__=="__main__":
    for filename in glob.glob(""):
        clean_emptylines(filename)
