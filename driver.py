#!/usr/bin/env python3
"""Driver script for the wavestimation experiments."""

import json
import pickle
import os
import sys
import time
import scipy.io.wavfile
import numpy as np

import algs
import evals

DEFAULT_FILENAME = "data/masterlist.json"
VERBOSE = False


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
        except TypeError:
            print("error: incorrect json filename list")
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

    jtarget = data['target']
    if isinstance(jtarget, str):  # wav
        _, frames = scipy.io.wavfile.read(data['target'])
        target = collapse_channels(frames)
    else:  # array with numbers in it.
        target = np.array(data['target'])

    components = np.zeros((len(data['components']), len(target)))
    for i, comp in enumerate(data['components']):
        if isinstance(comp, str):
            _, frames = scipy.o.wavfile.read(data['comp'])
            component = collapse_channels(frames)
            component.resize(len(target))
            components[i] = component
        else:
            component = np.array(comp)
            component.resize(len(target))
            components[i] = component

    return Sample(name, target, components)


def collapse_channels(data):
    """Convert multi-channel audio in a numpy array to mono."""
    _, n_channels = data.shape
    return np.sum(data // n_channels, axis=1, dtype=data.dtype)


class Sample():
    """Store a single sample to be operated on."""

    def __init__(self, name, target, components):
        """Initialize Sample class with sample name, target, and components."""
        self.name = name
        self.target = target
        self.components = components  # maybe check if these are valid


if __name__ == '__main__':
    main()
