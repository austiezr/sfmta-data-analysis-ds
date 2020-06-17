# This file contains multiple functions, each used in different steps of the
# daily report generation

from report_classes import Schedule, Route
import pandas as pd
import psycopg2 as pg

# Used to easily read in bus location data
import pandas.io.sql as sqlio

# Used to find distances between lat/lon points, and match closest stops
from math import sqrt, cos
from scipy.spatial.distance import cdist


def load_locations(date, connection):
    """
    Loads all bus locations for the given date, returns a Dataframe

    Arguments:
        date (str or Timestamp): the date to load data from
        connection (postgresql connection): the connection to the database
    """

    # get begin and end timestamps for the date
    # uses 7am to account for UTC timestamps
    begin = pd.to_datetime(date).replace(hour=7)
    end = begin + pd.Timedelta(days=1)

    # Build query to select location data
    query = f"""
    SELECT *
    FROM locations
    WHERE timestamp > '{begin}'::TIMESTAMP AND
          timestamp < '{end}'::TIMESTAMP
    ORDER BY id;
    """

    # read the query directly into pandas
    locations = sqlio.read_sql_query(query, connection)

    if len(locations) == 0:
        raise Exception(f"No bus location data found between",
                        f"{begin} and {end} (UTC)")

    # Convert those UTC timestamps to local PST by subtracting 7 hours
    locations['timestamp'] = locations['timestamp'] - pd.Timedelta(hours=7)

    # return the result
    return locations


def fcc_projection(loc1, loc2):
    """
    function to apply FCC recommended formulae
    for calculating distances on earth projected to a plane

    significantly faster computationally, negligible loss in accuracy

    Args:
    loc1 - a tuple of lat/lon
    loc2 - a tuple of lat/lon

    Returns distance between the two points, in kilometers
    """
    lat1, lat2 = loc1[0], loc2[0]
    lon1, lon2 = loc1[1], loc2[1]

    mean_lat = (lat1+lat2)/2
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    k1 = 111.13209 - 0.56605*cos(2*mean_lat) + .0012*cos(4*mean_lat)
    k2 = (111.41513*cos(mean_lat) - 0.09455*cos(3*mean_lat) +
          0.00012*cos(5*mean_lat))

    distance = sqrt((k1*delta_lat)**2 + (k2*delta_lon)**2)

    return distance


def clean_locations(locations, stops):
    """
    1. removes location reports older than 60 seconds
    2. removes location reports with no direction value
    3. shifts timestamps according to the age column, so the lat/lon location
        and timestamp match
    4. uses the cdist function from scipy to quickly get all distances between
        each pair of location report and potential stop
    5. saves the closest stop to each location report
    6. drops any rows where closest stop is too far away.
        - This makes sense for longer routes that can go for a few kilometers
          without a stop, such as route 25 over the golden gate bridge.
        - Right now we are approximating by saying the closest stop is where
          the bus actually is at that time.  If we improve that approximation,
          we should probably stop dropping these rows.

    Arguments:
        locations (DataFrame): a dataframe of bus locations
        stops (DataFrame): a dataframe of stops for this route

    Returns the modified locations dataframe with nearest stops added
    """

    # remove old location reports that would be duplicates
    df = locations[locations['age'] < 60].copy()

    # remove rows with no direction value
    df = df[~pd.isna(df['direction'])]

    # shift timestamps according to the age column
    df['timestamp'] = df.apply(shift_timestamp, axis=1)

    # Make lists of all inbound or outbound stops
    inbound_stops = stops[stops['direction'] == 'inbound'] \
        .reset_index(drop=True)
    outbound_stops = stops[stops['direction'] == 'outbound'] \
        .reset_index(drop=True)

    # Assign closest stops
    # separate inbound and outbound so we compare the right stops
    df_in = df[df['direction'].str.contains('_I_')].copy()
    df_out = df[df['direction'].str.contains('_O_')].copy()

    # use scipy to find the closest stop to each location report
    closest_in = cdist(df_in[['latitude', 'longitude']].to_numpy(),
                       inbound_stops[['lat', 'lon']].to_numpy(),
                       metric=fcc_projection)
    closest_out = cdist(df_out[['latitude', 'longitude']].to_numpy(),
                        outbound_stops[['lat', 'lon']].to_numpy(),
                        metric=fcc_projection)

    # save results back to df
    df_in['closestStop'] = [closest_in[i].argmin()
                            for i in range(len(closest_in))]
    df_in['distance'] = [closest_in[i].min()
                         for i in range(len(closest_in))]
    df_out['closestStop'] = [closest_out[i].argmin()
                             for i in range(len(closest_out))]
    df_out['distance'] = [closest_out[i].min()
                          for i in range(len(closest_out))]

    # cdist gives us the index of closestStop, convert it to the stop tag
    df_in['closestStop'] = df_in['closestStop'].apply(
        lambda x: int(inbound_stops.at[x, 'tag']))
    df_out['closestStop'] = df_out['closestStop'].apply(
        lambda x: int(outbound_stops.at[x, 'tag']))

    # df_in and df_out back together
    df = df_in.append(df_out).sort_values(['timestamp', 'vid']) \
        .reset_index(drop=True)

    # drop any rows that were more than .5 kilometers away from a stop
    df = df[df['distance'] < .5]

    return df


