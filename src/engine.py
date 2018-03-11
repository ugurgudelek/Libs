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

    Args:
        iomanager(IOManager):
        analyzer(Analyzer):
        calibrator(Calibrator):
        config(Config):
    """
    def __init__(self, iomanager, analyzer, calibrator, config):

        self.config = config
        self.iomanager = iomanager
        self.analyzer = analyzer
        self.calibrator = calibrator

        # input directories
        self.input_dir = config.input_dir
        self.db_dir = config.db_dir
        self.calibration_input_dir = config.calibration_input_dir
        self.fake_sample_dir = config.fake_sample_dir

        # output directories
        self.output_dir = config.output_dir
        self.sample_output_dir = config.sample_output_dir
        self.calibration_output_dir = config.calibration_output_dir

        self.fake = config.fake
        self.calibration_epsilon = config.calibration_epsion

        self.loc_name = None
        self.sample_id = None
        self.readings = None


    def connect_to_gui(self, loc_name, sample_id):
        """
        This method set loc_name and sample_id attr
        and then check for prerequisites for locnamedir and sampledir
        Args:
            loc_name(str):
            sample_id(int):

        Returns:

        """
        self.loc_name = loc_name
        self.sample_id = sample_id

        sample_dir_exists = False

        # check prerequisites
        loc_dir = os.path.join(self.sample_output_dir, loc_name)
        if not os.path.exists(loc_dir):
            print('New directory will be created : {}'.format(loc_dir))
            os.mkdir(loc_dir)

        sample_dir = os.path.join(loc_dir, str(sample_id))
        if os.path.exists(sample_dir):
            print('File for {} is already exists'.format(sample_dir))
            sample_dir_exists = True

        return sample_dir_exists



    def load_readings(self, readings):
        self.readings = readings

    def read_io(self):

        name = time.time()
        if self.fake:
            fakenum = random.randint(1,10)
            reading = pd.read_csv(os.path.join(self.fake_sample_dir,'fakesample_{}.csv'.format(fakenum)))
            time.sleep(0.1)
            print('Fake data imported. fakesample_{}.csv'.format(fakenum))
        else:
            reading = self.iomanager.io_to_dataframe()

        return name, reading


    def save_readings(self):
        """

        Args:
            loc_name: e.g. Niğde, Yozgat
            sample_id: 1,2,... instead of toprak1,toprak2,...
            readings: (dict(pd.DataFrame)): all readings for one location

        Returns:

        """

        def _save_reading(loc_path, sample_id, name, reading):
            """

            Args:
                loc_path(str):
                sample_id(int):
                name(str):
                reading(pd.DataFrame):

            Returns:

            """
            sample_path = os.path.join(loc_path, str(sample_id))  # e.g output/Niğde/1
            if not os.path.exists(sample_path):
                os.mkdir(sample_path)

            reading.to_csv(os.path.join(sample_path, '{}.csv'.format(name)), index=False)


        # create path
        loc_path = os.path.join(self.sample_output_dir, self.loc_name) # e.g output/Niğde
        if not os.path.exists(loc_path):
            os.mkdir(loc_path)



        # it is time to store io readings
        for (key, reading) in self.readings.items():
            _save_reading(loc_path=loc_path, sample_id=self.sample_id, name=key, reading=reading)

        return os.path.join(loc_path, str(self.sample_id))

    def analyze(self, dir, plotnow=False):
        # find matches
        (sample, matches) = self.analyzer.process_samples(dir)

        if plotnow:
            # Plot
            fig, ax = plt.subplots()


            self.analyzer.plot_data(ax, point_peaks=True, draw_verticals=False)
            self.analyzer.plot_matches(ax)

            ax.legend()
            plt.show()

        return (sample, matches)

    def calibrate(self, matches):
        return self.calibrator.search_in_matches(matches=matches, epsilon=self.calibration_epsilon)


    def pipeline(self, loc_name):
        sample_path = os.path.join(self.sample_output_dir, loc_name)
        sample_folders = os.listdir(sample_path)
        sample_folders = sorted(sample_folders, key=int)

        calibration_df = pd.DataFrame()
        for folder in sample_folders:
            print('Analyzing {} {}'.format(loc_name, folder))
            (sample, matches) = self.analyze(dir=os.path.join(sample_path, folder), plotnow=False)

            # find equivalent peak for each element.
            # this values will be used in calibration curve process.
            print('Calibrating {} {}'.format(loc_name, folder))
            found_el_intensity_matches = self.calibrate(matches=matches)

            calibration_df = calibration_df.append(pd.Series(found_el_intensity_matches),
                                                   ignore_index=True)

         # write all calibration data to new excel file.
        self.calibrator.write_to_excel(sheet_name=loc_name,
                                       col_names=calibration_df.columns,
                                       values=calibration_df.values)

        # write to csv for test purposes
        self.calibrator.write_to_csv(calibration_df, loc_name=loc_name)

        # fit calibration values
        # self.calibrator.fit(calibration_df)

    def plot_readings(self, readings):
        pass

if __name__ == '__main__':

    config = Config('../config.ini')
    engine = Engine(iomanager=IOManager(),
                    analyzer=Analyzer(config=config, database=Database(config)),
                    calibrator=Calibrator(input_dir=config.calibration_input_dir,
                                          output_dir=config.calibration_output_dir),
                    config=config)

    # readings = {}
    # remainingrecord = 3
    # while remainingrecord > 0:
    #     name, reading = engine.read_io()
    #     readings[name] = reading
    #     remainingrecord -= 1
    # path = engine.save_readings(name='test', readings=readings)

    engine.pipeline(loc_name='niğde')






