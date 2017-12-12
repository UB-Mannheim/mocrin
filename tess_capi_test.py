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