def shift_timestamp(row):
    """
    Helper for the cleaning function,
    subtracts row['age'] from row['timestamp']
    """
    return row['timestamp'] - pd.Timedelta(seconds=row['age'])


def get_stop_times(locations, route):
    """
    Returns a dict, keys are stop tags and values are lists of timestamps
    that describe every time a bus was seen at that stop

    Uses interpolation to fill in times for some stops between each location
    report.  In practice, this usually adds about 10% more rows.

    Interpolation diagram:
    https://drive.google.com/uc?export=view&id=1lroClIK-i6_mysd5SA3mQCHsNKuy5t_r

    Arguments:
        locations (Dataframe): The dataframe of bus locations.  Expected to be
                               after the cleaning function.
        route (Route): The Route class object
    """

    # Initialize the data structure I will store results in
    stop_times = {}
    for stop in route.inbound + route.outbound:
        stop_times[str(stop)] = []

    for vid in locations['vid'].unique():
        # Process the route one vehicle at a time
        df = locations[locations['vid'] == vid]

        # process 1st row on its own
        prev_row = df.loc[df.index[0]]
        stop_times[str(prev_row['closestStop'])].append(prev_row['timestamp'])

        # loop through the rest of the rows, comparing each to the previous one
        for i, row in df[1:].iterrows():
            if row['direction'] != prev_row['direction']:
                # changed directions, don't compare to previous row
                stop_times[str(row['closestStop'])].append(row['timestamp'])
            else:
                # same direction, compare to previous row
                if '_I_' in row['direction']:  # get correct stop list
                    stoplist = route.inbound
                else:
                    stoplist = route.outbound

                current = stoplist.index(str(row['closestStop']))
                previous = stoplist.index(str(prev_row['closestStop']))
                gap = current - previous
                if gap > 1:  # need to interpolate
                    diff = (row['timestamp'] - prev_row['timestamp'])/gap
                    counter = 1
                    for stop in stoplist[previous+1:current]:
                        # save interpolated time
                        stop_times[str(stop)].append(prev_row['timestamp'] +
                                                     (counter * diff))

                    # increase counter for the next stop
                    # example: with 2 interpolated stops, gap would be 3
                    # 1st diff is 1/3, next is 2/3
                    counter += 1

                if row['closestStop'] != prev_row['closestStop']:
                    # only save time if the stop has changed,
                    # otherwise the bus hasn't moved since last time
                    stop_times[str(row['closestStop'])] \
                        .append(row['timestamp'])

            # advance for next row
            prev_row = row

    # Sort each list before returning
    for stop in stop_times.keys():
        stop_times[stop].sort()

    return stop_times


