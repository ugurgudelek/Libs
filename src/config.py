

import configparser

class Config:
    """

    """

    def __init__(self, config_path='config.ini'):
        c = configparser.ConfigParser()
        c.read(config_path)

        self.db_dir = c['Paths']['db_dir']
        self.output_dir = c['Paths']['output_dir']
        # self.sample_dir = c['Paths']['sample_dir']

        self.peak_interval = float(c['Params']['peak_interval'])
        self.match_interval = float(c['Params']['match_interval'])
        self.outlier_interval = float(c['Params']['outlier_interval'])
        self.mode = c['Params']['mode']

        self.element_mapping = {elementname: c.get('ElementMapping', elementname).split(',') for elementname in
                                c.options('ElementMapping')}