"""
This file contains some classes and methods to work with oceanview project.
"""
import time
import os
import pandas as pd
import matplotlib.pyplot as plt

from iomanager import IOManager
from analyzer import Analyzer, Database, Sample
from config import Config

class Engine:
    """

    """

    def __init__(self, iomanager, analyzer, config):
        self.config = config
        self.iomanager = iomanager
        self.analyzer = analyzer

        self.output_dir = config.output_dir

    def connect(self):
        pass

    def read_io(self, times=10):
        readings = {}
        fig = plt.figure()
        plt.show(block=False)
        for i in range(times):
            print("Press the laser trigger button. Remaining: {}".format(times-i))
            name = time.time()
            reading = self.iomanager.io_to_dataframe()
            readings[name] = reading

            reading.plot(x='wavelengths', y='intensities', label=name)
            plt.legend()
            plt.pause(0.1)
            fig.canvas.draw()

        return readings

    def save_readings(self, name, readings):
        """
        
        Args:
            name: 
            readings (dict(pd.DataFrame)): 

        Returns:

        """
        # create path
        path = os.path.join(self.output_dir, name)
        if not os.path.exists(path):
            os.mkdir(path)

        # it is time to store io readings
        for (key,reading) in readings.items():
            reading.to_csv(os.path.join(path, '{}.csv'.format(key)), index=False)

        return path

    def analyze(self, dir):
        matches = self.analyzer.process_samples(dir)


        # Plot
        fig, ax = plt.subplots()


        self.analyzer.plot_data(ax)
        # self.analyzer.plot_matches(ax)

        ax.legend()
        plt.show()



config = Config('../config.ini')
engine = Engine(iomanager=IOManager(),
                analyzer=Analyzer(config=config, database=Database(config)),
                config=config)

readings = engine.read_io(times=2)
path = engine.save_readings(name='test_sample', readings=readings)

# path = '../output/test_sample'
# engine.analyze(path)
