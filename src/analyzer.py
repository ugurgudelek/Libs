import pandas as pd
import numpy as np
import os
from scipy import signal
import matplotlib.pyplot as plt
from collections import defaultdict

# TODO S:
# fix find peak interval (nm) and average them but look for std in peaks because outliers can be found.

# fix elements map
# fix database read

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
# config txt for nm interval, paths, dev on/off




# CSV_DIR = '../input/toprak1/'
CSV_DIR = '../input/gubre'
DB_PATH = '../input/element_database.xlsx'
PEAK_INTERVAL = 0.5  # nm
MATCH_INTERVAL = 0.5  # nm
ELEMENTS_MAP = {'N': ['NI', 'NII', 'NIII', 'NIV', 'NV', 'NII-'],
                'C': ['CI', 'CII', 'CIII', 'CIV', 'CV'],
                'P': ['PI', 'PII', 'PIII', 'PIV', 'PV'],
                'K': ['KI', 'KII', 'KII', 'KIII', 'KXI'],
                'Fe': ['Fe','FeI', 'FeII'],
                'Al': ['Al', 'AlI', 'AlII'],
                'Cu': ['Cu','CuI']}


class Database:
    """

    """

    def __init__(self, db_path):

        self.database = self.open_db(db_path)
        self.database = self.filter_db()
        self.database = self.sort_db()

    def open_db(self, database_path):
        """
        Reads excel file.
        Returns dictonary which has keys as elements and values as wavelength
        """

        database = pd.read_excel(database_path, header=None)

        # TODO: refactor method
        database_al = pd.read_csv('../input/database/database_al.csv')
        database_cu = pd.read_csv('../input/database/database_cu.csv')
        database_fe = pd.read_csv('../input/database/database_fe.csv')

        database_groupdict = database.groupby(by=0).groups


        database_dict = dict()
        for (element_name, idxs) in database_groupdict.items():
            rows = database.iloc[idxs.values, 1:].values.flatten()  # fetch multiple lines at once
            rows = rows[~np.isnan(rows)]  # remove nan values
            database_dict[element_name] = rows

        database_dict['Al'] = database_al['nm'].values
        database_dict['Cu'] = database_cu['nm'].values
        database_dict['Fe'] = database_fe['nm'].values

        return database_dict

    def filter_db(self):
        # TODO: refactor this function
        filtered = defaultdict(lambda: np.array([]))
        for (element, other_versions) in ELEMENTS_MAP.items():
            for other_version in other_versions:
                filtered[element] = np.append(filtered[element], self.database[other_version])

        return filtered

    def search(self, value, threshold):
        """
        Searchs for only one value in entire database
        :param value:
        :param threshold:
        :return: (defaultdict(list)) matches:
        """
        matches = defaultdict(list)
        for (element, wavelengths) in self.database.items():
            for wavelength in wavelengths:
                if wavelength - threshold < value < wavelength + threshold:
                    matches[element].append(wavelength)

        return matches

    def sort_db(self):
        database = dict()
        for (element, wavelengths) in self.database.items():
            database[element] = np.sort(wavelengths)

        return database

class Analyzer:
    """

    """

    def __init__(self, csv_dir):

        filenames = os.listdir(csv_dir)

        intensities = []
        wavelengths = None

        for filename in filenames:
            if filename.split('.')[-1] == 'csv':
                df = pd.read_csv(os.path.join(csv_dir, filename))
                intensities.append(df['intensities'].values)
                wavelengths = df['wavelengths'].values

        self.intensities = np.array(intensities).mean(axis=0)
        self.wavelengths = wavelengths

        self.peak_ixs = None
        self.peak_intensities = None
        self.peak_wavelengths = None

        self.matches = None


    def find_peaks(self, width=5, drop_below=1000):
        """

        :param width: width in nm
        :param drop_below:
        :return:
        """
        wavelengths_range = self.wavelengths.max() - self.wavelengths.min()
        sampling_interval = wavelengths_range / self.wavelengths.shape[0]
        # relative_ratio = width / wavelengths_range
        # relative_width = int(relative_ratio * self.wavelengths.shape[0])
        # v = vector.copy()
        # v[v < drop_below] = 0
        # widths = np.arange(0.0001, relative_width, 0.1)
        # return signal.find_peaks_cwt(vector=vector, widths=widths,
        #                              min_snr=1, noise_perc=0.1,
        #                              max_distances=widths,
        #                              min_length=int(width/space))[1:-1]

        self.peak_ixs = peak_ixs = signal.argrelmax(self.intensities, order=int(width / sampling_interval))[0]
        self.peak_intensities = self.intensities[peak_ixs]
        self.peak_wavelengths = self.wavelengths[peak_ixs]



        return peak_ixs, self.peak_wavelengths, self.peak_intensities

    def match_peaks(self, database, threshold):
        """

        :param database:
        :param threshold:
        :return:
        """
        # return like
        # 404.57 nm: Ca
        matches = {}
        for peak_w in self.peak_wavelengths:
            matches[peak_w] = database.search(peak_w, threshold)

        self.matches = matches
        return matches

    def plot_data(self, point_peaks=True):
        verticals = []
        current = self.wavelengths.min()
        while current < self.wavelengths.max():
            verticals.append(current)
            current += PEAK_INTERVAL
        plt.plot(self.wavelengths, self.intensities, c='g')
        if point_peaks:
            plt.scatter(x=self.wavelengths[peak_ixs], y=self.intensities[peak_ixs], c='r')
        # for vertical in verticals:
        #     plt.axvline(x=vertical, c='y', linestyle='--', alpha=0.3)

    def plot_matches(self, only=None):

        nodes = []
        for (peak_w, elements_wavelengths) in self.matches.items():
            for (element, wavelengths) in elements_wavelengths.items():
                for wavelength in wavelengths:
                    nodes.append({'wavelength': wavelength,
                                  'element': element,
                                  'nn_peak': peak_w,
                                  'intensity': self.intensities[np.where(self.wavelengths == peak_w)][0]})   # be careful, this lines ignores equal points!

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





if __name__ == "__main__":
    analyzer = Analyzer(csv_dir=CSV_DIR)
    database = Database(db_path=DB_PATH)
    (peak_ixs, peak_wavelengths, peak_intensities) = analyzer.find_peaks(width=PEAK_INTERVAL)
    matches = analyzer.match_peaks(database, MATCH_INTERVAL)

    plt.figure()
    analyzer.plot_data()
    plt.legend()

    plt.figure()
    analyzer.plot_data(point_peaks=False)
    # analyzer.plot_matches()
    analyzer.plot_matches(only=['K','N','P','C','Al','Cu'])
    plt.legend()
    plt.show()

