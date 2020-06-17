# sfmta-data-analysis-ds/sfmta-api

This folder contains a Flask app that pulls data from the AWS database,\
and serves it to the web front end through API calls.\
Includes basic templates and a couple of baseline endpoints.

Currently this API isn't used in production, but serves as a quick and easy vehicle for exploratory work and testing\
for the DS team. Eventually API will be used in production app very rarely, to generate custom reports outside of our\
storage window. See TODO [here][TODO].

05/20 - Folder also contains Dockerfile and requirements.txt for Elastic Beanstalk deployment via docker.\
06/15 - Also includes the schedule package (implemented) and routes package (not implemented) to facilitate handling\
schedule and route data, as well as a brief TODO.

## Endpoints

### Usable for exploratory work and prototyping

- /daily-general-json, method=['GET']
  - Expects date as string: YYYY-MM-DD, defaults to previous day if none given
  - full locations data from given date
- /daily-route-json, method=['GET']
  - Expects date as string: YYYY-MM-DD, defaults to previous day if none given
  - Expects route as route id as string, defaults to '1' (california-1 line) if none given
  - full locations data for given date and route
- /get-route-info, methods=['GET'] 
  - Expects date as string: YYYY-MM-DD, defaults to previous day if none given
  - Expects route as route id as string, defaults to '1' (california-1 line) if none given
  - schedule info for specified route and date, used as above

### Mainly used for testing

- / 
  - returns "Hello there!" 
  - used to quickly test successful deployment
- /test 
  - returns head of locations table 
  - used to quickly test DB connection
- /system-real-time 
  - returns 100 most recent entries in locations, human readable 
  - previously used for testing, no longer needed
- /system-real-time-json 
  - same as above, machine readable

# For Future Cohorts, With Love From Labs 24:

An instance of this API is currently (as of 5/21 and for the foreseeable future)\
deployed and functioning via a docker container on Elastic Beanstalk [here][live-api].

You should receive credentials to manage it from your TL;\
If not, reach out to me through email (austin-robinson@lambdastudents.com)\
and I may be able to help.

It is very finicky and easily upset. You must be gentle and kind or it will punish you.

The most reliable method of interacting with this environment\
is through the EB command line; see [here][install] and [here][use].

You will need to set up your directory for this api to track to the correct environment,\
or create a new environment via eb init, eb create, etc.

In order to deploy changes to it, you will first need to git pull from master,\
and ensure you've committed or stashed any local changes.

I'll say it again.

COMMIT BEFORE YOU DEPLOY.\
COMMIT. BEFORE. YOU. DEPLOY.

Then, eb deploy SHOULD push and deploy your new build to the live instance.

If everything is working correctly, you should be able to consistently eb deploy changes\
even if eb is telling you the deploys are failing; if the deploy "fails" but actually does\
deploy the changes, you'll need to eb setenv afterwards to restore the DB connection.

If the deploy succeeds without errors, env. variables should be maintained.

Obsessively test anyway because EB has violated your trust so many times before.\
The health dashboard will lie to you about being broken, and it will lie to you about being fine.

If and when it inevitably breaks for absolutely no reason,\
and your dashboard is covered with upsetting words like WARNING, DEGRADED, SEVERE,\
the following process has proven to be the only way to (almost) reliably fix it.

From [this link][EC2 instances]:
1) find the appropriate instance id for sfmta-test

From [this link][EC2 auto-scaling]:
1) select the appropriate auto-scaling group; you can check by selecting one,\
 hitting the instances tab at the bottom,\
and comparing to the instance id from above
2) Edit
3) set Desired Capacity, Min, and Max to 0
4) Save
5) wait until your number of instances changes from 1 to 0

Then from your command line, within the right directory, using the EB CLI:\
1) eb deploy
2) wait in panicked silence until the deploy completes
3) eb setenv USERNAME=whatever_username PASSWORD=whatever_password_is HOST=whatever_host_is DATABASE=whatever_db_is
4) wait in panicked silence until the configuration completes

Then back at [this link][EC2 auto-scaling]:
1) select the appropriate auto-scaling group; should be the only ASG with no instances
2) Edit
3) set Desired Capacity, Min, and Max to 1 (or from the command line: eb scale 1)
4) Save
5) wait until your number of instances changes from 0 to 1

There is a 90% chance your dashboard will still be horrifying,\
but the application should now function as expected regardless.\
If application functions but doesn't connect to DB, eb setenv again.\
If application doesn't run at all, eb deploy, eb setenv.\
Application should now function.

Eventually the dashboard health should normalize.\
Or it won't.\
As long as everything functions it doesn't really matter.

If that still doesn't fix it, or if your deploys aren't pushing new code anymore,\
which can happen even if the dashboard says everything is fine and that your latest\
version of the application is deployed,\
do the following.

From [your dashboard][dash]:
1) Environment actions
2) Rebuild environment
3) wait in horrified silence for between 5 and 20 minutes until the rebuild is complete

If still broken, follow all steps from first fix process again at this point.\
Dashboard should now be green and application functioning.\
If not, hopefully at least application is functioning.\
If not, sob quietly for a while, then repeat all steps ad infinitum.

After rebuilds, resetting instances, and deploys, the dashboard may indicate errors or degradations.\
Sometimes these resolve themselves with time (5-30 minutes).\
Sometimes they don't.\
Sometimes the logs are useful in troubleshooting and resolving these issues.\
Usually they aren't.\
Also your system health may spontaneously degrade for no apparent reason.\
Assuming you didn't do anything to cause this,\
this almost always resolves itself and doesn't affect performance.

Follow the process and be patient and eventually things will generally stabilize.

If you initiate a process (deployment, config change, etc.) never abort it.\
This will almost always break the environment and generally requires a full rebuild/redeploy as outlined above.

[live-api]: http://ds.datadriventransit.org/
[install]: https://github.com/aws/aws-elastic-beanstalk-cli-setup
[use]: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html
[EC2 auto-scaling]: https://console.aws.amazon.com/ec2/autoscaling/home?region=us-east-1#AutoScalingGroups:id=awseb-e-46ix3awcsk-stack-AWSEBAutoScalingGroup-241DU78KAD94;view=details
[dash]: https://console.aws.amazon.com/elasticbeanstalk/home?region=us-east-1#/environment/dashboard?applicationName=sfmta-test&environmentId=e-46ix3awcsk
[todo]: sfmta-data-analysis-ds/sfmta-api/TODO.md
