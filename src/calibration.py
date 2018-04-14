import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

# class CalibrationColumn:
#     """
#
#         Args:
#             colname(str):
#
#     """
#     def __init__(self, colname):
#
#         parts = colname.split(' ')
#         self.raw_name = parts[0]
#         self.name = parts[0].lower()
#         self.id = int(parts[1])
#         self.nm = float(parts[-1])
#
#     def __str__(self):
#         return '{el} {id} @ {nm}'.format(el=self.raw_name,
#                                          id=self.id,
#                                          nm=self.nm)

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

    def __repr__(self):
        return self.__str__()



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
        return self.xlsx.parse(sheet_name, header=1)

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
        sheet.loc[:values.shape[0] - 1, col_names] = values  # selects up to and including
        sheet.to_excel(os.path.join(self.output_dir, '{}.xlsx'.format(sheet_name)))


    def read_calibration_file(self, path=None):
        calibration_num = 1
        loc_name = 'adana'

        calibration_csv = u'../output/calibration/{}/{}.csv'.format(calibration_num, loc_name)
        calibration_xlsx = u'../output/calibration/{}/{}.xlsx'.format(calibration_num, loc_name)

        df = pd.read_csv(open(calibration_csv, 'rb'))
        df['sample_id'] = list(range(1, df.shape[0] + 1))

        N_values = pd.read_excel(open(calibration_xlsx, 'rb'))['% Azot'].values
        df['%N'] = N_values

        elements = [CalibrationColumn(colname) for colname in df.columns[:-2]]

        regplot = sns.regplot(data=df, x=str(elements[0]), y='%N', color='r', marker='+')

        x = df['C 1 @ 279.408'].values
        y = df['%N'].values
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

        return (slope, intercept)

    def fit(self, X):
        """

        Args:
            dataframe(pd.DataFrame):

        Returns:

        """
        # raise Exception("These files are implement in calibration_fit.ipynb")


        # (slope, intercept) = self.read_calibration_file()
        # return slope*X + intercept

        return (X - 140) / 741.2


    def write_to_csv(self, dataframe, loc_name):
        dataframe.to_csv(os.path.join(self.output_dir, '{}.csv'.format(loc_name)), index=False)









