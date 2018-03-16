"""Module for storing the estimation algorithms used in driver.py."""

import numpy as np
import multiprocessing as mp
import scipy.signal

import sample
import config


def matching_pursuit2_mp(samp):
    """
    Run matching pursuit, with time shifted signals in the dictionary.

    Convolution again, but this time multiprocess because I am impatient.
    """
    if config.VERBOSE:
        print("Matching Pursuit on " + samp.s_name)

    if config.PLOT:
        plotfile = open(config.RESULTS_DIR +
                        "matching_pursuit2-" +
                        samp.s_name +
                        ".txt", 'w')

    R = samp.get_target()
    ret = []
    maxinn = 1
    itt = 1
    while np.abs(maxinn) > 0 and itt <= config.N_SIGNALS:
        if config.VERBOSE:
            print("\tChoosing Signal " + str(itt))

        maxinn = 0
        mp_args = [(R, samp, i) for i in range(len(samp.components))]
        p = mp.Pool(config.POOL_SIZE)
        processresults = p.starmap(_matching_pusuit2_mp_in, mp_args)

        maxres = max(processresults, key=lambda x: np.abs(x[2]))

        g = np.pad(samp.comp_to_signal(maxres[0]), (maxres[1], 0), 'constant')
        g = g * maxres[2]
        R, g = sample.pad(R, g)
        R = R - g
        R = np.trim_zeros(R, 'b')
        if config.PLOT:
            plotfile.write(str(1 - np.linalg.norm(R)) + "\n")
        ret.append(maxres)
        itt += 1
        maxinn = maxres[2]
    return AlgResult(samp, ret)


def _matching_pusuit2_mp_in(R, samp, i):
    f = samp.comp_to_signal(i)
    inners = scipy.signal.fftconvolve(R, f[::-1], 'full')[f.size - 1:]
    offset = np.argmax(np.abs(inners))
    a = inners[offset]

    return (i, offset, a)


def matching_pursuit2(samp):
    """
    Run matching pursuit, with time shifted signals in the dictionary.

    Imagine if I didn't forget about the convolution theorem
    and cross correlation when it is overly relevent.

    Normal test stop condition doesn't currently work
    because of floating point errors;
    need new one, but this is good enough to test for time
    """
    if config.VERBOSE:
        print("Matching Pursuit on " + samp.s_name)

    if config.PLOT:
        plotfile = open(config.RESULTS_DIR +
                        "matching_pursuit2-" +
                        samp.s_name +
                        ".txt", 'w')

    R = samp.get_target()
    ret = []
    maxinn = 1
    itt = 1
    while np.abs(maxinn) > 0 and itt <= config.N_SIGNALS:
        if config.VERBOSE:
            print("\tChoosing Signal " + str(itt))

        maxinn = 0
        maxres = (-1, -1, -1)
        for i, s in enumerate(samp.components):
            f = samp.get_signal(s)
            # convolving with 2nd arg reversed is cross correlation
            # cross correlation essentially sliding dot product
            inners = scipy.signal.fftconvolve(R, f[::-1], 'full')[f.size - 1:]
            offset = np.argmax(np.abs(inners))
            a = inners[offset]
            if np.abs(a) < np.abs(maxinn):
                continue
            maxinn = a
            maxres = (i, offset, a)

        g = np.pad(samp.comp_to_signal(maxres[0]), (maxres[1], 0), 'constant')
        g = g * maxres[2]
        R, g = sample.pad(R, g)
        R = R - g
        R = np.trim_zeros(R, 'b')
        if config.PLOT:
            plotfile.write(str(1 - np.linalg.norm(R)) + "\n")

        ret.append(maxres)
        itt += 1
    return AlgResult(samp, ret)


