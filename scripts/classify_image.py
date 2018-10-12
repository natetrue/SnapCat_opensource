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

class SegmentClassifier:
  def __init__( self  ):

    self.model_file = settings.graph['graph']
    self.label_file = settings.graph['labels']
    self.input_height = settings.graph['input_height']
    self.input_width = settings.graph['input_width']
    self.input_mean = settings.graph['input_mean']
    self.input_std = settings.graph['input_std']
    self.input_layer = settings.graph['input_layer']
    self.output_layer = settings.graph['output_layer']

    graph = tools.load_graph(model_file)
    labels = tools.load_labels(label_file)

    self.sess = tf.Session(graph=graph)

  def __exit__(self):
    self.sess.close()

  def classify_segment( self, segmented_images ):

    for file in segmented_images:

      if not os.path.isfile(file):
        print("***************ERROR - File doesn't exist")
        continue

      cat_classification = False
      not_cat_classification = False
      unsure_classification = False
      current_burst = int(burst_num)

      t = tools.read_tensor_from_image_file( file,
                                             input_height = self.input_height,
                                             input_width  = self.input_width,
                                             input_mean   = self.input_mean,
                                             input_std    = self.input_std)

      # todo, suspect this is what's printing a lot of messages. Attempt to consolidate calls to this function
      results = sess.run( output_operation.outputs[0], 
                          { input_operation.outputs[0]: t } )
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
    # todo find some sort of enumeration rather than defining strings in both files
    if cat_classification:
      return "cat"
    elif not_cat_classification:
      return "not_cat"
    elif unsure_classification:
      return "unsure"
    else:
      return "Error, classification undefined"

if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument("--sorted_blob_directory", help="directory to place sorted blobs")
  parser.add_argument("--sorted_burst_directory", help="directory to place sorted bursts")
  parser.add_argument("--blob_directory", help="directory of blobs")  
  parser.add_argument("--burst_directory", help="directory of bursts") 
  args = parser.parse_args()

  sort_images(args.sorted_blob_directory, args.sorted_burst_directory, args.blob_directory, args.burst_directory)