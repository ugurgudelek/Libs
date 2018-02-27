"""
This file contains some classes and methods to work with oceanview project.
"""

class Engine:
    """

    """

    def __init__(self, spectrometers):
        self.spectrometers = spectrometers

    def connect(self):
        pass

    def read_io(self, times=10):

        for _ in range(times):
            intensities