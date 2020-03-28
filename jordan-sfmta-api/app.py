from flask import Flask, url_for, request
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.utils as pu
from decouple import config
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
token = config('MAPBOX_TOKEN')
file = open('sfmta-api/schedule_data.json')
schedule_data = pd.read_json(file, orient='split')
file = open('sfmta-api/route_data_new.json')
new_route_info = pd.read_json(file, orient='split')
file = open('sfmta-api/route_paths.json')
path_df = pd.read_json(file, orient='split')


@app.route("/")
def index():
    return "Hello"


@app.route("/all-routes", methods=['GET'])
def all_routes():
    traces, layout, names, types = create_graph()
    return json.dumps(
        {"traces": traces, 'layout': layout, 'names': names, 'types': types},
        cls=pu.PlotlyJSONEncoder)


@app.route("/type-map", methods=['GET'])
def type_routes():
    route_type = request.args.get('type', type=str)
    traces, layout, names = create_graph(route_type)
    return json.dumps(
        {"traces": traces, 'layout': layout, 'names': names},
                      cls=pu.PlotlyJSONEncoder)


@app.route("/testing", methods=['GET'])
def testing():
    traces, layout, names, types = create_graph(testing=True)
    return json.dumps(
        {"traces": traces, 'layout': layout, 'names': names, 'types': types},
        cls=pu.PlotlyJSONEncoder)


