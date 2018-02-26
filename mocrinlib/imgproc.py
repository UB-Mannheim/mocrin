###################### INFORMATION #############################
#           Module for talking to the tesseract api through tesserocr

########## IMPORT ##########
import warnings
import os
from mocrinlib.common import create_dir
from skimage import color, img_as_uint
import skimage.filters as imgfilter
from skimage.io import imread, find_available_plugins
from skimage.external.tifffile import imread as timread
import scipy.misc as misc


########## FUNCTIONS ##########
def safe_imread(file:str):
    """
    Reads the image and prints an error if something went wrong
    :param file:
    :return:
    """
    try:
        image = misc.imread("%s" % file)
    except IOError:
        print("cannot open %s" % file)
        #logging.warning("cannot open %s" % input)
        return 1
    return image

def get_uintimg(image:str):
    """
    Generates a uintimg from the given image
    :param image:
    :return:
    """
    if len(image.shape) > 2:
        uintimg = color.rgb2gray(image)
    else:
        uintimg = image
    if uintimg.dtype == "float64":
        with warnings.catch_warnings():
            # Transform rotate convert the img to float and save convert it back
            warnings.simplefilter("ignore")
            uintimg = img_as_uint(uintimg, force_copy=True)
    return uintimg

def get_binary(args, image, file:str,binpath:str)->str:
    """
    Binarize image with different algorithms
    :param args:
    :param image:
    :param file:
    :param binpath:
    :return:
    """
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