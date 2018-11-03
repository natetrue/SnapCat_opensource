"""
███████╗███╗   ██╗ █████╗ ██████╗  ██████╗ █████╗ ████████╗
██╔════╝████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔══██╗╚══██╔══╝
███████╗██╔██╗ ██║███████║██████╔╝██║     ███████║   ██║   
╚════██║██║╚██╗██║██╔══██║██╔═══╝ ██║     ██╔══██║   ██║   
███████║██║ ╚████║██║  ██║██║     ╚██████╗██║  ██║   ██║   
╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝      ╚═════╝╚═╝  ╚═╝   ╚═╝                  
"""
import os
import argparse
import time
import datetime
from progressbar import ProgressBar
import settings
import random
from PIL import Image
from PIL.ExifTags import TAGS
import json_database
import cv2

latest_timestamp = 0
current_burst_grayscale = False

def get_exif_data_from_file(filename):
	exif = {}
	try:
		img = Image.open(filename)
		if hasattr( img, '_getexif' ):
			exifinfo = img._getexif()
			if exifinfo != None:
				for tag, value in exifinfo.items():
					TAG2text = TAGS.get(tag)
					exif[TAG2text] = value
	except IOError:
		print ("IOERROR " + fname)

	return exif

def get_filename_datetime(exif_datetime_string, format):
	return datetime.datetime.strptime(exif_datetime_string, '%Y:%m:%d %H:%M:%S').timestamp()

def is_same_burst(img_path):
	same_burst = True
	global latest_timestamp
	global current_burst_grayscale

	exif_data = get_exif_data_from_file(img_path)

	timestamp = 0

	try:
	  timestamp = get_filename_datetime((exif_data['DateTimeOriginal']), '%Y_%m_%d_%H_%M_%S')
	except:
	  print ("Error: no timestamp available for:", img_path, " -- skipping")
	  return 0, False

	if latest_timestamp == 0:
		latest_timestamp = timestamp
		current_burst_grayscale = is_grayscale(img_path)

	if not is_grayscale(img_path) == current_burst_grayscale or abs(timestamp - latest_timestamp) > settings.burst['burst_threshold']:
		latest_timestamp = timestamp
		same_burst = False
		current_burst_grayscale = is_grayscale(img_path)


	return same_burst


# determine if image was taken at night or day
def is_grayscale(img_path):
	img = cv2.imread(img_path, 1)
	height, width, channels = img.shape

	img_buffer = settings.burst['img_buffer']

	for i in range(0, 5):
		x = random.randint(img_buffer, height-img_buffer+1)
		y = random.randint(img_buffer, width-img_buffer+1)

		# values should be consistent across all channels (RGB)
		if not img[x, y, 0] == img[x, y, 1] == img[x, y, 2]:
			return False

	return True

# Group into bursts
def label_burst(images_list, snapcat_json):
	
	for image_name in images_list:
		snapcat_json.update( image_name, "burst_images", images_list)
	

def create_bursts( snapcat_json, image_directory ):

	global latest_timestamp

	pbar = ProgressBar()

	img_count = 0
	burst_count = 0

	# Adds entry to JSON file for each grouping of images segmentation based on the files date and time 
	for path, _, files in os.walk( image_directory ):

		burst_images_list = []

		pbar = ProgressBar()
		pbar.maxval = len(files)
		pbar.start()

		# Reset for each trap
		latest_timestamp = 0
		burst_count = 0

		for filename in pbar(files):

			# only work with JPG 
			if not filename.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
			    continue

			# add every file to the database
			file_path = os.path.join(path, filename)
			snapcat_json.update( filename, "path", file_path)

			# If in the same burst, add to list and move on
			if is_same_burst( file_path ):
				burst_images_list.append( filename )
			# otherwise group images into a burst
			else:
				label_burst(burst_images_list, snapcat_json)
				burst_images_list = []
				
				# the current file is not part of this burst, so it is the beginning of the new burst
				burst_images_list.append( filename )

		# the last image in the folder ends burst detection
		label_burst(burst_images_list, snapcat_json)

	snapcat_json.save()

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("--image_dir", help="searches this directory to group images into bursts based on timestamps")
	parser.add_argument("--json_dir", help="path to the json database for images" )

	args = parser.parse_args()

	snapcat_json = json_database.JSONDatabase( args.json_dir )
	create_bursts( snapcat_json, args.image_dir )