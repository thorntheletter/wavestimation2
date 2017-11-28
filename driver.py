#!/usr/bin/env python3

import json
import numpy as np
import os
import sys
import wave

DEFAULT_FILENAME = "samplefiles.json"

def main():
  if len(sys.argv) != 1:
    samples = []
    for arg in sys.argv[1:]:
      try:
        samples.extend(parse_json_file_list(arg))
      except TypeError:
        sample = parse_json_sample_file(arg)
        if sample != None:
          samples.append(sample)

  else:
    try:
      samples = parse_json_file_list(DEFAULT_FILENAME)
    except (TypeError):
      print("error: incorrect json filename list")
      sys.exit(1)
    # except (FileNotFoundError):
    #   print("error: file \"" + DEFAULT_FILENAME + "\" does not exist")
    #   sys.exit(1)
    return samples



def parse_json_file_list(filename):
  if(not os.path.exists(filename)):
    print("error: file " + filename + " does not exist")
    sys.exit(1)

  file = open(filename)
  data = json.load(file)
  file.close()
  if(type(data) != list or any(map(lambda x: type(x) != str, data))):
    raise TypeError

  json_list = map(parse_json_sample_file, data)

  return list(filter(lambda x: x != None, json_list))


def parse_json_sample_file(filename):
  if(not os.path.exists(filename)):
    return None

  file = open(filename)
  data = json.load(file)
  file.close()

  if 'name' in data:
    name = data['name']
  else:
    name = filename

  jtarget = data['target']
  if type(jtarget) == str: #16 bit wav, maybe check for other widths / types
    target_file = wave.open(data['target'])
    frames = target_file.readframes(target_file.getnframes())
    target = np.fromstring(frames, dtype = 'int16')
    target_file.close()
  else: #string with numbers in it
    target = np.array(data['target'])

  components = np.zeros((len(data['components']), len(target)))
  for i, c in enumerate(data['components']):
    if type(c) == str:
      component_file = wave.open(c)
      frames = component_file.readframes(component_file.getnframes())
      component = np.fromstring(frames, dtype = 'int16')
      component.resize(len(target))
      components[i] = component
      component_file.close()
    else:
      component = np.array(c)
      component.resize(len(target))
      components[i] = component

  return sample(name, target, components)



class sample():
  def __init__(self, name, target, components):
    self.name = name
    self.target = target
    self.components = components #maybe check if these are valid


#untested: wav files, commandline arguments



#load json lists of json
#load samples from json files

#run every algorithm on every sample
#run evaluations on every output
#put output into files

if __name__ == '__main__':
  main()