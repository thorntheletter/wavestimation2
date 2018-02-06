"""Module for storing the evaluation algorithms used in driver.py."""
import numpy as np
import driver


def MSE_L2_time(results):
    """Mean Square Error where error is the L2 norm."""
    total = 0
    res_string = "Single Sample L2 Norms:\n\n"
    for r in results:
        rsignal, tsignal = driver.pad(r.to_signal(), r.get_target())
        single = np.linalg.norm(tsignal - rsignal)
        res_string += r.s_name + ": " + single.__str__()
        total += single ** 2
    total /= len(results)
    res_string = "total: " + total + res_string
    return res_string


def MSE_L1_time(results):
    """Mean Square Error where error is the L1 norm."""
    total = 0
    res_string = "Single Sample L1 Norms:\n\n"
    for r in results:
        rsignal, tsignal = driver.pad(r.to_signal, r.get_target)
        single = np.linalg.norm(tsignal - rsignal, ord=1)
        res_string += r.s_name + ": " + single.__str__()
        total += single ** 2
    total /= len(results)
    res_string = "total: " + total + res_string
    return res_string


def e_testo(results):
    """Test dummy function."""
    return EvalResult("e_testo", results.__repr__() + "eval is good")


def e_testo_jr(results):
    """Test dummy function."""
    return EvalResult("e_testo_jr", results.__repr__() + "eval is meh")


eval_list = [MSE_L2_time, MSE_L1_time]


class EvalResult():
    """Stores and displays a single evaluation algorithm result."""

    def __init__(self, e_name, e_result):
        """Initialize an EvalResult with a name and the result."""
        self.e_name = e_name
        self.e_result = e_result

    def __repr__(self):
        """Display the EvalResult as a string."""
        ret = "EVAL ALG NAME:      "
        ret += self.e_name + "\n"
        ret += "EVAL RESULT\n"
        ret += self.e_result.__repr__()
        return ret
