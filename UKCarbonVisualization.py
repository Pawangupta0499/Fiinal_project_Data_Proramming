#!/usr/bin/env python
# coding: utf-8

# In[9]:


from dash import Dash, dcc, html, Input, Output
from pymongo import MongoClient

client = MongoClient('mongodb+srv://data_programming:dpfall2023#@cluster0.dkjfyrj.mongodb.net/?retryWrites=true&w=majority')
database = client['UKCarbonAPI']
collection1 = database['HalfHourlyRegionalStats']  
collection2 = database['OverallCarbonStats'] 

app = dash.Dash(__name__)
server = app.server


def get_plot_data_collection2():
    data = collection2.find_one()['data']
    
    timestamps = [entry['from'] for entry in data]
    avg_intensity = [entry['intensity']['average'] for entry in data]
    min_intensity = [entry['intensity']['min'] for entry in data]
    max_intensity = [entry['intensity']['max'] for entry in data]
    
    return timestamps, avg_intensity, min_intensity, max_intensity


def get_plot_data_collection1():
    data = collection1.find_one()['data']
    
    region_names = []
    forecast_intensity = []
    
    for period in data:
        for region in period['regions']:
            region_names.append(region['shortname'])
            forecast_intensity.append(region['intensity']['forecast'])
    
    return region_names, forecast_intensity


def get_generation_mix_data(period_index, region_id):
    data = collection1.find_one()['data'][period_index]['regions'][region_id - 1] 
    
    fuel_types = [entry['fuel'] for entry in data['generationmix']]
    percentages = [entry['perc'] for entry in data['generationmix']]
    
    return fuel_types, percentages


app.layout = html.Div(children=[
    html.H1(children='Data Visualization'),

    dcc.Graph(
        id='graph2',
        figure={
            'data': [
                {'x': get_plot_data_collection2()[0], 'y': get_plot_data_collection2()[1], 'type': 'line', 'name': 'Average Intensity'},
                {'x': get_plot_data_collection2()[0], 'y': get_plot_data_collection2()[2], 'type': 'line', 'name': 'Min Intensity'},
                {'x': get_plot_data_collection2()[0], 'y': get_plot_data_collection2()[3], 'type': 'line', 'name': 'Max Intensity'}
            ],
            'layout': {
                'title': 'Carbon Intensity Over Time',
                'xaxis': {'title': 'Timestamp'},
                'yaxis': {'title': 'Intensity'}
            }
        }
    ),

    dcc.Graph(
        id='graph1-intensity',
        figure={
            'data': [
                {'x': get_plot_data_collection1()[0], 'y': get_plot_data_collection1()[1], 'type': 'bar', 'name': 'Forecast Intensity'}
            ],
            'layout': {
                'title': 'Carbon Intensity Forecast by Region',
                'xaxis': {'title': 'Region'},
                'yaxis': {'title': 'Forecast Intensity'}
            }
        }
    ),

    dcc.Dropdown(
        id='region-dropdown',
        options=[{'label': region, 'value': i + 1} for i, region in enumerate(get_plot_data_collection1()[0])],
        value=1, 
        style={'width': '50%'}
    ),

    
    dcc.Graph(
        id='graph1-generation-mix'
    )
])


@app.callback(
    Output('graph1-generation-mix', 'figure'),
    [Input('region-dropdown', 'value')]
)
def update_generation_mix(selected_region):
    
    period_index = 0 

    fuel_types, percentages = get_generation_mix_data(period_index, selected_region)

    pie_chart = {
        'data': [
            {
                'labels': fuel_types,
                'values': percentages,
                'type': 'pie',
                'hole': 0.4,
                'hoverinfo': 'label+percent'
            }
        ],
        'layout': {
            'title': f'Generation Mix for Region {selected_region} in Period {period_index + 1}',
            'showlegend': True
        }
    }

    return pie_chart

if __name__ == '__main__':
    app.run_server(debug=True)


# In[ ]:




