# SFMTA Daily Report Documentation

This document describes the data structure of the daily reports. Below is an example report. Each day’s report is stored in a single row in the database, as a list of these objects.  Each item in the list is the report for that route or group of routes.

    {
	    "route_id": "All",
	    "route_name": "All",
	    "route_type": "All",
	    "date": "2020-06-01 00:00:00",
	    "overall_health": 73.68,
	    "num_bunches": 9517,
	    "num_gaps": 43809,
	    "bunched_percentage": 5.49,
	    "gapped_percentage": 25.27,
	    "total_intervals": 173366,
	    "on_time_percentage": 42.54,
	    "scheduled_stops": 36866,
	    "coverage": 42.8,
	    "line_chart": {
		    "times": ["12:30", "12:40", "12:50", "13:00", "13:10", "13:20"],
		    "bunches": [11, 22, 29, 15, 16, 26],
		    "gaps": [29, 33, 39, 35, 34]
	    },
	    "route_table": [
		    {
			    "route_id": "All",
			    "route_name": "All",
				"overall_health": 63.41,
			    "bunched_percentage": 12.62,
			    "gapped_percentage": 38.42,
			    "on_time_percentage": 42.54,
			    "coverage": 42.8
		    }, ...
	    ],
	    "map_data": {
		    "type": "FeatureCollection",
		    "bunches": [
		    {
			    "type": "Feature",
			    "geometry": {
				    "type": "Point",
				    "coordinates": [-122.4931, 37.7797]
			    },
			    "properties": {
				    "time": "2020-06-02 14:02:24",
				    "stopId": "14277"
			    }
			},... ]
		}
	}
	
    {
	    "route_id": "1",
	    "route_name": "1-California",
	    "route_type": "Bus",
	    ...
    }

## Overall Structure

-   The report is an array of json objects. Each object is either the report for a specific route, or an aggregate report for all routes of one type.
-   Each object should include all the data needed for a particular view.

## Field Explanations

-   **route_id**, **route_name**, and **route_type**
	-   Text
	-   These all identify the route itself. For aggregate reports they are all the same (eg. “All”, “Bus”, or “Rail”)
-   **date**
	-   Text
	-   The date this report is for
-   **overall_health**
	-   Decimal number
	-   The overall health score for this report, a percentage
-   **num_bunches**
	-   Whole number
	-   The total number of bunches observed on this route, or group of routes
-   **num_gaps**
	-   Whole number
	-   The total number of gaps observed on this route, or group of routes
-   **bunched_percentage**
	-   Decimal number
	-   The percentage of bunches (num_bunches / total_intervals)
-   **gapped_percentage**
	-   Decimal number
	-   The percentage of gaps (num_gaps / total_intervals)
-   **total_intervals**
	-   Whole number
	-   The total number of intervals measured for bunches and gaps.
-   **on_time_percentage**
	-   Decimal number
	-   The percentage of stops that were made on-time
	-   Calculated by finding the number of on-time stops vs the number of scheduled stops.
-   **scheduled_stops**
	-   Whole number
	-   The number of scheduled stops on a route. This is also not displayed on the main page.
	-   The SFMTA schedule only sets specific times for some stops, so this will be much lower than total_intervals.
-   **coverage**
	-   Decimal number
	-   The percentage of coverage a route had for the day
	-   Defined as (on-time stops + number of gaps) / scheduled stops
	-   This is meant to give a percentage of how much of the schedule was covered, so it combines stops that were made on time and times the buses were too close together (meaning buses arrived more frequently than scheduled)
-   **line_chart**
	-   JSON object with 3 arrays
	-   This object holds the data for the line chart at the bottom
	-   The times array is all x-axis values
	-   The bunches and gaps arrays are y-axis values for each line
	-   Currently we are using 10 minute intervals, so there should be 144 items in each array
-   **route_table**
	-   An array of JSON objects
	-   This array holds the data for the routes table at the bottom (shares a space with the line chart)
	-   Each object in the array is one row of the table
	-   Aggregate reports have their own row, plus rows of each route of that type
	-   Specific route reports will only have the one row for that route
-   **map_data**
	-   Array of geojson objects
	-   This object will hold the data for the map display

