# This file contains the main executable code that generates daily reports
# and saves them to the database

# Import code from the other files in this folder
import report_functions

# Library imports
import pandas as pd
import psycopg2 as pg
from psycopg2.extras import execute_batch
import json
from dotenv import load_dotenv
import os

def generate_report(date):
    """
    Generates the daily report for the given date

    (Before deployment to AWS Lambda, remove date parameter and set it's 
    value automatically.  Easier to test this way)
    """

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

    # get all active routes 
    route_ids = report_functions.get_active_routes(date, cursor)
    route_ids.sort()
    print(f"Found {len(route_ids)} active routes")

    # get the report for all routes
    # (this loop takes 3-4 minutes with 28 active routes)
    all_reports = []
    for rid in route_ids:
        try:
            print(f"Generating report for route {rid}...")
            all_reports.append(report_functions.generate_route_report(rid,
                                                                date, cnx))
        except KeyboardInterrupt:
            # if a user wants to stop this early
            break
        except Exception as err: 
            # if any particular route throws an error
            print(f"Route {rid} failed, error:")
            print(err, '\n')
    
    # Calculate aggregates for "All" and each type of transit
    all_reports = report_functions.calculate_aggregate_report(all_reports)
    print("Done generating report for", date)

    # save new report in the database (all one row)
    query = """
        INSERT INTO reports (date, report)
        VALUES (%s, %s);
    """
    cursor.execute(query, (date, json.dumps(all_reports)))
    cnx.commit()
    print("Report saved")

    # Extra code with more options to save or update reports:

    # Save the reports object to a file in the current directory (if needed)

    # with open(f'report_{date}.json', 'w') as outfile:
    #     json.dump(all_reports, outfile)


    # Update an existing report in the database (if needed)

    # query = """
    #     UPDATE reports
    #     SET report = %s
    #     WHERE date = %s ::TIMESTAMP;
    # """

    # d = str(pd.to_datetime(date).date())
    # cursor.execute(query, (json.dumps(all_reports), d))
    # cnx.commit()


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

import time
if __name__ == "__main__":
    # Used for local testing, generate a report and save it
    before = time.time()

    generate_report('2020-5-26')
    
    elapsed = time.time() - before
    minutes = int(elapsed / 60)
    seconds = round(elapsed % 60, 2)
    print(f"\nFinished in {minutes} minutes and {seconds} seconds")
