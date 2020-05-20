# AWS Lambda Scripts

This folder contains the files running on AWS Lambda.  In order to deploy there, we have to package all needed dependencies into a zip file with the script we are running then upload it to AWS.  Changes to the files in this repository will not affect the live code unless you re-deploy.

The zip file in this directory is a copy of the currently deployed one.

## Adding dependencies

AWS Lambda runs on a Linux environment, so any packages you include need to be compatible with Linux.  AWS provides a built-in Layer that has the SciPy and Numpy libraries already, all other packages need to be in the zip file.

Many packages are compatible with any operating system, and you can just use pip to get the files.  This command will install the requests library in the current working directory, into a subdirectory named "lambda_package".

`pip install -t ./lambda_package requests`

If a package is built for a specific os, then you can either run that command on a linux machine, or download the linux distribution yourself.  Just download the correct .whl file from pypi.org and extract it to get the same files that pip would install.

For example, the pandas library is available here: <https://pypi.org/project/pandas/#files>

From that page you would download `pandas-1.0.3-cp37-cp37m-manylinux1_x86_64.whl`.  Note that cp37 is for Python 3.7, other versions are available as well.

One last exception, we had to obtain the psycopg2 library files from this repository since pypi.org only lists Windows .whl files.  <https://github.com/jkehler/awslambda-psycopg2>
