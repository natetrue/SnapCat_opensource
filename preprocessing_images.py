from os import walk
import numpy as np
import os
import cv2
from imgaug import augmenters as iaa
import random

def random_coords(img):
	height, width = img.shape[:2]
	crop_height = 224
	crop_width = 224

	if height < 224:
		crop_height = height

	if width < 224:
		crop_width = width

	max_height_start = random.randint(0, height - crop_height)
	max_width_start = random.randint(0, width - crop_width)

	return max_height_start, max_width_start

def process_image(dirpath, new_dirpath, filenames):

	seq = iaa.Sequential([
		iaa.Grayscale(1.0)
	])
	
	img = cv2.imread(dirpath + "/" + filename, 1)
	img_aug = seq.augment_image(img)

	random_height_coord, random_width_coord = random_coords(img)

	crop_img = img_aug[random_height_coord:random_height_coord+224, random_width_coord:random_width_coord+224]

	cv2.imwrite(new_dirpath + "/" + filename, crop_img)


if __name__ == '__main__':

	image_files = []
	path = "./images/"
	output_path = "./processed_images"

	if not os.path.exists(output_path):
		os.makedirs(output_path)

	for (dirpath, dirnames, filenames) in walk(path):
		new_dirpath = dirpath.replace('./images/','./processed_images/')

		for filename in filenames:
			if ".jpg" not in filename:
				continue

			process_image(dirpath, new_dirpath, filename)

			
			