def get_bunches_gaps(stop_times, schedule,
                     bunch_threshold=.2, gap_threshold=1.5):
    """
    Returns a dataframe of all bunches and gaps found

    Default thresholds define a bunch as 20% and a gap as 150% of
    scheduled headway

    Arguments:
        stop_times (dict): the dict object returned by get_stop_times()
        schedule (Schedule): the Schedule class object
        bunch_threshold (float): the bunch threshold (default .2)
        gap_threshold (float): the gap threshold (default 1.5)
    """

    # Initialize dataframe for the bunces and gaps
    problems = pd.DataFrame(columns=['type', 'time', 'duration', 'stop'])
    counter = 0

    # Set the bunch/gap thresholds (in seconds)
    bunch_threshold = (schedule.common_interval * 60) * bunch_threshold
    gap_threshold = (schedule.common_interval * 60) * gap_threshold

    for stop in stop_times.keys():
        # ensure we have any times at all for this stop
        if len(stop_times[stop]) == 0:
            # print(f"Stop {stop} had no recorded times")
            continue  # go to next stop in the loop

        # save initial time
        prev_time = stop_times[stop][0]

        # loop through all others, comparing to the previous one
        for time in stop_times[stop][1:]:
            diff = (time - prev_time).seconds
            if diff <= bunch_threshold:
                # bunch found, save it
                problems.at[counter] = ['bunch', prev_time, diff, stop]
                counter += 1
            elif diff >= gap_threshold:
                problems.at[counter] = ['gap', prev_time, diff, stop]
                counter += 1

            prev_time = time

    return problems


def helper_count(expected_times, observed_times):
    """
    Helper function for calculate_ontime()

    Returns the number of on-time stops found

    Arguments:
    expected_times (Dataframe): the dataframe of scheduled stops from
                                Schedule's inbound_table or outbound_table
    observed_times (dict): the dict object returned by get_stop_times()
    """

    # set up early/late thresholds (in seconds)
    early_threshold = pd.Timedelta(seconds=60)  # 1 minute early
    late_threshold = pd.Timedelta(seconds=240)  # 4 minutes late

    count = 0
    for stop in expected_times.columns:
        for expected in expected_times[stop]:
            if pd.isna(expected):
                continue  # skip NaN values in the expected schedule

            # for each expected time...
            # find first observed time after the early threshold
            found_time = None
            early = expected - early_threshold

            # BUG: some schedule data may have stop tags that are not in
            # the inbound or outbound definitions for a route.
            # That throws a key error here.
            # Example: stop 14148 on route 24
            # current solution ignores those stops with the try/except block
            try:
                for observed in observed_times[stop]:
                    if observed >= early:
                        found_time = observed
                        break
            except:
                continue

            # if found time is None, then all observed times were too early
            # if found_time is before the late threshold then we were on time
            if (not pd.isna(found_time)) and (found_time <=
                                              (expected + late_threshold)):
                # found_time is within the on-time window
                count += 1

    return count


def calculate_ontime(stop_times, schedule):
    """
    Returns the on-time percentage and total scheduled stops for this route

    Arguments:
    stop_times (dict): the dict object returned by get_stop_times()
    schedule (Schedule): the Schedule class object
    """

    # Save schedules with timestamp data types, set date to match
    inbound_times = schedule.inbound_table
    for col in inbound_times.columns:
        inbound_times[col] = pd.to_datetime(inbound_times[col]).apply(
            lambda dt: dt.replace(year=schedule.date.year,
                                  month=schedule.date.month,
                                  day=schedule.date.day))

    outbound_times = schedule.outbound_table
    for col in outbound_times.columns:
        outbound_times[col] = pd.to_datetime(outbound_times[col]).apply(
            lambda dt: dt.replace(year=schedule.date.year,
                                  month=schedule.date.month,
                                  day=schedule.date.day))

    # count times for both inbound and outbound schedules
    on_time_count = (helper_count(inbound_times, stop_times) +
                     helper_count(outbound_times, stop_times))

    # get total expected count
    total_expected = inbound_times.count().sum() + outbound_times.count().sum()

    # return on-time percentage
    return (on_time_count / total_expected), total_expected


