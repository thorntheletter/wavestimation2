"""Module for storing the estimation algorithms used in driver.py."""
import numpy as np
import driver


def testo(sample):
    """Test dummy function."""
    return AlgResult(sample, [(0, 0, 1)])


def testo2(sample):
    """Test dummy function."""
    return AlgResult(sample, "not as good result")


algorithm_list = [testo]


class AlgResult(driver.Sample):
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
            signal, s = driver.pad(signal, s,)
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
