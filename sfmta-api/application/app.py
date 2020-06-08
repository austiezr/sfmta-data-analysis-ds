# Flask app providing API links for the web front end to use

from flask import Flask, request, render_template
import json
import os
from flask_cors import CORS
from datetime import date, timedelta
import psycopg2 as pg
from dotenv import load_dotenv
from schedule.schedule import Schedule

# Instantiating app w/ CORS, loading env. variables
load_dotenv()
app = Flask(__name__)
CORS(app)

# credentials for DB connection
creds = {
  'user': os.environ.get('USERNAME'),
  'password': os.environ.get('PASSWORD'),
  'host': os.environ.get('HOST'),
  'dbname': os.environ.get('DATABASE')
}


@app.route("/")
def index():
    return "Hello there!"


@app.route('/test')
def test():
    """
    Temporary route to test DB connection
    Returns first 10 rows from locations table
    """
    cnx = pg.connect(**creds)
    cursor = cnx.cursor()

    query = """
    SELECT * FROM locations LIMIT 10
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    return json.dumps(rows, sort_keys=False, default=str)


@app.route('/system-real-time')
def get_system_real_time():
    """
    Hits the database for the 100 most recent entries
    Returns each entry in a separate dictionary
    """
    cnx = pg.connect(**creds)
    cursor = cnx.cursor()

    query = """
    SELECT 
    timestamp, rid, vid, age, kph, heading, latitude, longitude, direction
    FROM locations
    ORDER BY timestamp DESC
    LIMIT 100
    """

    query2 = """
    SELECT
    column_name
    FROM information_schema.columns
    WHERE table_name = 'locations'
    """

    cursor.execute(query2)
    columns = cursor.fetchall()

    cursor.execute(query)
    rows = cursor.fetchall()

    elements = []

    for element in rows:
        elements.append(
            {columns[x+1][0]: element[x] for x in range(len(element))})

    return render_template('system_real_time.html',
                           elements=elements)


@app.route('/system-real-time-json')
def jsonify_system_real_time():
    """
    Hits the database for the 100 most recent entries
    Returns a single json containing all called entries
    """
    cnx = pg.connect(**creds)
    cursor = cnx.cursor()

    query = """
    SELECT 
    timestamp, rid, vid, age, kph, heading, latitude, longitude, direction
    FROM locations
    ORDER BY timestamp DESC
    LIMIT 100
    """

    query2 = """
    SELECT
    column_name
    FROM information_schema.columns
    WHERE table_name = 'locations'
    """

    cursor.execute(query2)
    columns = cursor.fetchall()

    cursor.execute(query)
    rows = cursor.fetchall()

    elements = []

    for element in rows:
        elements.append(
            {columns[x+1][0]: element[x] for x in range(len(element))})

    return json.dumps(elements, sort_keys=False, default=str)


@app.route('/daily-general-json', methods=['GET'])
def get_daily_usage():
    """
     Pulls all data from the specified date as json
     Expects date as string: YYYY-MM-DD
     Defaults to previous day if none given
    """
    day = request.args.get('day',
                           default=(date.today() - timedelta(days=1)))
    day = f'%{day}%'

    cnx = pg.connect(**creds)
    cursor = cnx.cursor()

    query = """
    SELECT
    (timestamp AT TIME ZONE 'utc' AT TIME ZONE 'pst'), 
    rid, vid, age, kph, heading, latitude, longitude, direction
    FROM locations
    WHERE (timestamp AT TIME ZONE 'utc' AT TIME ZONE 'pst')::TEXT LIKE %s
    ORDER BY timestamp
    """

    query2 = """
    SELECT
    column_name
    FROM information_schema.columns
    WHERE table_name = 'locations'
    """

    cursor.execute(query, (day,))
    rows = cursor.fetchall()

    cursor.execute(query2)
    columns = cursor.fetchall()

    elements = []

    for element in rows:
        elements.append(
            {columns[x+1][0]: element[x] for x in range(len(element))})

    return json.dumps(elements, sort_keys=False, default=str)


@app.route('/daily-route-json', methods=['GET'])
def get_daily_by_route():
    """
     Pulls all data from the specified date as json
     Expects date as string: YYYY-MM-DD
     Defaults to previous day if none given
    """
    day = request.args.get('day',
                           default=(date.today() - timedelta(days=1)))
    day = f'%{day}%'

    route = request.args.get('route',
                             default='1')

    cnx = pg.connect(**creds)
    cursor = cnx.cursor()

    query = """
    SELECT
    (timestamp AT TIME ZONE 'utc' AT TIME ZONE 'pst'), 
    rid, vid, age, kph, heading, latitude, longitude, direction
    FROM locations
    WHERE (timestamp AT TIME ZONE 'utc' AT TIME ZONE 'pst')::TEXT LIKE %s
    AND rid = %s
    ORDER BY timestamp
    """

    query2 = """
    SELECT
    column_name
    FROM information_schema.columns
    WHERE table_name = 'locations'
    """

    cursor.execute(query, (day, route))
    rows = cursor.fetchall()

    cursor.execute(query2)
    columns = cursor.fetchall()

    elements = []

    for element in rows:
        elements.append(
            {columns[x+1][0]: element[x] for x in range(len(element))})

    return json.dumps(elements, sort_keys=False, default=str)


@app.route('/get-route-info', methods=['GET'])
def get_route_schedule():
    """
    Pulls general schedule info for a specified route and date
    Returns:
        date specified
        route specified
        inbound, outbound dataframes as json
        list of stops
        mean, mode intervals between stops fou route
    Expects date as string: YYYY-MM-DD
    Expects route as string
    """
    route_id = request.args.get('route_id',
                                default='1')
    day = request.args.get('day',
                           default=(date.today() - timedelta(days=1)))

    sched = Schedule(route_id, day, creds)

    tables = {'date': day,
              'route': sched.route_id,
              'inbound': sched.inbound_table.to_json(),
              'outbound': sched.outbound_table.to_json(),
              'stops': sched.list_stops(),
              'intervals': {'mean': sched.mean_interval,
                            'mode': sched.common_interval}}

    return json.dumps(tables, sort_keys=False, default=str)


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=False, host='0.0.0.0')
