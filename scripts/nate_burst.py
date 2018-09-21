import cv2
import os
import argparse
import time
import datetime
from progressbar import ProgressBar
import settings
import sys

# Some images have the Reconyx logo at top and bottom of image
latest_id = 0
#minimum_burst_length = 10
#current_burst_length = 0
current_burst_grayscale = False

# Group Bursts
def group_bursts(img_path):
	
	same_burst = True
	#global current_burst_length
	global latest_id
	global current_burst_grayscale

	filename_id = os.path.basename(img_path).rsplit( ".", 1 )[ 0 ]

	current_id = filename_id[0:9]
	#print (current_id)
	#sys.exit(0)

	if latest_id == 0:
		latest_id = current_id
		current_burst_grayscale = is_grayscale(img_path)

	if not (is_grayscale(img_path) == current_burst_grayscale) or not (current_id == latest_id):
		latest_id = current_id
		same_burst = False
		current_burst_grayscale = is_grayscale(img_path)

	return same_burst


# determine if image was taken at night or day
def is_grayscale(img_path):
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
		dir_burst = '%s/%d' % (dir_camera_trap, burst_count)

		if not os.path.exists(dir_burst):
			os.makedirs(dir_burst)

		outfile = '%s/%s' % (dir_burst, os.path.basename(i_path))
		os.rename(i_path, outfile)

def main():
	global latest_timestamp
	pbar = ProgressBar()

	img_count = 0
	burst_count = 0

	parser = argparse.ArgumentParser()
	parser.add_argument("--unsorted_directory", help="directory of raw images")
	parser.add_argument("--burst_directory", help="directory to place segregated bursts")
	args = parser.parse_args()

	if args.unsorted_directory:
		dir_unsorted = args.unsorted_directory
	if args.burst_directory:
		dir_out = args.burst_directory

	if not os.path.exists(dir_out):
		os.makedirs(dir_out)


	# Create a new folder for each segmentation based on the current date and time 
	# (This will allow segmentation of images from the same camera traps in the future to be placed in
	#  a different location, thereby preventing overwrites)
	analysis_datetime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M") 

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
				same_burst = group_bursts(os.path.join(path, name))

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

if __name__ == "__main__":
  main()