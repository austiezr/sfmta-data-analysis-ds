# AWS Lambda script that runs every minute
# pulls data from Restbus and stores in our database

import requests
import pandas as pd
import psycopg2 as pg
from psycopg2.extras import execute_batch
from dotenv import load_dotenv
import os
import time

def lambda_handler(event, context):

    # credentials for DB connection
    load_dotenv()
    creds = {
      'user': os.environ.get('USER'),
      'password': os.environ.get('PASSWORD'),
      'host': os.environ.get('HOST'),
      'dbname': os.environ.get('DATABASE')
    }
    
    # set up database connection
    cnx = pg.connect(**creds)
    cursor = cnx.cursor()
    
    # get the vehicles data
    url = 'http://restbus.info/api/agencies/sf-muni/vehicles'
    r = requests.get(url)
    
    # store api response in a dataframe for convenience
    df = pd.DataFrame.from_dict(r.json())
    
    # drop columns we aren't storing
    df = df.drop(['_links', 'predictable', 'leadingVehicleId'], axis=1)
    
    # add a timestamp to each row
    df['timestamp'] = [pd.to_datetime(time.ctime())] * len(df)
    
    # name columns to match the database
    df.columns = ['vid', 'rid', 'direction', 'age', 'kph', 'heading', 
                  'latitude', 'longitude', 'timestamp']
    
    # format data into a list of dicts, each row becomes a separate dict
    rows = list(df.to_dict('index').values())
    
    # psycopg2.extras.execute_batch
    # inserts the whole dataframe into the database
    execute_batch(cursor, """
        INSERT INTO locations(timestamp, rid, vid, age, kph, heading, 
                              latitude, longitude, direction) 
        VALUES (
            %(timestamp)s,
            %(rid)s,
            %(vid)s,
            %(age)s,
            %(kph)s,
            %(heading)s,
            %(latitude)s,
            %(longitude)s,
            %(direction)s
        );
    """, rows)
    
    print(f"Inserted {len(df)} rows")
    
    cursor.close()
    cnx.commit()
    cnx.close()
