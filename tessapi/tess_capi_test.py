# /usr/bin/env python3
# coding: utf-8
from ctypes.util import find_library
import os

PATH_TO_LIBTESS = '/usr/local/lib/'+find_library("tesseract")

lang = "deu"
filename = "/media/sf_ShareVB/many_years_firmprofiles/short/1957/0301_1957_hoppa-405844417-0050_0373.jpg"

TESSDATA_PREFIX = os.environ.get('TESSDATA_PREFIX')
if not TESSDATA_PREFIX:
    TESSDATA_PREFIX = "/usr/local/share/tessdata/"



import cffi  # requires "pip install cffi"

ffi = cffi.FFI()
ffi.cdef("""
struct Pix;
typedef struct Pix PIX;
PIX * pixRead ( const char *filename );
char * getLeptonicaVersion (  );

typedef struct TessBaseAPI TessBaseAPI;
typedef int BOOL;

const char* TessVersion();

TessBaseAPI* TessBaseAPICreate();
int TessBaseAPIInit3(TessBaseAPI* handle, const char* datapath, const char* language);

void TessBaseAPISetImage2(TessBaseAPI* handle, struct Pix* pix);

BOOL   TessBaseAPIDetectOrientationScript(TessBaseAPI* handle, char** best_script_name, 
                                                            int* best_orientation_deg, float* script_confidence, 
                                                            float* orientation_confidence);
""")

libtess = ffi.dlopen(PATH_TO_LIBTESS)
liblept = ffi.dlopen(find_library('lept'))

print(ffi.string(libtess.TessVersion()))

ffi.string(liblept.getLeptonicaVersion())

api = libtess.TessBaseAPICreate()

libtess.TessBaseAPIInit3(api, ffi.NULL, b"deu")

pix = liblept.pixRead(filename.encode())

libtess.TessBaseAPISetImage2(api, pix)

script_name = ffi.new('char **')
orient_deg = ffi.new('int *')
script_conf = ffi.new('float *')
orient_conf = ffi.new('float *')
libtess.TessBaseAPIDetectOrientationScript(api, script_name, orient_deg, script_conf, orient_conf)

ffi.string(script_name[0])

print(orient_deg[0])
print(script_conf[0])
print(orient_conf[0])

asdflkj = 1

























import os
import ctypes
from ctypes.util import find_library
from PIL import Image
import tesserpy
import cv2

from _TessAPI import ffi, lib

buffer_in = ffi.new("int[]", 1000)
# initialize buffer_in here...

# easier to do all buffer allocations in Python and pass them to C,
# even for output-only arguments
buffer_out = ffi.new("int[]", 1000)

result = lib.foo(buffer_in, buffer_out, 1000)



lang = "deu"
filename = "/media/sf_ShareVB/many_years_firmprofiles/short/1957/0301_1957_hoppa-405844417-0050_0373.jpg"
image = Image.open(filename).convert('L')
TESSDATA_PREFIX = os.environ.get('TESSDATA_PREFIX')
if not TESSDATA_PREFIX:
    TESSDATA_PREFIX = "/usr/local/share/tessdata/"

tessapi = tesserpy.Tesseract(TESSDATA_PREFIX,language="eng")
print(tessapi.version())
tessapi.tessedit_char_whitelist = """'"!@#$%^&*()_+-=[]{};,.<>/?`~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"""
image = cv2.imread(filename)
tessapi.set_image(image)
page_info = tessapi.orientation()
print(page_info.textline_order == tesserpy.TEXTLINE_ORDER_TOP_TO_BOTTOM)
print("#####")
print(tessapi.get_utf8_text())
print("#####")
print("Word\tConfidence\tBounding box coordinates")
for word in tessapi.words():
    bb = word.bounding_box
    print("{}\t{}\tt:{}; l:{}; r:{}; b:{}".format(word.text, word.confidence, bb.top, bb.left, bb.right, bb.bottom))



tesseract = ctypes.cdll.LoadLibrary(find_library("tesseract"))
tesseract.TessVersion.restype = ctypes.c_char_p
tesseract_version = tesseract.TessVersion()
api = tesseract.TessBaseAPICreate()
rc = tesseract.TessBaseAPIInit3(api, TESSDATA_PREFIX, lang)
if (rc):
    tesseract.TessBaseAPIDelete(api)
    print("Could not initialize tesseract.\n")
    exit(3)
# height = tesseract.TessBaseAPIGetSourceYResolution(rc)
text_out = tesseract.TessBaseAPIGetWords(api, image)
result_text = ctypes.string_at(text_out)

print('Tesseract-ocr version', tesseract_version)
print(result_text)

