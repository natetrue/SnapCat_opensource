"""
███████╗███╗   ██╗ █████╗ ██████╗  ██████╗ █████╗ ████████╗
██╔════╝████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔══██╗╚══██╔══╝
███████╗██╔██╗ ██║███████║██████╔╝██║     ███████║   ██║   
╚════██║██║╚██╗██║██╔══██║██╔═══╝ ██║     ██╔══██║   ██║   
███████║██║ ╚████║██║  ██║██║     ╚██████╗██║  ██║   ██║   
╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝      ╚═════╝╚═╝  ╚═╝   ╚═╝                  
"""
import cv2
import os
import numpy as np
import argparse
import time
import datetime
import settings
import tools
import sys
from skimage import img_as_ubyte
from progressbar import ProgressBar
from PIL import Image

import json_database

def get_bursts( json_data ):
	bursts = []
	for image in json_data:
		burst = json_data[image]["burst_images"]
		if not burst in bursts:
			bursts.append(burst)

	return bursts


def segment_images( snapcat_json ):
	
	pbar = ProgressBar()
	bursts = get_bursts( snapcat_json.json_data )

	for burst in bursts:

		pbar = ProgressBar()
		pbar.maxval = len(burst)
		pbar.start()

		burst_imgs = []

		for filename in pbar(burst):

			image_path = snapcat_json.json_data[filename]["path"]

			img = cv2.imread(image_path)
			img = img.astype(np.float32)/255.0
			#TODO: make this a setting in the settings file as it is used later when we crop the image
			img = img[50:-50,:] # remove the black bar from top and bottom
			burst_imgs.append((image_path, img))


		if len(burst_imgs) > 0:
			avg_burst_img = np.mean(np.median(list(dict(burst_imgs).values()), axis=0), axis=-1)


		for image_path, i in burst_imgs:

			diffimg = np.abs(np.mean(i,-1) - avg_burst_img)
			diffimg = cv2.blur(diffimg, (25,25))

			"""
			# TODO investigate options to identify local differences

			# display color map of diff image
			wide_diffimg = cv2.blur(diffimg, (100,100))
			wide_diff = np.abs(wide_diffimg - diffimg)
			unsigned_image = img_as_ubyte(wide_diff)
			im_color = cv2.applyColorMap(unsigned_image, cv2.COLORMAP_JET)
			cv2.imshow('image',im_color)
			cv2.waitKey(0)
			cv2.destroyAllWindows()
			"""

			thresimg = diffimg > np.max(diffimg) * settings.segmentation['diff_threshold']

			if len(burst_imgs) == 1:
				x1 = 0
				y1 = 0
				x2, y2, _ = np.shape(i)
			else:

				#find the x bounds of where the threshold is exceeded
				x1, x2 = np.where( np.any(thresimg, 0))[0][[0,-1]]

				#find the x bounds of where the threshold is exceeded
				y1, y2 = np.where( np.any(thresimg, 1))[0][[0,-1]]

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
			
			opt_x1, opt_x2, opt_y1, opt_y2 = tools.optimal_square(int(x1),int(x2),int(y1),int(y2),i)

			# Save this information in JSON file
			area_of_interest = [opt_x1, opt_x2, opt_y1, opt_y2]
			image_name = os.path.basename(image_path)
			snapcat_json.update( image_name , "area_of_interest", area_of_interest )

			# note call -- tools.save_areas_of_interest() -- to save the areas of interest to files for review
			
			"""
			# TODOs remaining
			1. segmentation (nate)
		    7. plan party
			"""

	snapcat_json.save()


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--json_dir", help="path to the json database for images" )
	args = parser.parse_args()

	snapcat_json = json_database.JSONDatabase( args.json_dir )

	segment_images( snapcat_json )