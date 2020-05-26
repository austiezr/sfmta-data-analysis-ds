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
    url = 'http://restbus.info/api/agencies/sf-muni/routes'
    r = requests.get(url)

    # extract id's
    route_list = []
    for route in r.json():
        route_list.append(route['id'])

    # return the list
    return route_list

def collect_schedules(event, context, verbose=True):
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
        url = 'http://webservices.nextbus.com/service/publicJSONFeed?command=schedule&a=sf-muni&r='+rid

        # get the schedule json
        r = requests.get(url)
        new_schedule = r.json()

        # check if it exists already
        # run query to get latest schedule with this rid
        query = """
            SELECT *
            FROM schedules
            WHERE rid = %s
            ORDER BY begin_date DESC
            LIMIT 1;
        """
        cursor.execute(query, (rid,))
        row = cursor.fetchone()
        # row is a tuple of (id, rid, begin_date, end_date, content)

        if row == None:
            # no schedule with this rid was found, just insert the new schedule
            query = """
                INSERT INTO schedules (rid, begin_date, content)
                VALUES (%s, %s, %s);
            """
            cursor.execute(query, (rid, date.today().isoformat(), 
                                   json.dumps(new_schedule)))

            if verbose:
                print(f"No schedule with rid {rid} found, inserted new row")

        elif row[4] != new_schedule:
            # new schedule is different
            # update the end date of the old schedule
            query = """
                UPDATE schedules
                SET end_date = %s
                WHERE id = %s;
            """
            cursor.execute(query, (date.today().isoformat(), row[0]))

            # and insert the new schedule
            query = """
                INSERT INTO schedules (rid, begin_date, content)
                VALUES (%s, %s, %s);
            """
            cursor.execute(query, (rid, date.today().isoformat(), 
                                   json.dumps(new_schedule)))

            if verbose:
                print(f"Schedule for route {rid} updated")

        else:
            # new schedule is same as old schedule, no updates needed
            if verbose:
                print(f"Schedule for route {rid} is unchanged")

    cursor.close()
    cnx.commit()
    cnx.close()
