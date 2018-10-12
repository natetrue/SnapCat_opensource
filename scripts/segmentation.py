import cv2
import os
import numpy as np
import argparse
import time
import datetime
import matplotlib.pyplot as plt
import settings
import tools

from progressbar import ProgressBar

def segment_images( burst_images, save_image=False ):

	pbar = ProgressBar()

	img_count = 0
	burst_count = 0
	burst_imgs = []
	segmented_images = []

	pbar = ProgressBar()
	pbar.maxval = len(burst_images)
	pbar.start()

	for image in pbar(burst_images):

		# only work with JPG 
		if image.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):

			img = cv2.imread(image)

			img = img.astype(np.float32)/255.0 # todo why divide by 255?
			img = img[50:-50,:] #todo what is this doing?
			burst_imgs.append((image, img))

	if len(burst_imgs) > 0:
		avg_burst_img = np.mean(np.median(list(dict(burst_imgs).values()), axis=0), axis=-1)

	for i_path, i in burst_imgs:
		diffimg = np.abs(np.mean(i,-1) - avg_burst_img)
		
		diffimg = cv2.blur(diffimg, (25,25))
		thresimg = diffimg > np.max(diffimg) * settings.segmentation['diff_threshold']
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

		segmented_images.append(subimg)


	# todo figure out where we want to save the segmented images from a burst
	"""
	if save_images:
		for image in segmented_images:
			outfile = os.dirname(???)
			plt.imsave(outfile, subimg)
	"""
	
	return segmented_images
	


if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("--burst_directory", help="directory of bursts to be blobbed")
	parser.add_argument("--output_directory", help="directory to place blobs")
	args = parser.parse_args()


	segment_images(args.burst_directory, args.output_directory)