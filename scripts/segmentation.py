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
from skimage import img_as_ubyte

from progressbar import ProgressBar

from PIL import Image

def segment_images( burst_directory, output_directory, curr_datetime=None):
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
				img = img[50:-50,:] # remove the black bar from top and bottom
				burst_imgs.append((image_path, img))

		if len(burst_imgs) > 0:
			#print(path)
			avg_burst_img = np.mean(np.median(list(dict(burst_imgs).values()), axis=0), axis=-1)


		for i_path, i in burst_imgs:

			diffimg = np.abs(np.mean(i,-1) - avg_burst_img)
			
			diffimg = cv2.blur(diffimg, (25,25))

			#cv2.imshow('image',diffimg)
			#cv2.waitKey(0)
			#cv2.destroyAllWindows()

			thresimg = diffimg > np.max(diffimg) * settings.segmentation['diff_threshold']

			#print ("threshimg", thresimg)

			if len(burst_imgs) == 1:
				x1 = 0
				y1 = 0
				x2, y2, _ = np.shape(i)
			else:

				#find the x bounds of where the threshold is exceeded
				x1, x2 = np.where( np.any(thresimg, 0))[0][[0,-1]]

				#find the x bounds of where the threshold is exceeded
				y1, y2 = np.where( np.any(thresimg, 1))[0][[0,-1]]



			#print (i_path)
			w=x2-x1
			#print( "w", w )

			h=y2-y1
			#print( "h", h )

			w = max(w, h/2)
			#print( "w", w )

			h = max(h, w/2)
			#print( "h", h )

			# Minimum segmentation square size
			w = max(w, settings.segmentation['min_square_size'])
			#print( "w", w )

			h = max(h, settings.segmentation['min_square_size'])
			#print( "h", h )

			x1 = max(0, x1 - w*0.2)
			x2 = min(i.shape[1]-1, x2 + w*0.2)
			y1 = max(0, y1 - h*0.2)
			y2 = min(i.shape[0]-1, y2 + h*0.8)

			image_obj = Image.open(i_path)
			subimg = image_obj.crop((x1, y1, x2, y2))

			opt_x1, opt_x2, opt_y1, opt_y2 = tools.optimal_square(int(x1),int(x2),int(y1),int(y2),i)

			expected_x = opt_x2 - opt_x1
			expected_y = opt_y2 - opt_y1

			"""
			image_obj = Image.open(i_path)
			image_obj = image_obj.crop((x1, y1+50, x2, y2-50))
			subimg = image_obj.crop((opt_x1, opt_y1, opt_x2, opt_y2))
			subimg = subimg.resize((224,224))
			subimg.show()
			"""

			img = i[opt_y1:opt_y2 , opt_x1:opt_x2,:]
			resized_image = cv2.resize(img, (224, 224)) 	
			#cv2.imshow('image',resized_image)
			#cv2.waitKey(0)

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

			resized_image = img_as_ubyte(resized_image)
			cv2.imwrite(outfile, resized_image)
			cv2.destroyAllWindows()

		burst_imgs = []

	return analysis_datetime


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--burst_directory", help="directory of bursts to be blobbed")
	parser.add_argument("--output_directory", help="directory to place blobs")
	args = parser.parse_args()


	segment_images(args.burst_directory, args.output_directory)