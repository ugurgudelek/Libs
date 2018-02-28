"""
This file contains some classes and methods to work with oceanview project.
"""
import time
import os
import pandas as pd
import matplotlib.pyplot as plt



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

    def read_io(self, fake=False):

        name = time.time()
        if fake:
            reading = pd.read_csv('../output/test_sample/1519737006.0222373.csv')
            time.sleep(1)
            print('Fake data imported.')
        else:
            reading = self.iomanager.io_to_dataframe()

        return name, reading


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




