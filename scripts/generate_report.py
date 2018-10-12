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

def list_all_jpgs( directory ):
  jpeg_files = []

  for (dirpath, dirnames, filenames) in os.walk( directory):
    for file in filenames:
      if file.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
        jpeg_files.append( os.path.join( dirpath, file) )

  return jpeg_files

def generate_report( cat_dir, outdir ):

  # verify that there are images present
  try:
    camera_directories = next( os.walk( cat_dir ) )[1]
  except:
    camera_directories = []
  if len( camera_directories ) == 0:
    return

  cats_detected = dict()

  # iterate over all cameras within the cats detected folder
  for camera_directory in camera_directories:

    num_cats = 0

    # iterate over all the bursts in the camera directory
    burst_directories = next( os.walk( os.path.join( cat_dir, camera_directory ) ) )[1]

    # make sure there are bursts present
    if len( burst_directories ) > 0:

      # count all bursts in directory
      for burst_directory in burst_directories:
        
        # make sure burst has images
        jpegs_in_dir = list_all_jpgs( os.path.join( cat_dir, camera_directory, burst_directory ) )
        if len( jpegs_in_dir ) > 0:
          num_cats = num_cats + 1
    
    cats_detected[camera_directory] = num_cats
 
  # sort data alphabetically
  cameras = sorted( list( cats_detected.keys() ) )
  num_cats = []
  for camera in cameras:
    num_cats.append( cats_detected[camera] )

  # create plot  
  y_pos = np.arange( len(cameras) )
  plt.bar(y_pos, num_cats, align='center', alpha=0.5)
  plt.xticks(y_pos, cameras)
  plt.ylabel('Number of Cats')
  plt.title('Number of Cats Per Camera')
 
  # save and show plot
  if not os.path.isdir(outdir):
    os.makedirs(outdir)

  plt.savefig( os.path.join( outdir, 'report.png') )
  plt.show()

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--cat_dir", help="directory containing bursts classified as cat")
  parser.add_argument("--report", help="directory to store report")

  args = parser.parse_args()
  
  generate_report( args.cat_dir, args.report )

if __name__ == "__main__":
  main()