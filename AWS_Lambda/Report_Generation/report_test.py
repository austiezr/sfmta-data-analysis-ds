# Used for local testing and manual report generation
# This is not used in the AWS Lambda deployment

from report_main import generate_report
import pandas as pd
import time

import psycopg2 as pg
import json
from dotenv import load_dotenv
import os


def download_report(date):
    """
    Loads a report from the database and saves to a local json file

    date (str): the date to pull
    """

    # Set up database connection
    load_dotenv()
    creds = {
      'user': os.environ.get('USER'),
      'password': os.environ.get('PASSWORD'),
      'host': os.environ.get('HOST'),
      'dbname': os.environ.get('DATABASE')
    }
    cnx = pg.connect(**creds)
    cursor = cnx.cursor()

    # Fetch report from the database
    query = """
        SELECT report
        FROM reports
        WHERE date = %s ::TIMESTAMP;
    """
    cursor.execute(query, (date,))
    data = cursor.fetchone()[0]

    # Save to a file
    with open(f'report_{date}.json', 'w') as outfile:
         json.dump(data, outfile)


if __name__ == "__main__":
    # Used this code to update past reports with new changes, ran locally
    begin = pd.to_datetime('2020-5-21')
    end = pd.to_datetime('2020-6-15')

    while begin <= end:
        start_time = time.time()

        # generate report for this day
        # (change new_report to False to update existing reports instead)
        generate_report(event='', context='', date=begin, new_report=False)

        # print execution time
        elapsed = time.time() - start_time
        minutes = int(elapsed / 60)
        seconds = round(elapsed % 60, 2)
        print(f"\nFinished in {minutes} minutes and {seconds} seconds\n\n")

        # move to next day
        begin += pd.Timedelta(days=1)
