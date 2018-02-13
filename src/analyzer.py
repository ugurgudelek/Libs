import pandas as pd
import numpy as np
import os
from scipy import signal
import matplotlib.pyplot as plt

class Analyzer:
    """

    """
    def __init__(self, csv_dir):

        filenames = os.listdir(csv_dir)

        intensities = []
        wavelengths = None

        for filename in filenames:
            df = pd.read_csv(os.path.join(csv_dir, filename))
            intensities.append(df['intensities'].values)
            wavelengths = df['wavelengths'].values

        self.intensities = np.array(intensities).mean(axis=0)
        self.wavelengths = wavelengths

    def find_peaks(self, vector: np.ndarray, width=5, drop_below=1000):
        """

        :param vector:
        :param width: width in nm
        :param drop_below:
        :return:
        """
        wavelengths_range = self.wavelengths.max() - self.wavelengths.min()
        sampling_interval = wavelengths_range/self.wavelengths.shape[0]
        # relative_ratio = width / wavelengths_range
        # relative_width = int(relative_ratio * self.wavelengths.shape[0])
        # v = vector.copy()
        # v[v < drop_below] = 0
        # widths = np.arange(0.0001, relative_width, 0.1)
        # return signal.find_peaks_cwt(vector=vector, widths=widths,
        #                              min_snr=1, noise_perc=0.1,
        #                              max_distances=widths,
        #                              min_length=int(width/space))[1:-1]

        return signal.argrelmax(vector, order=int(width/sampling_interval))

    def match_peaks(self, peaks):
        # return like
        # 404.57 nm: Ca
        pass

    def scatter_element(self):
        pass

    def find_curve_fit(self, element):
        pass

    def get_tp(self, element):
        pass

    def calculate_how_much_N_needed(self):
        pass

CSV_DIR = '../input/toprak1/'
PEAK_INTERVAL = 10  # nm

analyzer = Analyzer(csv_dir=CSV_DIR)
peak_ixs = analyzer.find_peaks(vector=analyzer.intensities, width=PEAK_INTERVAL)

verticals = []
current = analyzer.wavelengths.min()
while current < analyzer.wavelengths.max():
    verticals.append(current)
    current += PEAK_INTERVAL
plt.plot(analyzer.wavelengths, analyzer.intensities)
plt.scatter(x=analyzer.wavelengths[peak_ixs], y=analyzer.intensities[peak_ixs], c='r')
for vertical in verticals:
    plt.axvline(x=vertical, c='y', linestyle='--')
plt.show()
