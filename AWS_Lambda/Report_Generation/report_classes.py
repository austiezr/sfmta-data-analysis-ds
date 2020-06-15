# This file contains the Schedule and Route classes, which load data from our
# database and provide methods and variables to help access it

import pandas as pd
import numpy as np
import psycopg2 as pg
from scipy import stats

# Schedule class definition
# (has some extra methods that are not all used in this notebook)


class Schedule:
    """
    The Schedule class loads schedule data for a given route and date

    Attributes:
        route_id (str): the id of the route loaded
        date (pd.Timestamp): the date of the schedule loaded
        route_data (dict): the raw schedule data
        inbound_table (pd.DataFrame): a dataframe of the inbound schedule
        outbound_table (pd.DataFrame): a dataframe of the outbound schedule
        mean_interval (float): the average time in minutes between each
                               scheduled stop
        common_interval (float): the most common time (mode) in minutes between
                                 each scheduled stop
    """

    def __init__(self, route_id, date, connection):
        """
        The Schedule class loads the schedule for a particular route and day,
        and makes several accessor methods available for it.

        Parameters:

        route_id (str or int)
            - The route id to load

        date (str or pandas.Timestamp)
            - Which date to load
            - Converted with pandas.to_datetime so many formats are acceptable

        connection (psycopg2 connection object)
            - The connection object to connect to the database with
        """

        self.route_id = str(route_id)
        self.date = pd.to_datetime(date)

        # load the schedule for that date and route
        self.route_data = load_schedule(self.route_id, self.date, connection)

        # process data into a table
        self.inbound_table, self.outbound_table = \
            extract_schedule_tables(self.route_data)

        # calculate the common interval values
        self.mean_interval, self.common_interval = get_common_intervals(
                                    [self.inbound_table, self.outbound_table])

    def list_stops(self):
        """
        returns the list of all stops used by this schedule
        """

        # get stops for both inbound and outbound routes
        inbound = list(self.inbound_table.columns)
        outbound = list(self.outbound_table.columns)

        # convert to set to ensure no duplicates,
        # then back to list for the correct output type
        return list(set(inbound + outbound))

    def get_specific_interval(self, stop, time, inbound=True):
        """
        Returns the expected interval, in minutes, for a given stop and
        time of day.

        Parameters:

        stop (str or int)
            - the stop tag/id of the bus stop to check

        time (str or pandas.Timestamp)
            - the time of day to check, uses pandas.to_datetime to convert
            - examples that work: "6:00", "3:30pm", "15:30"

        inbound (bool, optional)
            - whether to check the inbound or outbound schedule
            - ignored unless the given stop is in both inbound and outbound
        """

        # ensure correct parameter types
        stop = str(stop)
        time = pd.to_datetime(time)

        # check which route to use, and extract the column for the given stop
        if (stop in self.inbound_table.columns and
                stop in self.outbound_table.columns):
            # stop exists in both, use inbound parameter to decide
            if inbound:
                sched = self.inbound_table[stop]
            else:
                sched = self.outbound_table[stop]
        elif (stop in self.inbound_table.columns):
            # stop is in the inbound schedule, use that
            sched = self.inbound_table[stop]
        elif (stop in self.outbound_table.columns):
            # stop is in the outbound schedule, use that
            sched = self.outbound_table[stop]
        else:
            # stop doesn't exist in either, throw an error
            raise ValueError(f"Stop id '{stop}' doesn't exist in either",
                             "inbound or outbound schedules")

        # 1: convert schedule to datetime for comparison statements
        # 2: drop any NaN values
        # 3: convert to list since pd.Series threw errors on i indexing
        sched = list(pd.to_datetime(sched).dropna())

        # reset the date portion of the time parameter to
        # ensure we are checking the schedule correctly
        time = time.replace(year=self.date.year, month=self.date.month,
                            day=self.date.day)

        # iterate through that list to find where the time parameter fits
        for i in range(1, len(sched)):
            # start at 1 and move forward,
            # is the time parameter before this schedule entry?
            if(time < sched[i]):
                # return the difference between this entry and the previous one
                return (sched[i] - sched[i-1]).seconds / 60

        # can only reach this point if the time parameter is after all entries
        # in the schedule, return the last available interval
        return (sched[len(sched)-1] - sched[len(sched)-2]).seconds / 60


