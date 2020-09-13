#!/usr/bin/env python
# coding: utf-8

# In[2]:


#Importing my libraries and GEMs new coal capacity data

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import json

coal_data = pd.read_csv('https://raw.githubusercontent.com/pmshea/coal_data/master/New%20Coal%20Plants%20by%20Country%20(MW)_____________.csv')


# In[3]:


#Cleaning GEM coal capacity data

columns = list(coal_data)

columns.remove('Country')

columns.remove('July 2020')

coal_data = coal_data.replace({',':''}, regex=True)

coal_data[columns] = coal_data[columns].apply(pd.to_numeric)

coal_data = coal_data.dropna()

years = columns


# In[4]:


#Drawing stacked area graph

area_graph = go.Figure()

area_graph.update_layout(legend=dict(
    yanchor="top",
    y=0.99,
    xanchor="left",
    x=0.01),
    title="",
    xaxis_title="",
    yaxis_title="MW of New Coal Capacity",
    legend_title=""
    )

area_graph.add_trace(go.Scatter(
    x=columns, y=coal_data[columns][coal_data.Country == 'Japan'].values.tolist()[0],
    mode='lines',
    name='Japan',
    line=dict(width=0.5, color='rgb(239, 51, 64)'),
    stackgroup='one'
))

area_graph.add_trace(go.Scatter(
    x=columns, y=coal_data[columns][coal_data.Country == 'Germany'].values.tolist()[0],
    mode='lines',
    name='Germany',
    line=dict(width=0.5, color='rgb(0, 0, 0)'),
    stackgroup='one'
))

area_graph.add_trace(go.Scatter(
    x=columns, y=coal_data[columns][coal_data.Country == 'United States'].values.tolist()[0],
    mode='lines',
    name='U.S.',
    line=dict(width=0.5, color='rgb(60, 59, 110)'),
    stackgroup='one'
))

area_graph.add_trace(go.Scatter(
    x=columns, y=coal_data[columns][coal_data.Country == 'India'].values.tolist()[0],
    mode='lines',
    name='India',
    line=dict(width=0.5, color='rgb(80, 158, 47)'),
    stackgroup='one'
))

area_graph.add_trace(go.Scatter(
    x=columns, y=coal_data[columns][coal_data.Country == 'China'].values.tolist()[0],
    mode='lines',
    name='China',
    line=dict(width=0.5, color='rgb(255, 255, 0)'),
    stackgroup='one'
))

area_graph.show()


# In[5]:


#Preparing GEM data for geographic animation -- basic cleaning & adding continent field

list_of_country_tables = []
for country in coal_data['Country']:
    year_list = []
    for year in columns: 
        year_list.append([country, coal_data[year][coal_data['Country'] == country].values, year])
    list_of_country_tables += year_list
    
split_countries = pd.DataFrame(list_of_country_tables)

countries_continents = pd.read_csv('https://raw.githubusercontent.com/pmshea/coal_data/master/Countries_Continents.csv')

countries_continents_coal = pd.merge(
    countries_continents, 
    split_countries.rename(columns={0: 'CNTRY_NAME'}),
    how='right'
)

countries_continents_coal = countries_continents_coal.dropna()
countries_continents_coal.rename(columns={1: 'MW_coal', 2: 'Year'}, inplace=True)
countries_continents_coal = countries_continents_coal[countries_continents_coal['Year'] != 'July 2020']

countries_continents_coal['MW_coal'] = countries_continents_coal['MW_coal'].str.get(0)

convert_dict = {'MW_coal': float, 
                'Year': int
               } 

countries_continents_coal = countries_continents_coal.astype(convert_dict)

print(countries_continents_coal.head())
print(countries_continents_coal.dtypes)


# In[6]:


#Preparing GEM data -- adding GDP data

GDP_data = pd.read_csv('https://raw.githubusercontent.com/pmshea/coal_data/master/gdppercapita_us_inflation_adjusted.csv')

list_final_2 = []
for country in GDP_data['country']:
    year_list2 = []
    for year in columns: 
        year_list2.append([country, GDP_data[year][GDP_data['country'] == country].values, year])
    list_final_2 += year_list2

GDP_split = pd.DataFrame(list_final_2)
convert_dict = {1: float, 
                2: int
               } 

GDP_split = GDP_split.astype(convert_dict)

GDP_split.rename(columns={1: 'GDP_per_capita', 2: 'Year'}, inplace=True)

Coal_GDP = pd.merge(
    countries_continents_coal, 
    GDP_split.rename(columns={0: 'CNTRY_NAME'}),
    how='left'
)


# In[7]:


#Preparing GEM data -- adding population data

pop_data = pd.read_csv('https://raw.githubusercontent.com/pmshea/coal_data/master/population_total%20(1).csv')

list_final_3 = []
for country in pop_data['country']:
    year_list3 = []
    for year in columns: 
        year_list3.append([country, pop_data[year][pop_data['country'] == country].values, year])
    list_final_3 += year_list3

pop_split = pd.DataFrame(list_final_3)
convert_dict = {1: float, 
                2: int
               } 

pop_split = pop_split.astype(convert_dict)

pop_split.rename(columns={1: 'Population', 2: 'Year'}, inplace=True)

Coal_GDP_Pop = pd.merge(
    Coal_GDP, 
    pop_split.rename(columns={0: 'CNTRY_NAME'}),
    how='left'
)

Grouped_Coal_GDP_Pop = Coal_GDP_Pop.groupby(['CONTINENT', 'Year'], as_index=False).agg({
    'GDP_per_capita': 'mean', 
    'Population': 'sum', 
    'MW_coal': 'sum'
}).reset_index()

