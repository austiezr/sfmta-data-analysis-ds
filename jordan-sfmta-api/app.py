from flask import Flask, url_for
import json
import pandas as pd
import requests
import plotly.graph_objects as go
import plotly.utils as pu
from decouple import config

app = Flask(__name__)
token = config('MAPBOX_TOKEN')
file = open('sfmta-api/schedule_data.json')
schedule_data = pd.read_json(file, orient='split')
file = open('sfmta-api/stop_data.csv')
stop_data = pd.read_csv(file)
file = open('sfmta-api/route_paths.json')
path_df = pd.read_json(file, orient='split')


@app.route("/")
def index():
    return "Hello"


@app.route("/all-routes", methods=['GET'])
def all_routes():
    traces, layout = create_graph()
    return json.dumps({"traces": traces, 'layout': layout}, cls=pu.PlotlyJSONEncoder)


def create_graph():
    traces = []
    routes = [9, 23, 15, 7]
    symbols = ['rail-metro', 'bus', 'bus', 'rail-light']
    colors = ['blue', 'red', 'red', 'green']
    i = 0

    for index, row in path_df.iloc[routes, :].iterrows():
        stopcoords = {'lats': [], 'lngs': []}
        for path in row['path']:
            lats, lngs = [], []
            for p in path:
                lats.append(p[0])
                lngs.append(p[1])

            # Create route lines for individual routes
            traces.append(go.Scattermapbox(
                mode="lines",
                lon=lngs, lat=lats,
                hoverinfo='none',
                marker={'color': colors[i]},
                ids=[row['tag']] * len(path)))

        # Get Bus/tram locations
        mask = stop_data['route_id'] == row['tag']
        stopcoords['lats'].extend(stop_data[mask]['lat'])
        stopcoords['lngs'].extend(stop_data[mask]['lon'])
        # Create Bus/train stop icons
        traces.append(go.Scattermapbox(
            mode="markers",
            lon=stopcoords['lngs'], lat=stopcoords['lats'],
            marker={'size': 12, 'color': 'black',
                    'symbol': [symbols[i]] * len(stopcoords['lats'])},
            ids=[row['tag']] * len(stopcoords['lats'])))
        i += 1

    layout = go.Layout(
        mapbox_style="outdoors",
        mapbox_zoom=11.25,
        mapbox_center={"lat": 37.76, "lon": -122.4},
        mapbox={
            'accesstoken': token},
        showlegend=False,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        width=800,
        height=800
    )

    return traces, layout

def create_route(coords):
    """Coords: start_lon, start_lat, end_lon, end_lat"""
    """Get route JSON."""
    base_url = 'https://api.mapbox.com/directions/v5/mapbox/walking/'
    url = base_url + str(coords[0]) + \
          ',' + str(coords[1]) + \
          ';' + str(coords[2]) + \
          ',' + str(coords[3])
    params = {
        'geometries': 'geojson',
        'access_token': token
    }
    req = requests.get(url, params=params)
    route_json = req.json()['routes'][0]

    lats = []
    lons = []

    for coords in route_json['geometry']['coordinates']:
        lats.append(coords[1])
        lons.append(coords[0])

    return lats, lons


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0')
