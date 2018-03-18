#!/usr/bin/env python3
"""Reconstruct result waves from pickle."""

import sys
import pickle
import wave
import numpy as np
import os

import sample
import config


def main():
    """Run when run as a script."""
    _, picfile, directory = sys.argv
    pic = pickle.load(open(picfile, 'rb'))
    os.makedirs(directory, exist_ok=True)
    if directory[-1] != '/':
        directory += '/'
    for alg in pic:
        for result in alg.r_list:
            params = process_files(result)
            # print(params)
            data = scaleup_floats(result.to_signal()).astype('int16')
            wfile = wave.open(directory +
                              alg.a_name + '-' +
                              result.s_name + '.wav',
                              'wb')
            wfile.setparams(params)
            wfile.writeframes(data.tostring())


def scaleup_floats(vector):
    """Scales up a floats vector so that the max element is int16_max."""
    m = np.max(vector)
    ratio = (2**15-1) / m
    return vector * ratio


def process_files(result):
    """Add files for result to dictionary."""
    add_dict(result.target)
    for c in result.components:
        add_dict(c)

    if isinstance(result.target, str):
        q = wave.open(result.target)
        r = q.getparams()
        q.close()
        return (1, 2, r[2], 0, 'NONE', 'not compressed')
    else:
        return (1, 2, 44100, 0, 'NONE', 'not compressed')


def add_dict(fname):
    """Add file to dictionary if fname is a string."""
    # print(fname)
    if isinstance(fname, str):  # wav
        if fname not in config.F_DICT.keys():
            frames = sample.get_sound_data(fname)
            config.F_DICT[fname] = frames


if __name__ == '__main__':
    main()
