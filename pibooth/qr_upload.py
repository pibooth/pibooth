import os
import sys
import fileinput

import hashlib
from PIL import Image
from ftplib import FTP 
import qrcode

from pibooth.utils import LOGGER

 
def generate_qr_code(data,filename,path):
    qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(path + filename, "JPEG", quality=80, optimize=True,
    progressive=True)


def ftp_upload(filename, uploadpath, serveraddress, user, pwd):
    ftp_status=False
    ftp = FTP()
    ftp.set_debuglevel(0)
    try:
        ftp.connect(serveraddress, 21)
        ftp.login(user,pwd)
        ftp.cwd(uploadpath)
        fp = open(filename, 'rb')
        ftp.storbinary('STOR %s' % os.path.basename(filename), fp, 1024)
        ftp_status=True
        fp.close()
        ftp.close()
    except Exception as e:
        LOGGER.error("FTP upload failed! " + str(e))
    return ftp_status

    
def gen_hash_filename(filename):
    return hashlib.sha224(str(filename).encode("utf-8")).hexdigest() + ".jpg"
