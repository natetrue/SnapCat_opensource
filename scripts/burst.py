import cv2
import os
import argparse
import time
import datetime
from progressbar import ProgressBar
import settings
import random
from PIL import Image
from PIL.ExifTags import TAGS

# Some images have the Reconyx logo at top and bottom of image
latest_timestamp = 0
#minimum_burst_length = 10
#current_burst_length = 0
current_burst_grayscale = False

def get_exif_data_from_file(filename):
	exif = {}
	try:
		print ("FILENAME =>" + filename)
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

def get_epoch():
	return '%f' % time.time()

# Convert string to seconds
def convert_timestamp(img_path):
	# Example of Reconyx saved image
	# 01-05-2013 9-58-15
	same_burst = True
	#global current_burst_length
	global latest_timestamp
	global current_burst_grayscale

	exif_data = get_exif_data_from_file(img_path)
	timestamp = get_filename_datetime((exif_data['DateTimeOriginal']), '%Y_%m_%d_%H_%M_%S')

	if latest_timestamp == 0:
		latest_timestamp = timestamp
		current_burst_grayscale = is_grayscale(img_path)

	#if current_burst_length > minimum_burst_length and (timestamp - latest_timestamp) > burst_threshold:
	if not is_grayscale(img_path) == current_burst_grayscale or abs(timestamp - latest_timestamp) > settings.burst['burst_threshold']:
		latest_timestamp = timestamp
		same_burst = False
		current_burst_grayscale = is_grayscale(img_path)
		#current_burst_length = 0

	#current_burst_length += 1

	return timestamp, same_burst


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
def create_burst(images_list, dir_camera_trap, burst_count):
	for i_path in images_list:
		dir_burst = '%s/%d' % (dir_camera_trap, burst_count)

		if not os.path.exists(dir_burst):
			os.makedirs(dir_burst)

		outfile = '%s/%s' % (dir_burst, os.path.basename(i_path))
		os.rename(i_path, outfile)

def create_bursts(unsorted_directory, burst_directory, curr_datetime=None):

	global latest_timestamp
	pbar = ProgressBar()

	img_count = 0
	burst_count = 0

	if unsorted_directory:
		dir_unsorted = unsorted_directory
	if burst_directory:
		dir_out = burst_directory

	if not os.path.exists(dir_out):
		os.makedirs(dir_out)


	# Create a new folder for each segmentation based on the current date and time 
	# (This will allow segmentation of images from the same camera traps in the future to be placed in
	#  a different location, thereby preventing overwrites)
	if not curr_datetime:
		analysis_datetime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
	else:
		analysis_datetime = curr_datetime

	for path, subdirs, files in os.walk(dir_unsorted):

		images_list = []
		burst_imgs = []
		camera_trap = os.path.join(analysis_datetime, os.path.basename(path))
		dir_camera_trap = '%s/%s' % (dir_out, camera_trap)

		if len(files) > 1 and not os.path.exists(dir_camera_trap):
			os.makedirs(dir_camera_trap)

		pbar = ProgressBar()
		pbar.maxval = len(files)
		pbar.start()

		# Reset for each trap
		latest_timestamp = 0
		burst_count = 0

		for name in pbar(files):
			# only work with JPG 
			if name.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
				timestamp, same_burst = convert_timestamp(os.path.join(path, name))

				# If in the same burst, add to list and move on
				if same_burst:
					images_list.append(os.path.join(path, name))
				# Else, read images, average, and attempt to segment
				else:
					
					create_burst(images_list, dir_camera_trap, burst_count)
					
					images_list = []
					burst_imgs = []
					burst_count += 1
					images_list.append(os.path.join(path, name))

		# Don't forget the last 
		create_burst(images_list, dir_camera_trap, burst_count)

	return analysis_datetime

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("--unsorted_directory", help="directory of raw images")
	parser.add_argument("--burst_directory", help="directory to place segregated bursts")
	args = parser.parse_args()
	
	create_bursts(args.unsorted_directory, args.burst_directory)