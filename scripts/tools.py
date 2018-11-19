"""
███████╗███╗   ██╗ █████╗ ██████╗  ██████╗ █████╗ ████████╗
██╔════╝████╗  ██║██╔══██╗██╔══██╗██╔════╝██╔══██╗╚══██╔══╝
███████╗██╔██╗ ██║███████║██████╔╝██║     ███████║   ██║   
╚════██║██║╚██╗██║██╔══██║██╔═══╝ ██║     ██╔══██║   ██║   
███████║██║ ╚████║██║  ██║██║     ╚██████╗██║  ██║   ██║   
╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝      ╚═════╝╚═╝  ╚═╝   ╚═╝                  
"""
import os
import random
import tensorflow as tf
import argparse
import json_database
import cv2
from skimage import img_as_ubyte
from shutil import copyfile


def optimal_square(x1,x2,y1,y2,i):
  max_x = i.shape[1]
  max_y = i.shape[0]

  ret_x1 = x1
  ret_x2 = x2
  ret_y1 = y1
  ret_y2 = y2

  x_length = x2-x1
  y_length = y2-y1
  square_size = 0
  affected_dimension = ''

  side_1 = 0
  side_2 = 0
  delta = 0

  #print( x1, x2, y1, y2 )
  #print( max_x, max_y)

  #width is bigger than height
  if( x_length == y_length):
    return x1, x2, y1, y2

  elif (x_length > y_length):

    #reducing x 
    if x_length > max_y:
      square_size = max_y
      affected_dimension = 'x'
      ret_y1 = 0
      ret_y2 = max_y
      delta = abs(square_size - x_length)
    
    # increasing y to x_length
    else:
      square_size = x_length
      affected_dimension = 'y'
      delta = abs(square_size - y_length)
      #print("hooray")

  #height is bigger than width
  elif (y_length > x_length):

    # reducing y and extending x
    if y_length > max_x:
      square_size = max_x
      affected_dimension = 'y'
      ret_x1 = 0
      ret_x2 = max_x
      delta = abs(square_size - y_length)

    # extending x to y_length
    else:
      square_size = y_length
      affected_dimension = 'x'
      delta = abs(square_size - x_length)

  # Split up addition/subtraction on both sides of proposed subimage
  side_1 = int(round(delta / 2))
  side_2 = delta - side_1
  #print("side 1 should be 4 - it is: ", side_1)
  #print("side 2 should be 3 - it is: ", side_2)

  #print("square size:", square_size)
  #print(" y_length:", y_length)
  if affected_dimension == 'y':

    # attempting to extend y
    if square_size > y_length:
      if y1 < side_1:
        side_2 = side_2 + (side_1-y1)

        ret_y1 = 0
        ret_y2 = y2 + side_2

      elif (side_2 + y2) > max_y:
        side_1 = side_1 + (side_2 - (max_y-y2))

        ret_y1 = y1 - side_1
        ret_y2 = max_y

      else:
        ret_y1 = y1 - side_1
        ret_y2 = y2 + side_2

        #print("ret_y1 should be 425 - it s: ", ret_y1)
        #print("ret_y2 should be 740 - it s: ", ret_y2)

    elif square_size < y_length:
      ret_y1 = y1 + side_1
      ret_y2 = y2 - side_2

  elif affected_dimension == 'x':
    if square_size > x_length:
      if x1 < side_1:
        side_2 = side_2 + (side_1-x1)

        ret_x1 = 0
        ret_x2 = x2 + side_2

      elif (side_2 + x2) > max_x:
        side_1 = side_1 + (side_2 - (max_x-x2))

        ret_x1 = x1 - side_1
        ret_x2 = max_x

      else:
        ret_x1 = x1 - side_1
        ret_x2 = x2 + side_2

    elif square_size < x_length:
      ret_x1 = x1 + side_1
      ret_x2 = x2 - side_2


  return int(ret_x1), int(ret_x2), int(ret_y1), int(ret_y2)

def random_coords(img):
  height, width = img.shape[:2]
  crop_height = 224
  crop_width = 224

  if height < 224:
    crop_height = height

  if width < 224:
    crop_width = width

  max_height_start = random.randint(0, height - crop_height)
  max_width_start = random.randint(0, width - crop_width)

  return max_height_start, max_width_start

def get_image_info(imagepath):
  head_1, filename = os.path.split(imagepath)
  head_2, burst_num = os.path.split(head_1)
  head_3, trap_name = os.path.split(head_2)
  head_4, segmentation_datetime = os.path.split(head_3)

  return (segmentation_datetime, trap_name, burst_num, filename)

