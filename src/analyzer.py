import pandas as pd
import numpy as np
import os
from scipy import signal
import matplotlib.pyplot as plt
from collections import defaultdict

import configparser


# TODO S:
# DONE:fix find peak interval (nm) and average them but look for std in peaks because outliers can be found.

# DONE:fix elements map
# DONE:fix database read

# make gui to read sample from spectrometer.
# fix database issues

# get new excel
# create calibration curve

# gui
# ---
# save only amount of N (textbox maybe)
# killi, kumlu, silt radio button
# logos of companies

# maybe developer mode on/off


# DONE: config txt for nm interval, paths, dev on/off


class Database:
    """

    """

    def __init__(self, config):

        self.element_mapping = config.element_mapping
        self.db_dir = config.db_dir

        self.database = self._open_db()
        self._filter_db()
        self.database.sort_values(by=['name', 'nm'], inplace=True)

    def _open_db(self):
        """
        Reads excel file.
        Returns dictonary which has keys as elements and values as wavelength
        """

        database = pd.DataFrame()

        for filename in os.listdir(self.db_dir):
            if 'csv' in filename:
                database = database.append(pd.read_csv(os.path.join(self.db_dir, filename), skipinitialspace=True))

        return database

    def _filter_db(self):
        """
        Filter database with respect to database mapping
        :return:
        """

        # reverse the mapping
        inverse_db = {}
        for (_from, _tos) in self.element_mapping.items():
            inverse_db.update({_to: _from for _to in _tos})

        self.database['name'] = self.database['name'].map(inverse_db)

    def search(self, value, threshold):
        """
        Searchs for only one value within the range of threshold in entire database
        :param value:
        :param threshold:
        :return: (pd.DataFrame) matches: values +- threshold
        """

        return self.database.loc[((self.database['nm'] - threshold) < value) &
                                 (value < (self.database['nm'] + threshold))]

        # matches = defaultdict(list)
        # for (element, wavelengths) in self.database.items():
        #     for wavelength in wavelengths:
        #         if wavelength - threshold < value < wavelength + threshold:
        #             matches[element].append(wavelength)
        #
        # return matches


class Sample:
    """

    """


    @classmethod
    def from_file(cls, path, peak_interval):
        cls.sample = cls.read_sample(path)
        cls.name = path.split('/')[-2]  # e.g toprak1
        cls.peak_interval = peak_interval
        cls.is_valid = False


    @classmethod
    def from_device(cls, spectrometer, name, peak_interval):
        cls.sample = spectrometer.io_to_dataframe()
        cls.name = name
        cls.peak_interval = peak_interval
        cls.is_valid = False

    @classmethod
    def from_array(cls, name, wavelengths, intensities, peak_interval, is_valid=True):
        cls.name = name
        cls.sample = pd.DataFrame()
        cls.sample['wavelengths'] = wavelengths
        cls.sample['intensities'] = intensities
        cls.peaks = cls.find_peaks(cls.sample, peak_interval)
        cls.is_valid = is_valid

        return cls

    def peaks_mean(self):
        return self.peaks['intensities'].values.mean()

    @classmethod
    def read_sample(cls, sample_path):
        return pd.read_csv(sample_path, index_col=0)

    @classmethod
    def find_peaks(cls, sample, peak_interval):
        """

        :param width: width in nm
        :return: (pd.DataFrame) peaks
        """
        wavelengths_range = sample['wavelengths'].max() - sample['wavelengths'].min()
        sampling_interval = wavelengths_range / sample['wavelengths'].shape[0]

        peak_ixs = signal.argrelmax(sample['intensities'].values, order=int(peak_interval / sampling_interval))[0]
        peak_intensities = sample.loc[peak_ixs, 'intensities']
        peak_wavelengths = sample.loc[peak_ixs, 'wavelengths']

        return pd.DataFrame({'ixs': peak_ixs,
                             'wavelengths': peak_wavelengths.values,
                             'intensities': peak_intensities.values},
                            index=range(peak_ixs.shape[0]))


