# /usr/bin/env python3
# coding: utf-8
from ctypes.util import find_library

find_library("tesseract")

PATH_TO_LIBTESS = find_library("tesseract")+'/libtesseract.so'

ffibuilder = FFI()


ffibuilder.set_source("_tess_capi",
r"""
    static int foo(int *buffer_in, int *buffer_out, int x)
    {
        /* some algorithm that is seriously faster in C than in Python */
    }
""")


ffibuilder.cdef("""
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





if __name__ == "__main__":
    ffibuilder.compile(verbose=True)