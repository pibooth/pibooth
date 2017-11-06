#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os.path as osp
from setuptools import setup, find_packages

if sys.version_info[0] == 2:
    if not sys.version_info >= (2, 7):
        raise ValueError('This package requires Python 2.7 or newer')
elif sys.version_info[0] == 3:
    if not sys.version_info >= (3, 2):
        raise ValueError('This package requires Python 3.2 or newer')
else:
    raise ValueError('Unrecognized major version of Python')

if "bdist_wheel" not in sys.argv:
    raise ValueError('Please use the "wheel" format to generate a release')

HERE = osp.abspath(osp.dirname(__file__))
sys.path.insert(0, HERE)
import pibooth


def main():
    setup(
        name=pibooth.__name__,
        version=pibooth.__version__,
        description=pibooth.__doc__,
        long_description=open(osp.join(HERE, 'README.rst')).read(),
        classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
        ],
        author="Vincent Verdeil, Antoine Rousseaux",
        url="https://github.com/werdeil/pibooth",
        download_url="https://github.com/werdeil/pibooth/archive/{}.tar.gz".format(pibooth.__version__),
        license='MIT license',
        platforms=['unix', 'linux'],
        keywords=[
            'raspberrypi',
            'camera',
            'photobooth'
        ],
        packages=find_packages(),
        package_data={
            'pibooth': ['*.ini'],
            'pibooth.fonts': ['*.ttf'],
            'pibooth.pictures': ['*.png'],
        },
        include_package_data=True,
        install_requires=[
            'RPi.GPIO',
            'picamera',
            'Pillow',
            'pygame',
            'gphoto2'
        ],
        extras_require={
            'doc':   ['sphinx'],
            'test':  ['coverage', 'pytest'],
        },
        zip_safe=False,  # Don't install the lib as an .egg zipfile
        entry_points={'console_scripts': ["pibooth = pibooth.ptb:main"]},
    )


if __name__ == '__main__':
    main()
