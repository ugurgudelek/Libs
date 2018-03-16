import math
import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import seaborn as sns

def rename(path, search_name):

    valid_folders = [foldername for foldername in os.listdir(path) if search_name in foldername]

    for foldername in valid_folders:
        src_name = foldername
        target_name = foldername.split(search_name)[-1]
        os.rename(os.path.join(path, src_name), os.path.join(path, target_name))


def plot_calibration_fit(loc_name='niğde', calibration_num=1):

    df = pd.read_csv(open(u'../output/calibration/{}/{}.csv'.format(calibration_num,loc_name), 'rb'))
    df['sample_id'] = list(range(1, df.shape[0] + 1))

    N_values = pd.read_excel(open(u'../output/calibration/{}/{}.xlsx'.format(calibration_num,loc_name), 'rb'))['% Azot'].values
    df['%N'] = list(map(float,N_values))

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

    elements = [CalibrationColumn(colname) for colname in df.columns[:-2]]

    def plot_calibrations(elements, path):
        for element in elements:
            regplot = sns.regplot(data=df, x=str(element), y='%N', color='r', marker='+')
            regplot.get_figure().savefig(os.path.join(path, '{}.png'.format(str(element))))
            plt.clf()

    try:

        os.makedirs('../output/calibration_plots/{}/{}'.format(calibration_num,loc_name))
    except:
        pass

    plot_calibrations(elements, '../output/calibration_plots/{}/{}'.format(calibration_num,loc_name))


def subplot(dictionary, xname, yname, ncols=None, nrows=None):
    """

    Args:
        self:
        dictionary:
        xname:
        yname:
        ncols:

    Returns:

    """

    if nrows is None:
        if ncols is None:
            raise Exception('Please enter nrows or ncols only, not both')
        nrows = int(math.ceil(len(dictionary) / ncols))
    if ncols is None:
        if nrows is None:
            raise Exception('Please enter nrows or ncols only, not both')
        ncols = int(math.ceil(len(dictionary) / nrows))

    fig, axs = plt.subplots(nrows, ncols, sharex=True, sharey=True)
    axs = axs.reshape(nrows, ncols)
    for i, (name, reading) in enumerate(dictionary.items()):

        x = reading[xname]
        y = reading[yname]
        axs[i // ncols, i % ncols].plot(x, y)
        axs[i // ncols, i % ncols].set_title(name)
        axs[i // ncols, i % ncols].grid( which='both', color='r', linestyle='--', linewidth=0.5)


    plt.show()


if __name__ == "__main__":
    # plot_calibration_fit('niğde', calibration_num=2)
    # plot_calibration_fit('adana', calibration_num=2)
    plot_calibration_fit('samsun', calibration_num=2)
    plot_calibration_fit('yozgat', calibration_num=2)