def matching_pursuit(samp):
    """
    Run matching pursuit, with time shifted signals in the dictionary.

    Abandoned because too slow, not fully tested.
    """
    R = samp.get_target()
    ret = []
    maxinn = 1
    while maxinn > 0:
        print("iter: " + str(len(ret)))
        maxinn = 0
        maxres = (-1, -1, -1)
        for i, s in enumerate(samp.components):
            print("file: " + str(i))
            for offset in range(len(R)):
                f = np.pad(samp.comp_to_signal(i), (offset, 0), 'constant')
                f, R = sample.pad(f, R)
                a = np.inner(R, f)  # np.inner uses dot product
                if(np.abs(a) < maxinn):
                    continue
                maxinn = a
                maxres = (i, offset, a)

        g = np.pad(samp.comp_to_signal(maxres[0]), (maxres[1], 0), 'constant')
        g = g * maxres[2]
        g, R = sample.pad(g, R)
        R = R - g
        R = np.trim_zeros(R, 'b')
        ret.append(maxres)
    return AlgResult(samp, ret)


def matching_pursuit_mp(samp):
    """
    Run matching pursuit, with time shifted signals in the dictionary.

    Abandoned because too slow, not fully tested.

    """
    R = samp.get_target()
    ret = []
    maxinn = 1
    while maxinn > 0:
        print("iter: " + str(len(ret)))
        maxinn = 0
        maxres = (-1, -1, -1)
        mp_args = [(R, samp, i) for i in range(len(samp.components))]
        p = mp.Pool(config.POOL_SIZE)
        processresults = p.imap(_matching_pusuit_mp_in, mp_args)

        maxres = max(processresults, key=lambda x: x[2])
        g = np.pad(samp.comp_to_signal(maxres[0]), (maxres[1], 0), 'constant')
        g = g * maxres[2]
        R, g = sample.pad(R, g)
        R = R - g
        R = np.trim_zeros(R, 'b')
        ret.append(maxres)
    return AlgResult(samp, ret)


def _matching_pusuit_mp_in(args):
    target, samp, i = args
    maxinn = 0
    sig = samp.comp_to_signal(i)
    for offset in range(len(target)):
        f = np.pad(sig, (offset, 0), 'constant')
        f, R = sample.pad(f, target)
        a = np.inner(R, f)  # np.inner uses dot product
        if(np.abs(a) < maxinn):
            continue
        maxinn = a
        maxres = (i, offset, a)

    return maxres


def testo(samp):
    """Test dummy function."""
    return AlgResult(samp, [(0, 0, 1)])


def testo2(samp):
    """Test dummy function."""
    return AlgResult(samp, "not as good result")


algorithm_list = [matching_pursuit2_mp]


class AlgResult(sample.Sample):
    """Stores and displays a result from an estimation algorithm."""

    def __init__(self, sample, a_result):
        """Initialize AlgResult with Sample and result."""
        self.s_name = sample.s_name
        self.target = sample.target
        self.components = sample.components
        self.a_result = a_result

    def __repr__(self):
        """Display the AlgResult as a string."""
        ret = "SAMPLE NAME:        "
        ret += self.s_name + "\n"
        ret += "SAMPLE RESULT:\n"
        ret += self.a_result.__repr__()
        return ret

    def to_signal(self):
        """Use the components and result from to create the result signal."""
        signal = np.ndarray((0))
        for c in self.a_result:
            s = np.pad(self.comp_to_signal(c[0]), (c[1], 0), 'constant') * c[2]
            signal, s = sample.pad(signal, s,)
            signal += s
        return signal


class AlgResultList():
    """Stores all results & evaluations of a single estimation algorithm."""

    def __init__(self, name):
        """Initialize AlgResultList with algorithm name."""
        self.a_name = name
        self.r_list = []
        self.e_list = []

    def __repr__(self):
        """Display the AkgResultList as a string."""
        ret = "ALGORITHM NAME:     "
        ret += self.a_name + "\n\n"
        ret += "SAMPLE RESULTS--------------------------\n\n"
        for result in self.r_list:
            ret += result.__repr__() + "\n\n"
        ret += "EVAL RESULTS----------------------------\n\n"
        for e_result in self.e_list:
            ret += e_result.__repr__() + "\n\n"
        return ret
