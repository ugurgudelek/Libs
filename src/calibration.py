import pandas as pd
import numpy as np
import os

class CalibrationColumn:
    """

        Args:
            colname(str):

    """
    def __init__(self, colname):

        parts = colname.split(' ')
        self.element = parts[0]
        self.id = parts[1]
        self.nm = parts[-1]

    def __str__(self):
        return '{el} {id} @ {nm}'.format(el=self.element,
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
        self.req_elements = self.extract_req_elements(sheet_name=self.xlsx.sheet_names[0]) # parse first sheet only

    def _parse_sheet(self, sheet_name):
        return self.xlsx.parse(sheet_name=sheet_name, header=1)

    def extract_req_elements(self, sheet_name):
        sheet = self._parse_sheet(sheet_name=sheet_name)
        # calibration_cols = [colname for colname in xlsx.columns if 'cal' in colname]
        # elements_at = [xlsx.loc[0, colname] for colname in calibration_cols]
        elements_at = sheet.columns[7:].values
        elements = dict()
        for element_at in elements_at:
            element_name = element_at.split('@')[0].strip()
            nm = float(element_at.split('@')[1].strip())
            elements[element_name] = nm
        return elements

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
        for element, at in self.req_elements.items():
            name, num = element.split(' ')
            df = matches.loc[matches['name'] == name.lower()]
            df = df.loc[((df['nm'] - epsilon) < at) & (at < (df['nm'] + epsilon))]

            intensity = _max(df['peak_intensities'])

            col_name = '{name} {num} @ {at}'.format(name=name, num=num, at=at)
            found[col_name] = intensity

        return found

    def write_to_excel(self, sheet_name, col_names, values):
        #  write all calibration data to new excel file.
        sheet = self._parse_sheet(sheet_name=sheet_name)
        sheet[col_names] = values
        sheet.to_excel(os.path.join(self.output_dir, '{}.xlsx'.format(sheet_name)))






