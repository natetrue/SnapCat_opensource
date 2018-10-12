# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from os import listdir
from os.path import isfile, join, split
from os import walk
import os

import argparse

import numpy as np
import tensorflow as tf

import settings
import tools
import shutil

def move_image_folder(segmentation_datetime, trap_name, burst_num, current_burst,
                      cat_classification, unsure_classification, not_cat_classification):
  global dir_burst_sorted
  global dir_blob_sorted
  global dir_burst
  global dir_blob

  dir_burst_new = ''
  dir_burst_old = ''
  dir_blob_new = ''
  dir_blob_old = ''

  # If one image contains cat, move whole burst to Cat folder
  if cat_classification:
    dir_burst_new = os.path.join(dir_burst_sorted, 'cats', segmentation_datetime, trap_name)
    dir_blob_new = os.path.join(dir_blob_sorted, 'cats', segmentation_datetime, trap_name)

  # If any image is unsure, then move to Unsure folder
  elif unsure_classification:
    dir_burst_new = os.path.join(dir_burst_sorted, 'not_cats', segmentation_datetime, trap_name)
    dir_blob_new = os.path.join(dir_blob_sorted, 'not_cats', segmentation_datetime, trap_name)

  # If all images have been labeled as not_cat, move to not_cat folder
  else:
    dir_burst_new = os.path.join(dir_burst_sorted, 'unsure', segmentation_datetime, trap_name)
    dir_blob_new = os.path.join(dir_blob_sorted, 'unsure', segmentation_datetime, trap_name)

  if not os.path.exists(dir_burst_new):
    os.makedirs(dir_burst_new)

  if not os.path.exists(dir_blob_new):
    os.makedirs(dir_blob_new)

  dir_burst_old = os.path.join(dir_burst, segmentation_datetime, trap_name, str(current_burst))
  dir_blob_old = os.path.join(dir_blob, segmentation_datetime, trap_name, str(current_burst))

  try:
    shutil.move(dir_burst_old, dir_burst_new)
  except:
    print("***************ERROR - can't move: ", dir_burst_old)
    print("Check this just in case: ", dir_burst_new)

  try:
    shutil.move(dir_blob_old, dir_blob_new)
  except:
    print("***************ERROR - can't move: ", dir_blob_old)
    print("Check this just in case: ", dir_blob_new)


def sort_images(sorted_blob_directory, sorted_burst_directory, blob_directory, burst_directory):

  global dir_burst_sorted
  global dir_blob_sorted
  global dir_burst
  global dir_blob

  current_burst = 0
  first_burst = True
  cat_classification = False
  not_cat_classification = False
  unsure_classification = False

  model_file = settings.graph['graph']
  label_file = settings.graph['labels']
  input_height = settings.graph['input_height']
  input_width = settings.graph['input_width']
  input_mean = settings.graph['input_mean']
  input_std = settings.graph['input_std']
  input_layer = settings.graph['input_layer']
  output_layer = settings.graph['output_layer']

  if sorted_blob_directory:
    dir_blob_sorted = sorted_blob_directory
  if sorted_burst_directory:
    dir_burst_sorted = sorted_burst_directory
  if blob_directory:
    dir_blob = blob_directory
  if burst_directory:
    dir_burst = burst_directory

  graph = tools.load_graph(model_file)
  labels = tools.load_labels(label_file)

  unsorted_files = []
  previous_file = ''

  # Find all JPG files 
  for (dirpath, dirnames, filenames) in walk(dir_blob):
    for file in filenames:
      if file.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
        complete = os.path.join(dirpath, file)
        unsorted_files.append(complete)

  # Create Full path
  # todo, should this be outside the loop, one TF session and then parse all the images?
  with tf.Session(graph=graph) as sess:

    for file in unsorted_files:

      if not os.path.isfile(file):
        print(file)
        print("***************ERROR - File doesn't exist")
        continue

      segmentation_datetime, trap_name, burst_num, file_name =  tools.get_image_info(file)

      if first_burst:
        current_burst = int(burst_num)
        print(current_burst)
        first_burst = False

      if not current_burst == int(burst_num):

        move_image_folder(segmentation_datetime, trap_name, burst_num, current_burst,
                        cat_classification, unsure_classification, not_cat_classification)

        cat_classification = False
        not_cat_classification = False
        unsure_classification = False
        current_burst = int(burst_num)

      previous_file = file

      t = tools.read_tensor_from_image_file(
          file,
          input_height=input_height,
          input_width=input_width,
          input_mean=input_mean,
          input_std=input_std)

      input_name = "import/" + input_layer
      output_name = "import/" + output_layer
      input_operation = graph.get_operation_by_name(input_name)
      output_operation = graph.get_operation_by_name(output_name)

      # todo, suspect this is what's printing a lot of messages. Attempt to consolidate calls to this function
      results = sess.run(output_operation.outputs[0], {
          input_operation.outputs[0]: t
      })
      results = np.squeeze(results)

      # get classification
      top_k = results.argsort()[-5:][::-1]
      for i in top_k:
          
          # if confidence level is below certain value, put in "unsure" folder
          if results[i] < settings.sort_image['confidence_threshold']:
            unsure_classification = True
          # else, place it in the proper sorted folder
          else:
            if labels[i] == 'cats':
              cat_classification = True
            else:
              not_cat_classification = True

          break

  # Final Burst needs to be sorted
  segmentation_datetime, trap_name, burst_num, file_name =  tools.get_image_info(file)
  move_image_folder(segmentation_datetime, trap_name, burst_num, current_burst,
                      cat_classification, unsure_classification, not_cat_classification)

if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument("--sorted_blob_directory", help="directory to place sorted blobs")
  parser.add_argument("--sorted_burst_directory", help="directory to place sorted bursts")
  parser.add_argument("--blob_directory", help="directory of blobs")  
  parser.add_argument("--burst_directory", help="directory of bursts") 
  args = parser.parse_args()

  sort_images(args.sorted_blob_directory, args.sorted_burst_directory, args.blob_directory, args.burst_directory)