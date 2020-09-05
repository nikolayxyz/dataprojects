#!/usr/bin/python
# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine

db_config = {'user': 'user1',         # имя пользователя
             'pwd': '123456', # пароль
             'host': 'localhost',       # адрес сервера
             'port': 5432,              # порт подключения
             'db': 'zen'}             # название базы данных


connection_string = 'postgresql://{}:{}@{}:{}/{}'.format(db_config['user'],
                                                                     db_config['pwd'],
                                                                       db_config['host'],
                                                                       db_config['port'],
                                                                       db_config['db'])

engine = create_engine(connection_string)

query='''SELECT * FROM dash_visits '''
dash_visits = pd.io.sql.read_sql(query, con = engine)

query='''SELECT * FROM dash_engagement '''
dash_engagement = pd.io.sql.read_sql(query, con = engine)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Дашборд для Яндекс.Дзена'),

    html.Div(children='''
        На данном дешборде вы сможете проанализировать данные из Яндекс.Дзена в разрезе времени, тем, возрастных категорий.
        Используйте выбор интервала даты и времени истории событий по темам карточек и интервал возрастных категорий для управления дашбордом.
        Используйте выбор тем карточек для анализа графика разбивки событий по темам источников.
    '''),
    html.Div([  

        html.Div([
            # выбор временного периода
            html.Label('Временной период:'),
            dcc.DatePickerRange(
                start_date = dash_visits['dt'].min(),
                end_date = dash_visits['dt'].max(),
                display_format = 'YYYY-MM-DD HH:MM',
                id = 'dt_selector',       
            ),
        ], className = 'two columns'),

        html.Div([    
            # фильтр возрастных категорий
            html.Label('Возрастные категории:'),
            dcc.Dropdown(
                options = [{'label': x, 'value': x} for x in dash_visits['age_segment'].unique()],
                value = dash_visits['age_segment'].unique().tolist(),
                multi = True,
                id = 'age-dropdown'
            ),                   
        ], className = 'four columns') ,               

        html.Div([         
            # фильтр тем
            html.Label('Темы карточек:'),
            dcc.Dropdown(
                options = [{'label': x, 'value': x} for x in dash_visits['source_topic'].unique()],
                value = dash_visits['source_topic'].unique().tolist(),
                multi = True,
                id = 'item-topic-dropdown'
            ),                
        ], className = 'six columns'),
        html.Div([
            html.Label('История событий по темам карточек'),
            dcc.Graph(
            id = 'history-absolute-visits',
            style = {'height': '50vw'}),
        ], className = 'six columns'),
        html.Div([
            html.Div([
            html.Label('Разбивка событий по темам источников'),
            dcc.Graph(
            id = 'pie-visits',
            style = {'height': '25vw'}),
        ], className = 'six columns'),
        html.Div([
            html.Div([
            html.Label('Среднее количество уникальных пользователей'),
            dcc.Graph(
            id = 'engagement-graph',
            style = {'height': '25vw'})
        ], className = 'six columns')
        ])
        ])

    ], className = 'row') , 
])

@app.callback([Output('history-absolute-visits', 'figure'),
               Output('pie-visits', 'figure'),
               Output('engagement-graph', 'figure')],
              [Input('item-topic-dropdown', 'value'),
               Input('age-dropdown', 'value'),
               Input('dt_selector', 'start_date'),
               Input('dt_selector', 'end_date')
    ])
def update_figures(selected_item_topics,selected_ages,start_date, end_date):
    dash_visits_filtered=dash_visits.query('item_topic.isin(@selected_item_topics) and \
       dt >= @start_date and dt <= @end_date \
       and age_segment.isin(@selected_ages)')
    
    dash_visits_by_item=dash_visits_filtered.groupby(['item_topic', 'dt']).agg({'visits': 'count'}).reset_index()
                         
    history_absolute_visits = []
                         
    for item_topic in dash_visits_by_item['item_topic'].unique():
                         history_absolute_visits += [go.Scatter(x = dash_visits_by_item.query('item_topic == @item_topic')['dt'],y = dash_visits_by_item.query('item_topic == @item_topic')['visits'],mode = 'lines',                               stackgroup = 'one',name = item_topic)]
    dash_visits_by_source = dash_visits.groupby('source_topic').agg({'visits': 'count'}).reset_index()
    pie_visits=[go.Pie(labels = dash_visits_by_source['source_topic'],values = dash_visits_by_source['visits'])]
    dash_engagement_filtered = dash_engagement.query('item_topic.isin(@selected_item_topics) and \
 dt >= @start_date and dt <= @end_date \
 and age_segment.isin(@selected_ages)')
    dash_engagement_by_event = dash_engagement_filtered.groupby('event').agg({'unique_users': 'mean'}).reset_index()
    dash_engagement_by_event = dash_engagement_by_event.sort_values('unique_users', ascending = False)
    engagement_graph = [go.Bar(x = dash_engagement_by_event['event'],
                               y = dash_engagement_by_event['unique_users'])]
    return (
            {
                'data': history_absolute_visits,
                'layout': go.Layout(xaxis = {'title': 'Время'},
                                    yaxis = {'title': 'События'})
            },
        
            {
                'data': pie_visits,
                'layout': go.Layout()
            },             
            {
                'data': engagement_graph,
                'layout': go.Layout(xaxis = {'title' : 'Событие'},yaxis = {'title': 'Количество пользователей'})
            }
    )


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=3000)