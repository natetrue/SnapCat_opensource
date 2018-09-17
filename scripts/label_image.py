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

def main():
  predicted_cat_actual_cat = 0
  predicted_cat_actual_NC = 0
  predicted_NC_actual_cat = 0
  predicted_NC_actual_NC = 0

  sort = False


  parser = argparse.ArgumentParser()
  parser.add_argument("--sorted_directory", help="directory to place sorted images")
  parser.add_argument("--unsorted_directory", help="directory of images to be sorted")  
  parser.add_argument('--sort', default=False, type=lambda x: (str(x).lower() == 'true'))
  args = parser.parse_args()

  model_file = settings.label_image['graph']
  dir_cat = settings.label_image['cat_directory']
  dir_NC = settings.label_image['NC_directory']
  label_file = settings.label_image['labels']
  input_height = settings.label_image['input_height']
  input_width = settings.label_image['input_width']
  input_mean = settings.label_image['input_mean']
  input_std = settings.label_image['input_std']
  input_layer = settings.label_image['input_layer']
  output_layer = settings.label_image['output_layer']

  if args.sorted_directory:
    dir_sorted = args.sorted_directory
  if args.unsorted_directory:
    dir_unsorted = args.unsorted_directory
  if args.sort:
    sort = True

  graph = load_graph(model_file)
  labels = load_labels(label_file)

  if sort:
    unsorted_files = []
    dir_sorted_cats = dir_sorted + '/cats/'
    dir_sorted_not_cats = dir_sorted + '/not_cats/'
    dir_unsure = dir_sorted + '/unsure/'

    # Find all JPG files 
    for (dirpath, dirnames, filenames) in walk(dir_unsorted):
      for file in filenames:
        if file.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
          head_1, tail_1 = os.path.split(dirpath)
          head_2, tail_2 = os.path.split(head_1)
          complete = os.path.join(tail_2, tail_1, file)
          #print(complete)
          unsorted_files.append(complete)

    # Create Full path
    for file_name in unsorted_files:

      unsorted_file_name = os.path.join(dir_unsorted, file_name)
      
      # create directories that don't exist
      if not os.path.exists(dir_sorted):
        os.makedirs(dir_sorted)
      if not os.path.exists(dir_sorted_cats):
        os.makedirs(dir_sorted_cats)
      if not os.path.exists(dir_sorted_not_cats):
        os.makedirs(dir_sorted_not_cats)
      if not os.path.exists(dir_unsure):
        os.makedirs(dir_unsure)

      t = read_tensor_from_image_file(
          unsorted_file_name,
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

      # get classification
      top_k = results.argsort()[-5:][::-1]
      for i in top_k:
          
          # if confidence level is below certain value, put in "unsure" folder
          if results[i] < settings.label_image['confidence_threshold']:
            unsure_file_destination = dir_unsure + file_name
            nested_directory, tail = os.path.split(unsure_file_destination)

            if not os.path.exists(nested_directory):
              os.makedirs(nested_directory)
            os.rename(unsorted_file_name, unsure_file_destination)

          # else, place it in the proper sorted folder
          else:
            if labels[i] == 'cats':
              sorted_file_destination = dir_sorted + '/cats/' + file_name
            else:
              sorted_file_destination = dir_sorted + '/not_cats/' + file_name

            nested_directory, tail = os.path.split(sorted_file_destination)

            if not os.path.exists(nested_directory):
              os.makedirs(nested_directory)
            os.rename(unsorted_file_name, sorted_file_destination)

          break

  # Same logic as above but no sorting. Produces classification accuracy metrics
  else:
    cat_files = [f for f in listdir(dir_cat) if isfile(join(dir_cat, f))]
    NC_files = []

    for (dirpath, dirnames, filenames) in walk(dir_NC):
      for file in filenames:
        if file.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
          NC_files.append(os.path.join(os.path.split(dirpath)[1], file))

    for cat_file_name in cat_files:
      cat_file_name = dir_cat + cat_file_name

      t = read_tensor_from_image_file(
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

      t = read_tensor_from_image_file(
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

def load_graph(model_file):
  graph = tf.Graph()
  graph_def = tf.GraphDef()

  with open(model_file, "rb") as f:
    graph_def.ParseFromString(f.read())
  with graph.as_default():
    tf.import_graph_def(graph_def)

  return graph

def printTensors(pb_file):

    # read pb into graph_def
    with tf.gfile.GFile(pb_file, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    # import graph_def
    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def)

    # print operations
    for op in graph.get_operations():
        print(op.name)


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


def load_labels(label_file):
  label = []
  proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
  for l in proto_as_ascii_lines:
    label.append(l.rstrip())
  return label


if __name__ == "__main__":
  main()