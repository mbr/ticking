#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup


def read(fname):
    buf = open(os.path.join(os.path.dirname(__file__), fname), 'rb').read()
    return buf.decode('utf8')


setup(
    name='ticking',
    version='0.4.0',
    description=
    'A small timing utility library, handling framerates and rough benchmarks.',
    long_description=read('README.rst'),
    author='Marc Brinkmann',
    author_email='git@marcbrinkmann.de',
    url='https://github.com/mbr/ticking',
    license='MIT',
    py_modules=['ticking'],
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ])
