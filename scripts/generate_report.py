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
import numpy as np
import matplotlib.pyplot as plt
import json_database
import tools

def generate_report( snapcat_json, outdir ):

  bursts = tools.get_bursts( snapcat_json )

  cats_detected = dict()

  for burst in bursts:
    
    cat_detected = False
    for image in burst:
      if tools.cat_label_exists( snapcat_json, image ):
        cat_detected = True 
        break

    image = burst[0]
    image_path = snapcat_json.json_data[image]["path"]
    image_directory = os.path.dirname(image_path)
    image_directory = os.path.split(image_directory)[-1]

    if not image_directory in cats_detected:
        cats_detected[image_directory] = 0

    if cat_detected:
      cats_detected[image_directory] = cats_detected[image_directory] + 1
 
  # sort data alphabetically
  num_cats = []
  for camera in cats_detected:
    num_cats.append( cats_detected[camera] )

  # create plot
  y_pos = np.arange( len(cats_detected) )
  plt.bar(y_pos, num_cats, align='center', alpha=0.5)
  plt.xticks(y_pos, cats_detected)
  plt.ylabel('Number of Cats')
  plt.title('Number of Cats Per Camera')
 
  # save and show plot
  if not os.path.isdir(outdir):
    os.makedirs(outdir)

  plt.savefig( os.path.join( outdir, 'report.png') )
  plt.show()

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--json_dir", help="path to the json database for images" )
  parser.add_argument("--report", help="directory to store report")

  args = parser.parse_args()
  
  snapcat_json = json_database.JSONDatabase( args.json_dir )

  generate_report( snapcat_json, args.report )