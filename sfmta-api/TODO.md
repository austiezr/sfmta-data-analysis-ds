There's really only one major update the API needs soon; currently we're storing daily reports on a 60-day rolling\
window. This was done to help manage storage creep while still providing enough recent data to satisfy stakeholder\
requirements, but we do still need to generate reports at-will outside of that window on the rare occasion that\
someone might need that.

This will require implementing some of the code in [AWS_Lambda][lambda] within the API, 
similarly to [sfmta-api/schedule][schedule], to generate the requested report from the historical data\
(which we're saving indefinitely) for the specified date.

Slightly less pressing, but stakeholder has also indicated interest in being able to generate at-will reports for\
ranges outside of a single day; aggregating reports at the week/month level.

The largest hurdles with both of these will be execution time; to a certain extent, we can communicate to a user\
that it will take a while for a fresh report to generate. At the same time, 3-4 minutes of wall time is certainly\
not ideal. Optimization within the report generation functions will be key.

[lambda]: sfmta-data-analysis-ds/AWS_Lambda
[schedule]: sfmta-data-analysis-ds/sfmta-api/application/schedule