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

import json
import argparse
import os
from json_database import JSONDatabase

def update_json_path(json_path, image_dir):
	myJSON = JSONDatabase( json_path )

	for path, _, files in os.walk( image_dir ):

		for filename in files:

			# only work with JPG 
			if not filename.endswith(('.jpg', '.jpeg', '.JPG', '.JPEG')):
			    continue

			file_path = os.path.join(path, filename)
			myJSON.update(filename, "path", file_path )
			print (file_path)

	myJSON.save()



if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--json_path", help="directory of json database file")
  parser.add_argument("--image_dir", help="directory of images to update path for")
  
  args = parser.parse_args()
  
  update_json_path( args.json_path, args.image_dir )
