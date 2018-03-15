"""Module for storing samples."""
import json
import numpy as np
import os
import sys
import wave

FLOAT = 'float64'
files_dict = {}


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
    vector = np.trim_zeros(vector)
    if np.linalg.norm(vector) >= 0:
        return vector / np.linalg.norm(vector)
    return vector


def pad(v1, v2):
    """Pad vector ends with 0s if they are not the smae size."""
    if v1.size < v2.size:
        v1 = np.pad(v1, (0, v2.size - v1.size), 'constant')
    elif v2.size < v1.size:
        v2 = np.pad(v2, (0, v1.size - v2.size), 'constant')
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
