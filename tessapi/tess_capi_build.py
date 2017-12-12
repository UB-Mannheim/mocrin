# /usr/bin/env python3
# coding: utf-8
from ctypes.util import find_library
import os
from cffi import FFI

tesslibpath = os.path.dirname(os.path.abspath(find_library("tesseract")))


PATH_TO_LIBTESS = '/usr/local/lib/'+find_library("tesseract")

ffibuilder = FFI()


ffibuilder.set_source("_tess_capi",
r"""
# include <stdio.h>
# include <allheaders.h>
# include <capi.h>
""",
  include_dirs = ['/usr/local/include/tesseract/include'],
  libraries = ["tesseract"],
  library_dirs = ['/usr/local/lib/'])


ffibuilder.cdef("""
""")

if __name__ == "__main__":
    ffibuilder.compile(verbose=True)