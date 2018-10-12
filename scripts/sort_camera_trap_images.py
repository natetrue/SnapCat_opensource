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
import classify_image
import user_label_image
import generate_report
import shutil



def sort_camera_trap_images(unsorted_dir):

  #TODO create temproary directory that automatically deletes itself for all of these( https://docs.python.org/2/library/tempfile.html )
  root_dir =    os.path.dirname(unsorted_dir)
  burst_dir =   os.path.join( root_dir, "tmp_image_bursts" )
  segment_dir = os.path.join( root_dir, "tmp_segmented" )
  sorted_dir =  os.path.join( root_dir, "tmp_sorted" )
  report_dir =  os.path.join( root_dir, "tmp_report" )


  tmp_dirs = [burst_dir, segment_dir, sorted_dir, report_dir]
  for dirname in tmp_dirs:
    if os.path.isdir(dirname):
      print( "deleting: ", dirname )
      shutil.rmtree(dirname)


  ######################### burst.py #########################
  # sort images into bursts based on timestamp
  #TODO: don't move original image, if process gets interrupted this will cause issues for the user.
  #TODO: This takes forever. Pass names to the files instead of actually moving them. Should be < 1s operation
  camera_bursts = burst.create_bursts( unsorted_dir )

  # todo - re enable image_classifier = classify_image.SegmentClassifier()

  #TODO: progress bars happen a lot, create overall progress bar
  sorted_images_per_camera = dict()

  cat_bursts = []
  not_cat_bursts = []
  unsure_bursts = []

  for camera in camera_bursts:
    print(camera)
    camera_burst = camera_bursts[camera]

    for burst_images in camera_burst:
      # Segment images based on movement
      # todo probably rename to motion detect
      segmented_images = segmentation.segment_images( burst_images, save_image=False )

      # todo make a class for sort_images to avoid calling multiple instances of graph init
      # todo rename sort to classify
      # todo - re enable  classification = image_classifier.classify_segment( segmented_images )
      classification = "unsure" # todo remove

      if classification == "cat":
        cat_bursts += camera_burst
      elif classification == "not_cat":
        not_cat_bursts += camera_burst 
      elif classification == "unsure":
        unsure_bursts += camera_burst
      else:
        print("Undefined classification:", classification )

  user_labeled_cat_bursts, user_labeled_not_cat_bursts, unsure_bursts = user_label_image.user_label_images( unsure_bursts )
  cat_bursts += user_labeled_cat_bursts
  not_cat_bursts += user_labeled_not_cat_bursts

  print( "total_cat_bursts", cat_bursts )
  print( "total_not_cat_bursts", not_cat_bursts )
  print( "total_unsure_bursts", unsure_bursts )

  return # todo remove, break to avoid calling functions not yet modified for list variation

  # todo calculate the cat_bursts based on camera ( pull out of path )

  ######################### generate_report.py #########################
  sorted_cat_dir = os.path.join( sorted_dir, "cats", date_string)
  print( sorted_cat_dir ) # todo - date string corrupted
  generate_report.generate_report( sorted_cat_dir, report_dir )


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--unsorted_dir", help="directory containing camera images")
  
  args = parser.parse_args()
  
  sort_camera_trap_images( args.unsorted_dir)

