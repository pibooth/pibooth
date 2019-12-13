from PIL import Image
import piexif

from pibooth.utils import LOGGER


def write_exif(filename, capture_nbr, pic_id):
	try:
		im = Image.open(filename)
		exif_dict = piexif.load(filename)
		# process im and exif_dict...
		w, h = im.size
		exif_dict["0th"][piexif.ImageIFD.XResolution] = (w, 1)
		exif_dict["0th"][piexif.ImageIFD.YResolution] = (h, 1)
		exif_dict["0th"][piexif.ImageIFD.Model] = "Fotobox vom Prinsenhof"
		exif_dict["0th"][piexif.ImageIFD.Make] = "Prinsenhof"
		exif_dict["0th"][piexif.ImageIFD.Software] = "pibooth"
		exif_dict["0th"][piexif.ImageIFD.ImageDescription] = "Ein Foto aus der Fotobooth vom Prinsenhof in Porta Westfalica"
		exif_dict["0th"][piexif.ImageIFD.DocumentName] = "Fotobox Image"
		exif_dict["0th"][piexif.ImageIFD.Artist] = "bpw23"
		exif_dict["0th"][piexif.ImageIFD.HostComputer] = "www.prinsenhof.de"
		exif_dict["0th"][piexif.ImageIFD.ImageNumber] = capture_nbr
		exif_dict["0th"][piexif.ImageIFD.Copyright] = "www.prinsenhof.de"
		exif_dict["Exif"][piexif.ExifIFD.ImageUniqueID] = str(pic_id)
		exif_dict["Exif"][piexif.ExifIFD.CameraOwnerName] = "Prinsenhof"	
		#exif_dict["Exif"][piexif.ExifIFD.UserComment] = "Ein Foto aus der Fotobooth vom Prinsenhof in Porta Westfalica"
		exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = "N"
		exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = "O"		
		#exif_dict["GPS"][piexif.ImageIFD.GPSLatitude] = ()
		#exif_dict["GPS"][piexif.ImageIFD.GPSLongitude] = ()	
		exif_bytes = piexif.dump(exif_dict)
		LOGGER.info("EXIF: adding metadata to image file")
		im.save(filename, "jpeg", exif=exif_bytes)
	except Exception as e:
		LOGGER.warning(f"EXIF: couldn't add exif informations to picture [{e}]")