def load_schedule(route, date, connection):
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

    # DB connection
    cursor = connection.cursor()

    # build selection query
    query = """
        SELECT content
        FROM schedules
        WHERE rid = %s AND
            begin_date <= %s::TIMESTAMP AND
            (end_date IS NULL OR end_date >= %s::TIMESTAMP);
    """

    # execute query and save the route data to a local variable
    cursor.execute(query, (route, str(date), str(date)))
    if cursor.rowcount == 0:
        raise Exception(f"No schedule data found for route {route}",
                        f"on {date.date()}")

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

    # get each entry in the data list with the correct serviceClass
    result = [sched for sched in data if
              (sched['serviceClass'] == serviceClass)]

    # make sure there's data
    # (most commonly reason to be here: some routes don't run on weekends)
    if len(result) == 0:
        print(f"No schedule data found for route {route} on {date.date()}")

    return result


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

    # initialize dataframe
    inbound_df = pd.DataFrame(columns=inbound_stops)

    # extract each row from the data
    if type(route_data[inbound]['tr']) == list:
        # if there are multiple trips in a day, structure will be a list
        i = 0
        for trip in route_data[inbound]['tr']:
            for stop in trip['stop']:
                # '--' indicates the bus is not going to that stop on this trip
                if stop['content'] != '--':
                    inbound_df.at[i, stop['tag']] = stop['content']
            # increment for the next row
            i += 1
    else:
        # if there is only 1 trip in a day, the object is a dict and
        # must be handled slightly differently
        for stop in route_data[inbound]['tr']['stop']:
            if stop['content'] != '--':
                    inbound_df.at[0, stop['tag']] = stop['content']

    # flip between 0 and 1
    outbound = int(not inbound)

    # repeat steps for the outbound schedule
    outbound_stops = [s['tag'] for s in route_data[outbound]['header']['stop']]
    outbound_df = pd.DataFrame(columns=outbound_stops)

    if type(route_data[outbound]['tr']) == list:
        i = 0
        for trip in route_data[outbound]['tr']:
            for stop in trip['stop']:
                if stop['content'] != '--':
                    outbound_df.at[i, stop['tag']] = stop['content']
            i += 1
    else:
        for stop in route_data[outbound]['tr']['stop']:
            if stop['content'] != '--':
                    outbound_df.at[0, stop['tag']] = stop['content']

    # return both dataframes
    return inbound_df, outbound_df


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
    intervals = pd.DataFrame(columns=df.columns)
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


# Route class definition
# (also has some extra methods that are not all used in this notebook)

class Route:
    """
    The Route class loads route definition data for a given route and date,
    such as stop location and path coordinates

    Attributes:
        route_id (str): the id of the route loaded
        date (pd.Timestamp): the date of the route definition loaded
        route_data (dict): the raw route data
        route_type (str): the type of route loaded
        route_name (str): the name of the route loaded
        stops_table (pd.DataFrame): a table of all stops on this route
        inbound (list): a list of stop tags in the order they appear on the
                        inbound route
        outbound (list): a list of stop tags in the order they appear on the
                         outbound route

        Not fully implemented:
        path_coords (list): a list of (lat,lon) tuples describing the route
                            path.  These are stored as an unordered collection
                            of sub-paths in the raw data.
    """

    def __init__(self, route_id, date, connection):
        """
        The Route class loads the route configuration data for a particular
        route, and makes several accessor methods available for it.

        Parameters:

        route_id (str or int)
            - The route id to load

        date (str or pandas.Timestamp)
            - Which date to load
            - Converted with pandas.to_datetime so many formats are acceptable

        connection (psycopg2 connection object)
            - The connection object to connect to the database with
        """

        self.route_id = str(route_id)
        self.date = pd.to_datetime(date)

        # load the route data
        self.route_data, self.route_type, self.route_name = \
            load_route(self.route_id, self.date, connection)

        # extract stops table
        self.stops_table, self.inbound, self.outbound = \
            extract_stops(self.route_data)

        # The extract_path method is not complete

        # extract route path, list of (lat, lon) pairs
        # self.path_coords = extract_path(self.route_data)


