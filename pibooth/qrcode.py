import qrcode
import sys
from PIL import Image

def generate_qr_code(filename,path):
	qr = qrcode
	qr.add_data(filename)
	qr.make(fit=True)

	img = qr.make_image(fill_color="black", back_color="white")
	img.save(path + "qr_link.jpg", "JPEG", quality=80, optimize=True,
	 progressive=True)

print(sys.version)
generate_qr_code("www.prinsenhof.de",".\\test\\")
