

import configparser
import os

class Config:
    """

    """

    def __init__(self, config_path='config.ini'):
        c = configparser.ConfigParser()
        c.read(config_path)

        # Inputs
        self.input_dir = c['Paths']['input_dir']
        self.db_dir = os.path.join(self.input_dir, 'database')
        self.calibration_input_dir = os.path.join(self.input_dir, 'calibration')
        self.fake_sample_dir = os.path.join(self.input_dir, 'fakesamples')

        # Outputs
        self.output_dir = c['Paths']['output_dir']
        self.sample_output_dir = os.path.join(self.output_dir, 'samples')
        self.calibration_output_dir = os.path.join(self.output_dir, 'calibration')


        self.peak_interval = float(c['Params']['peak_interval'])
        self.match_interval = float(c['Params']['match_interval'])
        self.outlier_interval = float(c['Params']['outlier_interval'])
        self.spectrometer_interval = [float(interval) for interval in c['Params']['spectrometer_interval'].split(',')]
        self.mode = c['Params']['mode']
        self.fake = False if c['Params']['fake'] == 'False' else True
        self.calibration_epsion = float(c['Params']['calibration_epsilon'])


        self.element_mapping = {elementname: c.get('ElementMapping', elementname).split(',') for elementname in
                                c.options('ElementMapping')}