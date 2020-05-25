# Flask app providing API links for the web front end to use

from flask import Flask, request, render_template
# from flask import url_for
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.utils as pu
from flask_cors import CORS
from datetime import datetime, date, timedelta
import pytz
import psycopg2 as pg
import requests
from dotenv import load_dotenv, find_dotenv
import os

# Instantiating app w/ CORS, loading env. variables
load_dotenv()
app = Flask(__name__)
CORS(app)

# Used for currently unimplemented Labs 22 Routes
# mapbox_token = os.environ.get('MAPBOX_TOKEN')
# file = open('schedule_data.json')
# schedule_data = pd.read_json(file, orient='split')
# file = open('route_data_new.json')
# new_route_info = pd.read_json(file, orient='split')
# file = open('route_paths.json')
# path_df = pd.read_json(file, orient='split')

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


# returns a JSON of raw vehicle location data, given a route id
# @app.route('/real-time', methods=['GET'])
# def get_real_time():
#     route_id = request.args.get('id', default=None)
#     last_call = request.args.get('last', default=None)
#
#     vehicles = {'rid': [], 'vid': [], 'lat': [], 'lng': [], 'dir': []}
#     cnx = pg.connect(**creds)
#     cursor = cnx.cursor()
#
#     # if last call is none, then return all buses on that route
#     if last_call is None:
#         query = (
#             "SELECT datetime, rid, vid, lat, lon, dir FROM location WHERE "
#             "rid = %s ORDER BY `datetime` DESC LIMIT 20")
#
#         cursor.execute(query, (str(route_id),))
#
#         for (d_datetime, rid, vid, lat, lon, d_dir) in cursor:
#             if vid not in vehicles['vid']:
#                 vehicles['rid'].append(rid)
#                 vehicles['vid'].append(vid)
#                 vehicles['lat'].append(lat)
#                 vehicles['lng'].append(lon)
#                 vehicles['dir'].append(d_dir)
#
#                 last_call = datetime.strftime(d_datetime, '%Y%m%d%H%M%S')
#
#         cursor.close()
#         cnx.close()
#     else:
#         dt = datetime.strptime(str(last_call), '%Y%m%d%H%M%S')
#         query = (
#             "SELECT datetime, rid, vid, lat, lon, dir FROM location WHERE rid"
#             "= %s AND `datetime` >= %s GROUP BY vid LIMIT 20")
#
#         cursor.execute(query, (str(route_id), str(dt)))
#
#         for (d_datetime, rid, vid, lat, lon, d_dir) in cursor:
#             vehicles['rid'].append(rid)
#             vehicles['vid'].append(vid)
#             vehicles['lat'].append(lat)
#             vehicles['lng'].append(lon)
#             vehicles['dir'].append(d_dir)
#
#             if last_call < datetime.strftime(d_datetime, '%Y%m%d%H%M%S'):
#                 last_call = datetime.strftime(d_datetime, '%Y%m%d%H%M%S')
#
#         cursor.close()
#         cnx.close()
#
#     return json.dumps({'vehicles': vehicles,
#                        'last_call': last_call})
#
#
# # returns the output of create_graph() in JSON format
# @app.route("/all-routes", methods=['GET'])
# def all_routes():
#     traces, layout, names, types = create_graph()
#     return json.dumps({"traces": traces,
#                        'layout': layout,
#                        'names': names,
#                        'types': types},
#                       cls=pu.PlotlyJSONEncoder)
#
#
# # this route returns the "type" argument passed to it
# # possibly unfinished
# @app.route("/type-map", methods=['GET'])
# def type_routes():
#     route_type = request.args.get('type', type=str)
#     return route_type
#
#
# # creates the plotly map of San Francisco showing a specific route
# def create_graph():
#     traces = []
#     colors = {'bus': 'blue',
#               'rapid': 'blue',
#               'rail': 'red',
#               'streetcar': 'green',
#               'express': 'blue',
#               'shuttle': 'yellow',
#               'overnight': 'blue',
#               'cablecar': 'green'}
#
#     symbols = {'bus': 'bus',
#                'rapid': 'bus',
#                'rail': 'rail-metro',
#                'streetcar': 'rail-light',
#                'express': 'bus',
#                'shuttle': 'car',
#                'overnight': 'bus',
#                'cablecar': 'rail-light'}
#
#     names = []
#     types = {'bus': []}
#     i, y = 0, 0
#
#     for col, row in path_df.iterrows():
#         stopcoords = {'lats': [], 'lngs': []}
#         mask = new_route_info['route_id'] == row['tag']
#         names.append(
#             {'route_id': row['tag'],
#              'route_name': row['name'],
#              'traces': []})
#
#         for path in row['path']:
#             lats, lngs = [], []
#
#             for p in path:
#                 lats.append(float(p[0]))
#                 lngs.append(float(p[1]))
#
#             # Create route lines for individual routes
#             traces.append(go.Scattermapbox(
#                 mode="lines",
#                 lon=lngs, lat=lats,
#                 hoverinfo='none',
#                 marker={
#                     'color': colors[new_route_info[mask]['type'].values[0]]}))
#
#             names[i]['traces'].append(y)
#             y += 1
#
#         # Get Bus/tram locations
#         stopcoords['lats'].extend(new_route_info[mask]['lat'].values[0])
#         stopcoords['lngs'].extend(new_route_info[mask]['lon'].values[0])
#
#         # Create Bus/train stop icons
#         data = [io.capitalize()
#                 for io in new_route_info[mask]["dir"].values[0]]
#
#         traces.append(go.Scattermapbox(
#             mode="markers",
#             lon=stopcoords['lngs'], lat=stopcoords['lats'],
#             marker={'size': 12,
#                     'color': 'black',
#                     'symbol': [symbols[new_route_info[mask][
#                         'type'].values[0]]] * len(stopcoords['lats'])},
#             text=new_route_info[mask]["title"].values[0],
#             customdata=data,
#             hovertemplate='<b>Name:</b> %{text}<br>' +
#                           '<b>Direction:</b> %{customdata}' +
#                           '<extra></extra>'))
#
#         names[i]['traces'].append(y)
#         if new_route_info[mask]['type'].values[0] in types.keys():
#             types[new_route_info[mask]['type'].values[0]].append(i)
#         else:
#             types[new_route_info[mask]['type'].values[0]] = [i]
#         y += 1
#         i += 1
#
#     layout = go.Layout(
#         mapbox_style="outdoors",
#         mapbox_zoom=11.25,
#         mapbox_center={"lat": 37.76, "lon": -122.4},
#         mapbox={
#             'accesstoken': mapbox_token},
#         showlegend=False,
#         margin={"r": 0, "t": 0, "l": 0, "b": 0},
#         width=800,
#         height=800
#     )
#
#     return traces, layout, names, types
#
#
# # gets a list of lat/lon coordinates from the mapbox api
# def create_route(coords):
#     """Coords: start_lon, start_lat, end_lon, end_lat"""
#     """Get route JSON."""
#     base_url = 'https://api.mapbox.com/directions/v5/mapbox/walking/'
#     url = base_url + str(coords[0]) + \
#         ',' + str(coords[1]) + \
#         ';' + str(coords[2]) + \
#         ',' + str(coords[3])
#
#     params = {
#         'geometries': 'geojson',
#         'access_token': mapbox_token
#     }
#
#     req = requests.get(url, params=params)
#     route_json = req.json()['routes'][0]
#
#     lats = []
#     lons = []
#
#     for coords in route_json['geometry']['coordinates']:
#         lats.append(coords[1])
#         lons.append(coords[0])
#
#     return lats, lons


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=False, host='0.0.0.0')
