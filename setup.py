#!/usr/bin/env python
from distutils.core import setup
import glob

profiles = [c for c in glob.glob("profiles/**/*.json")]
setup(
    name='mocrin',
    version='0.1',
    author='JKamlah',
    scripts = "mocrin.py",
    py_modules=['mocrin'],
    packages=['mocrinlib'],
    package_data={'profiles': "profiles/*",
                  "":'config.ini'},
    description='Multiple OCR Interface',
    long_description=open('README.md').read(),
)