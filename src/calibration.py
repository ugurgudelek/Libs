import pandas as pd
import numpy as np



class Calibrator():

    def __init__(self, config):
        self.path = config.calibration_path


        self.elements, self.xlsx = self.parse_excel(self.path)

    def parse_excel(self, path):
        xlsx = pd.read_excel(path, 'NİĞDE', header=1)
        # calibration_cols = [colname for colname in xlsx.columns if 'cal' in colname]
        # elements_at = [xlsx.loc[0, colname] for colname in calibration_cols]
        elements_at = xlsx.columns[7:].values
        elements = dict()
        for element_at in elements_at:
            element_name = element_at.split('@')[0].strip()
            nm = float(element_at.split('@')[1].strip())
            elements[element_name] = nm
        return elements, xlsx

    def search_in_matches(self, matches, epsilon=0.1):
        """

        Args:
            matches:
            epsilon:

        Returns:
            found(dict):

        """
        def _max(series):
            return 0 if len(series) == 0 else series.max()

        found = dict()
        for element, at in self.elements.items():
            name, num = element.split(' ')
            df = matches.loc[matches['name'] == name.lower()]
            df = df.loc[((df['nm'] - epsilon) < at) & (at < (df['nm'] + epsilon))]

            intensity = _max(df['peak_intensities'])

            col_name = '{name} {num} @ {at}'.format(name=name, num=num, at=at)
            found[col_name] = intensity

        return found






