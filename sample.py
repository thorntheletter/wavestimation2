"""Module for storing samples."""
import numpy as np
files_dict = {}


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
