import pandas as pd
import numpy as np
import os

import matplotlib.pyplot as plt
from collections import defaultdict
from sample import Sample

from database import Database

from config import Config



# DONE:fix find peak interval (nm) and average them but look for std in peaks because outliers can be found.

# DONE:fix elements map
# DONE:fix database read

# DONE:make gui to read sample from spectrometer.
# DONE:fix database issues

# todo:get new excel
# todo:create calibration curve

# region:gui
# ---
# todo:save only amount of N (textbox maybe)
# todo:killi, kumlu, silt radio button
# todo:logos of companies

# DONE: maybe developer mode on/off


# DONE: config txt for nm interval, paths, dev on/off







class Analyzer:
    """

    """

    def __init__(self, config, database):


        self.peak_interval = config.peak_interval
        self.match_interval = config.match_interval
        self.outlier_interval = config.outlier_interval
        self.validate = config.validate_samples

        self.database = database

        self.sample = None
        self.matches = None


    def process_samples(self, dir, find_matches=True):
        """

        Args:
            dir:

        Returns:

        """
        samples = self.read_samples(dir)
        if self.validate:
            samples = self.validate_samples(samples)
        self.sample = self.mean(samples)

        self.matches = None
        if find_matches:
            self.matches = self.match_peaks(threshold=self.match_interval).reset_index(drop=True)

        return self.sample, self.matches

    def read_samples(self, dir):
        """

        Args:
            dir:

        Returns:

        """
        samples = []
        for filename in os.listdir(dir):
            if 'csv' in filename:
                name = dir.split('/')[-1]  # e.g toprak1
                sample = Sample.from_file(name, os.path.join(dir, filename),
                                          self.peak_interval, is_valid=False)
                samples.append(sample)

        return samples

    def validate_samples(self, samples):
        """

        :param samples:
        :return:
        """
        means = np.array([sample.peaks_mean() for sample in samples])
        norm_means = (means - means.min()) / (means.max() - means.min())
        mean_of_means = norm_means.mean()

        valid_cnt = 0
        for sample in samples:
            norm_mean = (sample.peaks_mean() - means.min()) / (means.max() - means.min())
            # check for outlier
            # if mean_of_means - self.outlier_interval < norm_mean < mean_of_means + self.outlier_interval:
            if  mean_of_means < norm_mean:  # take only if im above mean.
                # valid sample
                sample.is_valid = True
                valid_cnt += 1

        print('{} samples have been marked as valid.'.format(valid_cnt))

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
        matches = pd.DataFrame(columns=['name', 'nm', 'peak_nm'])
        for peak_w in self.sample.peaks['wavelengths']:
            found = self.database.search(peak_w, threshold)
            found['peak_nm'] = peak_w
            matches = matches.append(found)

        # find related peak intensities
        sample = self.sample.sample.copy()
        sample.index = sample['wavelengths']  # change index for easy use with .loc

        # fetch intensities from sample for each peak_nm in matches
        matches['peak_intensities'] = matches.apply(lambda row: sample.loc[row['peak_nm'], 'intensities'], axis=1)

        return matches


    def plot_data(self, ax, point_peaks=True, draw_verticals=True):
        """

        Args:
            ax:
            point_peaks:
            draw_verticals:

        Returns:

        """
        # chunk whole spectrum to the little pieces.
        # start with min, end with max.
        verticals = []
        current = self.sample.sample['wavelengths'].min()
        while current < self.sample.sample['wavelengths'].max():
            verticals.append(current)
            current += self.peak_interval
        ax.plot(self.sample.sample['wavelengths'], self.sample.sample['intensities'], c='g')

        if draw_verticals:
            # draw vertical lines
            for vertical in verticals:
                ax.axvline(x=vertical, c='y', linestyle='--', alpha=0.3)

        if point_peaks:
            ax.scatter(x=self.sample.peaks['wavelengths'], y=self.sample.peaks['intensities'], c='r', marker='x')



    def plot_matches(self, ax):
        """

        Args:
            ax:
            elements:

        Returns:

        """

        groups = self.matches.groupby('name')

        ax.margins(0.05)  # Optional, just adds 5% padding to the autoscaling
        for name, group in groups:
            ax.scatter(x=group['nm'], y=group['peak_intensities'], marker='o', label=name)








if __name__ == "__main__":
    config = Config('../config.ini')
    database = Database(config=config)
    analyzer = Analyzer(config=config, database=database)

    (sample, matches) = analyzer.process_samples('../output/samples/adana/1')


    # Plot
    fig, ax = plt.subplots()

    analyzer.plot_data(ax, point_peaks=True, draw_verticals=False)
    analyzer.plot_matches(ax)

    ax.legend()
    plt.show()
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
