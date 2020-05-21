# defines the database schema

# import datetime
import psycopg2 as pg
from dotenv import load_dotenv
import os

load_dotenv()

creds = {
  'user': os.environ.get('USER'),
  'password': os.environ.get('PASSWORD'),
  'host': os.environ.get('HOST'),
  'dbname': os.environ.get('DATABASE'),
  'port': os.environ.get('PORT')
}


def Location(datetime, rid, vid, secs,
             kph, head, lat, lon,
             dir, timeInSec, timeInMin, timeInHour,
             year, doy, dow):
    sql = "INSERT INTO location " \
          "(datetime, rid, vid, secs, kph, head, lat," \
          "lon, dir, timeInSec, timeInMin, timeInHour, year, doy, dow) " \
          "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = con.cursor()
    cursor.execute(sql, (datetime, rid, vid, secs, kph, head, lat, lon, dir,
                         timeInSec, timeInMin, timeInHour, year, doy, dow))
    con.commit()


def init_database():
    con = pg.connect(**creds)
    global con


#
#
# class Location(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     datetime = db.Column(db.DateTime)
#     rid = db.Column(db.String(8))
#     vid = db.Column(db.Integer)
#     secs = db.Column(db.Integer)
#     kph = db.Column(db.Integer)
#     head = db.Column(db.Integer)
#     lat = db.Column(db.Float)
#     lon = db.Column(db.Float)
#     dir = db.Column(db.String(16))
#     timeInSec = db.Column(db.Integer)
#     timeInMin = db.Column(db.Integer)
#     timeInHour = db.Column(db.Integer)
#     year = db.Column(db.Integer)
#     doy = db.Column(db.Integer)
#     dow = db.Column(db.Integer)
#
#
#     def __repr__(self):
#         return '<ID %r>' % self.id
#
# def init_db():
#     db.create_all()
#     db.session.commit()
#


if __name__ == '__main__':
    init_database()
