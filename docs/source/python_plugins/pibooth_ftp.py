"""Plugin to upload pictures on a FTP server."""

import os
from ftplib import FTP
import pibooth

__version__ = "0.0.2"

@pibooth.hookimpl
def pibooth_startup(app):
    app.ftp = FTP()
    app.ftp.set_debuglevel(0)
    app.ftp.connect("ftp.pibooth.org", 21)
    app.ftp.login("pibooth", "1h!gR4/opK")

@pibooth.hookimpl
def state_processing_exit(app):
    name = os.path.basename(app.previous_picture_file)

    with open(app.previous_picture_file, 'rb') as fp:
        app.ftp.storbinary('STOR {}'.format(name), fp, 1024)

@pibooth.hookimpl
def pibooth_cleanup(app):
    app.ftp.close()
