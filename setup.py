#!/usr/bin/env python
from distutils.core import setup

setup(
    name='mocrin',
    version='0.1',
    author='JKamlah',
    py_modules=['mocrin'],
    packages=['mocrinlib'],
    description='Multiple OCR Interface',
    long_description=open('README.md').read(),
)