def bunch_gap_graph(problems, interval=10):
    """
    returns data for a graph of the bunches and gaps throughout the day

    Arguments:
        problems (Datafame): the dataframe of bunches and gaps
        interval (int): the number of minutes to bin data into (default: 10)

    returns dict:
    {
    "times": [time values (x)],
    "bunches": [bunch counts (y1)],
    "gaps": [gap counts (y2)]
    }
    """

    # set the time interval
    interval = pd.Timedelta(minutes=interval)

    # rest of code doesn't work if there are no bunches or gaps
    # return the empty graph manually
    if len(problems) == 0:
        # generate list of times according to the interval
        start = pd.Timestamp('today').replace(hour=0, minute=0, second=0)
        t = start
        times = []
        while t.day == start.day:
            times.append(str(t.time())[:5])
            t += interval

        return {
            "times": times,
            "bunches": [0] * len(times),
            "gaps": [0] * len(times)
        }

    # generate the DatetimeIndex needed
    index = pd.DatetimeIndex(problems['time'])
    df = problems.copy()
    df.index = index

    # lists for graph data
    bunches = []
    gaps = []
    times = []

    # set selection times
    start_date = problems.at[0, 'time'].replace(hour=0, minute=0, second=0)
    select_start = start_date
    select_end = select_start + interval

    while select_start.day == start_date.day:
        # get the count of each type of problem in this time interval
        count = df.between_time(select_start.time(),
                                select_end.time())['type'].value_counts()

        # append the counts to the data list
        if 'bunch' in count.index:
            bunches.append(int(count['bunch']))
        else:
            bunches.append(0)

        if 'gap' in count.index:
            gaps.append(int(count['gap']))
        else:
            gaps.append(0)

        # save the start time for the x axis
        times.append(str(select_start.time())[:5])

        # increment the selection window
        select_start += interval
        select_end += interval

    return {
        "times": times,
        "bunches": bunches,
        "gaps": gaps
    }


def create_simple_geojson(bunches, rid):
    """
    Returns a geojson object containing points for each bunch on the route

    Arguments:
        bunches (Dataframe): a dataframe of bunches
        rid (str): the route id the bunches were found on
    """

    geojson = {'type': 'FeatureCollection',
               'bunches': create_geojson_features(bunches)}

    return geojson


def create_geojson_features(df):
    """
    Function to generate list of geojson features
    for plotting vehicle locations on timestamped map

    Expects a dataframe containing lat/lon, vid, timestamp
    returns list of basic geojson formatted features:

    {
      type: Feature
      geometry: {
        type: Point,
        coordinates:[lat, lon]
      },
      properties: {
        time: timestamp
        stopId: stop id
      }
    }
    """
    # initializing empty features list
    features = []

    # iterating through df to pull coords, stopid, timestamp
    # and format for json
    for index, row in df.iterrows():
        feature = {
          'type': 'Feature',
          'geometry': {
                'type': 'Point',
                'coordinates': [round(row.lon, 4), round(row.lat, 4)]
            },
            'properties': {
                'time': row.time.__str__().rstrip('0').rstrip('.')
                        if '.' in row.time.__str__()
                        else row.time.__str__(),
                'stopId': row.stopId.__str__()
            }
        }
        features.append(feature)  # adding point to features list
    return features


def calculate_health(bunch_percentage, gap_percentage, on_time_percentage):
    """
    Calculates an average of 3 main statistics, returns a float

    (does not use coverage since that is
    already dependent on on-time and bunches)

    Arguments:
        bunch_percentage (float): the bunched percentage score
        gap_percentage (float): the gapped percentage score
        on_time_percentage (float): the on-time percentage score
    """

    # invert bunches and gaps, since fewer of those is better
    bunch_percentage = 1 - bunch_percentage
    gap_percentage = 1 - gap_percentage

    return (bunch_percentage + gap_percentage + on_time_percentage) / 3


