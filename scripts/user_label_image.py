"""
███████╗███╗   ██╗ █████╗ ██████╗  ██████╗ █████╗ ████████╗
██╔════╝████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔══██╗╚══██╔══╝
███████╗██╔██╗ ██║███████║██████╔╝██║     ███████║   ██║   
╚════██║██║╚██╗██║██╔══██║██╔═══╝ ██║     ██╔══██║   ██║   
███████║██║ ╚████║██║  ██║██║     ╚██████╗██║  ██║   ██║   
╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝      ╚═════╝╚═╝  ╚═╝   ╚═╝                  
"""
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import argparse
import cv2
import numpy as np

def main():

  parser = argparse.ArgumentParser()
  parser.add_argument("--image_dir", help="directory containing images to sort")
  parser.add_argument("--outdir", help="directory to store images classified")

  args = parser.parse_args()

  files_to_label = []
  # Find all JPG files 
  for (dirpath, dirnames, filenames) in os.walk( args.image_dir):
    for file in filenames:
      if file.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
        files_to_label.append( os.path.join( dirpath, file) )

  for file in files_to_label:
    print(file)

    done = False

    while not done:
      image = cv2.imread(file, cv2.IMREAD_COLOR)
      cv2.imshow("is this image a cat or not?", image)

      key = cv2.waitKeyEx(0)

      print(key)

      # TODO some images are not the same size and this fails
      # TODO split this up more intelligently
      # TODO move images into the proper folders
      # TODO move backwards in array for backspace to allow user to go back

      if key == 2424832:
        print("left")
        red = cv2.imread("C:\\Users\\aadit\\projects\\SnapCat_opensource\\scripts\\red.jpg")
        vis = cv2.add(image, red)
        cv2.imshow("is this image a cat or not?", vis)
        cv2.waitKey(100) #todo find a better way to delay to show image here
        done = True
      elif key == 2555904:
        print("right")
        green = cv2.imread("C:\\Users\\aadit\\projects\\SnapCat_opensource\\scripts\\green.jpg")
        vis = cv2.add(image, green)
        cv2.imshow("is this image a cat or not?", vis)
        cv2.waitKey(100) #todo find a better way to delay to show image here
        done = True
      elif key == 27:
        return
      else:
        print("that wasn't an arrow key: esc to quit")

  
if __name__ == "__main__":
  main()