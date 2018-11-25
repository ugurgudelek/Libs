
# coding: utf-8

# # Implementation of interactive bokeh plot for LIBS

# In[32]:

from bokeh.plotting import figure,show, output_file, output_notebook,save
from bokeh.models import ColumnDataSource, HoverTool, Div
from bokeh.models.widgets import Slider, Select, Panel, Tabs
from bokeh.layouts import widgetbox, row
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

def make_dataset(dataset, location_name, line_color):
    """
        element: C 1 @ 279.482
        value : %N,%C,%K,%P
    """
    xname = display_attribute_selector.value
    yname = element_selector.value
    df = pd.DataFrame()

    df['xs'] = dataset[xname]
    df['ys'] = dataset[yname]
    df['xname'] = xname
    df['yname'] = yname
    df['sample_id'] = dataset['sample_id']
    df['lab_no'] = dataset['lab_no']
    df['N'] = dataset['%N']
    df['C'] = dataset['%C']
    df['K'] = dataset['%K']
    df['P'] = dataset['%P']
    df['line_color'] = line_color
    df['location'] = location_name
    return df

def make_multi_dataset():
    d_adana = make_dataset(datasets['adana'], location_name='adana', line_color='blue')
    d_samsun = make_dataset(datasets['samsun'], location_name='samsun', line_color='green')
    d_yozgat = make_dataset(datasets['yozgat'], location_name='yozgat', line_color='red')
    d_nigde = make_dataset(datasets['nigde'], location_name='nigde', line_color='yellow')

    df = d_adana.append(d_samsun, ignore_index=True)
    df = df.append(d_yozgat, ignore_index=True)
    df = df.append(d_nigde, ignore_index=True)

    return df



def make_plot(src):
    p = figure(plot_height=700, plot_width=700, title="Kalibrasyon Grafikleri",
               toolbar_location="below",
               toolbar_sticky=False)
    p.circle(source=src, x='xs', y='ys', fill_color='line_color', size=8, legend='location')
    hover = HoverTool(tooltips=[("Loc", "@location"),
                                ("Sample ID", "@sample_id"),
                                ("Lab No", "@lab_no"),
                                ("%N","@N"),
                                ("%C","@C"),
                                ("%K","@K"),
                                ("%P","@P"),
                                ("index", "$index"),
                                ("data (x,y)", "($x, $y)"),
                                ("coor (x,y)", "($sx, $sy)")
                                ])
    p.add_tools(hover)
    return p

def update(attr, old, new):

    if MULTI:
        new_source = make_multi_dataset()
    else:
        new_source = make_dataset(datasets[loc_selector.value],
                                  location_name = loc_selector.value,
                                  line_color = 'blue')
    src.data.update(ColumnDataSource(new_source).data)
    p.xaxis.axis_label =  display_attribute_selector.value
    p.yaxis.axis_label =  element_selector.value

loc_names = ['adana','samsun','yozgat', 'nigde']
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



# one-by-one plot
# MULTI=False
# src = ColumnDataSource(make_dataset(datasets[loc_selector.value], location_name=loc_selector.value, line_color='blue'))
# p = make_plot(src)
# p.xaxis.axis_label =  display_attribute_selector.value
# p.yaxis.axis_label =  element_selector.value
# layout = row(controls, p)


# all-in-one plot
MULTI=True
src = ColumnDataSource(make_multi_dataset())
p = make_plot(src)
p.xaxis.axis_label =  display_attribute_selector.value
p.yaxis.axis_label =  element_selector.value
layout = row(controls, p)


p.legend.location = "top_right"
p.legend.click_policy="hide"

tab = Panel(child=layout, title="Kalibrasyon")
tabs = Tabs(tabs=[tab])
curdoc().add_root(tabs)



# handler = FunctionHandler(modify_doc)
# app = Application(handler)

# output_notebook()

# show(app)