def load_route(route, date, connection):
    """
    loads raw route data from the database

    Parameters:

        route (str or int)
            - The route id to load

        date (str or pd.Timestamp)
            - Which date to load
            - Converted with pandas.to_datetime so many formats are acceptable

    Returns route_data (dict), route_type (str), route_name (str)
    """

    # ensure correct parameter types
    route = str(route)
    date = pd.to_datetime(date)

    # DB connection
    cursor = connection.cursor()

    # build selection query
    query = """
        SELECT route_name, route_type, content
        FROM routes
        WHERE rid = %s AND
            begin_date <= %s::TIMESTAMP AND
            (end_date IS NULL OR end_date > %s::TIMESTAMP);
    """

    # execute query and return the route data
    cursor.execute(query, (route, str(date), str(date)))
    if cursor.rowcount == 0:
        raise Exception(f"No route data found for route {route}",
                        f"on {date.date()}")

    result = cursor.fetchone()
    return result[2]['route'], result[1], result[0]


def extract_path(route_data):
    """
    Extracts the list of path coordinates for a route.

    The raw data stores this as an unordered list of sub-routes, so this
    function deciphers the order they should go in and returns a single list.
    """

    # KNOWN BUG
    # this approach assumed all routes were either a line or a loop.
    # routes that have multiple sub-paths meeting at a point break this,
    # route 24 is a current example.
    # I'm committing this now to get the rest of the code out there

    # this part is also not currently used in the daily report generation

    # extract the list of subpaths as just (lat,lon) coordinates
    # also converts from string to float (raw data has strings)
    path = []
    for sub_path in route_data['path']:
        path.append([(float(p['lat']), float(p['lon']))
                     for p in sub_path['point']])

    # start with the first element, remove it from path
    final = path[0]
    path.pop(0)

    # loop until the first and last coordinates in final match
    counter = len(path)
    done = True
    while final[0] != final[-1]:
        # loop through the sub-paths that we haven't yet moved to final
        for i in range(len(path)):
            # check if the last coordinate in final matches the first
            # coordinate of another sub-path
            if final[-1] == path[i][0]:
                # match found, move it to final
                # leave out the first coordinate to avoid duplicates
                final = final + path[i][1:]
                path.pop(i)
                break  # break the for loop

        # protection against infinite loops, if the path never closes
        counter -= 1
        if counter < 0:
            done = False
            break

    if not done:
        # route did not connect in a loop, perform same steps backwards
        # to get the rest of the line
        for _ in range(len(path)):
            # loop through the sub-paths that we haven't yet moved to final
            for i in range(len(path)):
                # check if the first coordinate in final matches the last
                # coordinate of another sub-path
                if final[0] == path[i][-1]:
                    # match found, move it to final
                    # leave out the last coordinate to avoid duplicates
                    final = path[i][:-1] + final
                    path.pop(i)
                    break  # break the for loop

    # some routes may have un-used sub-paths
    # Route 1 for example has two sub-paths that are almost identical, with the
    # same start and end points
    # if len(path) > 0:
    #     print(f"WARNING: {len(path)} unused sub-paths")

    # return the final result
    return final


def extract_stops(route_data):
    """
    Extracts a dataframe of stops info

    Returns the main stops dataframe, and a list of inbound and outbound stops
    in the order they are intended to be on the route
    """

    stops = pd.DataFrame(route_data['stop'])
    directions = pd.DataFrame(route_data['direction'])

    # Change stop arrays to just the list of numbers
    for i in range(len(directions)):
        directions.at[i, 'stop'] = [s['tag'] for s in directions.at[i, 'stop']]

    # Find which stops are inbound or outbound
    inbound = []
    for stop_list in directions[directions['name'] == "Inbound"]['stop']:
        for stop in stop_list:
            if stop not in inbound:
                inbound.append(stop)

    outbound = []
    for stop_list in directions[directions['name'] == "Outbound"]['stop']:
        for stop in stop_list:
            if stop not in inbound:
                outbound.append(stop)

    # Label each stop as inbound or outbound
    stops['direction'] = ['none'] * len(stops)
    for i in range(len(stops)):
        if stops.at[i, 'tag'] in inbound:
            stops.at[i, 'direction'] = 'inbound'
        elif stops.at[i, 'tag'] in outbound:
            stops.at[i, 'direction'] = 'outbound'

    # Convert from string to float
    stops['lat'] = stops['lat'].astype(float)
    stops['lon'] = stops['lon'].astype(float)

    return stops, inbound, outbound
