
# coding: utf-8

# # Implementation of interactive bokeh plot for LIBS

# In[32]:

from bokeh.plotting import figure,show, output_file, output_notebook,save
from bokeh.models import ColumnDataSource, HoverTool, Div
from bokeh.models.widgets import Slider, Select
from bokeh.layouts import layout, widgetbox, row
from bokeh.io import curdoc
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application

import pandas as pd
import os


# In[14]:

def read_dataset(path):

    xlsx = pd.read_excel(open(path, 'rb'))

    xlsx = xlsx.rename(columns={'SIRA NO':'sample_id', 'LAB NO':'lab_no', 'DERİNLİK':'depth',
                       '% Azot':'%N', '% Organik Madde':'%C','Potasyum(ppm)':'%K', 'Fosfor(ppm)':'%P'})
    return xlsx


# In[33]:
output_file('calibration.html', title='Kalibrasyon')

def read_datasets():
    """Reads all location files and returns dictionary of datasets"""


    datasets = dict()
    for loc_name in loc_names:
        path = u'../output/calibration/{}.xlsx'.format(loc_name)
        dataset = read_dataset(path)
        datasets[loc_name] = dataset

    return datasets

def make_dataset(dataset, xname, yname):
    """
        element: C 1 @ 279.482
        value : %N,%C,%K,%P
    """
    df = pd.DataFrame()
    df['xs'] = dataset[xname]
    df['ys'] = dataset[yname]
    df['sample_id'] = dataset['sample_id']
    return df

def make_plot(src):
    p = figure(plot_height=600, plot_width=700, title="Kalibrasyon Grafikleri", toolbar_location=None)
    p.circle(source=src, x='xs', y='ys', line_color='blue')
    hover = HoverTool(tooltips=[("Sample ID", "@sample_id")])
    p.add_tools(hover)
    return p

def update(attr, old, new):
    new_source = make_dataset(datasets[loc_selector.value],
                                    element_selector.value,
                                    display_attribute_selector.value)
    new_source = ColumnDataSource(new_source)
    src.data.update(new_source.data)

loc_names = ['adana','samsun','yozgat']
datasets = read_datasets()
elements = list(datasets['adana'].columns.values[7:])
display_attributes = ['%N','%C','%K','%P']



loc_selector = Select(title="Location", value=loc_names[0],
                          options=loc_names)

display_attribute_selector = Select(title="Display Elements", value=display_attributes[0],
                          options=display_attributes)
element_selector = Select(title="Elements", value=elements[0],
                          options=elements)

loc_selector.on_change('value', update)
display_attribute_selector.on_change('value', update)
element_selector.on_change('value', update)
controls = widgetbox([loc_selector, display_attribute_selector, element_selector])

# initial dataset
src = ColumnDataSource(make_dataset(datasets[loc_selector.value],
                                    element_selector.value,
                                    display_attribute_selector.value))
p = make_plot(src)


layout = row(controls, p)
curdoc().add_root(layout)



# handler = FunctionHandler(modify_doc)
# app = Application(handler)

# output_notebook()

# show(app)
