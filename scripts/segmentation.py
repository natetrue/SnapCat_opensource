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

def convert_to_ms(timestamp_string):
	# Example of Reconyx saved image
	# 01-05-2013 9-58-15

	timestamp = time.mktime(datetime.datetime.strptime(timestamp_string, "%d-%m-%Y %H-%M-%S").timetuple())
	print timestamp


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
		night_imgs = []
		day_imgs = []

		# Find all JPG files

		for name in files:
			if name.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
				images_list.append(os.path.join(path, name))

		if len(images_list) == 0:
			continue

		print("%d images" % len(images_list))

		pbar.maxval = img_length_cap
		pbar.start()

		counter = 0
		for image_path in pbar(images_list):
			if counter > img_length_cap:
				break
			img = cv2.imread(image_path)
			img = img.astype(np.float32)/255.0
			img = img[50:-50,:]

			if is_grayscale(image_path):
				night_imgs.append(img)
			else:
				day_imgs.append(img)
			counter += 1

		# Take the average of the images (separate for night and day)
		avg_day_img = np.mean(np.median(day_imgs, axis=0), axis=-1)
		avg_night_img = np.mean(np.median(night_imgs, axis=0), axis=-1)

		print ("Num Day Images: %d\n" % len(day_imgs))
		pbar = ProgressBar()
		pbar.maxval = len(day_imgs)
		pbar.start()

		for i in pbar(day_imgs):
			diffimg = np.abs(np.mean(i,-1) - avg_day_img)
			diffimg = cv2.blur(diffimg, (25,25))
			thresimg = diffimg > np.max(diffimg) * 0.6
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

			outfile = '%s/%s.jpg' % (dir_out, "blob_day_" + uuid.uuid4().hex)
			plt.imsave(outfile, subimg)

		print ("Num Night Images: %d\n" % len(night_imgs))
		pbar = ProgressBar()
		pbar.maxval = len(day_imgs)
		pbar.start()

		for i in pbar(night_imgs):
			diffimg = np.abs(np.mean(i,-1) - avg_night_img)
			diffimg = cv2.blur(diffimg, (25,25))
			thresimg = diffimg > np.max(diffimg) * 0.6
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

			outfile = '%s/%s.jpg' % (dir_out, "blob_night_" + uuid.uuid4().hex)
			plt.imsave(outfile, subimg)


if __name__ == "__main__":
  main()