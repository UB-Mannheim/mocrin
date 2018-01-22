#!/usr/bin/env python
from distutils.core import setup


scripts = ["akf_mocrin"]
setup(
    name='akf_mocrin',
    version='0.1',
    author='JKamlah',
    packages=['mocrinlib'],
    scripts=scripts,
    description='Multiple OCR Interface',
    long_description=open('README.txt').read(),
)