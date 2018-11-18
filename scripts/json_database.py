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
class JSONDatabase:
  
  def __init__(self, json_path):
    """ initialize the class by opening the json file and loading the data """
    self.json_path = json_path  
    self.load()

  
  def __exit__(self):
    """  upon exit saves the JSON file """
    self.save()


  def load(self):
    """ loads data from json file """
    if not os.path.isfile(self.json_path):
      self.json_data = dict()
      self.save()

    with open(self.json_path) as f:
      self.json_data = json.load(f)


  def save(self):
    """ saves data to json file """
    print("saving json file:", self.json_path)
    with open(self.json_path, 'w') as outfile:
      outfile.write( json.dumps(self.json_data, indent=2) )


  def update( self, image, parameter, value ):
    """ update json setting 

      args:
        image - name of file (excluding path) of the image the data pertains to
        parameter - name of the json setting to be updated
        value - the value to be stored for the parameter
    """

    # TODO: add special case for user labels in order to append 
    # rather than replace entry if it exists
    
    if not image in self.json_data:
      self.json_data[image] = { parameter: value }
    else:
      image_params = self.json_data[image]
      image_params[parameter] = value

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--json_path", help="directory of json database file")
  
  args = parser.parse_args()
  
  myJSON = JSONDatabase( args.json_path )
  myJSON.update("dummy_image", "path", "dummy_path\\dummy_folder")
  myJSON.save() # todo this should save as soon as we exit

  