def get_active_routes(date, cursor):
    """
    returns a list of all route id's that had reported
    bus locations on the given date
    """

    # Set hour to 7 to account for UTC time change
    date = pd.to_datetime(date).replace(hour=7)
    end = date + pd.Timedelta(days=1)

    query = """
        SELECT DISTINCT rid
        FROM locations
        WHERE timestamp >= %s ::TIMESTAMP AND
            timestamp < %s ::TIMESTAMP;
    """

    cursor.execute(query, (date, end))
    return [result[0] for result in cursor.fetchall()]


def generate_route_report(rid, date, connection, locations):
    """
    Generates a daily report for a single route

    Arguments:
        rid (str): the route id to generate a report for
        date (str or pd.Datetime): the date to generate a report for
        connection (psycopg2 connection): the connection to the database
        locations (Dataframe): the pre-loaded location data

    returns a dict of the report info
    """

    # Load schedule, route, and location data
    schedule = Schedule(rid, date, connection)
    route = Route(rid, date, connection)

    # Apply cleaning function (this usually takes 1-2 minutes)
    locations = clean_locations(locations, route.stops_table)

    # Calculate all times a bus was at each stop
    stop_times = get_stop_times(locations, route)

    # Find all bunches and gaps
    problems = get_bunches_gaps(stop_times, schedule)

    # Calculate on-time percentage
    on_time, total_scheduled = calculate_ontime(stop_times, schedule)

    # Build result dict

    # Number of recorded intervals:
    # (sum(len(each list of time)) - number or lists of times)
    intervals = 0
    for key in stop_times.keys():
        intervals += len(stop_times[key])
    intervals = intervals-len(stop_times)

    # Bunches, gaps, and coverage stats
    bunches = len(problems[problems['type'] == 'bunch'])
    gaps = len(problems[problems['type'] == 'gap'])
    coverage = (total_scheduled * on_time + bunches) / total_scheduled

    # Get overall health
    health = calculate_health(bunches/intervals, gaps/intervals, on_time)

    # Isolating bunches, merging with stops to assign locations to bunches
    bunch_df = problems[problems.type.eq('bunch')]
    bunch_df = bunch_df.merge(route.stops_table, left_on='stop',
                              right_on='tag', how='left')

    # Creating GeoJSON of bunch times / locations
    geojson = create_simple_geojson(bunch_df, rid)

    # int/float conversions are because the json
    # library doesn't work with numpy types
    result = {
        'route_id': rid,
        'route_name': route.route_name,
        'route_type': route.route_type,
        'date': str(pd.to_datetime(date)),
        'overall_health': float(round(health * 100, 2)),
        'num_bunches': bunches,
        'num_gaps': gaps,
        'bunched_percentage': round(bunches/intervals*100, 2),
        'gapped_percengage': round(gaps/intervals*100, 2),
        'total_intervals': intervals,
        'on_time_percentage': float(round(on_time * 100, 2)),
        'scheduled_stops': int(total_scheduled),
        'coverage': float(round(coverage * 100, 2)),
        # line_chart contains all data needed to generate the line chart
        'line_chart': bunch_gap_graph(problems, interval=10),
        # route_table is an array of all rows that should show up in the table
        # it will be filled in after all reports are generated
        'route_table': [
            {
                'route_id': rid,
                'route_name': route.route_name,
                'overall_health': float(round(health * 100, 2)),
                'bunched_percentage': round(bunches/intervals*100, 2),
                'gapped_percengage': round(gaps/intervals*100, 2),
                'on_time_percentage': float(round(on_time * 100, 2)),
                'coverage': float(round(coverage * 100, 2))
            }
        ],
        'map_data': geojson
    }

    return result


