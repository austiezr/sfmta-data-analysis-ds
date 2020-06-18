## Data Files

- dropdown.txt
  - a collection of routes containing lists for type, name, and id
- dropdown_new.txt
  - a collection of routes, matches format of the dropdown menus in the labs 22 site
- listfile.txt
  - 45 sets of lat/lon coordinates
- route_data_new.json
  - Dataframe of routes
  - 86 rows
  - columns: route_id, route_name, type, lat, lon, stopId, tag, title, dir
  - same as jordan-sfmta-api/route_data_new.json
- route_info.csv
  - Dataframe of individual stops
  - 6290 rows
  - columns: route_id, lat, lon, stopId, tag, title, dir
  - same as jordan-sfmta-api/route_info.csv
- route_paths.json
  - Dataframe of latitude/longitude coordinates describing each bus route
  - 86 rows
  - columns: tag (rout id), path, name
  - same as jordan-sfmta-api/route_paths.json
- schedule_data.json  
  - Dataframe of times each stop is scheduled to have a bus
  - 404 rows
  - columns: day, route_tag, times, direction
  - same as jordan-sfmta-api/schedule_data.json
- schedule_data_new.json
  - updated version of schedule_data.json, same columns
  - 416 rows
  - same as jordan-sfmta-api/schedule_data_new.json
- stop_data.csv
  - Dataframe of individual stops, same as route_info.csv but missing the dir column
  - 6420 rows
  - columns: lat, lon, stopId, tag, title, route_id
  - same as jordan-sfmta-api/stop_data.csv
- temp.json
  - list of lat/lon coordinates

## Additional Data

Labs 22 had their own data stored in a MySQL database.  That was taken down by Labs 24 for two reasons: Labs requirements said to use PostgreSQL instead, and the data itself was incomplete.  The bus location data had gaps where entire days were not recorded, and schedules or route definitions were not stored at all, so Labs 24 could not use it when making the daily reports.

Since the database was taken down and the data files were too large to upload to github, we have uploaded the data to a google drive under SFMTALAMBDA@gmail.com.  Your team lead should have credentials for that if you need to access it.

That database had three tables:

- location
  - This was bus location data the Labs 22 team collected themselves, with a similar schema to the one currently used in the production database.
  - It contains data between 4/13 and 4/30 (12 out of 18 days)
  - CSV (~740k rows, 77 MB): https://drive.google.com/file/d/1gzL29wYU_CIYeC1p4aKDBfzBL3XWuVJr/view?usp=sharing
- historic_location
  - This table had bus locations collected before Labs 22, we assume Jarie collected it.  It uses the exact same schema as the location table.
  - It contains data between 1/20 and 4/13 (47 out of 84 days)
  - CSV (~15 million rows, 2 GB): https://drive.google.com/file/d/1rRh5qm9NJO6szg8Mvo6lD4fWRNpbQnCP/view?usp=sharing
- historic_location_stops
  - This table contained a subset of the historic_location data, with added columns for stop_id, stop_lat, and stop_lon.
  - We believe this was part of the calculations when trying to match up bus locations to stops on their route, but we did not find anything else that used this data.
  - CSV (~3.3 million rows, 406 MB): https://drive.google.com/file/d/1umyr7Es8XcdmHjDyc_1xuF-reKi2V7-K/view?usp=sharing

Lastly, there is also a .sql dump file of the entire database.  If you have MySQL installed, this can be used to restore the database itself.  It is also 2 GB: https://drive.google.com/file/d/1Bk5JIZuvZGMrIZdO-xsQNZ0LpJjXMk5s/view?usp=sharing
