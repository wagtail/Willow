#!/usr/bin/env python

import sys, os

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


# Hack to prevent "TypeError: 'NoneType' object is not callable" error
# in multiprocessing/util.py _exit_function when setup.py exits
# (see http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
try:
    import multiprocessing
except ImportError:
    pass



setup(
    name='Willow',
    version='0.3b3',
    description='A Python image library that sits on top of Pillow, Wand and OpenCV',
    author='Karl Hobley',
    author_email='karlhobley10@gmail.com',
    url='',
    packages=find_packages(),
    include_package_data=True,
    license='BSD',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    install_requires=[],
    zip_safe=False,
)
