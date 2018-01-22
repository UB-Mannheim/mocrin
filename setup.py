#!/usr/bin/env python
from distutils.core import setup

setup(
    name='mocrin',
    version='0.1',
    author='JKamlah',
    packages=['mocrin','mocrinlib'],
    scripts=scripts,
    description='Multiple OCR Interface',
    long_description=open('README.txt').read(),
)