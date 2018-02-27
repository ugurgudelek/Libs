import pandas as pd
import numpy as np
import os

import matplotlib.pyplot as plt
from collections import defaultdict
from sample import Sample




# TODO S:
# DONE:fix find peak interval (nm) and average them but look for std in peaks because outliers can be found.

# DONE:fix elements map
# DONE:fix database read

# make gui to read sample from spectrometer.
# DONE:fix database issues

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





class Analyzer:
    """

    """

    def __init__(self, config, database):


        self.peak_interval = config.peak_interval
        self.match_interval = config.match_interval
        self.outlier_interval = config.outlier_interval

        self.database = database


    def process_samples(self, dir):
        samples = self.read_samples(dir)
        samples = self.valid_samples(samples)
        self.sample = sample = self.mean(samples)
        self.matches = matches = self.match_peaks(threshold=self.match_interval)
        return (sample, matches)

    def read_samples(self, dir):
        """

        :param dir:
        :return:
        """
        samples = []
        for filename in os.listdir(dir):
            if 'csv' in filename:
                name = dir.split('/')[-1]  # e.g toprak1
                sample = Sample.from_file(name, os.path.join(dir, filename),
                                          self.peak_interval, is_valid=False)
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
        name = None
        for sample in samples:
            intensities.append(sample.sample['intensities'])
            wavelengths = sample.sample['wavelengths']
            name = sample.name

        mean_intensities = np.array(intensities).mean(axis=0)
        return Sample.from_array(name=name,
                                 wavelengths=wavelengths,
                                 intensities=mean_intensities,
                                 peak_interval=self.peak_interval,
                                 is_valid=True)

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
            matches = matches.append(self.database.search(peak_w, threshold))

        return matches


    def plot_data(self, ax, point_peaks=True):
        # chunk whole spectrum to the little pieces.
        # start with min, end with max.
        verticals = []
        current = self.sample.sample['wavelengths'].min()
        while current < self.sample.sample['wavelengths'].max():
            verticals.append(current)
            current += self.peak_interval
        ax.plot(self.sample.sample['wavelengths'], self.sample.sample['intensities'], c='g')

        # draw vertical lines
        for vertical in verticals:
            ax.axvline(x=vertical, c='y', linestyle='--', alpha=0.3)

        if point_peaks:
            ax.scatter(x=self.sample.peaks['wavelengths'], y=self.sample.peaks['intensities'], c='r')


    def plot_matches(self, ax,elements=None):

        # TODO: fix this function
        matches = self.matches.copy()
        sample = self.sample.sample.copy()
        sample.index = sample['wavelengths']
        matches['intensities'] = sample[matches['nm'].values, 'intensities']



        if elements is not None:
            matches = matches.loc[matches['name'].isin(elements)]
        groups = matches.groupby('name')

        ax.margins(0.05)  # Optional, just adds 5% padding to the autoscaling
        for name, group in groups:
            ax.scatter(x=group['nm'], y=group['intensities'], marker='o', label=name)



        # for name, group in pd.DataFrame.from_dict(nodes).groupby(by='element'):
        #     if only is not None:
        #         if name in only:
        #             plt.scatter(x=group['wavelength'], y=group['intensity'], label=name, alpha=1)
        #     else:
        #         plt.scatter(x=group['wavelength'], y=group['intensity'], label=name, alpha=1)








#
# if __name__ == "__main__":
#     config = Config('../config.ini')
#     database = Database(config=config)
#     analyzer = Analyzer(config=config, database=database, inner_dir='toprak1')
#
#     # (peak_ixs, peak_wavelengths, peak_intensities) = analyzer.find_peaks(width=PEAK_INTERVAL)
#     # matches = analyzer.match_peaks(database, MATCH_INTERVAL)
#     #
#     plt.figure()
#     analyzer.plot_data()
#     plt.legend()
#     #
#     # plt.figure()
#     # analyzer.plot_data(point_peaks=False)
#     # # analyzer.plot_matches()
#     # analyzer.plot_matches(only=['K','N','P','C','Al','Cu'])
#     # plt.legend()
#     plt.show()
#
#     print()
