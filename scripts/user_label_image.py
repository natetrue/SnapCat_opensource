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
NONE_STRING = "none"
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


def update_image_label ( snapcat_json, image_name, label ):
  snapcat_json.update( image_name, "user_label", label )
  snapcat_json.save()


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
      update_image_label( snapcat_json, image_name, INVALID_STRING )
      index = index + 1

    elif key == RIGHT_KEY:
      update_image_label( snapcat_json, image_name, VALID_STRING )
      index = index + 1

    elif key == DOWN_KEY:
      update_image_label( snapcat_json, image_name, UNSURE_STRING )
      index = index + 1

    elif key == BACKSPACE_KEY:
      # ensure we don't go negative with the index
      if ( index > 0 ):
        index = index - 1      
      update_image_label( snapcat_json, image_name, NONE_STRING )
    elif key == ESCAPE_KEY:
      cv2.destroyAllWindows()
      done = True
    
    if index >= len(image_list):
      done = True

  cv2.destroyAllWindows()
    

#todo - duplicated in generate_report.py, move to tools
def get_bursts( json_data ):
  bursts = []
  for image in json_data:
    burst = json_data[image]["burst_images"]
    if not burst in bursts:
      bursts.append(burst)

  return bursts


def update_user_burst_label( snapcat_json, burst, label ):
  for image_name in burst:
    snapcat_json.update( image_name, "user_burst_label", label )
     
  snapcat_json.save()


def user_label_images_burst( snapcat_json ):
  ######################### sort image bursts #########################

  bursts = get_bursts( snapcat_json.json_data )

  done = False
  index = 0

  # Skip bursts that definitely contain a cat
  # only review bursts that have an unsure label
  unsure_bursts = []
  for burst in bursts:

    cat_detected = False
    unsure_label = False
    for image_name in burst:
      if snapcat_json.json_data[image_name]["classifier_label"] == "cat":
        cat_detected = True
        break

      if snapcat_json.json_data[image_name]["classifier_label"] == "unsure":
        unsure_label = True

    if cat_detected:
      continue
    elif unsure_label:
      unsure_bursts.append( burst )


  # iterate over all of the bursts and get a label
  while not done:
    image_list = []

    for image_name in unsure_bursts[index]:
      image_list.append( snapcat_json.json_data[image_name]["path"] )
      
    print( image_list )

    key = display_directory_get_input( image_list )
    
    if key == LEFT_KEY:
      update_user_burst_label( snapcat_json, unsure_bursts[index], INVALID_STRING)
      index = index + 1

    elif key == RIGHT_KEY:
      update_user_burst_label( snapcat_json, unsure_bursts[index], VALID_STRING)
      index = index + 1

    elif key == DOWN_KEY:
      update_user_burst_label( snapcat_json, unsure_bursts[index], UNSURE_STRING)
      index = index + 1

    elif key == BACKSPACE_KEY:
      # ensure we don't go negative with the index
      if ( index > 0 ):
        index = index - 1      

      update_user_burst_label( snapcat_json, unsure_bursts[index], NONE_STRING )

    elif key == ESCAPE_KEY:
      cv2.destroyAllWindows()
      done = True
    
    if index >= len(unsure_bursts):
      done = True

  cv2.destroyAllWindows()
  

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--image_dir", help="will list all the images within this directory and have user label them", default="")
  parser.add_argument("--json_dir", help="path to the json database for images" )
  parser.add_argument("--gif", help="display all images from burst or not", default="false" )

  args = parser.parse_args()
  

  snapcat_json = json_database.JSONDatabase( args.json_dir )
  image_list = list_all_jpgs ( args.image_dir )

  print( "gif", args.gif.lower() )
  if args.gif.lower() == "true":
    user_label_images_burst( snapcat_json )
  else:
    user_label_images_single( snapcat_json, image_list )

if __name__ == "__main__":
  main()