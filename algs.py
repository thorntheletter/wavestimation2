"""Module for storing the estimation algorithms used in driver.py."""

import numpy as np
import multiprocessing as mp

import sample

# p = mp.Pool(mp.cpu_count())
# p = mp.Pool(1)


def matching_pursuit(samp):
    """Run matching pursuit, with time shifted signals in the dictionary."""
    R = samp.get_target()
    # unit = np.array([1])
    ret = []
    # thing = True
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
                # print(f)
                # print(R.dtype, f.dtype)
                # if f.dtype != 'float64':
                #     print(f)
                a = np.inner(R, f)  # np.inner uses dot product
                if(np.abs(a) < maxinn):
                    next
                maxres = (i, offset, a)

        # for offset in range(len(R)):  # unit impulse stop condition
        #     f = np.pad(unit, (offset, 0), 'constant')
        #     if np.abs(np.inner(R, f)) < maxinn:
        #         return ret

        g = np.pad(samp.comp_to_signal(maxres[0]), (maxres[1], 0), 'constant')
        g = g * maxres[2]
        R = R - g
        R = np.trim_zeros(R, 'b')
        ret.append(maxres)
    return AlgResult(samp, ret)


def matching_pursuit_mp(samp):
    """Run matching pursuit, with time shifted signals in the dictionary."""
    R = samp.get_target()
    ret = []
    maxinn = 1
    while maxinn > 0:
        print("iter: " + str(len(ret)))
        maxinn = 0
        maxres = (-1, -1, -1)
        # for i, s in enumerate(samp.components):
        mp_args = [(R, samp, i) for i in range(len(samp.components))]
        # print(mp_args[0])
        p = mp.Pool(mp.cpu_count())
        processresults = p.imap(_matching_pusuit_mp_in, mp_args)

        maxres = max(processresults, key=lambda x: x)
        g = np.pad(samp.comp_to_signal(maxres[0]), (maxres[1], 0), 'constant')
        g = g * maxres[2]
        R, g = sample.pad(R, g)
        R = R - g
        R = np.trim_zeros(R, 'b')
        ret.append(maxres)
    return AlgResult(samp, ret)


def _matching_pusuit_mp_in(args):
    # print("file: " + str(i))
    R, samp, i = args
    maxinn = 0
    maxres = (-1, -1, -1)
    sig = samp.comp_to_signal(i)
    for offset in range(len(R)):
        f = np.pad(sig, (offset, 0), 'constant')
        f, R = sample.pad(f, R)
        a = np.inner(R, f)  # np.inner uses dot product
        if(np.abs(a) < maxinn):
            next
        maxres = (i, offset, a)

    return maxres


def testo(samp):
    """Test dummy function."""
    return AlgResult(samp, [(0, 0, 1)])


def testo2(samp):
    """Test dummy function."""
    return AlgResult(samp, "not as good result")


algorithm_list = [matching_pursuit_mp]


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