class Analyzer:
    """

    """

    def __init__(self, config, inner_dir, database):

        self.sample_dir = config.sample_dir
        self.inner_dir = inner_dir
        self.peak_interval = config.peak_interval
        self.match_interval = config.match_interval
        self.outlier_interval = config.outlier_interval

        self.database = database

        self.full_dir = os.path.join(self.sample_dir, self.inner_dir)

        samples = self.read_samples(self.full_dir)
        samples = self.valid_samples(samples)

        self.sample = self.mean(samples)

        self.matches = self.match_peaks(threshold=self.match_interval)

    def read_samples(self, dir):
        """

        :param dir:
        :return:
        """
        samples = []
        for filename in os.listdir(dir):
            if 'csv' in filename:
                sample = Sample(os.path.join(dir, filename), self.peak_interval)
                samples.append(sample)

        return samples

    def valid_samples(self, samples):
        """

        :param samples:
        :return:
        """
        means = np.array([sample.peaks_mean() for sample in samples])
        norm_means = (means - means.min()) / (means.max() - means.min())
        mean_of_means = norm_means.mean()

        for sample in samples:
            norm_mean = (sample.peaks_mean() - means.min()) / (means.max() - means.min())
            # check for outlier
            if mean_of_means - self.outlier_interval < norm_mean < mean_of_means + self.outlier_interval:
                # valid sample
                sample.is_valid = True

        return [sample for sample in samples if sample.is_valid]

    def mean(self, samples):
        """

        :param samples:
        :return:
        """
        intensities = []
        wavelengths = None
        for sample in samples:
            intensities.append(sample.sample['intensities'])
            wavelengths = sample.sample['wavelengths']

        mean_intensities = np.array(intensities).mean(axis=0)
        return Sample.from_array(name='mean',
                                 wavelenths=wavelengths,
                                 intensities=mean_intensities,
                                 peak_interval=self.peak_interval)

    def match_peaks(self, threshold):
        """

        :param database:
        :param threshold:
        :return:
        """
        # return like
        # 404.57 nm: Ca
        matches = pd.DataFrame()
        for peak_w in self.sample.peaks['wavelengths']:
            matches = matches.append(database.search(peak_w, threshold))

        return matches


    def plot_data(self, point_peaks=True):
        verticals = []
        current = self.sample.sample['wavelengths'].min()
        while current < self.sample.sample['wavelengths'].max():
            verticals.append(current)
            current += self.peak_interval
        plt.plot(self.sample.sample['wavelengths'], self.sample.sample['intensities'], c='g')

        for vertical in verticals:
            plt.axvline(x=vertical, c='y', linestyle='--', alpha=0.3)

        if point_peaks:
            plt.scatter(x=self.sample.peaks['wavelengths'], y=self.sample.peaks['intensities'], c='r')



    def plot_matches(self, only=None):

        nodes = []
        for (peak_w, elements_wavelengths) in self.matches.items():
            for (element, wavelengths) in elements_wavelengths.items():
                for wavelength in wavelengths:
                    nodes.append({'wavelength': wavelength,
                                  'element': element,
                                  'nn_peak': peak_w,
                                  'intensity': self.intensities[np.where(self.wavelengths == peak_w)][
                                      0]})  # be careful, this lines ignores equal points!

        for name, group in pd.DataFrame.from_dict(nodes).groupby(by='element'):
            if only is not None:
                if name in only:
                    plt.scatter(x=group['wavelength'], y=group['intensity'], label=name, alpha=1)
            else:
                plt.scatter(x=group['wavelength'], y=group['intensity'], label=name, alpha=1)

    def find_curve_fit(self, element):
        pass

    def get_tp(self, element):
        pass

    def calculate_how_much_N_needed(self):
        pass


class Config:
    """

    """

    def __init__(self, config_path='config.ini'):
        c = configparser.ConfigParser()
        c.read(config_path)

        self.db_dir = c['Paths']['db_dir']
        self.output_dir = c['Paths']['output_dir']
        self.sample_dir = c['Paths']['sample_dir']

        self.peak_interval = float(c['Params']['peak_interval'])
        self.match_interval = float(c['Params']['match_interval'])
        self.outlier_interval = float(c['Params']['outlier_interval'])
        self.mode = c['Params']['mode']

        self.element_mapping = {elementname: c.get('ElementMapping', elementname).split(',') for elementname in
                                c.options('ElementMapping')}


if __name__ == "__main__":
    config = Config('../config.ini')
    database = Database(config=config)
    analyzer = Analyzer(config=config, database=database, inner_dir='toprak1')

    # (peak_ixs, peak_wavelengths, peak_intensities) = analyzer.find_peaks(width=PEAK_INTERVAL)
    # matches = analyzer.match_peaks(database, MATCH_INTERVAL)
    #
    plt.figure()
    analyzer.plot_data()
    plt.legend()
    #
    # plt.figure()
    # analyzer.plot_data(point_peaks=False)
    # # analyzer.plot_matches()
    # analyzer.plot_matches(only=['K','N','P','C','Al','Cu'])
    # plt.legend()
    plt.show()

    print()
