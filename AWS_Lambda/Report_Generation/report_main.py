# This file contains the main executable code that generates daily reports
# and saves them to the database

# Import code from the other files in this folder
import report_functions as func

# Library imports
import pandas as pd
import psycopg2 as pg
from psycopg2.extras import execute_batch
import json
from dotenv import load_dotenv
import os
import traceback


def generate_report(event, context, date='yesterday', new_report=True):
    """
    Generates the daily report for the given date

    (Before deployment to AWS Lambda, remove date parameter and set it's
    value automatically to yesterday.  Easier to test this way)

    Arguments:
        event, context: keyword arguments required by AWS Lambda, not used

        date (str): the date of the report to generate (default: 'yesterday')

        new_report (bool): if true, the report is saved to a new row in the
                           database.  if false, updates the report object on an
                           existing row with the same date. (default: True)
    """

    if date == 'yesterday':
        # actually get a timestamp for yesterday
        date = pd.to_datetime('today') - pd.Timedelta(days=1)
        date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        date = pd.to_datetime(date)

    print('Generating report for', date)

    # Load credentials and connect to the database
    load_dotenv()
    creds = {
      'user': os.environ.get('USER'),
      'password': os.environ.get('PASSWORD'),
      'host': os.environ.get('HOST'),
      'dbname': os.environ.get('DATABASE')
    }
    cnx = pg.connect(**creds)
    cursor = cnx.cursor()

    # Load all location info
    all_locations = func.load_locations(date, cnx)
    print("Location reports for the day:", len(all_locations))

    # Get list of active routes
    route_ids = list(all_locations['rid'].unique())
    route_ids.sort()
    print(f"Found {len(route_ids)} active routes")

    # get the report for all routes
    # (this loop takes 3-4 minutes with 28 active routes)
    all_reports = []
    for rid in route_ids:
        try:
            print(f"Generating report for route {rid}...")
            loc = all_locations[all_locations['rid'] == rid]
            all_reports.append(func.generate_route_report(rid, date, cnx, loc))
        except KeyboardInterrupt:
            # if a user wants to stop this early
            print("Keyboard interrupt, quitting")
            quit()
        except:
            # if any particular route throws an error, print the traceback 
            # so we can troubleshoot it
            print(f"Route {rid} failed, traceback:\n")
            traceback.print_exc()
            print()

    # Calculate aggregates for "All" and each type of transit
    all_reports = func.calculate_aggregate_report(all_reports)
    print("Done generating report for", date)

    if new_report:
        # save new report in the database (all one row)
        query = """
            INSERT INTO reports (date, report)
            VALUES (%s, %s);
        """
        cursor.execute(query, (date, json.dumps(all_reports)))
        cnx.commit()
        print("Report saved")
    else:
        # Update an existing report in the database
        query = """
            UPDATE reports
            SET report = %s
            WHERE date = %s ::TIMESTAMP;
        """
        cursor.execute(query, (json.dumps(all_reports), date))
        cnx.commit()
        print("Report updated")


    # Extra code with more options to save or update reports:

    # Save the reports object to a file in the current directory (if needed)

    # with open(f'report_{date}.json', 'w') as outfile:
    #     json.dump(all_reports, outfile)


    # Save new report in the database (separate rows method)
    #   Saves each route id on it's own row in the
    #   database.  Expects an rid column.

    # # Set up an iterator to go through all the reports
    # iter_reports = ({
    #     'date': date,
    #     'rid': report['route_id'],
    #     'report': json.dumps(report)
    # } for report in all_reports)
    # # Build query and insert all rows
    # query = """
    #   INSERT INTO reports (date, rid, report)
    #   VALUES (%(date)s, %(rid)s, %(report)s);
    # """
    # execute_batch(cursor, query, iter_reports)
    # cnx.commit()
