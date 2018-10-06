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
import shutil
from win32api import GetSystemMetrics

LEFT_KEY = 2424832
RIGHT_KEY = 2555904
ESCAPE_KEY = 27
BACKSPACE_KEY = 8
RED = ( 255, 0, 0 )
GREEN = ( 0, 255, 0 )
WHITE = ( 255, 255, 255 )
INVALID_STRING = "not_cats"
VALID_STRING = "cats"

IMAGE_TEXT = "Does Image Contain Cat?"
IMAGE_PATH = os.path.join( os.path.dirname( os.path.realpath(__file__) ), "images" )
USAGE_IMG = os.path.join( IMAGE_PATH, "usage.jpg" )
ARROWS_IMG = os.path.join( IMAGE_PATH, "cat-notcat.jpg" )


def get_max_window_size():

  width = GetSystemMetrics(0)
  height = GetSystemMetrics(1)

  max_size = min(width, height) * 0.75

  return int(max_size)

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

  max_window_size = get_max_window_size()
  window_size = max( image.shape[0], image.shape[1] )

  ratio = max_window_size / window_size

  dimensions = ( int( image.shape[1] * ratio ) , int( image.shape[0] * ratio) )
  
  # resize image
  image = cv2.resize(image, dimensions)

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


def move_images( image_dir, image_labels, outdir ):
  
  valid_dir = os.path.join( outdir, VALID_STRING )
  invalid_dir = os.path.join( outdir, INVALID_STRING )

  # iterate over all the labeled images and put them within a foler
  for file in image_labels:

    file_dir = file.split(image_dir)[1] # split path to find any sub directories
    if file_dir[0] == '\\':
      file_dir = file_dir[1:] # get rid of the first slash on the filename

    if image_labels[file] == VALID_STRING:
      new_file = os.path.join( valid_dir, file_dir )

    if image_labels[file] == INVALID_STRING:
      new_file = os.path.join( invalid_dir, file_dir )

    # make sure the new sub directory exists
    new_file_dir = os.path.dirname(new_file)
    if not os.path.isdir( new_file_dir ):
      os.makedirs( new_file_dir )

    print(file, new_file)
    os.rename(file, new_file )


def move_directories( image_dir, directory_labels, outdir ):
  
  valid_dir = os.path.join( outdir, VALID_STRING )
  invalid_dir = os.path.join( outdir, INVALID_STRING )

  # iterate over all the labeled images and put them within a foler
  for directory in directory_labels:

    file_dir = directory.split(image_dir)[1] # split path to find any sub directories
    if file_dir[0] == '\\':
      file_dir = file_dir[1:] # get rid of the first slash on the filename

    if directory_labels[directory] == VALID_STRING:
      new_dir = os.path.join( valid_dir, file_dir )

    if directory_labels[directory] == INVALID_STRING:
      new_dir = os.path.join( invalid_dir, file_dir )

    # make sure the new sub directory exists
    new_file_dir = os.path.dirname(new_dir)
    if not os.path.isdir( new_file_dir ):
      os.makedirs( new_file_dir )

    shutil.move(directory, new_dir )


def disp_image_get_input( file ):

  # iterate over all files and add label
  while True:
    
    # display image to be labeled
    image = cv2.imread( file, cv2.IMREAD_COLOR)
    image = concatenate_images( image, ARROWS_IMG )
    key = display_image_wait_key( image, 0 )

    # wait for user input
    if key == LEFT_KEY:
      update = cv2.add(image, create_blank( image, RED) )
      display_image_wait_key( update, 100)
      return key

    elif key == RIGHT_KEY:
      update = cv2.add( image, create_blank( image, GREEN ) )
      display_image_wait_key( update, 100 )
      return key

    elif key == ESCAPE_KEY:
      return key

    elif key == BACKSPACE_KEY:
      return key

    else:
      image = cv2.imread( USAGE_IMG, cv2.IMREAD_COLOR)
      key = display_image_wait_key( image, 0)
      #todo, change image text to contain press any key to continue

def display_directory_get_input( files ):

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
        return key

      elif key == RIGHT_KEY:
        update = cv2.add(image, create_blank(image, GREEN))
        display_image_wait_key( update, 100)
        return key

      elif key == ESCAPE_KEY:
        return key

      elif key == BACKSPACE_KEY:
        return key

      elif key != -1:
        image = cv2.imread( USAGE_IMG, cv2.IMREAD_COLOR)
        key = display_image_wait_key( image, 0)
        #todo, change image text to contain press any key to continue

def list_all_jpgs( directory ):
  jpeg_files = []
  filenames = [f for f in os.listdir(directory) ]

  for file in filenames:
    if file.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
      jpeg_files.append( os.path.join( directory, file) )

  return jpeg_files


def user_label_images( image_dir, outdir, parse_burst ):
  
  # TODO: there's a lot of duplicated code here, maybe function pointers?
  ######################### sort individual files #########################
  if not parse_burst:
    images_to_label = list_all_jpgs( image_dir )
    if len(images_to_label) == 0:
      return

    image_labels = dict()
    done = False
    index = 0
    while not done: 
      image = images_to_label[index]
      key = disp_image_get_input( image )
      
      if key == LEFT_KEY:
        image_labels[image] = INVALID_STRING
        index = index + 1

      elif key == RIGHT_KEY:
        image_labels[image] = VALID_STRING
        index = index + 1

      elif key == BACKSPACE_KEY:
        # ensure we don't go negative with the index
        if ( index > 0 ):
          index = index - 1

        # remove the entry from dict
        image = images_to_label[index]
        del image_labels[image]

      elif key == ESCAPE_KEY:
        cv2.destroyAllWindows()
        done = True
      
      if index >= len(images_to_label):
        done = True

    move_images( image_dir, image_labels, outdir )

  ######################### sort image bursts #########################
  else:
    try:
      directories = next(os.walk(image_dir))[1]
    except:
      return

    if len(directories) == 0:
      return

    directory_labels = dict()
    index = 0
    done = False

    for burst_dir, subdirs, files in os.walk(image_dir):

      jpegs_in_dir = list_all_jpgs( burst_dir )

      if len(jpegs_in_dir) < 1:
        continue

      key = display_directory_get_input( jpegs_in_dir )
      
      if key == LEFT_KEY:
        directory_labels[burst_dir] = INVALID_STRING
        index = index + 1

      elif key == RIGHT_KEY:
        directory_labels[burst_dir] = VALID_STRING
        index = index + 1

      elif key == BACKSPACE_KEY:
        # ensure we don't go negative with the index
        if ( index > 0 ):
          index = index - 1

        # remove the entry from dict
        burst_dir = os.path.join( image_dir, directories[index] )
        del directory_labels[burst_dir]

      elif key == ESCAPE_KEY:
        cv2.destroyAllWindows()
        break
      
    move_directories( image_dir, directory_labels, outdir )
  
def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--image_dir", help="directory containing images to sort")
  parser.add_argument("--outdir", help="directory to store images classified. Creates ./cat/ and ./not_cat/")
  parser.add_argument("--burst", default="", help="if true, will display bursts as a gif style and label the whole burst, otherwise labels individual images")

  args = parser.parse_args()
  
  user_label_images( args.image_dir, args.outdir, args.burst.lower() == "true" )

if __name__ == "__main__":
  main()