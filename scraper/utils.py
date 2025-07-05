import json
import os

def read_json(path):
  data = None
  try:
    with open(path, "r") as file:
        data = json.load(file)
  except:
     print("Reading did not work")

  return data

def write_json(data, path):
  try:
    with open(path, "w") as file:
      json.dump(data, file, indent=4)
  except:
     print("Writing did not work")

def clear(path):
  os.remove(path=path)