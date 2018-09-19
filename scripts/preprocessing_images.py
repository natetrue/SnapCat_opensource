from os import walk
import numpy as np
import os
import cv2
from imgaug import augmenters as iaa
import random
import argparse
from progressbar import ProgressBar

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

	parser = argparse.ArgumentParser()
	parser.add_argument(
		'--input_dir',
		type=str,
		default='',
		help='Path to folders of input images.'
	)

	parser.add_argument(
		'--output_dir',
		type=str,
		default='',
		help='Path to folders of input images.'
	)

	FLAGS, unparsed = parser.parse_known_args()

	if FLAGS.input_dir == None:
		print("Please provide an input directory\n")
		exit()

	if FLAGS.output_dir == None:
		print("Please provide an output directory\n")
		exit()

	image_files = []
	input_path = FLAGS.input_dir
	output_path = FLAGS.output_dir
	allowed_extensions = ['jpg', 'jpeg', 'JPG', 'JPEG']
	pbar = ProgressBar()
	pbar.start()
	file_counter = 0

	if not os.path.exists(output_path):
		os.makedirs(output_path)

	# Get number of files for Progress Bar
	file_count = sum([len(files) for r, d, files in os.walk(input_path)])
	print (file_count)
	pbar.maxval = file_count

	for (dirpath, dirnames, filenames) in walk(input_path):
		new_dirpath = dirpath.replace(input_path, output_path)

		if not os.path.exists(new_dirpath):
			os.makedirs(new_dirpath)

		for filename in filenames:
			file_counter += 1
			pbar.update(file_counter)
			illegal_file = True
			for ext in allowed_extensions:
				if ext in filename:
					illegal_file = False

			if not illegal_file:
				process_image(dirpath, new_dirpath, filename)

			
			