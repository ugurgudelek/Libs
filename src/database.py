import pandas as pd
import os

class Database:
    """

    """

    def __init__(self, config):

        self.element_mapping = config.element_mapping
        self.db_dir = config.db_dir
        self.spectrometer_interval = config.spectrometer_interval

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
                # drop extension to check element mapping
                if filename.split('.')[0] in self.element_mapping.keys():
                    database = database.append(pd.read_csv(os.path.join(self.db_dir, filename), skipinitialspace=True))

        # drop out-of-range database
        database = database.loc[(database['nm'] > self.spectrometer_interval[0]) &
                                (database['nm'] < self.spectrometer_interval[1])]

        dataset = database.reset_index(drop=True)
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
        found = self.database.loc[((self.database['nm'] - threshold) < value) &
                                 (value < (self.database['nm'] + threshold))]
        return found