Grouped_Coal_GDP_Pop['MW_coal'] = Grouped_Coal_GDP_Pop['MW_coal'].astype(int)

print(Grouped_Coal_GDP_Pop.head())

print(Coal_GDP_Pop[Coal_GDP_Pop['CONTINENT'] == 'Antarctica'])


# In[8]:


#Building figure architecture

continents = []
for continent in Grouped_Coal_GDP_Pop['CONTINENT']:
    if continent not in continents:
        continents.append(continent)
        
countries = []
for country in coal_data['Country']:
    if country not in countries:
        countries.append(country)

fig_dict = {
    'data': [],
    'layout': {},
    'frames': []
}

fig_dict["layout"]["xaxis"] = {"range": [2000, 2020], "title": "Population", "type": "log", 'autorange': True}
fig_dict["layout"]["yaxis"] = {"title": "Mean Per Capita GDP", "type": "log", 'autorange': True}
fig_dict["layout"]["hovermode"] = "closest"
fig_dict['layout']['showlegend'] = True
fig_dict['layout']['sliders'] = {
    'args': [
        'slider.value', {
            'duration': 400,
            'ease': 'cubic-in-out'
        }
    ],
    'initialValue': '2000',
    'plotlycommand': 'animate',
    'values': years,
    'visible': True
}

fig_dict["layout"]["updatemenus"] = [
    {
        "buttons": [
            {
                "args": [None, {"frame": {"duration": 500, "redraw": False},
                                "fromcurrent": True, "transition": {"duration": 300,
                                                                    "easing": "quadratic-in-out"}}],
                "label": "Play",
                "method": "animate"
            },
            {
                "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                  "mode": "immediate",
                                  "transition": {"duration": 0}}],
                "label": "Pause",
                "method": "animate"
            }
        ],
        "direction": "left",
        "pad": {"r": 10, "t": 87},
        "showactive": False,
        "type": "buttons",
        "x": 0.1,
        "xanchor": "right",
        "y": 0,
        "yanchor": "top"
    }
]

sliders_dict = {
    "active": 0,
    "yanchor": "top",
    "xanchor": "left",
    "currentvalue": {
        "font": {"size": 20},
        "prefix": "Year:",
        "visible": True,
        "xanchor": "right"
    },
    "transition": {"duration": 300, "easing": "cubic-in-out"},
    "pad": {"b": 10, "t": 50},
    "len": 0.9,
    "x": 0.1,
    "y": 0,
    "steps": []
}

year = 2000
for continent in continents:
    dataset_by_year = Grouped_Coal_GDP_Pop[Grouped_Coal_GDP_Pop['Year'] == year]
    dataset_by_year_and_cont = dataset_by_year[
        dataset_by_year['CONTINENT'] == continent]

    data_dict = {
        'x': list(dataset_by_year_and_cont['Population']),
        'y': list(dataset_by_year_and_cont['GDP_per_capita']),
        'mode': 'markers',
        'text': list(dataset_by_year_and_cont['CONTINENT']),
        'marker': {
            'sizemode': 'area',
            'sizeref': 5,
            'size': list(dataset_by_year_and_cont['MW_coal'])
        },
        'name': continent
    }
    fig_dict['data'].append(data_dict)

for year in columns:
    frame = {"data": [], "name": str(year)}
    for continent in continents:
        dataset_by_year = Grouped_Coal_GDP_Pop[Grouped_Coal_GDP_Pop['Year'] == int(year)]
        dataset_by_year_and_cont = dataset_by_year[
            dataset_by_year['CONTINENT'] == continent]

        data_dict = {
            "x": list(dataset_by_year_and_cont["Population"]),
            "y": list(dataset_by_year_and_cont["GDP_per_capita"]),
            "mode": "markers",
            "text": list(dataset_by_year_and_cont["CONTINENT"]),
            "marker": {
                "sizemode": "area",
                "sizeref": 5,
                "size": list(dataset_by_year_and_cont['MW_coal'])
            },
            "name": continent
        }
        frame["data"].append(data_dict)

    fig_dict["frames"].append(frame)
    slider_step = {"args": [
        [year],
        {"frame": {"duration": 300, "redraw": False},
         "mode": "immediate",
         "transition": {"duration": 300}}
    ],
        "label": year,
        "method": "animate"}
    sliders_dict["steps"].append(slider_step)

fig_dict["layout"]["sliders"] = [sliders_dict]

fig = go.Figure(fig_dict)

fig.show()


# In[ ]:


#Deploying elements to server as a dashboard with Plotly's Dash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

application = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = application.server

fig.update_layout(
    autosize=False,
    width=875,
    height=500,
    font=dict(family="Arial, monospace"),
    margin=dict(
        l=100,
        r=10,
        b=20,
        t=30,
        pad=4
    )
)

fig.add_layout_image(
    dict(
        source="endcoal-logo_real.png",
        xref="paper", yref="paper",
        x=1, y=1.05,
        sizex=0.2, sizey=0.2,
        xanchor="right", yanchor="bottom"
    )
)
    
area_graph.update_layout(
    autosize=False,
    width=600,
    height=500,
    font=dict(family="ProximaNova, monospace"),
    margin=dict(
        l=50,
        r=50,
        b=20,
        t=30,
        pad=4
    )
)

application.layout = html.Div([
    
    html.Div(
        dcc.Graph(id='g1', figure=area_graph),
        className='four columns'
    ),
    
    html.Div(
        dcc.Graph(id='g2', figure=fig),
        className='four columns'
    )
], className='row')

if __name__ == '__main__':
    application.run_server()


# In[ ]:




