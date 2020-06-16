# Daily Report Generation

This folder contains all the code that generates the daily reports seen on the website.  Just like with the other AWS Lambda functions, it was packaged into a zip file to be deployed.

The code is divided into 4 files:
- `report_classes.py` includes the Route and Schedule classes, which load route and schedule definitions from the database and help process them.
- `report_functions.py` includes all the separate functions used to process data while generating the report.
- `report_main.py` is the main file, and contains the function called by AWS Lambda
- `report_test.py` can be used for local testing or updating past reports in case any updates are made to the process.  It does not need to be uploaded to AWS Lambda.

The report generation process has several steps and goes through a lot of data, so it does take some time to get the report for an entire day.  As of now it takes about 3 minutes on a local machine and about 6 on AWS Lambda.  There are also fewer buses and bus routes running because of the stay-at-home orders, so we expect it will take about 2-3x as long once service returns to normal.  While we were able to optimize some (the original un-optimized version took 20 minutes locally), there's definitely room for improvement.

AWS Lambda has a 15 minute limit, so if this function starts to take longer than that we will have to find an alternative.  One option Labs 24 found was [AWS Step Functions](https://aws.amazon.com/step-functions/), which essentially lets you break up this process into multiple parts, but there was not enough time left in Labs to switch over to it then.

The report structure itself is described in [report_data_structure.md](https://github.com/Lambda-School-Labs/sfmta-data-analysis-ds/blob/master/AWS_Lambda/Report_Generation/report_data_structure.md).

## The Process

While this is meant to describe what the code is doing, it also gives a basic overview of our methodology.

- Everything is started by calling `generate_report()` in `report_main.py`.  After loading the environment variables it needs, it loads all bus location data up-front.  It then calls `generate_route_report()` for each of the active routes, which does the following steps:
	- Load the schedule and route definition for that route on that day.
	- Run the `clean_locations()` function, which does several cleaning steps (see the docstring for those specifics), and most importantly finds the closest stop on the route to each location report.
	- Use that info to generate a list of times that each bus was at each stop. ( `get_stop_times()` )
	- Calculate bunches and gaps by analyzing those times.  If a stop did not see any buses for too long it was a gap, and any time two buses were too close to each other it was a bunch.  Also track the total number of time intervals measured so we can get the percentages. ( `get_bunches_gaps()` )
	- Calculate on-time percentage by checking each time a stop was scheduled to have a bus, and seeing if any of the observed buses were at the stop at that time. ( `calculate_ontime()` )
	- Calculate coverage and overall health based on the other statistics obtained so far.
	- Save everything in a dict, to be converted to json at the end.
- After all individual routes have been processed, we calculate aggregate reports with `calculate_aggregate_report()`. This is able to use sums and averages of all the other statistics calculated so far, so it does not directly analyze any of the data and is much faster.
- Finally, save the report object as json in the database.

## Approximations

The process so far is not perfect, and we had to make some approximations in order to get everything working before Labs 24 ended.  While the statistics generated are pretty close, we're sure they could get more accurate with more work.

**Stop times**

Right now we take each location report and find the closest stop to it.  We then approximate and say that bus was at that stop at that time.  It will take more work to figure out exactly when a bus was at each stop, since it is difficult to tell if each location report was approaching that closest stop or leaving it.  This approximation affects all statistics on the daily report.

Our best idea is to get a list of coordinates, or path, that describes the route.  We could then project bus locations onto that path and have bus locations represented by only time and distance along the route.  We could then use the current speed of each location report to calculate when it was at or will get to that closest stop.

**On-time percentage**

There is no easy way to tell which bus is making which trip on the schedule, so we simply calculate on-time by asking "was *any* bus at this stop at the scheduled time?"  This covers things from the rider's view, they don't care which bus it is so long as it's there when the schedule says it will be.  However this does not account for the individual buses sticking to their schedules.  This approximation may be good enough to leave as-is, but it is worth being aware of.

**Location reports**

We currently only calculate the report using bus location reports that list a direction (inbound or outbound).  Some rows will have no direction, which we assume means it was transitioning between inbound and outbound.  However, looking at the inbound and outbound trips that way does not always get us location reports for all stops on the route.  Defining a "trip" as a sequence of location reports with the same direction will sometimes not capture the stops at each end of the route.  It should be possible to include some extra rows at the end of each trip to ensure those stops are captured.

More rarely, a trip will only include half of a route.  When that happens, it is unclear if the bus just didn't finish the route, if it just wasn't reporting its direction for half the route, or if it was something else.  For now we assume that first case and only calculate reports with the data we have.  It's also hard to tell when this happens without plotting the points on a map and looking at them.
