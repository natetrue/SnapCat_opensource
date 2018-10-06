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

import argparse
import os
import burst
import segmentation
import sort_image
import user_label_image
import generate_report
import shutil
import datetime

def sort_camera_trap_images(unsorted_dir):

  #TODO create temproary directory that automatically deletes itself for all of these( https://docs.python.org/2/library/tempfile.html )
  root_dir =    os.path.dirname(unsorted_dir)
  burst_dir =   os.path.join( root_dir, "tmp_image_bursts" )
  segment_dir = os.path.join( root_dir, "tmp_segmented" )
  sorted_dir =  os.path.join( root_dir, "tmp_sorted" )
  report_dir =  os.path.join( root_dir, "tmp_report" )

  analysis_datetime = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M") 

  tmp_dirs = [burst_dir, segment_dir, sorted_dir, report_dir]
  for dirname in tmp_dirs:
    if os.path.isdir(dirname):
      print( "deleting: ", dirname )
      shutil.rmtree(dirname)


  ######################### burst.py #########################
  # sort images into bursts based on timestamp
  #TODO: don't move original image, if process gets interrupted this will cause issues for the user.
  #TODO: This takes forever. Pass names to the files instead of actually moving them. Should be < 1s operation
  nested_burst_dir = os.path.join( burst_dir, burst.create_bursts( unsorted_dir, burst_dir, analysis_datetime ) )


  ######################### segmentation.py #########################
  # Segment images based on movement
  segmentation.segment_images( nested_burst_dir, segment_dir, analysis_datetime )


  ######################## format.py #########################
  # TODO, format segmented images


  # ######################### sort.py #########################
  blob_dir = segment_dir
  sorted_burst_dir = os.path.join( sorted_dir, "bursts")
  sorted_blob_dir = os.path.join( sorted_dir, "blobs")
  sort_image.sort_images(sorted_blob_dir, sorted_burst_dir, blob_dir, burst_dir)


  ######################### user_label_image.py #########################
  #todo, add progress bar so that user knows how many images there are in a burst
  #todo - make sure to destroy window at the end. still popped up
  not_sure_dir = os.path.join( sorted_burst_dir, "unsure")
  not_sure_blob_dir = os.path.join( sorted_blob_dir, "unsure")
  user_label_image.user_label_images( not_sure_dir, not_sure_blob_dir, sorted_burst_dir, sorted_blob_dir, "true" ) # display images as bursts


  ######################### generate_report.py #########################
  sorted_cat_dir = os.path.join( sorted_burst_dir, "cats", analysis_datetime)
  generate_report.generate_report( sorted_cat_dir, report_dir )


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--unsorted_dir", help="directory containing camera images")
  
  args = parser.parse_args()
  
  sort_camera_trap_images( args.unsorted_dir)

