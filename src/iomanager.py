"""
Ugur Gudelek
13.02.2018 11:00
"""

import seabreeze
seabreeze.backends.use('pyseabreeze')
import seabreeze.spectrometers as sb



import matplotlib.pyplot as plt
import time
import numpy as np
import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool

import warnings

class IOManager:
    def __init__(self):

        devices = sb.list_devices()

        # Assert device count
        if len(devices) != 2:
            warnings.warn("Should have 2 devices but we have these:{}".format(devices))

        print(devices)

        # Assert backend
        # TODO: check backend

        time.sleep(2)  # wait a little bit for usb connection
        self.spectrometers = []
        for device in devices:
            self.spectrometers.append(sb.Spectrometer(device=device))
            time.sleep(0.1)

        # sort by lowest wavelength to highest
        self.spectrometers = sorted(self.spectrometers, key=lambda spec: spec.wavelengths().mean())

        for i, spectrometer in enumerate(self.spectrometers):

            #  Integration time is the length of time that the detector is allowed to collect photons
            #  before passing the accumulated charge to the A/D converter for processing.
            #  The minimum integration time is the shortest integration time the device supports
            #  and is dependent on how fast the detector can read out all of the pixel information.
            #  Integration time should not be confused with data transfer speed.
            spectrometer.integration_time_micros(10000)


            #  Available Trigger Modes
            # 'HR2000PLUS'  : {
            #        'FREE_RUNNING' : 0,
            #        'SOFTWARE'     : 1,
            #        'EXT_HW'       : 2,
            #        'EXT_HW_SYNC'  : 3,
            #        'EXT_HW_EDGE'  : 4,
            #         }
            spectrometer.trigger_mode(mode=4)  # 'EXT_HW_EDGE'

        self.intensities = None  # to store lastly fetched intensities
        self.wavelengths = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for spectrometer in self.spectrometers:
            spectrometer.close()

    def _intensity(self, spectrometer):
        return np.array(spectrometer.intensities(correct_dark_counts=True, correct_nonlinearity=True))

    def _get_intensities(self):
        pool = ThreadPool(2)
        self.intensities = np.array(pool.map(self._intensity, self.spectrometers))
        self.intensities = self.intensities.flatten()
        return self.intensities

    def _get_wavelengths(self):
        self.wavelengths = np.array([spectrometer.wavelengths() for spectrometer in self.spectrometers]).flatten()
        self.wavelengths = self.wavelengths.flatten()
        return self.wavelengths

    def io_to_dataframe(self):
        return pd.DataFrame({'wavelengths': self._get_wavelengths(),
                             'intensities': self._get_intensities()})

# ========================  IOMANAGER  ========================

if __name__ == "__main__":
    with IOManager() as iomanager:
        print(iomanager.spectrometers)
        df = iomanager.io_to_dataframe()
        print("Done!")

        df.plot(x='wavelengths',y='intensities')
        plt.show()


# ========================  IOMANAGER  ========================

# main()





# toprak_df = pd.DataFrame()
# for i, filename in enumerate(os.listdir('./')):
#     if 'data_toprak1' in filename:
#         df = pd.read_csv(filename)
#         toprak_df['{}_intensities'.format(i)] = df['intensities']
#         toprak_df['wavelengths'] = df['wavelengths']
#
# toprak_df.plot(x='wavelengths', alpha=0.7)
# plt.show()







