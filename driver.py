#!/usr/bin/env python3
"""Driver script for the wavestimation experiments."""

import json
import pickle
import os
import sys
import time
import wave
import numpy as np

import algs
import evals

DEFAULT_FILENAME = "data/masterlist.json"
VERBOSE = False
FLOAT = 'float64'
files_dict = {}


def main():
    """Strings all seperate parts together and handles file IO.

    If it has no arguments, runs on a default sample JSON list file.
    If it has one argument, it is a sample list JSON file to run it on.
    If it has more than one argument,
    they can be either sample or sample list JSON files.

    Runs all of the algorithms in algs.algorithm_list on all of the samples,
    then runs evals.eval_list on all of them.

    Results go in a directory in the results named after the current time.

    """
    results_dir = "results/" + time.strftime("%Y-%m-%d-%H:%M:%S")
    os.makedirs(results_dir)
    results_dir += "/"

    if len(sys.argv) != 1:
        samples = []
        for arg in sys.argv[1:]:
            try:
                samples.extend(parse_json_file_list(arg))
            except TypeError:
                samp = parse_json_sample_file(arg)
                if samp is not None:
                    samples.append(samp)

    else:
        try:
            samples = parse_json_file_list(DEFAULT_FILENAME)
        except TypeError as e:
            print("error: incorrect json filename list")
            print(e)
            sys.exit(1)

    alg_res = []
    for alg in algs.algorithm_list:
        a_results = algs.AlgResultList(alg.__name__)
        a_results.r_list = list(map(alg, samples))
        alg_res.append(a_results)

    for eval_alg in evals.eval_list:
        for alg_result in alg_res:
            alg_result.e_list.append(eval_alg(alg_result.r_list))

    for alg_result in alg_res:
        file = open(results_dir + alg_result.a_name, mode='w')
        file.write(alg_result.__repr__())
        file.close()

    file = open(results_dir + "results.p", mode="wb")
    pickle.dump(alg_res, file)


def parse_json_file_list(filename):
    """Parse JSON sample list file and returns list of samples."""
    if not os.path.exists(filename):
        print("error: file " + filename + " does not exist")
        sys.exit(1)

    file = open(filename)
    data = json.load(file)
    file.close()
    if (not isinstance(data, list) or
            any(map(lambda x: not isinstance(x, str), data))):
        raise TypeError

    json_list = map(parse_json_sample_file, data)

    return list(filter(lambda x: x is not None, json_list))


def parse_json_sample_file(filename):
    """Parse individual sample JSON file and returns Sample object."""
    if not os.path.exists(filename):
        return None

    file = open(filename)
    data = json.load(file)
    file.close()

    if 'name' in data:
        name = data['name']
    else:
        name = filename

    if isinstance(data['target'], str):  # wav
        target = data['target']
        if target not in files_dict.keys():
            frames = get_sound_data(target)
            files_dict[target] = frames
    else:  # array with numbers in it.
        target = normalize(np.array(data['target'], dtype=FLOAT))

    components = []
    for i, comp in enumerate(data['components']):
        if isinstance(comp, str):
            components.append(comp)
            if comp not in files_dict.keys():
                frames = get_sound_data(comp)
                files_dict[comp] = frames
        else:
            components.append(normalize(np.array(comp, dtype=FLOAT)))

    return Sample(name, target, components)


def get_sound_data(filename):
    """Return numpy array with the sound data in the file."""
    w = wave.open(filename)
    if w.getsampwidth() != 2:
        raise ValueError(filename + " sample width is not 16 bits")
    frames = w.readframes(w.getnframes())
    data = np.fromstring(frames, dtype='int16')
    data = np.reshape(data, (-1, w.getnchannels()))
    return normalize(collapse_channels(data))


def collapse_channels(data):
    """Convert multi-channel audio in a numpy array to mono."""
    _, n_channels = data.shape
    return np.sum(data / n_channels, axis=1, dtype=FLOAT)


def normalize(vector):
    """Normalize a vector into a unit vector."""
    if np.linalg.norm(vector) >= 0:
        return vector / np.linalg.norm(vector)
    return vector


def pad(v1, v2):
    """Pad vector ends with 0s if they are not the smae size."""
    if v1.size < v2.size:
            v1 = np.pad(v1, (0, v2.size - v1.size), 'constant')
    elif v2.size < v1.size:
        v2 = np.pad(v2, (0, v1.size - v1.size), 'constant')
    return v1, v2


class Sample():
    """Store a single sample to be operated on."""

    def __init__(self, name, target, components):
        """Initialize Sample class with sample name, target, and components."""
        self.s_name = name
        self.target = target
        self.components = components  # maybe check if these are valid

    def get_target(self):
        """Get target signal."""
        return self.get_signal(self.target)

    def get_signal(self, comp):
        """Return signal from signal or filename."""
        if isinstance(comp, str):
            return files_dict[comp]
        elif isinstance(comp, np.ndarray):
            return comp
        else:
            raise ValueError("component does not refer to proper signal")

    def comp_to_signal(self, i):
        """Covert index in components list to numpy array with signal."""
        return self.get_signal(self.components[i])


if __name__ == '__main__':
    main()
