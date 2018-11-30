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


def segment_images( snapcat_json, speckle_removal_size=10, expansion=50, interactive_examine=False ):
	# Create CLAHE object (contrast limited adaptive histogram equalization, compensates for brightness changes)
	clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

	pbar = ProgressBar()
	bursts = tools.get_bursts( snapcat_json )

	for burst in bursts:

		pbar = ProgressBar()
		pbar.maxval = len(burst)
		pbar.start()

		burst_imgs = []

		for filename in pbar(burst):

			image_path = snapcat_json.json_data[filename]["path"]

			img = cv2.imread(image_path)
			#TODO: make this a setting in the settings file as it is used later when we crop the image
			img = img[50:-50,:] # remove the black bar from top and bottom
			burst_imgs.append((image_path, img))

		# Image bursts less than 3 images can't be median'd, so ignore
		if len(burst_imgs) < 3:
			continue

		# Get all the images in the burst
		imgs = [b[1] for b in burst_imgs]
		# Scale them to fit within 320x320 (speeds up calculations)
		img_scale = max(imgs[0].shape[0]/320.0, imgs[0].shape[1]/320.0)
		imgs_small = [cv2.resize(i, (int(i.shape[1]/img_scale),int(i.shape[0]/img_scale)), interpolation=cv2.INTER_AREA) for i in imgs]
		# Apply CLAHE to compensate for in-burst brightness changes. Also convert to grayscale
		imgs_small = [clahe.apply(np.uint8(np.mean(i,-1))) for i in imgs_small]
		# Take the median across the images pixel by pixel
		avg_burst_img = np.median(imgs_small, axis=0)
		# Calculate diff images from the median
		diffimgs = [np.abs(smimg.astype(np.int16) - avg_burst_img) for smimg in imgs_small]

		# Start with a high motion threshold for the burst and iteratively bring it down if we don't find anything
		for seq_thres in [30, 25, 20, 15, 10]:
			tot_imgs = 0
			areas_of_interest = {image_path:[] for image_path,_ in burst_imgs}
			# Process each image in the burst
			for burst_index, (image_path, i) in enumerate(burst_imgs):
				diffimg = diffimgs[burst_index]
				# Threshold the image based on our threshold
				thresimg = np.uint8(diffimg > seq_thres)
				# This morphology operation first shrinks any 'islands' of motion (which deletes little speckles),
				# then it expands the remaining islands back to approximate original size.
				# To deal with larger 'speckle' areas, increase the size of the MORPH_ELLIPSE
				thresimg = cv2.morphologyEx(thresimg, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (speckle_removal_size,speckle_removal_size)))
				# Now to ensure we have a border around the subject motion, expand islands. This will also merge nearby islands
				thresimg = cv2.dilate(thresimg, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (expansion,expansion)))
				if interactive_examine:
					cv2.imshow('diff', diffimg / np.max(diffimg))
					cv2.imshow('thres', thresimg*255)
				# Now label each island individually with a number in a new label image
				nlabels, labelimg = cv2.connectedComponents(thresimg, connectivity=4)
				nimgs = 0
				# Take each island individually
				for l in range(1, nlabels):
					# This magic incantation gets the bounding box of that island
					x1, x2 = np.int32(np.where(np.any(labelimg == l, 0))[0][[0,-1]] * img_scale)
					y1, y2 = np.int32(np.where(np.any(labelimg == l, 1))[0][[0,-1]] * img_scale)
					# Make sure it's a square region
					w = x2-x1
					h = y2-y1
					if w > h:
						y1 -= (w-h)//2
						y2 = y1 + w
					elif h > w:
						x1 -= (h-w)//2
						x2 = x1 + h
					# That may have pushed the region off the bounds of the image.
					# Shrink the square until it is no longer out of bounds.
					while x1 < 0 or y1 < 0 or x2 >= i.shape[1] or y2 >= i.shape[0]:
						x1 += 1
						x2 -= 1
						y1 += 1
						y2 -= 1

					# Save the area of interest for this image.
					areas_of_interest[image_path].append([x1,x2,y1,y2])
					if interactive_examine:
						subimg = i[y1:y2,x1:x2,:]
						print(x1,x2,y1,y2)
						cv2.imshow('image', subimg)
						if cv2.waitKey(0) == ord('q'):
							exit(1)
			if len(areas_of_interest) > 0:
				break

		for image_path in areas_of_interest.keys():
			image_name = os.path.basename(image_path)
			snapcat_json.update( image_name , "areas_of_interest", areas_of_interest[image_path] )

	snapcat_json.save()


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--json_dir", help="path to the json database for images" )
	args = parser.parse_args()

	snapcat_json = json_database.JSONDatabase( args.json_dir )

	segment_images( snapcat_json )