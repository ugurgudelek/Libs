"""
This file contains some classes and methods to work with oceanview project.
"""
import time
import os
import pandas as pd
import matplotlib.pyplot as plt

import random

from config import Config
from iomanager import IOManager
from database import Database
from analyzer import Analyzer
from calibration import Calibrator

class Engine:
    """

    """

    def __init__(self, iomanager, analyzer, calibrator, config):
        self.config = config
        self.iomanager = iomanager
        self.analyzer = analyzer
        self.calibrator = calibrator

        self.output_dir = config.output_dir
        self.fake = config.fake

    def connect(self):
        pass

    def read_io(self):

        name = time.time()
        if self.fake:
            fakenum = random.randint(1,10)
            reading = pd.read_csv('../input/fakesamples/fakesample_{}.csv'.format(fakenum))
            time.sleep(0.1)
            print('Fake data imported. fakesample_{}.csv'.format(fakenum))
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

    def analyze(self, dir, plotnow=False):
        # find matches
        (sample, matches) = self.analyzer.process_samples(dir)


        # find equivalent peak for each element.
        # this values will be used in calibration curve process.
        found = self.calibrator.search_in_matches(matches=matches)





        if plotnow:
            # Plot
            fig, ax = plt.subplots()


            self.analyzer.plot_data(ax, point_peaks=True, draw_verticals=False)
            self.analyzer.plot_matches(ax)

            ax.legend()
            plt.show()

        print(found)
        return found


if __name__ == '__main__':

    config = Config('../config.ini')
    engine = Engine(iomanager=IOManager(),
                    analyzer=Analyzer(config=config, database=Database(config)),
                    calibrator=Calibrator(config=config),
                    config=config)

    # readings = {}
    # remainingrecord = 3
    # while remainingrecord > 0:
    #     name, reading = engine.read_io()
    #     readings[name] = reading
    #     remainingrecord -= 1
    # path = engine.save_readings(name='test', readings=readings)

    nigde_folders = os.listdir(os.path.join(config.output_dir, 'Niğde'))
    nigde_folders = sorted(nigde_folders, key=int)

    calibration_df = pd.DataFrame()
    for folder in nigde_folders:
        print('Analyzing {}'.format(folder))
        found = engine.analyze(dir=os.path.join(config.output_dir,'Niğde', folder))

        calibration_df = calibration_df.append(pd.Series(found), ignore_index=True)

    excel = engine.calibrator.xlsx
    excel[calibration_df.columns] = calibration_df.values

    excel.to_excel('test.xlsx')
    print()





