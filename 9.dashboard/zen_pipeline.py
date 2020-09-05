#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import getopt
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine

if __name__ == "__main__":
    unixOptions = "s:e"  
    gnuOptions = ["start_dt=", "end_dt="]

    fullCmdArguments = sys.argv
    argumentList = fullCmdArguments[1:]

    try:  
        arguments, values = getopt.getopt(argumentList, unixOptions, gnuOptions)
    except getopt.error as err:  
        print (str(err))
        sys.exit(2)
        
    start_dt = '2019-09-24 18:00:00'
    end_dt = '2019-09-24 19:00:00'
    for currentArgument, currentValue in arguments:  
        if currentArgument in ("-s", "--start_dt"):
            start_dt = currentValue                                   
        elif currentArgument in ("-e", "--end_dt"):
            end_dt = currentValue  
        
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
    
    query = '''
                select * from log_raw
            '''

    raw = pd.io.sql.read_sql(query, con = engine)
    raw['dt']=raw['ts'].apply(lambda x: datetime.fromtimestamp(x/1000))
    raw['dt']=pd.to_datetime(raw['dt']).dt.round('min')
    
    dash_visits=raw.groupby(['item_topic','source_topic','age_segment','dt']).agg({'event':'count'})
    dash_visits.columns=['visits']
    dash_visits=dash_visits.reset_index()
    
    
    dash_engagement=raw.groupby(['dt','item_topic','event','age_segment']).agg({'user_id':'nunique'})
    dash_engagement.columns=['unique_users']
    dash_engagement=dash_engagement.reset_index()
    
    tables = {'dash_visits': dash_visits,'dash_engagement': dash_engagement}

    for table_name, table_data in tables.items():
        query = '''
                DELETE FROM {} WHERE dt BETWEEN '{}'::TIMESTAMP AND '{}'::TIMESTAMP
                '''.format(table_name, start_dt, end_dt)
        engine.execute(query)

        table_data.to_sql(name = table_name, con = engine, if_exists = 'append', index = False)
    print('All done')

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    