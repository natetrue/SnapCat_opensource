import os
import random
import tensorflow as tf

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

  if (x_length > y_length):
    if x_length > max_y:
      square_size = y_length
      affected_dimension = 'x'
      delta = abs(square_size - x_length)
    else:
      square_size = x_length
      affected_dimension = 'y'
      delta = abs(square_size - y_length)

  elif (y_length > x_length):

    if y_length > max_x:
      square_size = x_length
      affected_dimension = 'y'
      delta = abs(square_size - y_length)
    else:
      square_size = y_length
      affected_dimension = 'x'
      delta = abs(square_size - x_length)

  # Split up addition/subtraction on both sides of proposed subimage
  side_1 = int(round(delta / 2))
  side_2 = delta - side_1

  if affected_dimension == 'y':
    if square_size > y_length:
      if y1 < side_1:
        side_2 = side_2 + (side_1-y1)

        ret_y1 = 0
        ret_y2 = y2 + side_2

      elif (max_y - y2) > side_2:
        side_1 = side_1 + (side_2 - (max_y-y2))

        ret_y1 = y1 - side_1
        ret_y2 = max_y

      else:
        ret_y1 = y1 - side_1
        ret_y2 = y2 + side_2

    elif square_size < y_length:
      ret_y1 = y1 + side_1
      ret_y2 = y2 - side_2

  elif affected_dimension == 'x':
    if square_size > x_length:
      if x1 < side_1:
        side_2 = side_2 + (side_1-x1)

        ret_x1 = 0
        ret_x2 = x2 + side_2

      elif (max_x - x2) > side_2:
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