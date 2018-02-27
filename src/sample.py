import pandas as pd
from scipy import signal

class Sample:
    """

    """

    def __init__(self, name, dataframe, peak_interval, is_valid):
        self.name = name
        self.sample = dataframe
        self.is_valid = is_valid
        self.peak_interval = peak_interval

        self.peaks = self._find_peaks()



    @classmethod
    def from_file(cls, name, path, peak_interval, is_valid):
        dataframe = pd.read_csv(path)
        return cls(name=name, dataframe=dataframe,
                   peak_interval=peak_interval, is_valid=is_valid)

    @classmethod
    def from_array(cls, name, wavelengths, intensities, peak_interval, is_valid):

        dataframe = pd.DataFrame()
        dataframe['wavelengths'] = wavelengths
        dataframe['intensities'] = intensities
        return cls(name=name, dataframe=dataframe,
                   peak_interval=peak_interval, is_valid=is_valid)

    def peaks_mean(self):
        return self.peaks['intensities'].values.mean()

    def _find_peaks(self):
        """

        :param width: width in nm
        :return: (pd.DataFrame) peaks
        """
        wavelengths_range = self.sample['wavelengths'].max() - self.sample['wavelengths'].min()
        sampling_interval = wavelengths_range / self.sample['wavelengths'].shape[0]

        peak_ixs = signal.argrelmax(self.sample['intensities'].values,
                                    order=int(self.peak_interval / sampling_interval))[0]
        peak_intensities = self.sample.loc[peak_ixs, 'intensities']
        peak_wavelengths = self.sample.loc[peak_ixs, 'wavelengths']

        return pd.DataFrame({'ixs': peak_ixs,
                             'wavelengths': peak_wavelengths.values,
                             'intensities': peak_intensities.values},
                            index=range(peak_ixs.shape[0]))