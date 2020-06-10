# A class that loads route data from the database and
# provides various accessor methods for it

import pandas as pd
import psycopg2 as pg
# from dotenv import load_dotenv
import os

class Route:
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
        """

        self.route_id = str(route_id)
        self.date = pd.to_datetime(date)

        # load the route data
        self.route_data = load_route(self.route_id, self.date, connection)

        # extract stops info and rearrange columns to be more human readable
        # note: the stop tag is what was used in the schedule data, not stopId
        self.stops_table = pd.DataFrame(self.route_data['stop'])
        self.stops_table = self.stops_table[['stopId', 'tag', 'title', 'lat', 'lon']]

        # extract route path, list of (lat, lon) pairs
        self.path_coords = extract_path(self.route_data)


def load_route(route, date, connection):
    """
    loads raw route data from the database and returns it

    Parameters:

        route (str or int)
            - The route id to load

        date (str or pd.Timestamp)
            - Which date to load
            - Converted with pandas.to_datetime so many formats are acceptable
    """

    # ensure correct parameter types
    route = str(route)
    date = pd.to_datetime(date)

    # load environment variables for DB connection
    # load_dotenv()
    # creds = {
    #     'user': os.environ.get('USER'),
    #     'password': os.environ.get('PASSWORD'),
    #     'host': os.environ.get('HOST'),
    #     'dbname': os.environ.get('DATABASE')
    # }

    # initialize DB connection
    # cnx = pg.connect(**creds)
    cursor = connection.cursor()

    # build selection query
    query = """
        SELECT content
        FROM routes
        WHERE rid = %s AND
            begin_date <= %s::TIMESTAMP AND
            (end_date IS NULL OR end_date > %s::TIMESTAMP);
    """

    # execute query and return the route data
    cursor.execute(query, (route, str(date), str(date)))
    return cursor.fetchone()[0]['route']


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
    if len(path) > 0:
        print(f"WARNING: {len(path)} unused sub-paths")

    # return the final result
    return final