def calculate_aggregate_report(all_reports):
    """
    Calculates aggregate reports based on the individual reports

    Arguments:
        all_reports (list): the list of report objects

    Returns: all_reports with the aggregate reports inserted
    """

    if all_reports[0]['route_id'] == "All":
        print("Warning: aggregate reports being calculated",
              "when aggregates already exists")

    # read existing reports into a dataframe to work with them easily
    df = pd.DataFrame(all_reports)

    # for each aggregate type
    types = list(df['route_type'].unique()) + ['All']
    for t in types:
        # filter df to the routes we are adding up
        if t == 'All':
            filtered = df
        else:
            filtered = df[df['route_type'] == t]

        # on-time percentage: sum([all on-time stops]) /
        #                     sum([all scheduled stops])
        count_on_time = (filtered['on_time_percentage'] *
                         filtered['scheduled_stops']).sum()
        on_time_perc = count_on_time / filtered['scheduled_stops'].sum()

        # coverage: (sum([all on-time stops]) + sum([all bunches])) /
        #            sum([all scheduled stops])
        coverage = (count_on_time + filtered['num_bunches'].sum()) / \
                   filtered['scheduled_stops'].sum()

        # aggregate the graph object
        # x-axis is same for all
        first = filtered.index[0]
        times = filtered.at[first, 'line_chart']['times']

        # sum up all y-axis values
        bunches = pd.Series(filtered.at[first, 'line_chart']['bunches'])
        gaps = pd.Series(filtered.at[first, 'line_chart']['gaps'])

        # same pattern for the geojson list
        geojson = filtered.at[first, 'map_data']['bunches']

        for i, report in filtered[1:].iterrows():
            # pd.Series adds all values in the lists together
            bunches += pd.Series(report['line_chart']['bunches'])
            gaps += pd.Series(report['line_chart']['gaps'])

            # lists concatenate together
            geojson += report['map_data']['bunches']

        # again, convert to native python types since the json library
        # doesn't work with numpy types
        n_bunches = int(filtered['num_bunches'].sum())
        n_gaps = int(filtered['num_gaps'].sum())
        n_intervals = int(filtered['total_intervals'].sum())

        # Get overall health
        health = calculate_health(n_bunches/n_intervals, n_gaps/n_intervals,
                                  on_time_perc/100)

        # save a new report object
        new_report = {
            'route_id': t,
            'route_name': t,
            'route_type': t,
            'date': all_reports[0]['date'],
            'overall_health': float(round(health*100, 2)),
            'num_bunches': n_bunches,
            'num_gaps': n_gaps,
            'bunched_percentage': round(n_bunches/n_intervals*100, 2),
            'gapped_percentage': round(n_gaps/n_intervals*100, 2),
            'total_intervals': n_intervals,
            'on_time_percentage': float(round(on_time_perc, 2)),
            'scheduled_stops': int(filtered['scheduled_stops'].sum()),
            'coverage': float(round(coverage, 2)),
            'line_chart': {
                'times': times,
                'bunches': list(bunches),
                'gaps': list(gaps)
            },
            'route_table': [
                {
                    'route_id': t,
                    'route_name': t,
                    'overall_health': float(round(health*100, 2)),
                    'bunched_percentage': round(n_bunches/n_intervals*100, 2),
                    'gapped_percentage': round(n_gaps/n_intervals*100, 2),
                    'on_time_percentage': float(round(on_time_perc, 2)),
                    'coverage': float(round(coverage, 2))
                }
            ],
            'map_data': {
                'type': 'FeatureCollection',
                'bunches': geojson
            }
        }

        # put aggregate reports at the beginning of the list
        all_reports.insert(0, new_report)

    # Add route_table rows to the aggregate report
    # Set up a dict to hold each aggregate table
    tables = {}
    for t in types:
        tables[t] = []

    # Add rows from each report
    for report in all_reports:
        # add to the route type's table
        tables[report['route_type']].append(report['route_table'][0])

        # also add to all routes table
        if report['route_id'] != "All":
            # if statement needed to not duplicate the "All" row twice
            tables['All'].append(report['route_table'][0])

    # find matching report and set the table there
    for key in tables.keys():
        for report in all_reports:
            if report['route_id'] == key:
                # override it because the new table includes the row
                # that was already there
                report['route_table'] = tables[key]
                break  # only 1 report needs each aggregate table

    return all_reports
