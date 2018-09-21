"""
███████╗███╗   ██╗ █████╗ ██████╗  ██████╗ █████╗ ████████╗
██╔════╝████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔══██╗╚══██╔══╝
███████╗██╔██╗ ██║███████║██████╔╝██║     ███████║   ██║   
╚════██║██║╚██╗██║██╔══██║██╔═══╝ ██║     ██╔══██║   ██║   
███████║██║ ╚████║██║  ██║██║     ╚██████╗██║  ██║   ██║   
╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝      ╚═════╝╚═╝  ╚═╝   ╚═╝                  
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import argparse
import cv2
import numpy as np

LEFT_KEY = 2424832
RIGHT_KEY = 2555904
RED = ( 255, 0, 0 )
GREEN = ( 0, 255, 0 )
WHITE = ( 255, 255, 255 )

IMAGE_TEXT = "Does Image Contain Cat?"
IMAGE_PATH = os.path.join( os.path.dirname( os.path.realpath(__file__) ), "images" )
USAGE_IMG = os.path.join( IMAGE_PATH, "usage.jpg" )
ARROWS_IMG = os.path.join( IMAGE_PATH, "cat-notcat.jpg" )


def create_blank( image, rgb_color=(0, 0, 0)):

  height = image.shape[0]
  width = image.shape[1]

  """Create new image(numpy array) filled with certain color in RGB"""
  # Create black blank image
  image = np.zeros((height, width, 3), np.uint8)

  # Since OpenCV uses BGR, convert the color first
  color = tuple(reversed(rgb_color))
  # Fill image with color
  image[:] = color

  return image


def display_image_wait_key( image, delay_ms=0 ):
  cv2.imshow(IMAGE_TEXT, image)
  return cv2.waitKeyEx( delay_ms )


# todo combine these two functions
def concatenate_images( image1, image2 ):
  
  image2 = cv2.imread( image2, cv2.IMREAD_COLOR)

  ratio = image2.shape[1] / image1.shape[1]
  dimensions = ( image1.shape[1], int(image2.shape[0] / ratio) )
  
  # resize image
  resized = cv2.resize(image2, dimensions)
  return np.concatenate( ( image1, resized ), axis=0)


def sort_images( image_dir, image_classifications, outdir ):
  
  cat_dir = os.path.join( outdir, "cats" )
  not_cat_dir = os.path.join( outdir, "not_cats" )

  if not os.path.isdir( cat_dir ):
    os.mkdir( cat_dir )  
  
  if not os.path.isdir( not_cat_dir ):
    os.mkdir( not_cat_dir )  

  # iterate over all the labeled images and put them within a foler
  for file in image_classifications:

    file_dir = file.split(image_dir)[1] # split path to find any sub directories
    if file_dir[0] == '\\':
      file_dir = file_dir[1:] # get rid of the first slash on the filename

    if image_classifications[file] == "cat":
      new_file = os.path.join( cat_dir, file_dir )

    if image_classifications[file] == "not_cat":
      new_file = os.path.join( not_cat_dir, file_dir )

    # make sure the new sub directory exists
    new_file_dir = os.path.dirname(new_file)
    if not os.path.isdir( new_file_dir ):
      os.mkdir( new_file_dir )

    print( file, new_file )
    os.rename(file, new_file )


def get_image_labels( files ):

  num_files = len( files )
  index = 0

  image_classifications = dict()

  # iterate over all files and add label
  while index < num_files:
    file_name = files[index]
    
    # display image to be labeled
    image = cv2.imread( file_name, cv2.IMREAD_COLOR)
    image = concatenate_images( image, ARROWS_IMG )
    key = display_image_wait_key( image, 0 )

    # wait for user input
    done = False
    while not done:
      if key == LEFT_KEY:
        update = cv2.add(image, create_blank(image, RED))
        display_image_wait_key( update, 100)
        image_classifications[file_name] = "not_cat"
        done = True
        index = index + 1

      elif key == RIGHT_KEY:
        update = cv2.add(image, create_blank(image, GREEN))
        display_image_wait_key( update, 100)
        image_classifications[file_name] = "cat"
        done = True
        index = index + 1

      elif key == 27: # escape
        # quit
        cv2.destroyAllWindows()
        return image_classifications

      # TODO: add user instructions that backspace can be used to back up
      elif key == 8: # backspace
        done = True

        # ensure we don't go negative with the index
        if ( index > 0 ):
          index = index - 1

      else:
        update = concatenate_images( image, USAGE_IMG )
        key = display_image_wait_key( update, 0)

  return image_classifications


def get_directory_label( files ):

  num_files = len( files )

  # iterate over all files and add label
  while True:

    for file in files:

      # display image to be labeled
      image = cv2.imread( file, cv2.IMREAD_COLOR)
      image = concatenate_images( image, ARROWS_IMG )
      key = display_image_wait_key( image, 100 )
      
      # wait for user input
      if key == LEFT_KEY:
        update = cv2.add(image, create_blank(image, RED))
        display_image_wait_key( update, 100)
        return "not_cat"

      elif key == RIGHT_KEY:
        update = cv2.add(image, create_blank(image, GREEN))
        display_image_wait_key( update, 100)
        return "cat"
      
      elif key == 27: # escape
        cv2.destroyAllWindows()
        return "quit"

      elif key == 8: # backspace
        return "back"

      elif key != -1:
        image = cv2.imread( USAGE_IMG, cv2.IMREAD_COLOR)
        key = display_image_wait_key( image, 0)
        #todo, change image text to contain press any key to continue


def list_all_jpgs( directory ):
  jpeg_files = []

  for (dirpath, dirnames, filenames) in os.walk( directory):
    for file in filenames:
      if file.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
        jpeg_files.append( os.path.join( dirpath, file) )

  return jpeg_files


def user_label_images( image_dir, outdir, parse_burst ):
  
  # TODO, this may make more sense to iterate over all the files and label each image instead of calling get_image_labels()
  if not parse_burst:
    images_to_label = list_all_jpgs( image_dir )
    image_classificationss = get_image_labels( images_to_label )
    sort_images( image_dir, image_classificationss, outdir )

  else:
    directories = next(os.walk(image_dir))[1]
    for directory in directories:
      search_dir = os.path.join(image_dir, directory)
      jpegs_in_dir = list_all_jpgs( search_dir )
      label = get_directory_label( jpegs_in_dir )
      print( label)
      #TODO move whole directory based on label
  
def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--image_dir", help="directory containing images to sort")
  parser.add_argument("--outdir", help="directory to store images classified. Creates ./cat/ and ./not_cat/")
  parser.add_argument("--burst", default="", help="if true, will display bursts as a gif style and label the whole burst, otherwise labels individual images")

  args = parser.parse_args()
  
  user_label_images( args.image_dir, args.outdir, args.burst.lower() == "true" )

if __name__ == "__main__":
  main()