# Script that collects route data from Restbus and stores it in the database

import os
import json
import requests
import psycopg2 as pg
from dotenv import load_dotenv
from datetime import date


def load_db():
    """ loads the database and returns the connection object """

    # load credentials
    load_dotenv()
    creds = {
      'user': os.environ.get('USER'),
      'password': os.environ.get('PASSWORD'),
      'host': os.environ.get('HOST'),
      'dbname': os.environ.get('DATABASE')
    }

    # return the database connection
    return pg.connect(**creds)


def get_active_routes():
    """ returns a list of active route id's """

    # call api to get all current routes
    #url = 'http://restbus.info/api/agencies/sf-muni/routes'
    url = 'http://webservices.nextbus.com/service/publicJSONFeed?command=routeList&a=sf-muni'
    r = requests.get(url)

    # extract id's
    route_list = []
    for route in r.json()['route']:
        route_list.append(route['tag'])

    # return the list
    return route_list


def get_type(id, name):
    """ 
    returns the type of route based on its id and full name

    reverse-engineered from observed patterns since we could not 
    find a data source for them

    Possible types:
    Bus, Rail, Streetcar, Express, Cable Car, Shuttle, Overnight, Rapid
    """

    if id[-1] == 'X':  # if id ends in 'X'
      return 'Express'
    
    if id[-1] == 'R':  # if id ends in 'R'
      return 'Rapid'

    if name[-3:] == 'Owl' or id[-3:] == 'OWL':  # if id or name ends in 'Owl'
      return 'Overnight'
    
    if 'Bart' in name or 'BART' in name:  # if name includes 'Bart'
      return 'Shuttle'
    
    # Historic streetcar routes, should never be more than these 2
    # This line should change if they ever get renamed
    if id in ['E', 'F']:
      return 'Streetcar'
    
    # Purely numeric id's are only busses or shuttles
    # Additionally, some extra routes were added to temporarily 
    # replace rail lines, such as id 'LBUS'
    if id.isnumeric() or id[-3:] == 'BUS' or name[-3:] == 'Bus':
      return "Bus"
    
    # Of the 3 known cable cars, only 1 (C) has 'Cable Car' in the name
    # The rest have no pattern that can distinguish them from the rail lines
    # So those 3 are hard-coded
    if id in ['PH', 'PM', 'C'] or 'Cable Car' in name:
      return 'Cable Car'

    # else
    return "Rail"


def collect_routes(event, context, verbose=True):
    """
    main handler function, called by AWS Lambda

    params event and context:
        automatically passed by AWS Lambda, not used here

    param verbose: 
        enables print statements that go to the AWS logs
    """

    # set up database connection
    cnx = load_db()
    cursor = cnx.cursor()

    # get a list of active route id's
    route_list = get_active_routes()
    if verbose:
        print(f"Found {len(route_list)} active routes")

    # for each route id
    for rid in route_list:
        # build API url
        #url = 'http://restbus.info/api/agencies/sf-muni/routes/'+rid
        url = 'http://webservices.nextbus.com/service/publicJSONFeed?command=routeConfig&a=sf-muni&r='+rid

        # get the schedule json
        new_route = requests.get(url).json()

        # check if it exists already
        # run query to get latest schedule with this rid
        query = """
            SELECT *
            FROM routes
            WHERE rid = %s
            ORDER BY begin_date DESC
            LIMIT 1;
        """
        cursor.execute(query, (rid,))
        row = cursor.fetchone()
        # row is a tuple of (id, rid, route_name, route_type, begin_date, end_date, content)

        if row == None:
            # no route with this rid was found, just insert the new route data
            query = """
                INSERT INTO routes (rid, route_name, route_type, begin_date, content)
                VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(query, (rid, new_route['route']['title'],
                                   get_type(rid, new_route['route']['title']),
                                   date.today().isoformat(),
                                   json.dumps(new_route)))

            if verbose:
                print(f"No Route with rid {rid} found, inserted new row")

        elif row[6] != new_route:
            # new route is different
            # update the end date of the old route definition
            query = """
                UPDATE routes
                SET end_date = %s
                WHERE id = %s;
            """
            cursor.execute(query, (date.today().isoformat(), row[0]))

            # and insert the new schedule
            query = """
                INSERT INTO routes (rid, route_name, route_type, begin_date, content)
                VALUES (%s, %s, %s, %s, %s);
            """
            cursor.execute(query, (rid, new_route['route']['title'],
                                   get_type(rid, new_route['route']['title']),
                                   date.today().isoformat(),
                                   json.dumps(new_route)))

            if verbose:
                print(f"Definition for route {rid} updated")

        else:
            # new route definition is same as the old one, no updates needed
            if verbose:
                print(f"Definition for route {rid} is unchanged")

    cursor.close()
    cnx.commit()
    cnx.close()
