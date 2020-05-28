# A class that loads schedule data from the database and
# provides various accessor methods for it

import pandas as pd
import psycopg2 as pg
import numpy as np
from scipy import stats
from dotenv import load_dotenv
import os

class Schedule:
    def __init__(self, route_id, date):
        """
        The Schedule class loads the schedule for a particular route and day,
        and makes several accessor methods available for it.

        Parameters:

        route_id (str)
            - The route id to load
        
        date (str or pd.Timestamp)
            - Which date to load  
            - Converted with pandas.to_datetime so many formats are acceptable
        """

        self.route_id = str(route_id)
        self.date = pd.to_datetime(date)

        # load the schedule for that date and route
        self.route_data = load_schedule(self.route_id, self.date)

        # process data into a table
        self.inbound_table, self.outbound_table = extract_schedule_tables(self.route_data)

        # calculate the common interval values
        self.mean_interval, self.common_interval = get_common_intervals(
                                    [self.inbound_table, self.outbound_table])

def extract_schedule_tables(route_data):
    """
    converts raw schedule data to two pandas dataframes

    columns are stops, and rows are individual trips

    returns inbound_df, outbound_df
    """

    # assuming 2 entries, but not assuming order
    if(route_data[0]['direction'] == 'Inbound'):
        inbound = 0
    else:
        inbound = 1

    # extract a list of stops to act as columns
    inbound_stops = [s['tag'] for s in route_data[inbound]['header']['stop']]

    #initialize dataframe
    inbound_df = pd.DataFrame(columns=inbound_stops)

    # extract each row from the data
    i = 0
    for trip in route_data[inbound]['tr']:
        for stop in trip['stop']:
            # '--' indicates the bus is not going to that stop on this trip
            if stop['content'] != '--':
                inbound_df.at[i, stop['tag']] = stop['content']
        # increment for the next row
        i += 1

    # flip between 0 and 1
    outbound = int(not inbound)

    # repeat steps for the outbound schedule
    outbound_stops = [s['tag'] for s in route_data[outbound]['header']['stop']]
    outbound_df = pd.DataFrame(columns=outbound_stops)

    i = 0
    for trip in route_data[outbound]['tr']:
        for stop in trip['stop']:
            if stop['content'] != '--':
                outbound_df.at[i, stop['tag']] = stop['content']
        i += 1
    
    # return both dataframes
    return inbound_df, outbound_df

def load_schedule(route, date):
    """ 
    loads schedule data from the database and returns it

    Parameters:

        route (str)
            - The route id to load
        
        date (str or pd.Timestamp)
            - Which date to load  
            - Converted with pandas.to_datetime so many formats are acceptable
    """

    # ensure correct parameter types
    route = str(route)
    date = pd.to_datetime(date)

    # load environment variables for DB connection
    load_dotenv()
    creds = {
        'user': os.environ.get('USER'),
        'password': os.environ.get('PASSWORD'),
        'host': os.environ.get('HOST'),
        'dbname': os.environ.get('DATABASE')
    }

    # initialize DB connection
    cnx = pg.connect(**creds)
    cursor = cnx.cursor()

    # build selection query
    query = """
        SELECT content
        FROM schedules
        WHERE rid = %s AND
            begin_date >= %s::TIMESTAMP AND
            (end_date IS NULL OR end_date <= %s::TIMESTAMP);
    """

    # execute query and save the route data to a local variable
    cursor.execute(query, (route, str(date), str(date)))
    data = cursor.fetchone()[0]['route']

    # pd.Timestamp.dayofweek returns 0 for monday and 6 for Sunday
    # the actual serviceClass strings are defined by Nextbus
    # these are the only 3 service classes we can currently observe,
    # if others are published later then this will need to change
    if(date.dayofweek <= 4):
        serviceClass = 'wkd'
    elif(date.dayofweek == 5):
        serviceClass = 'sat'
    else:
        serviceClass = 'sun'

    # the schedule format has two entries for each serviceClass, 
    # one each for inbound and outbound.

    # return each entry in the data list with the correct serviceClass
    return [sched for sched in data if (sched['serviceClass'] == serviceClass)]

def get_common_intervals(df_list):
    """
    takes route schedule tables and returns both the average interval (mean)
    and the most common interval (mode), measured in number of minutes

    takes a list of dataframes and combines them before calculating statistics

    intended to combine inbound and outbound schedules for a single route
    """

    # ensure we have at least one dataframe
    if len(df_list) == 0:
        raise ValueError("Function requires at least one dataframe")

    # append all dataframes in the array together
    df = df_list[0].copy()
    for i in range(1, len(df_list)):
        df.append(df_list[i].copy())

    # convert all values to datetime so we can get an interval easily
    for col in df.columns:
        df[col] = pd.to_datetime(df[col])

    # initialize a table to hold each individual interval
    intervals = pd.DataFrame(columns = df.columns)
    intervals['temp'] = range(len(df))

    # take each column and find the intervals in it
    for col in df.columns:
        prev_time = np.nan
        for i in range(len(df)):
            # find the first non-null value and save it to prev_time
            if pd.isnull(prev_time):
                prev_time = df.at[i, col]
            # if the current time is not null, save the interval
            elif ~pd.isnull(df.at[i, col]):
                intervals.at[i, col] = (df.at[i, col] - prev_time).seconds / 60
                prev_time = df.at[i, col]

    # this runs without adding a temp column, but the above loop runs 3x as
    # fast if the rows already exist
    intervals = intervals.drop('temp', axis=1)

    # calculate the mean of the entire table
    mean = intervals.mean().mean()

    # calculate the mode of the entire table, the [0][0] at the end is
    # because scipy.stats returns an entire ModeResult class
    mode = stats.mode(intervals.values.flatten())[0][0]

    return mean, mode
