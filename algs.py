"""Module for storing the estimation algorithms used in driver.py."""


def testo(sample):
    """Test dummy function."""
    return AlgResult(sample, "good result")


def testo2(sample):
    """Test dummy function."""
    return AlgResult(sample, "not as good result")


algorithm_list = [testo, testo2]


class AlgResult():
    """Stores and displays a result from an estimation algorithm."""

    def __init__(self, sample, a_result):
        """Initialize AlgResult with Sample and result."""
        self.s_name = sample.name
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