def load_labels(label_file):
  label = []
  proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
  for l in proto_as_ascii_lines:
    label.append(l.rstrip())
  return label

def load_graph(model_file):
  graph = tf.Graph()
  graph_def = tf.GraphDef()

  with open(model_file, "rb") as f:
    graph_def.ParseFromString(f.read())
  with graph.as_default():
    tf.import_graph_def(graph_def)

  return graph

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


# save areas of interest 
def save_areas_of_interest( snapcat_json, output_directory ):
  for image in snapcat_json.json_data:

    image_path = snapcat_json.json_data[image]["path"]
    area_of_interest = snapcat_json.json_data[image]["area_of_interest"]

    img = cv2.imread(image_path)

    x1 = area_of_interest[0]
    x2 = area_of_interest[1]
    y1 = area_of_interest[2]
    y2 = area_of_interest[3]

    img = img[y1:y2 , x1:x2, :]
    
    
    """
    # for debugging
    cv2.imshow('image',img)
    cv2.waitKey(0)
    return
    """

    resized_image = cv2.resize(img, (224, 224))
    
    
    if not os.path.isdir(output_directory):
      os.makedirs(output_directory)

    outfile = os.path.join(output_directory, image )

    resized_image = img_as_ubyte(resized_image)
    cv2.imwrite(outfile, resized_image)
    cv2.destroyAllWindows()

def get_bursts( snapcat_json ):

  bursts = []
  for image in snapcat_json.json_data:
    burst = snapcat_json.json_data[image]["burst_images"]
    if not burst in bursts:
      bursts.append(burst)

  return bursts


def move_burst_images( images, directory, burst_number ):
  for image_path in images:

    image_directory = os.path.dirname( image_path )
    image_name = os.path.basename( image_path )

    new_image_path = os.path.join( directory, image_directory, burst_number, image_name )
    new_image_dir = os.path.dirname( new_image_path )

    if not os.path.isdir( new_image_dir ):
      os.makedirs( new_image_dir )

    copyfile(image_path, new_image_path)


def cat_label_exists( snapcat_json, image ):
  if "classifier_label" in snapcat_json.json_data[image] and snapcat_json.json_data[image]["classifier_label"] == "cat" :
    return True
  
  if "user_label" in snapcat_json.json_data[image] and snapcat_json.json_data[image]["user_label"] == "cat" :
    return True

  if "user_burst_label" in snapcat_json.json_data[image] and snapcat_json.json_data[image]["user_burst_label"] == "cat" :
    return True

  return False

def unsure_label_exists( snapcat_json, image ):
  if "classifier_label" in snapcat_json.json_data[image] and snapcat_json.json_data[image]["classifier_label"] != "unsure" :
    return False

  # not unsure if user has labeled one way or the other
  if "user_label" in snapcat_json.json_data[image] and snapcat_json.json_data[image]["user_label"] == "cat" :
    return False

  if "user_label" in snapcat_json.json_data[image] and snapcat_json.json_data[image]["user_label"] == "not_cat" :
    return False

  if "user_burst_label" in snapcat_json.json_data[image] and snapcat_json.json_data[image]["user_burst_label"] == "cat" :
    return False

  if "user_burst_label" in snapcat_json.json_data[image] and snapcat_json.json_data[image]["user_burst_label"] == "not_cat" :
    return False
    
  # user label does not exist or is also unsure
  return True

# Save a copy of original images in an organized directory
def organize_images( snapcat_json, output_directory ):
  
  cat_dir = os.path.join(output_directory, "cat")
  not_cat_dir = os.path.join(output_directory, "not_cat")
  unsure_dir = os.path.join(output_directory, "unsure")

  bursts = get_bursts( snapcat_json )
  burst_number = 0
  for burst in bursts:

    image_list = []

    for image_name in burst:
      image_list.append( snapcat_json.json_data[image_name]["path"] )

    cat_detected = False
    unsure_label = False
    for image_name in burst:
      if cat_label_exists( snapcat_json, image_name ):
        cat_detected = True
        break

      if unsure_label_exists( snapcat_json, image_name):
        unsure_label = True

    out_dir = ""

    if cat_detected:
      out_dir = cat_dir
    elif unsure_label:
      out_dir = unsure_dir
    else:
      out_dir = not_cat_dir

    move_burst_images( image_list, out_dir, str( burst_number ) )

    burst_number += 1
  

    

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--json_dir", help="path to the json database for images" )
  parser.add_argument("--out_dir", help="path to save images" )
  
  args = parser.parse_args()

  snapcat_json = json_database.JSONDatabase( args.json_dir )

  organize_images( snapcat_json, args.out_dir )