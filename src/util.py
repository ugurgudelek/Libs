import math
import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import seaborn as sns
from os.path import dirname, join

from bokeh.plotting import figure,show, output_file, output_notebook
from bokeh.models import ColumnDataSource, HoverTool, Div
from bokeh.models.widgets import Slider, Select
from bokeh.layouts import layout, widgetbox, row
from bokeh.io import curdoc



def rename(path, search_name):

    valid_folders = [foldername for foldername in os.listdir(path) if search_name in foldername]

    for foldername in valid_folders:
        src_name = foldername
        target_name = foldername.split(search_name)[-1]
        os.rename(os.path.join(path, src_name), os.path.join(path, target_name))


def plot_calibration_fit(loc_name='niğde', element_name='% Azot', calibration_num=1):

    df = pd.read_csv(open(u'../output/calibration/{}/{}.csv'.format(calibration_num,loc_name), 'rb'))
    df['sample_id'] = list(range(1, df.shape[0] + 1))

    element_values = pd.read_excel(open(u'../output/calibration/{}/{}.xlsx'.format(calibration_num,loc_name), 'rb'))[element_name].values
    df[element_name] = list(map(float, element_values))

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
            regplot = sns.regplot(data=df, x=str(element), y=element_name, color='r', marker='+')
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


if __name__ == "__main__":
    # plot_calibration_fit('niğde', calibration_num=2)
    # plot_calibration_fit('adana', element_name='Potasyum(ppm)',calibration_num=4)
    # plot_calibration_fit('samsun', calibration_num=2)
    # plot_calibration_fit('yozgat', calibration_num=2)

    loc_name = 'adana'
    element_name = '% Azot'
    calibration_num = 4



    xlsx = pd.read_excel(open(u'../output/calibration/{}/{}.xlsx'.format(calibration_num, loc_name), 'rb'))

    xlsx = xlsx.rename(columns={'SIRA NO':'sample_id', 'LAB NO':'lab_no', 'DERİNLİK':'depth',
                       '% Azot':'%N', '% Organik Madde':'%C','Potasyum(ppm)':'%K', 'Fosfor(ppm)':'%P'})


    def plot_bokeh(xlsx):

        # elements = [CalibrationColumn(colname) for colname in xlsx.columns[7:]]

        xlsx = xlsx.to_dict(orient='list')

        output_file("plot_sample.html", title="Plot sample")

        element_selector = Select(title="Elements", value=list(xlsx.keys())[7],
                       options=list(xlsx.keys())[7:])

        # Create Column Data Source that will be used by the plot
        # source = ColumnDataSource(data=dict(x=[], y=[], sample_id=[]))
        hover = HoverTool(tooltips=[
            ("Sample ID", "@sample_id")
        ])


        def create_figure():
            xs = xlsx[element_selector.value]
            ys = xlsx['%N']
            p = figure(plot_height=600, plot_width=700, title="Lel", toolbar_location=None, tools=[hover])
            p.circle(x=xs, y=ys, size=7, line_color=None)
            return p

        def update(attr, old, new):
            # element_name = element_selector.value
            # source.data = dict(x=xlsx[element_name], y=xlsx['%N'], sample_id=xlsx['sample_id'])
            layout.children[1] = create_figure()



        element_selector.on_change('value', update)

        controls = widgetbox(element_selector, sizing_mode='fixed')
        layout = row(controls, create_figure())
        # l = layout([inputs, p], sizing_mode='fixed')





        # show(widgetbox(genre))
        curdoc().add_root(layout)
        curdoc().title = "Test"


    plot_bokeh(xlsx)





