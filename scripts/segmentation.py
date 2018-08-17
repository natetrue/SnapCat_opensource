import cv2
import os
import matplotlib.pyplot as plt
import numpy as np
import argparse
import uuid

def main():
	images_list = []
	imgs = []
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
		for name in files:
			if name.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
				images_list.append(os.path.join(path, name))

	print("%d images" % len(images_list))

	for image_path in images_list:
		img = cv2.imread(image_path)
		img = img.astype(np.float32)/255.0
		img = img[50:-50,:]
		imgs.append(img)

	avg_img = np.mean(np.median(imgs, axis=0), axis=-1)

	for i in imgs:
		diffimg = np.abs(np.mean(i,-1) - avg_img)
		diffimg = cv2.blur(diffimg, (25,25))
		thresimg = diffimg > np.max(diffimg) * 0.7
		x1, x2 = np.where(np.any(thresimg, 0))[0][[0,-1]]
		y1, y2 = np.where(np.any(thresimg, 1))[0][[0,-1]]
		w=x2-x1
		h=y2-y1
		w = max(w, h/2)
		h = max(h, w/2)
		print(x1, x2, y1, y2)
		x1 = max(0, x1 - w*0.2)
		x2 = min(i.shape[1]-1, x2 + w*0.2)
		y1 = max(0, y1 - h*0.2)
		y2 = min(i.shape[0]-1, y2 + h*0.8)
		subimg = i[int(y1):int(y2),int(x1):int(x2),:]

		outfile = '%s/%s.jpg' % (dir_out, "blob_" + uuid.uuid4().hex)
		plt.imsave(outfile, subimg)


if __name__ == "__main__":
  main()