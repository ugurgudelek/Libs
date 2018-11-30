"""
This file contains some classes and methods to work with oceanview project.
"""
import time
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random

from config import Config
from iomanager import IOManager
from database import Database
from analyzer import Analyzer
from calibration import Calibrator

from PyQt5.QtWidgets import QTableWidgetItem

# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from collections import defaultdict
from matplotlib.figure import Figure


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
        self.fake_samples = config.fake_samples
        self.calibration_epsilon = config.calibration_epsion

        self.loc_name = None
        self.sample_id = None
        self.readings = None

        self.dev_mode = True if config.mode == 'dev' else False

        self.giris_info = None

    # GIRIS WINDOW METHODS
    def set_giris_info(self, giris_info):

        self.giris_info = giris_info

    def get_loc_dir(self):
        giris_info = self.giris_info
        il, ilce, koy = giris_info['il'], giris_info['ilce'], giris_info['koy']

        return os.path.join(self.config.sample_output_dir, il, ilce, koy)

    def save_giris_info(self):

        output_dir = self.get_loc_dir()

        os.makedirs(output_dir, exist_ok=True)

        pd.Series(self.giris_info).to_csv(os.path.join(output_dir, 'info.csv'))

    # ANALIZ WINDOW METHODS
    def set_numune_info(self, numune_info):
        self.numune_info = numune_info

    def get_sample_id(self):
        return self.numune_info['numuneadi']

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

            cur_fake_sample_dir = os.path.join(self.fake_sample_dir, self.numune_info['numuneadi']) if self.numune_info['numuneadi'] in self.fake_samples else self.fake_sample_dir
            random_path = os.path.join(cur_fake_sample_dir,
                                       random.choice([file for file in os.listdir(cur_fake_sample_dir)
                                                      if os.path.isfile(os.path.join(cur_fake_sample_dir, file))]))
            reading = pd.read_csv(random_path)

            time.sleep(2)
            print('Fdata imported. {}'.format(random_path.split('\\')[-1]))
        else:
            reading = self.iomanager.io_to_dataframe()

        return name, reading

    def read_remainingrecords(self, remainingrecord):
        self.readings = {}
        while remainingrecord > 0:
            name, reading = self.read_io()
            self.readings[name] = reading
            remainingrecord -= 1
            yield remainingrecord

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
        loc_path = self.get_loc_dir()  # e.g output/Niğde
        sample_id = self.get_sample_id()

        os.makedirs(loc_path, exist_ok=True)

        # it is time to store io readings
        for (key, reading) in self.readings.items():
            _save_reading(loc_path=loc_path, sample_id=sample_id, name=key, reading=reading)

        return os.path.join(loc_path, sample_id)

    def analyze(self, dir, plotnow=False):
        # find matches
        (sample, matches) = self.analyzer.process_samples(dir)

        if plotnow:
            # Plot
            fig, ax = plt.subplots()

            self.analyzer.plot_data(ax, point_peaks=True, draw_verticals=False)
            self.analyzer.plot_matches(ax)

            ax.legend()
            plt.show(block=False)

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

    def fit(self, X, name):
        return self.calibrator.fit(X, name)

    def data_to_row(self, table, numuneadi, element, miktar, birim, durumu):
        current_row = table.rowCount()
        table.setRowCount(current_row + 1)
        table.setItem(current_row, 0, QTableWidgetItem(numuneadi))
        table.setItem(current_row, 1, QTableWidgetItem(element))
        table.setItem(current_row, 2, QTableWidgetItem(miktar))
        table.setItem(current_row, 3, QTableWidgetItem(birim))
        table.setItem(current_row, 4, QTableWidgetItem(durumu))

    def limit_values(self, element, quantity):
        # çok az, az, yeterli, fazla, çok fazla
        limit_db = defaultdict(list)
        limit_db['N'] = [0.045, 0.09, 0.17, 0.32]
        limit_db['P2O5'] = [1.43, 4.58, 14.31, 45.8]
        limit_db['K2O'] = [15.33, 33.03, 87.30, 302.01]
        limit_db['OM'] = [1, 2, 3, 4]

        arr = limit_db[element]

        def find_interval(arr, q):
            for i,val in enumerate(arr):
                if q < val:
                    return i
            return 4 # last index

        int_to_quantityword = {0:'çok az', 1:'az', 2:'yeterli', 3:'fazla', 4:'çok fazla'}

        return int_to_quantityword[find_interval(arr, quantity)]

    def analysis_to_ppm_data(self, matches):

        elements = ['N 5 @ 443.506',
                    'P 4 @ 407.871',
                    'C 2 @ 280.146',
                    'K 2 @ 553.656']
        names = ['N', 'P2O5', 'OM', 'K2O']
        units = ['%', 'kg/da', '%', 'kg/da']

        if self.fake and self.numune_info['numuneadi'] in self.fake_samples:

            q_all = {'s1':['0.1', '10.25',  '2.30', '35.58'],
                     's2':['0.9', '19.13',  '2.32', '18.37'],
                     'a1':['0.05', '1.27',  '2.64', '70.42'],
                     'a3':['0.04', '14.11', '0.84', '16.28'],
                     'y1':['0.07', '1.69',  '1.48', '20.15']}

            quantities = q_all[self.numune_info['numuneadi']]
            statuses = ["yeterli", "yeterli", "yeterli", "yeterli"]


        else:
            Xs = [self.fit(matches[element], name) for element, name in zip(elements, names)]

            # ppm to kgda conversion
            multipliers = [1, 2.29 * 0.25, 1.724, 1.21 * 0.25]
            quantities = ['{:.2f}'.format(mul*X) for mul, X in zip(multipliers, Xs)]

            statuses = [self.limit_values(name, X) for name, X in zip(names, Xs)]

        return names, quantities, statuses, units

    def result_image(self, dataframe=None):
        # todo: implement

        if dataframe is None:
            dataframe = pd.DataFrame()
            dataframe['x'] = ['N', 'OM', 'P2O5', 'K2O']
            dataframe['y'] = [10, 20, 30, 40]

        canvas = FigureCanvas(Figure())
        _static_ax = canvas.figure.subplots()
        _static_ax.bar(list(range(len(dataframe))), dataframe['y'].values, tick_label=dataframe['x'].values)
        # _static_ax = sns.barplot(x='x', y='y', data=dataframe)
        return canvas


if __name__ == '__main__':
    config = Config('../config.ini')
    engine = Engine(iomanager=IOManager(),
                    analyzer=Analyzer(config=config, database=Database(config)),
                    calibrator=Calibrator(input_dir=config.calibration_input_dir,
                                          output_dir=config.calibration_output_dir,
                                          calibration_eqns=config.calibration_equation),
                    config=config)

    # engine.pipeline('adana')

    engine.analyze("../output/samples/adana/1", plotnow=True)
