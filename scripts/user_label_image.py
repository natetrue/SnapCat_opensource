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
import json_database

LEFT_KEY = 2424832
RIGHT_KEY = 2555904
DOWN_KEY = 2621440

ESCAPE_KEY = 27
BACKSPACE_KEY = 8
RED = ( 200, 0, 0 )
GREEN = ( 0, 150, 0 )
YELLOW = ( 150, 150, 0 )

WHITE = ( 255, 255, 255 )
INVALID_STRING = "not_cat"
VALID_STRING = "cat"
UNSURE_STRING = "unsure"
POLLING_DURATION_MS = 100
MAX_POLLING_TIMEOUT_MS = (60 * 2 * 1000) #2 mins

IMAGE_TEXT = "Does Image Contain Cat?"
IMAGE_PATH = os.path.join( os.path.dirname( os.path.realpath(__file__) ), "images" )
USAGE_IMG = os.path.join( IMAGE_PATH, "usage.jpg" )
ARROWS_IMG = os.path.join( IMAGE_PATH, "cat-notcat.jpg" )
LOGO_IMG = os.path.join( IMAGE_PATH, "logo.jpg" )


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


def resize_image( image ):
  max_window_size = get_max_window_size()
  window_size = max( image.shape[0], image.shape[1] )

  ratio = max_window_size / window_size

  dimensions = ( int( image.shape[1] * ratio ) , int( image.shape[0] * ratio) )

  # resize image
  image = cv2.resize(image, dimensions)

  return image

def display_image_wait_key( image, delay_ms=0 ):

  cat_image = resize_image(image)

  arrow_img = cv2.imread( ARROWS_IMG, cv2.IMREAD_COLOR)
  arrow_img = resize_image(arrow_img)

  logo_img = cv2.imread( LOGO_IMG, cv2.IMREAD_COLOR)
  logo_img = resize_image(logo_img)
  
  image = concatenate_images( logo_img, cat_image )
  image = concatenate_images( image, arrow_img )

  cv2.imshow(IMAGE_TEXT, image)
  return cv2.waitKeyEx( delay_ms )


# todo combine these two functions
def concatenate_images( image1, image2 ):
  
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
  timeout = 0

  while True:

    image = cv2.imread( file, cv2.IMREAD_COLOR)

    if timeout > MAX_POLLING_TIMEOUT_MS:
      key = 1234
      timeout = 0
    else:
      # display image to be labeled
      key = display_image_wait_key( image, POLLING_DURATION_MS )

    # wait for user input
    if key == LEFT_KEY:
      update = cv2.add(image, create_blank( image, RED) )
      display_image_wait_key( update, POLLING_DURATION_MS)
      return key

    elif key == RIGHT_KEY:
      update = cv2.add( image, create_blank( image, GREEN ) )
      display_image_wait_key( update, POLLING_DURATION_MS )
      return key

    elif key == DOWN_KEY:
      update = cv2.add( image, create_blank( image, YELLOW ) )
      display_image_wait_key( update, POLLING_DURATION_MS )
      return key

    elif key == ESCAPE_KEY:
      return key

    elif key == BACKSPACE_KEY:
      return key

    elif key != -1:
      alpha = 0.3

      # image to review as backgorund and usage as foreground
      img1 = image
      img2 = cv2.imread(USAGE_IMG)

      img1 = resize_image(img1)
      img2 = resize_image(img2)

      print( img1.size, img2.size )
      image = cv2.addWeighted(img1,alpha,img2,1-alpha,0)

      display_image_wait_key( image, 0)

      key = -1

    else:
      timeout += POLLING_DURATION_MS

def display_directory_get_input( files ):

  timeout = 0

  num_files = len( files )

  # iterate over all files and add label
  while True:

    for file in files:

      # display image to be labeled
      image = cv2.imread( file, cv2.IMREAD_COLOR)

      if timeout > MAX_POLLING_TIMEOUT_MS:
        key = 1234
        timeout = 0
      else:
        key = display_image_wait_key( image, POLLING_DURATION_MS )
      
      # wait for user input
      if key == LEFT_KEY:
        update = cv2.add(image, create_blank(image, RED))
        display_image_wait_key( update, POLLING_DURATION_MS)
        return key

      elif key == RIGHT_KEY:
        update = cv2.add(image, create_blank(image, GREEN))
        display_image_wait_key( update, POLLING_DURATION_MS)
        return key

      elif key == DOWN_KEY:
        update = cv2.add( image, create_blank( image, YELLOW ) )
        display_image_wait_key( update, POLLING_DURATION_MS )
        return key

      elif key == ESCAPE_KEY:
        return key

      elif key == BACKSPACE_KEY:
        return key

      elif key != -1:

        alpha = 0.3

        # image to review as backgorund and usage as foreground
        img1 = image
        img2 = cv2.imread(USAGE_IMG)

        img1 = resize_image(img1)
        img2 = resize_image(img2)

        print( img1.size, img2.size )
        image = cv2.addWeighted(img1,alpha,img2,1-alpha,0)

        display_image_wait_key( image, 0)

        key = -1
      
      elif key == -1:
        timeout += POLLING_DURATION_MS

def list_all_jpgs( directory ):
  jpeg_files = []    

  for root, dirs, files in os.walk(directory):
    for file in files:
      if file.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
        jpeg_files.append( os.path.join(root, file) )

  return jpeg_files


def user_label_images_single( snapcat_json, image_list ):  
  # TODO: there's a lot of duplicated code here, maybe function pointers?
  ######################### sort individual files #########################

  done = False
  index = 0

  while not done: 
    image = image_list[index]
    image_name = os.path.basename(image)
    
    key = disp_image_get_input( image )
    
    if key == LEFT_KEY:
      snapcat_json.update( image_name, "user_label", INVALID_STRING)
      snapcat_json.save()
      index = index + 1

    elif key == RIGHT_KEY:
      snapcat_json.update( image_name, "user_label", VALID_STRING)
      snapcat_json.save()
      index = index + 1

    elif key == DOWN_KEY:
      snapcat_json.update( image_name, "user_label", UNSURE_STRING)
      snapcat_json.save()
      index = index + 1

    elif key == BACKSPACE_KEY:
      # ensure we don't go negative with the index
      if ( index > 0 ):
        index = index - 1      

    elif key == ESCAPE_KEY:
      cv2.destroyAllWindows()
      done = True
    
    if index >= len(image_list):
      done = True

  cv2.destroyAllWindows()
    

def user_label_images_burst( burst_dir, outdir_blob ):  
  """
  ######################### sort image bursts #########################
  
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

    # todo add timeout that displays usage picture if no input for 2 mins. Display for a max of 30 sec and then continue
    """
  
def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--image_dir", help="will list all the images within this directory and have user label them")
  parser.add_argument("--json_dir", help="path tho the json database for images" )

  args = parser.parse_args()
  

  snapcat_json = json_database.JSONDatabase( args.json_dir )
  image_list = list_all_jpgs ( args.image_dir )

  user_label_images_single( snapcat_json, image_list )

if __name__ == "__main__":
  main()