from os import walk
import numpy as np
import os
import cv2
import argparse
from progressbar import ProgressBar
from PIL import Image
import tools

def process_image(dirpath, new_dirpath, filename):
	filepath = os.path.join(dirpath,filename)
	filepath_out = os.path.join(new_dirpath,filename)

	img = cv2.imread(filepath, 1)
	img = img.astype(np.float32)/255.0
	#img = img[50:-50,:]

	x1 = 0
	y1 = 0
	y2,x2,depth = np.shape(img)

	opt_x1, opt_x2, opt_y1, opt_y2 = tools.optimal_square(int(x1),int(x2),int(y1),int(y2),img)

	image_obj = Image.open(filepath)
	subimg = image_obj.crop((opt_x1, opt_y1, opt_x2, opt_y2))
	subimg = subimg.resize((224,224))

	subimg.save(filepath_out)


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
	#print (file_count)
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

			
			