import os
from skimage.io import imread

########## COMMON FUNCTIONS ##########
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

def safe_imread(file):
    """

    :param file:
    :return:
    """
    try:
        image = imread("%s" % file)
    except IOError:
        print("cannot open %s" % file)
        #logging.warning("cannot open %s" % input)
        return 1
    return image