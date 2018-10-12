import cv2
import os
import argparse
import time
import datetime
from progressbar import ProgressBar
import settings

# Some images have the Reconyx logo at top and bottom of image
latest_timestamp = 0
#minimum_burst_length = 10
#current_burst_length = 0
current_burst_grayscale = False

# Convert string to seconds
def convert_timestamp(img_path):
	# Example of Reconyx saved image
	# 01-05-2013 9-58-15
	same_burst = True
	#global current_burst_length
	global latest_timestamp
	global current_burst_grayscale

	timestamp_string = os.path.basename(img_path).rsplit( ".", 1 )[ 0 ]

	timestamp = time.mktime(datetime.datetime.strptime(timestamp_string, "%d-%m-%Y %H-%M-%S").timetuple())

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
	# todo remove - added to speed up
	return True

	img = cv2.imread(img_path, 1)
	height, width, channels = img.shape

	img_buffer = settings.burst['img_buffer']

	for x in range(img_buffer, height-img_buffer):
		for y in range(img_buffer, width-img_buffer):

			# values should be consistent across all channels (RGB)
			if not img[x, y, 0] == img[x, y, 1] == img[x, y, 2]:
				return False

	return True

# Group into bursts
def create_burst(images_list, dir_camera_trap, burst_count):


	for i_path in images_list:
		
		os.rename(i_path, outfile)

def create_bursts( unsorted_directory ):

	global latest_timestamp
	pbar = ProgressBar()

	img_count = 0
	burst_count = 0
	bursts_dict = dict()

	# Create a new folder for each segmentation based on the current date and time 
	# (This will allow segmentation of images from the same camera traps in the future to be placed in
	#  a different location, thereby preventing overwrites)
	analysis_datetime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M") 

	for path, subdirs, files in os.walk(unsorted_directory):

		images_list = []
		burst_imgs = []
		camera_trap = os.path.basename(path)

		pbar = ProgressBar()
		pbar.maxval = len(files)
		pbar.start()

		# Reset for each trap
		latest_timestamp = 0
		bursts = []

		for name in pbar(files):
			# only work with JPG 
			if name.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):

				#todo convert_timestamp also calls greyscale, rename
				# todo greyscale takes too long, speed up
				timestamp, same_burst = convert_timestamp(os.path.join(path, name))

				# If in the same burst, add to list and move on
				if same_burst:
					images_list.append(os.path.join(path, name))
				# Else, read images, average, and attempt to segment
				else:
					
					if images_list:
						bursts.append( images_list )
					
					images_list = []
					burst_imgs = []
					burst_count += 1
					images_list.append(os.path.join(path, name))

		# Don't forget the last 
		if images_list:
			bursts.append( images_list )

		if bursts:
			bursts_dict[camera_trap] = bursts

	return bursts_dict

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument("--unsorted_directory", help="directory of raw images")
	parser.add_argument("--burst_directory", help="directory to place segregated bursts")
	args = parser.parse_args()
	
	create_bursts(args.unsorted_directory, args.burst_directory)