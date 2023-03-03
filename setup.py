#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from io import open
import os.path as osp
from setuptools import setup, find_packages


HERE = osp.abspath(osp.dirname(__file__))
sys.path.insert(0, HERE)
import pibooth  # nopep8 : import shall be done after adding setup to paths


with open(osp.join(HERE, 'docs', 'requirements.txt')) as fd:
    docs_require = fd.read().splitlines()


def main():
    setup(
        name=pibooth.__name__,
        version=pibooth.__version__,
        description=pibooth.__doc__,
        long_description=open(osp.join(HERE, 'README.rst'), encoding='utf-8').read(),
        long_description_content_type='text/x-rst',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Other Environment',
            'Intended Audience :: Developers',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: MIT License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Natural Language :: Danish',
            'Natural Language :: Dutch',
            'Natural Language :: English',
            'Natural Language :: French',
            'Natural Language :: German',
            'Natural Language :: Hungarian',
            'Natural Language :: Italian',
            'Natural Language :: Norwegian',
            'Natural Language :: Spanish',
            'Topic :: Multimedia :: Graphics :: Capture :: Digital Camera',
        ],
        author="Vincent Verdeil, Antoine Rousseaux",
        url="https://github.com/pibooth/pibooth",
        download_url="https://github.com/pibooth/pibooth/archive/{}.tar.gz".format(pibooth.__version__),
        license='MIT license',
        platforms=['unix', 'linux'],
        keywords=[
            'Raspberry Pi',
            'camera',
            'photobooth'
        ],
        packages=find_packages(),
        package_data={
            'pibooth': ['*.ini'],
            'pibooth.fonts': ['*.ttf'],
            'pibooth.pictures': ['*/*.png'],
        },
        include_package_data=True,
        python_requires=">=3.6",
        install_requires=[
            'picamera2>=0.3.2 ; platform_machine>="armv0l" and platform_machine<="armv9l"',
            'Pillow>=9.2.0',
            'pygame>=2.1.2',
            'pygame-menu>=4.2.8',
            'pygame-vkeyboard>=2.0.8',
            'pygame-imslider>=1.0.1',
            'psutil>=5.9.1',
            'pluggy>=1.0.0',
            'gpiozero>=1.6.2',
            # RPi.GPIO backend for gpiozero (not always installed by default)
            'RPi.GPIO>=0.7.1 ; platform_machine>="armv0l" and platform_machine<="armv9l"'
        ],
        extras_require={
            'dslr': ['gphoto2>=2.3.4'],
            'printer': ['pycups>=2.0.1', 'pycups-notify>=0.0.6'],
            'doc': docs_require
        },
        zip_safe=False,  # Don't install the lib as an .egg zipfile
        entry_points={'console_scripts': ["pibooth = pibooth.__main__:main",
                                          "pibooth-count = pibooth.scripts.count:main",
                                          "pibooth-diag = pibooth.scripts.diagnostic:main",
                                          "pibooth-fonts = pibooth.scripts.fonts:main",
                                          "pibooth-regen = pibooth.scripts.regenerate:main",
                                          "pibooth-printer = pibooth.scripts.printer:main"]},
    )


if __name__ == '__main__':
    main()
