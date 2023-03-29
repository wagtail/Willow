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
    version='1.5',
    description='A Python image library that sits on top of Pillow, Wand and OpenCV',
    author='Karl Hobley',
    author_email='karl@kaed.uk',
    url='',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.7',
    install_requires=[
        "filetype>=1.0.10,!=1.1.0",
        "defusedxml>=0.7,<1.0",
    ],
    extras_require={"testing": [
        "Pillow>=9.1.0,<11.0.0",
        "Wand>=0.6,<1.0",
        "mock>=3.0,<4.0",
        "pillow-heif>=0.7.0,<1.0.0"
    ]},
    zip_safe=False,
)
