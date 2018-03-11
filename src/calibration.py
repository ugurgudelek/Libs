import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

class CalibrationColumn:
    """

        Args:
            colname(str):

    """
    def __init__(self, colname):

        parts = colname.split(' ')
        self.raw_name = parts[0]
        self.name = parts[0].lower()
        self.id = int(parts[1])
        self.nm = float(parts[-1])

    def __str__(self):
        return '{el} {id} @ {nm}'.format(el=self.raw_name,
                                         id=self.id,
                                         nm=self.nm)



class Calibrator:
    """

            # fixme: probably we have one calibration file??
            # todo: not necessary to loop req_elements ??
            Assumes all calibration elements are same
    """
    def __init__(self, input_dir, output_dir):
        self.input_dir = input_dir
        self.output_dir = output_dir

        filename = os.listdir(self.input_dir)[0]
        self.xlsx = pd.ExcelFile(os.path.join(self.input_dir, filename))
        self.req_elements = self.extract_req_elements(sheet_name=self.xlsx.sheet_names[0])  # parse first sheet only

    def _parse_sheet(self, sheet_name):
        return self.xlsx.parse(sheet_name=sheet_name, header=1)

    def extract_req_elements(self, sheet_name):
        sheet = self._parse_sheet(sheet_name=sheet_name)
        # calibration_cols = [colname for colname in xlsx.columns if 'cal' in colname]
        # elements_at = [xlsx.loc[0, colname] for colname in calibration_cols]
        element_cols = sheet.columns[7:].values
        return [CalibrationColumn(element_col) for element_col in element_cols]

    def search_in_matches(self, matches, epsilon):
        """
        Requires extracted elements from excel file
        Args:
            matches(pd.DataFrame):
            epsilon(float):

        Returns:
            found(dict):

        """
        def _max(series):
            return 0 if len(series) == 0 else series.max()

        found = dict()
        for element in self.req_elements:

            df = matches.loc[matches['name'] == element.name]
            df = df.loc[((df['nm'] - epsilon) < element.nm) & (element.nm < (df['nm'] + epsilon))]

            intensity = _max(df['peak_intensities'])
            found[str(element)] = intensity

        return found

    def write_to_excel(self, sheet_name, col_names, values):
        #  write all calibration data to new excel file.
        sheet = self._parse_sheet(sheet_name=sheet_name)
        sheet[col_names] = values
        sheet.to_excel(os.path.join(self.output_dir, '{}.xlsx'.format(sheet_name)))

    def fit(self, dataframe):
        """

        Args:
            dataframe(pd.DataFrame):

        Returns:

        """
        raise Exception("These files are implement in calibration_fit.ipynb")

    def write_to_csv(self, dataframe, loc_name):
        dataframe.to_csv(os.path.join(self.output_dir, '{}.csv'.format(loc_name)), index=False)









