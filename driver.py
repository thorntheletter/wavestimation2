#!/usr/bin/env python3
"""Driver script for the wavestimation experiments."""

import os
import pickle
import sys
import time

import sample
import algs
import evals
import config


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
    config.RESULTS_DIR = "results/" + time.strftime("%Y-%m-%d-%H:%M:%S")
    os.makedirs(config.RESULTS_DIR)
    config.RESULTS_DIR += "/"

    if config.VERBOSE:
        print("Loading Data")

    if len(sys.argv) != 1:
        samples = []
        for arg in sys.argv[1:]:
            try:
                samples.extend(sample.parse_json_file_list(arg))
            except TypeError:
                samp = sample.parse_json_sample_file(arg)
                if samp is not None:
                    samples.append(samp)

    else:
        try:
            samples = sample.parse_json_file_list(config.DEFAULT_FILENAME)
        except TypeError as e:
            print("error: incorrect json filename list")
            print(e)
            sys.exit(1)

    if config.VERBOSE:
        print("Running Estimation Algorithms")

    alg_res = []
    for alg in algs.algorithm_list:
        a_results = algs.AlgResultList(alg.__name__)
        a_results.r_list = list(map(alg, samples))
        alg_res.append(a_results)

    if config.VERBOSE:
        print("Running Evaluation algorithms")

    for eval_alg in evals.eval_list:
        for alg_result in alg_res:
            alg_result.e_list.append(eval_alg(alg_result.r_list))

    if config.VERBOSE:
        print("Preparing Results")

    for alg_result in alg_res:
        file = open(config.RESULTS_DIR + alg_result.a_name + '.txt', mode='w')
        file.write(alg_result.__repr__())
        file.close()

    file = open(config.RESULTS_DIR + "results.p", mode="wb")
    pickle.dump(alg_res, file)


if __name__ == '__main__':
    main()
