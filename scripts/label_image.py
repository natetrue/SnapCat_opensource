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

def main():
  predicted_cat_actual_cat = 0
  predicted_cat_actual_NC = 0
  predicted_NC_actual_cat = 0
  predicted_NC_actual_NC = 0

  sort = False


  parser = argparse.ArgumentParser()
  parser.add_argument("--sorted_directory", help="directory to place sorted images")
  parser.add_argument("--unsorted_directory", help="directory of images to be sorted")  
  args = parser.parse_args()

  model_file = settings.graph['graph']
  dir_cat = settings.label_image['cat_directory']
  dir_NC = settings.label_image['NC_directory']
  label_file = settings.graph['labels']
  input_height = settings.graph['input_height']
  input_width = settings.graph['input_width']
  input_mean = settings.graph['input_mean']
  input_std = settings.graph['input_std']
  input_layer = settings.graph['input_layer']
  output_layer = settings.graph['output_layer']

  if args.sorted_directory:
    dir_sorted = args.sorted_directory
  if args.unsorted_directory:
    dir_unsorted = args.unsorted_directory
  if args.sort:
    sort = True

  graph = tools.load_graph(model_file)
  labels = tools.load_labels(label_file)

  cat_files = [f for f in listdir(dir_cat) if isfile(join(dir_cat, f))]
  NC_files = []

  for (dirpath, dirnames, filenames) in walk(dir_NC):
    for file in filenames:
      if file.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
        NC_files.append(os.path.join(os.path.split(dirpath)[1], file))

  for cat_file_name in cat_files:
    cat_file_name = dir_cat + cat_file_name

    t = tools.read_tensor_from_image_file(
        cat_file_name,
        input_height=input_height,
        input_width=input_width,
        input_mean=input_mean,
        input_std=input_std)

    input_name = "import/" + input_layer
    output_name = "import/" + output_layer
    input_operation = graph.get_operation_by_name(input_name)
    output_operation = graph.get_operation_by_name(output_name)

    with tf.Session(graph=graph) as sess:
      results = sess.run(output_operation.outputs[0], {
          input_operation.outputs[0]: t
      })
    results = np.squeeze(results)
    print (cat_file_name)
    print (results)

    top_k = results.argsort()[-5:][::-1]
    for i in top_k:
      if labels[i] == 'cats':
        predicted_cat_actual_cat += 1
      else:
        predicted_NC_actual_cat += 1
      break

  for NC_file_name in NC_files:

    NC_file_name = dir_NC + NC_file_name

    t = tools.read_tensor_from_image_file(
        NC_file_name,
        input_height=input_height,
        input_width=input_width,
        input_mean=input_mean,
        input_std=input_std)

    input_name = "import/" + input_layer
    output_name = "import/" + output_layer
    input_operation = graph.get_operation_by_name(input_name)
    output_operation = graph.get_operation_by_name(output_name)

    with tf.Session(graph=graph) as sess:
      results = sess.run(output_operation.outputs[0], {
          input_operation.outputs[0]: t
      })
    results = np.squeeze(results)
    print (NC_file_name)
    print (results)

    top_k = results.argsort()[-5:][::-1]
    for i in top_k:
      if labels[i] == 'not_cats':
        predicted_NC_actual_NC += 1
      else:
        predicted_cat_actual_NC += 1
      break

  print("Predicted NC actual NC:%d" % predicted_NC_actual_NC)
  print("Predicted NC actual cat:%d" % predicted_NC_actual_cat)
  print("Predicted cat actual cat:%d" % predicted_cat_actual_cat)
  print("Predicted cat actual NC:%d" % predicted_cat_actual_NC)


def read_tensor_from_image_file(file_name,
                                input_height=299,
                                input_width=299,
                                input_mean=0,
                                input_std=255):
  input_name = "file_reader"
  output_name = "normalized"
  file_reader = tf.read_file(file_name, input_name)
  if file_name.endswith(".png"):
    image_reader = tf.image.decode_png(
        file_reader, channels=3, name="png_reader")
  elif file_name.endswith(".gif"):
    image_reader = tf.squeeze(
        tf.image.decode_gif(file_reader, name="gif_reader"))
  elif file_name.endswith(".bmp"):
    image_reader = tf.image.decode_bmp(file_reader, name="bmp_reader")
  else:
    image_reader = tf.image.decode_jpeg(
        file_reader, channels=3, name="jpeg_reader")
  float_caster = tf.cast(image_reader, tf.float32)
  dims_expander = tf.expand_dims(float_caster, 0)
  resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
  normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
  sess = tf.Session()
  result = sess.run(normalized)

  return result

if __name__ == "__main__":
  main()