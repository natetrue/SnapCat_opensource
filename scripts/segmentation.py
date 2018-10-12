import cv2
import os
import numpy as np
import argparse
import time
import datetime
import matplotlib.pyplot as plt
import settings
import tools
import sys

from progressbar import ProgressBar

from PIL import Image

def optimal_square(x1,x2,y1,y2,i):
	max_x = i.shape[1]
	max_y = i.shape[0]

	ret_x1 = x1
	ret_x2 = x2
	ret_y1 = y1
	ret_y2 = y2

	x_length = x2-x1
	y_length = y2-y1
	square_size = 0
	affected_dimension = ''

	side_1 = 0
	side_2 = 0
	delta = 0

	if (x_length > y_length):
		if x_length > max_y:
			square_size = y_length
			affected_dimension = 'x'
			delta = abs(square_size - x_length)
		else:
			square_size = x_length
			affected_dimension = 'y'
			delta = abs(square_size - y_length)

	elif (y_length > x_length):

		if y_length > max_x:
			square_size = x_length
			affected_dimension = 'y'
			delta = abs(square_size - y_length)
		else:
			square_size = y_length
			affected_dimension = 'x'
			delta = abs(square_size - x_length)

	# print("Square Size: %d\n" % square_size)
	# print("Affected_dimension: %s\n" % affected_dimension)
	# print("Max Y: %d\n" % max_y)
	# print("Max X: %d\n" % max_x)

	# Split up addition/subtraction on both sides of proposed subimage
	side_1 = int(round(delta / 2))
	side_2 = delta - side_1

	# print ("Side 1: %d\n" % side_1)
	# print ("Side 2: %d\n" % side_2)

	if affected_dimension == 'y':
		if square_size > y_length:
			if y1 < side_1:
				side_2 = side_2 + (side_1-y1)

				ret_y1 = 0
				ret_y2 = y2 + side_2

			elif (max_y - y2) > side_2:
				side_1 = side_1 + (side_2 - (max_y-y2))

				ret_y1 = y1 - side_1
				ret_y2 = max_y

			else:
				ret_y1 = y1 - side_1
				ret_y2 = y2 + side_2

		elif square_size < y_length:
			ret_y1 = y1 + side_1
			ret_y2 = y2 - side_2

	elif affected_dimension == 'x':
		if square_size > x_length:
			if x1 < side_1:
				side_2 = side_2 + (side_1-x1)

				ret_x1 = 0
				ret_x2 = x2 + side_2

			elif (max_x - x2) > side_2:
				side_1 = side_1 + (side_2 - (max_x-x2))

				ret_x1 = x1 - side_1
				ret_x2 = max_x

			else:
				ret_x1 = x1 - side_1
				ret_x2 = x2 + side_2

		elif square_size < x_length:
			ret_x1 = x1 + side_1
			ret_x2 = x2 - side_2

	# print ("Original X1 %d\n" % x1)
	# print ("X1 %d\n" % ret_x1)
	# print ("Original X2 %d\n" % x2)
	# print ("X2 %d\n" % ret_x2)
	# print ("Original Y1 %d\n" % y1)
	# print ("Y1 %d\n" % ret_y1)
	# print ("Original Y2 %d\n" % y2)
	# print ("Y2 %d\n" % ret_y2)

	# print("X length: %d\n" % (ret_x2-ret_x1))
	# print("Y length: %d\n" % (ret_y2-ret_y1))

	return int(ret_x1), int(ret_x2), int(ret_y1), int(ret_y2)

def segment_images( burst_directory, output_directory, curr_datetime):
	global latest_timestamp
	pbar = ProgressBar()

	img_count = 0
	burst_count = 0
	burst_imgs = []

	if burst_directory:
		dir_burst = burst_directory
	if output_directory:
		dir_out = output_directory

	if not os.path.exists(dir_out):
		os.makedirs(dir_out)


	# Create a new folder for each segmentation based on the current date and time 
	# (This will allow segmentation of images from the same camera traps in the future to be placed in
	#  a different location, thereby preventing overwrites)
	if not curr_datetime:
		analysis_datetime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M") 
	else:
		analysis_datetime = curr_datetime

	for path, subdirs, files in os.walk(dir_burst):

		pbar = ProgressBar()
		pbar.maxval = len(files)
		pbar.start()

		for name in pbar(files):

			# only work with JPG 
			if name.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
				image_path = os.path.join(path, name)

				img = cv2.imread(image_path)
				img = img.astype(np.float32)/255.0
				img = img[50:-50,:]
				burst_imgs.append((image_path, img))

		if len(burst_imgs) > 0:
			print(path)
			avg_burst_img = np.mean(np.median(list(dict(burst_imgs).values()), axis=0), axis=-1)


		for i_path, i in burst_imgs:
			diffimg = np.abs(np.mean(i,-1) - avg_burst_img)
			
			diffimg = cv2.blur(diffimg, (25,25))
			thresimg = diffimg > np.max(diffimg) * settings.segmentation['diff_threshold']

			if len(burst_imgs) == 1:
				x1 = 0
				y1 = 0
				x2,y2,depth = np.shape(i)
			else:
				x1, x2 = np.where(np.any(thresimg, 0))[0][[0,-1]]
				y1, y2 = np.where(np.any(thresimg, 1))[0][[0,-1]]
			w=x2-x1
			h=y2-y1
			w = max(w, h/2)
			h = max(h, w/2)

			# Minimum segmentation square size
			w = max(w, settings.segmentation['min_square_size'])
			h = max(h, settings.segmentation['min_square_size'])

			x1 = max(0, x1 - w*0.2)
			x2 = min(i.shape[1]-1, x2 + w*0.2)
			y1 = max(0, y1 - h*0.2)
			y2 = min(i.shape[0]-1, y2 + h*0.8)

			opt_x1, opt_x2, opt_y1, opt_y2 = optimal_square(int(x1),int(x2),int(y1),int(y2),i)

			expected_x = opt_x2 - opt_x1
			expected_y = opt_y2 - opt_y1

			image_obj = Image.open(i_path)
			subimg = image_obj.crop((opt_x1, opt_y1, opt_x2, opt_y2))
			subimg = subimg.resize((224,224))

			#subimg = i[opt_y1:opt_y2,opt_x1:opt_x2,:]

			# actual_x, actual_y, bogus = np.shape(subimg)
			# print (np.shape(i))

			# if not (expected_x == actual_x) or not (expected_y == actual_y):

			# 	print ("Optimal X length %d\n" % (expected_x))
			# 	print ("Actual X length %d\n" % (actual_x))
			# 	print ("Optimal Y length %d\n" % (expected_y))
			# 	print ("Actual Y length %d\n" % (actual_y))

			segmentation_datetime, trap_name, burst_num, filename = tools.get_image_info(i_path)
			dir_blob = os.path.join(dir_out, segmentation_datetime, trap_name, burst_num)

			if not os.path.exists(dir_blob):
				os.makedirs(dir_blob)

			outfile = os.path.join(dir_blob, filename )
			#plt.imsave(outfile, subimg)
			subimg.save(outfile)


		burst_imgs = []

	return analysis_datetime


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--burst_directory", help="directory of bursts to be blobbed")
	parser.add_argument("--output_directory", help="directory to place blobs")
	args = parser.parse_args()


	segment_images(args.burst_directory, args.output_directory)