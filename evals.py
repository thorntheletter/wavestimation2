"""Module for storing the evaluation algorithms used in driver.py."""


def e_testo(result):
    """Test dummy function."""
    return EvalResult("e_testo", result.__repr__() + "eval is good")


def e_testo_jr(result):
    """Test dummy function."""
    return EvalResult("e_testo_jr", result.__repr__() + "eval is meh")


eval_list = [e_testo, e_testo_jr]


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
        ret += "EVAL RESULT         \n"
        ret += self.e_result.__repr__()
        return ret
