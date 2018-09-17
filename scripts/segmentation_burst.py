import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
import argparse
import uuid
import time
import datetime

from progressbar import ProgressBar

# Some images have the Reconyx logo at top and bottom of image
img_buffer = 300
img_length_cap = 200
latest_timestamp = 0
burst_threshold = 3600 # images within one hour will be grouped in same "burst"
#minimum_burst_length = 10
#current_burst_length = 0
current_bust_greyscale = False

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
	if not is_grayscale(img_path) == current_burst_grayscale or abs(timestamp - latest_timestamp) > burst_threshold:
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

	for x in range(img_buffer, height-img_buffer):
		for y in range(img_buffer, width-img_buffer):

			# values should be consistent across all channels (RGB)
			if not img[x, y, 0] == img[x, y, 1] == img[x, y, 2]:
				return False

	return True

def main():
	pbar = ProgressBar()

	img_count = 0
	burst_count = 0

	parser = argparse.ArgumentParser()
	parser.add_argument("--unsorted_directory", help="directory of images to be blobbed")
	parser.add_argument("--output_directory", help="directory to place blobs")
	args = parser.parse_args()

	if args.unsorted_directory:
		dir_unsorted = args.unsorted_directory
	if args.output_directory:
		dir_out = args.output_directory

	if not os.path.exists(dir_out):
		os.makedirs(dir_out)

	for path, subdirs, files in os.walk(dir_unsorted):

		images_list = []
		burst_imgs = []
		camera_trap = os.path.basename(path)
		dir_camera_trap = '%s/%s' % (dir_out, camera_trap)

		if not os.path.exists(dir_camera_trap):
			os.makedirs(dir_camera_trap)

		pbar = ProgressBar()
		pbar.maxval = len(files)
		pbar.start()

		for name in pbar(files):
			# only work with JPG 
			if name.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
				timestamp, same_burst = convert_timestamp(os.path.join(path, name))

				# If in the same burst, add to list and move on
				if same_burst:
					images_list.append(os.path.join(path, name))
				# Else, read images, average, and attempt to segment
				else:
					for image_path in images_list:
						img = cv2.imread(image_path)
						img = img.astype(np.float32)/255.0
						img = img[50:-50,:]
						burst_imgs.append((image_path, img))

					avg_burst_img = np.mean(np.median(list(dict(burst_imgs).values()), axis=0), axis=-1)

					for i_path, i in burst_imgs:
						diffimg = np.abs(np.mean(i,-1) - avg_burst_img)
						diffimg = cv2.blur(diffimg, (25,25))
						thresimg = diffimg > np.max(diffimg) * 0.4
						x1, x2 = np.where(np.any(thresimg, 0))[0][[0,-1]]
						y1, y2 = np.where(np.any(thresimg, 1))[0][[0,-1]]
						w=x2-x1
						h=y2-y1
						w = max(w, h/2)
						h = max(h, w/2)
						x1 = max(0, x1 - w*0.2)
						x2 = min(i.shape[1]-1, x2 + w*0.2)
						y1 = max(0, y1 - h*0.2)
						y2 = min(i.shape[0]-1, y2 + h*0.8)
						subimg = i[int(y1):int(y2),int(x1):int(x2),:]

						dir_burst = '%s/%d' % (dir_camera_trap, burst_count)

						if not os.path.exists(dir_burst):
							os.makedirs(dir_burst)

						outfile = '%s/%s' % (dir_burst, os.path.basename(i_path))
						plt.imsave(outfile, subimg)

					images_list = []
					burst_imgs = []
					burst_count += 1
					images_list.append(os.path.join(path, name))


if __name__ == "__main__":
  main()