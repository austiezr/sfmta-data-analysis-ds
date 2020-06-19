# AWS Lambda Scripts

This folder contains the code running on AWS Lambda.  In order to deploy there, we have to package all needed dependencies into a zip file with the script we are running then upload it to AWS.  Changes to the files in this repository will not affect the live code unless you re-deploy.

There are currently four different functions deployed.  The location collector runs once per minute, and the other three all run once per day at 3am PST.

- `storeAPIResponseInDatabase`
  - This function collectes the vehicle location data.
  - The script here is location_collector.py.  The AWS function name isn't consistent with the others, since we learned after this one that it is not possible to rename AWS Lambda functions.
    - It pulls location data from this API route: http://restbus.info/api/agencies/sf-muni/vehicles
- `routeCollector`
  - This function collects route definition data, including path coordinates and stop information.
  - It saves the JSON response from this API route (for all bus routes): http://webservices.nextbus.com/service/publicJSONFeed?command=routeConfig&a=sf-muni&r=1
- `scheduleCollector`
  - This function collects schedule data, which tells us when buses are expected to be at different stops.
  - It saves the JSON response from this API route (for all bus routes): http://webservices.nextbus.com/service/publicJSONFeed?command=schedule&a=sf-muni&r=1
- `generateDailyReport`
  - This function is in the Report_Generation folder, and generates our daily report.  See the readme in that folder for more info.

The zip files in this directory are copies of the currently deployed ones.

## Adding dependencies

AWS Lambda runs on a Linux environment, so any packages you include need to be compatible with Linux.  AWS provides a built-in Layer that has the SciPy and Numpy libraries already, all other packages need to be in the zip file.

Many packages are compatible with any operating system, and you can just use pip to get the files.  This command will install the requests library in the current working directory, into a subdirectory named "lambda_package".

`pip install -t ./lambda_package requests`

If a package is built for a specific os, then you can either run that command on a linux machine, or download the linux distribution yourself.  Just download the correct .whl file from pypi.org and extract it to get the same files that pip would install.

For example, the pandas library is available here: <https://pypi.org/project/pandas/#files>

From that page you would download `pandas-1.0.3-cp37-cp37m-manylinux1_x86_64.whl`.  Note that "cp37" is for Python 3.7, other versions are available as well.

One last exception, we had to obtain the psycopg2 library files from this repository since pypi.org only lists Windows .whl files.  <https://github.com/jkehler/awslambda-psycopg2>

## Future Development

While this method of zipping up dependencies worked for us, there were two alternatives: layers and Docker.

AWS Lambda has a thing called "layers" which are essentially another way to upload the dependencies your scripts need.  There is one layer that AWS provides by default for Python 3.7, which gives Numpy and Scipy.  This is why those two libraries are not needed in our zip files.  It is also possible to create your own layers.  We did not look into that at the time, but it may be a way to simplify the deployment in the future.

The other option is to upload Docker images to AWS Lambda.  Most of us in Labs 24 ran Windows and could not use Docker, so we did not choose this option before.  We did not research it so it may be worth reading about it you want to try this.
