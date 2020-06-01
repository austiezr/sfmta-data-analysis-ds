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
                INSERT INTO routes (rid, route_name, begin_date, content)
                VALUES (%s, %s, %s, %s);
            """
            cursor.execute(query, (rid, new_route['route']['title'], 
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
                INSERT INTO routes (rid, route_name, begin_date, content)
                VALUES (%s, %s, %s, %s);
            """
            cursor.execute(query, (rid, new_route['route']['title'], 
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
