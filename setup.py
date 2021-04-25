#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from io import open
import os.path as osp
from setuptools import setup, find_packages


HERE = osp.abspath(osp.dirname(__file__))
sys.path.insert(0, HERE)
import pibooth


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
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Natural Language :: English',
            'Natural Language :: French',
            'Natural Language :: German',
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
        install_requires=[
            'picamera>=1.13 ; platform_machine>="armv0l" and platform_machine<="armv9l"',
            # Pillow freeze: higher versions bugged (see PR #5434)
            'Pillow==7.1.2',
            'pygame>=1.9.6',
            'pygame-menu==3.5.5',
            'pygame-vkeyboard>=2.0.7',
            'psutil>=5.5.1',
            'pluggy>=0.13.1',
            'gpiozero>=1.5.1',
            # RPi.GPIO backend for gpiozero (not always installed by default)
            'RPi.GPIO>=0.7.0 ; platform_machine>="armv0l" and platform_machine<="armv9l"'
        ],
        extras_require={
            'dslr': ['gphoto2>=2.0.0'],
            'printer': ['pycups>=1.9.73', 'pycups-notify>=0.0.4'],
        },
        options={
            'bdist_wheel':
                {'universal': True}
        },
        zip_safe=False,  # Don't install the lib as an .egg zipfile
        entry_points={'console_scripts': ["pibooth = pibooth.booth:main",
                                          "pibooth-count = pibooth.scripts.count:main",
                                          "pibooth-diag = pibooth.scripts.diagnostic:main",
                                          "pibooth-regen = pibooth.scripts.regenerate:main"]},
    )


if __name__ == '__main__':
    main()