def create_graph(route_type=None, testing=False):
    traces = []
    colors = {'bus': 'blue', 'rapid': 'blue', 'rail': 'red',
              'streetcar': 'green', 'express': 'blue', 'shuttle': 'yellow',
              'overnight': 'blue', 'cablecar': 'green'}
    symbols = {'bus': 'bus', 'rapid': 'bus', 'rail': 'rail-metro',
               'streetcar': 'rail-light', 'express': 'bus', 'shuttle': 'car',
               'overnight': 'bus', 'cablecar': 'rail-light'}

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

    if route_type is None and testing is False:
        names = []
        types = {'bus': []}
        i, y = 0, 0

        for index, row in path_df.iterrows():
            stopcoords = {'lats': [], 'lngs': []}
            mask = new_route_info['route_id'] == row['tag']
            names.append(
                {'route_id': row['tag'], 'route_name': row['name'], 'traces': []})
            for path in row['path']:
                lats, lngs = [], []
                for p in path:
                    lats.append(float(p[0]))
                    lngs.append(float(p[1]))

                # Create route lines for individual routes
                traces.append(go.Scattermapbox(
                    mode="lines",
                    lon=lngs, lat=lats,
                    hoverinfo='none',
                    marker={
                        'color': colors[new_route_info[mask]['type'].values[0]]}))
                names[i]['traces'].append(y)
                y += 1

            # Get Bus/tram locations
            stopcoords['lats'].extend(new_route_info[mask]['lat'].values[0])
            stopcoords['lngs'].extend(new_route_info[mask]['lon'].values[0])
            # Create Bus/train stop icons
            data = [io.capitalize() for io in new_route_info[mask]["dir"].values[0]]

            traces.append(go.Scattermapbox(
                mode="markers",
                lon=stopcoords['lngs'], lat=stopcoords['lats'],
                marker={'size': 12, 'color': 'black', 'symbol': [symbols[
                                                                     new_route_info[
                                                                         mask][
                                                                         'type'].values[
                                                                         0]]] * len(
                    stopcoords['lats'])},
                text=new_route_info[mask]["title"].values[0],
                customdata=data,
                hovertemplate='<b>Name:</b> %{text}<br>' +
                              '<b>Direction:</b> %{customdata}' +
                              '<extra></extra>'))
            names[i]['traces'].append(y)
            if new_route_info[mask]['type'].values[0] in types.keys():
                types[new_route_info[mask]['type'].values[0]].append(i)
            else:
                types[new_route_info[mask]['type'].values[0]] = [i]
            y += 1
            i += 1
        return traces, layout, names, types
    elif testing is True:
        names = []
        routes = [9,10,21,50,60]
        types = {'bus': []}
        i, y = 0, 0

        for index, row in path_df.iloc[routes,:].iterrows():
            stopcoords = {'lats': [], 'lngs': []}
            mask = new_route_info['route_id'] == row['tag']
            names.append(
                {'route_id': row['tag'], 'route_name': row['name'],
                 'traces': []})
            for path in row['path']:
                lats, lngs = [], []
                for p in path:
                    lats.append(float(p[0]))
                    lngs.append(float(p[1]))

                # Create route lines for individual routes
                traces.append(go.Scattermapbox(
                    mode="lines",
                    lon=lngs, lat=lats,
                    hoverinfo='none',
                    marker={
                        'color': colors[
                            new_route_info[mask]['type'].values[0]]}))
                names[i]['traces'].append(y)
                y += 1

            # Get Bus/tram locations
            stopcoords['lats'].extend(new_route_info[mask]['lat'].values[0])
            stopcoords['lngs'].extend(new_route_info[mask]['lon'].values[0])
            # Create Bus/train stop icons
            data = [io.capitalize() for io in
                    new_route_info[mask]["dir"].values[0]]

            traces.append(go.Scattermapbox(
                mode="markers",
                lon=stopcoords['lngs'], lat=stopcoords['lats'],
                marker={'size': 12, 'color': 'black', 'symbol': [symbols[
                                                                     new_route_info[
                                                                         mask][
                                                                         'type'].values[
                                                                         0]]]
                                                                * len(
                    stopcoords['lats'])},
                text=new_route_info[mask]["title"].values[0],
                customdata=data,
                hovertemplate='<b>Name:</b> %{text}<br>' +
                              '<b>Direction:</b> %{customdata}' +
                              '<extra></extra>'))
            names[i]['traces'].append(y)
            if new_route_info[mask]['type'].values[0] in types.keys():
                types[new_route_info[mask]['type'].values[0]].append(i)
            else:
                types[new_route_info[mask]['type'].values[0]] = [i]
            y += 1
            i += 1
        return traces, layout, names, types
    else:
        names = []
        i, y = 0, 0
        route_mask = new_route_info['type'] == route_type
        for index, row in path_df[route_mask].iterrows():
            stopcoords = {'lats': [], 'lngs': []}
            mask = new_route_info['route_id'] == row['tag']
            names.append(
                {'route_id': row['tag'], 'route_name': row['name'],
                 'traces': []})
            for path in row['path']:
                lats, lngs = [], []
                for p in path:
                    lats.append(float(p[0]))
                    lngs.append(float(p[1]))

                # Create route lines for individual routes
                traces.append(go.Scattermapbox(
                    mode="lines",
                    lon=lngs, lat=lats,
                    hoverinfo='none',
                    marker={
                        'color': colors[
                            new_route_info[mask]['type'].values[0]]}))
                names[i]['traces'].append(y)
                y += 1

            # Get Bus/tram locations
            stopcoords['lats'].extend(new_route_info[mask]['lat'].values[0])
            stopcoords['lngs'].extend(new_route_info[mask]['lon'].values[0])
            # Create Bus/train stop icons
            data = [io.capitalize() for io in
                    new_route_info[mask]["dir"].values[0]]

            traces.append(go.Scattermapbox(
                mode="markers",
                lon=stopcoords['lngs'], lat=stopcoords['lats'],
                marker={'size': 12, 'color': 'black', 'symbol': [symbols[
                                                                     new_route_info[
                                                                         mask][
                                                                         'type'].values[
                                                                         0]]]
                                                                * len(
                    stopcoords['lats'])},
                text=new_route_info[mask]["title"].values[0],
                customdata=data,
                hovertemplate='<b>Name:</b> %{text}<br>' +
                              '<b>Direction:</b> %{customdata}' +
                              '<extra></extra>'))
            names[i]['traces'].append(y)
            y += 1
            i += 1

        return traces, layout, names

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
