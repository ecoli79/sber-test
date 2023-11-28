from pydoc import classname
import dash
import numpy as np
from dash import html
from dash import dcc
from matplotlib.pyplot import figure
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
import dash_bootstrap_components as dbc
from dash import Input, Output
from plotly.subplots import make_subplots

# stylesheet with the .dbc class
#@dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

atms = pd.read_excel('Приложение №2.xlsx', engine='openpyxl')

zones = ['ОБСЛУЖИВАНИЕ УС', 'ОТМ', 'FLM', 'SLM', 'Средства', 'АДМ', 'ИТ']
#banks = atms['ТБ'].unique()
banks = np.append('Все банки', atms['ТБ'].unique())
types = atms['Тип УС'].unique()
atms['Доступность сети'] = round((100 - ((atms['Простой'] / atms['ФРВ']) * 100)),2)
for_plot = zones + ['Тип УС', 'Доступность сети', 'ДАТА']

def get_data_for_plot(bank, typeofatms):
    banks_for_plot = []
    
    if bank == "Все банки":
        banks_for_plot = banks
    else:
        banks_for_plot.append(bank)
        
    df_f = atms.loc[(atms['ТБ'].isin(banks_for_plot)) & (atms['Тип УС'].isin(typeofatms))][for_plot].groupby('ДАТА').mean()
    
    # setting for plot
    fig_zones = make_subplots(specs=[[{"secondary_y": True}]])

    fig_zones = px.bar(
        df_f,
        x = df_f.index,
        y = zones,
        labels = dict(x = 'дата', y = 'Зоны простоя'))

    fig_zones.add_trace(go.Scatter(x = df_f.index, y=df_f['Доступность сети'],
                                mode='lines+markers', name='Доступность сети', yaxis='y2'))

    fig_zones.update_layout(
            legend  = dict(
                            title = 'Зоны сети',
                            yanchor = 'top',
                            y = 1,
                            xanchor = 'left',
                            x= 1.1
                                    ),
            xaxis = dict(title = 'дата сообытия', 
                        tickangle = 45, 
                        tickformat='%d.%m.%Y', 
                        tickmode = 'linear'),
            yaxis = dict(title = 'Простои по зонам'),
            yaxis2 = dict(title = 'Доступность сети в %', 
                            title_standoff = 5, 
                            tickangle = 0, 
                            overlaying = 'y', 
                            side = 'right',
                            range = [0, 100]))
        
    return fig_zones


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(children=[
    html.H1(children='Простои и доступность сети', className="bg-primary text-white p-2 mb-2 text-center"),
    
    html.Div(children=[
    html.Div(children=[
    html.Div(children=[
    html.Div(
    [
        dbc.Label("Выбор банка:"),
        dcc.Dropdown(banks,banks[0], id="bank_choice"), 
    ],
    className="mb-4",
),
    html.Div([
        dbc.Label("Тип устройства:"),
        dbc.Checklist(
            id="type_of_atms",
            options=[{"label": i, "value": i} for i in types],
            value=types
        ),
    ],
    className="mb-4"),
    ],
     className="leftpanel col-2" ),
   
    ], className="row"),
    ], className="container" ),
    
     dcc.Graph(id='network_info', className="plot", figure={}),
])

@app.callback(
    Output('network_info', 'figure'),
    Input('bank_choice', 'value'),
    Input('type_of_atms', 'value'))
def update_plot(bank, typeofatms):
    
    fig_zones = get_data_for_plot(bank,typeofatms)
    fig_zones.update_layout()
    return fig_zones
    
if __name__ == "__main__":
    app.run_server(debug=True)