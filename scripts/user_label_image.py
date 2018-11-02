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
DOWN_KEY = 2621440

ESCAPE_KEY = 27
BACKSPACE_KEY = 8
RED = ( 200, 0, 0 )
GREEN = ( 0, 150, 0 )
YELLOW = ( 150, 150, 0 )

WHITE = ( 255, 255, 255 )
INVALID_STRING = "not_cats"
VALID_STRING = "cats"
UNSURE_STRING = "unsure"

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

  image = concatenate_images( image, ARROWS_IMG )

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
  for file, label in image_labels:

    file_dir = file.split(image_dir)[1] # split path to find any sub directories
    if file_dir[0] == '\\':
      file_dir = file_dir[1:] # get rid of the first slash on the filename

    if label == VALID_STRING:
      new_file = os.path.join( valid_dir, file_dir )

    if label == INVALID_STRING:
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
  for directory, label in directory_labels:

    file_dir = directory.split(image_dir)[1] # split path to find any sub directories
    if file_dir[0] == '\\':
      file_dir = file_dir[1:] # get rid of the first slash on the filename

    if label == VALID_STRING:
      new_dir = os.path.join( valid_dir, file_dir )

    if label == INVALID_STRING:
      new_dir = os.path.join( invalid_dir, file_dir )

    # make sure the new sub directory exists
    new_file_dir = os.path.dirname(new_dir)
    if not os.path.isdir( new_file_dir ):
      os.makedirs( new_file_dir )

    print(directory, new_dir)
    shutil.move(directory, new_dir )


def disp_image_get_input( file ):

  # iterate over all files and add label
  while True:
    
    # display image to be labeled
    image = cv2.imread( file, cv2.IMREAD_COLOR)
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

    elif key == DOWN_KEY:
      update = cv2.add( image, create_blank( image, YELLOW ) )
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

      elif key == DOWN_KEY:
        update = cv2.add( image, create_blank( image, YELLOW ) )
        display_image_wait_key( update, 100 )
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


# def user_label_images( burst_dir, blob_dir, outdir_burst, outdir_blob, parse_burst ):
def user_label_images( burst_dir, outdir_blob, parse_burst ):  
  # TODO: there's a lot of duplicated code here, maybe function pointers?
  ######################### sort individual files #########################
  images_to_label = []

  if not parse_burst:
    """
    for pburst_dir, subdirs, files in os.walk(burst_dir):
      jpegs_in_dir = list_all_jpgs( pburst_dir )

      if len(jpegs_in_dir) < 1:
        continue

      images_to_label += jpegs_in_dir

    if len(images_to_label) == 0:
      return

    image_labels = []
    image_blob_labels = []
    done = False
    index = 0
    while not done: 
      image = images_to_label[index]
      blob = blob_dir + image.split(burst_dir,1)[1]
      key = disp_image_get_input( image )
      
      if key == LEFT_KEY:
        image_labels.append((image, INVALID_STRING))
        image_blob_labels.append((blob, INVALID_STRING))
        index = index + 1

      elif key == RIGHT_KEY:
        image_labels.append((image, VALID_STRING))
        image_blob_labels.append((blob, VALID_STRING))
        index = index + 1

      elif key == BACKSPACE_KEY:
        # ensure we don't go negative with the index
        if ( index > 0 ):
          index = index - 1

          # remove the entry from dict
          image_labels.pop()
          image_blob_labels.pop()

      elif key == ESCAPE_KEY:
        cv2.destroyAllWindows()
        done = True
      
      if index >= len(images_to_label):
        done = True

    cv2.destroyAllWindows()
    move_images( burst_dir, image_labels, outdir_burst )
    move_images( blob_dir, image_blob_labels, outdir_blob)
    """
    pass

  ######################### sort image bursts #########################
  else:
    directory_labels = []
    directory_blob_labels = []
    directories_to_label = []
    index = 0
    done = False

    for pburst_dir, subdirs, files in os.walk(burst_dir):

      jpegs_in_dir = list_all_jpgs( pburst_dir )

      if len(jpegs_in_dir) < 1:
        continue

      directories_to_label.append(pburst_dir)

    if len(directories_to_label) == 0:
      return

    while not done: 
      pburst_dir = directories_to_label[index]

      jpegs_in_dir = list_all_jpgs( pburst_dir )

      if len(jpegs_in_dir) < 1:
        continue

      # pblob_dir = blob_dir + pburst_dir.split(blob_dir,1)[1]

      key = display_directory_get_input( jpegs_in_dir )
      
      if key == LEFT_KEY:
        directory_labels.append((pburst_dir, INVALID_STRING))
        # directory_blob_labels.append((pblob_dir, INVALID_STRING))
        index = index + 1

      elif key == RIGHT_KEY:
        directory_labels.append((pburst_dir, VALID_STRING))
        # directory_blob_labels.append((pblob_dir, VALID_STRING))
        index = index + 1

      elif key == DOWN_KEY:
        directory_labels.append((pburst_dir, UNSURE_STRING))
        # directory_blob_labels.append((pblob_dir, UNSURE_STRING))
        index = index + 1

      elif key == BACKSPACE_KEY:
        # ensure we don't go negative with the index
        if ( index > 0 ):
          index = index - 1

          directory_labels.pop()
          # directory_blob_labels.pop()

      elif key == ESCAPE_KEY:
        cv2.destroyAllWindows()
        done = True
      
      if index >= len(directories_to_label):
        done = True

    cv2.destroyAllWindows()  
    # move_directories( burst_dir, directory_labels, outdir_burst )
    # move_directories( blob_dir, directory_blob_labels, outdir_blob)
  
def main():
  parser = argparse.ArgumentParser()
  # parser.add_argument("--burst_dir", help="directory containing bursts to sort")
  parser.add_argument("--blob_dir", help="directory containing blobs to sort")
  # parser.add_argument("--outdir_burst", help="directory to store bursts classified. Creates ./cats/ and ./not_cats/")
  parser.add_argument("--outdir_blob", help="directory to store blobs classified. Creates ./cats/ and ./not_cats/")
  parser.add_argument("--burst", default="", help="if true, will display bursts as a gif style and label the whole burst, otherwise labels individual images")

  args = parser.parse_args()
  
  # user_label_images( args.burst_dir, args.blob_dir, args.outdir_burst, args.outdir_blob, args.burst.lower() == "true" )
  user_label_images( args.blob_dir, args.outdir_blob, True )

if __name__ == "__main__":
  main()