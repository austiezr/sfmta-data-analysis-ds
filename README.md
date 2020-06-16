# SFMTA Data Analysis

Take a look at our product [here!][live]

## Contributors

|                                       [Agustin Cody Vargas](https://github.com/AVData/)                        |                                       [Jordan Ireland](https://github.com/Jordan-Ireland/)                                        |                                       [Mathias Ragnarson Skreden](https://github.com/skredenmathias/)                                        |                                                            
| :-----------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------: | :-----------------------------------------------------------------------------------------------------------:  |
|                      [<img src="https://ca.slack-edge.com/T4JUEB3ME-UP8JY0CG6-cd15b5cb2cf1-512" width = "200" />](https://github.com/AVData/)                       |                      [<img src="https://ca.slack-edge.com/T4JUEB3ME-UL5US8MPA-f77dd1589c92-512" width = "200" width = "200" />](https://github.com/Jordan-Ireland/)                       |                      [<img src="https://www.dalesjewelers.com/wp-content/uploads/2018/10/placeholder-silhouette-male.png" width = "200" />](https://github.com/skredenmathias/)                                         
|                 [<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/AVdata/)                 |            [<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/Jordan-Ireland/)             |           [<img src="https://github.com/favicon.ico" width="15"> ](https://github.com/skredenmathias/)
| [ <img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/in/vargasstem/) | [ <img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/in/jordan-b-ireland/) | [ <img src="https://static.licdn.com/sc/h/al2o9zrvru7aqj8e1x2rzsrca" width="15"> ](https://www.linkedin.com/in/skredenmathias/) 

## Project Overview

[Product Canvas][notion]

### Project Description:

This project began as a greenfield project proposed by [Jarie Bolander][jarie] in collaboration with Lambda School Labs\
students. The aim of this project is to provide historical analysis of traffic flow within the SFMTA system.\
We hope to give citizens, oversight committee members, and SFMTA staff accurate and timely historical data,\
along with statistics and analysis, to make informed decisions for system wide improvements.

We are serving our reports generated from our data and analysis through [datadriventransit.org][live].\
Our raw data and analysis is available through our API[api];\
further information on accessing and maintaining the API can be found [here][apireadme].

[The Front End][live]

### Tech Stack

- [Python][python]
- [PostgreSQL][postgres]
- [AWS RDS][rds]
- [AWS Lambda][lambda]
- [AWS Elastic Beanstalk][eb]
- [AWS Amplify][amplify]
- [Pandas][pandas]
- [Mapbox][mapbox]
- [Flask][flask]
- [Google Colab][colab]
- [Jupyter Lab][jupyter]

### Predictions

Considering the complexity, volume, and feature engineering required for this project, a significant amount of time was\
invested in thinking about potential approaches to the analysis, pipeline engineering, and data storage.\
Much of the exploratory and experimental work done by Labs 24 is available [here][labs24];\
similarly, exploratory work done by Labs 22 is available [here][labs22].

We are not serving any predictions here, nor was that our goal. However, given the foundation now laid, it may be\
within grasp of a future cohort to begin actual predictive modeling on this data in the form of predicting ETAs,\
service disruptions, etc.

### Data Sources

Our primary source of data is [NextBus][nextbus], via the [RestBus API][restbus]. This data consists of route and\
schedule data made available by SFMTA, as well as detailed vehicle-level data for every active vehicle in the SFMTA\
system, every minute. A detailed breakdown of this data is available [here][data].

### README TODO:

- how-to:
  - connect to the db
  - onboard to AWS
- update contributors

## Contributing

Please note we have a [code of conduct][conduct]. 

Please follow it in all your interactions with the project.

### Issue/Bug Request

**If you are having an issue with the existing project code, please submit a bug report under the following guidelines:**
 - Check first to see if your issue has already been reported.
 - Check to see if the issue has recently been fixed by attempting to reproduce the issue
  using the latest master branch in the repository.
 - Create a live example of the problem.
 - Submit a detailed bug report including your environment & browser, 
 steps to reproduce the issue, actual and expected outcomes,  where you believe the issue is originating from, 
 and any potential solutions you have considered.

### Feature Requests

We would love to hear from you about new features which would improve this app and further the aims of our project. 

Please provide as much detail and information as possible to show us why you think your new feature should be implemented.

### Pull Requests

If you have developed a patch, bug fix, or new feature that would improve this app, please submit a pull request.\
It is best to communicate your ideas with the developers first before investing a great deal of time into a pull request to ensure that it will mesh smoothly with the project.

Remember that this project is licensed under the MIT license, and by submitting a pull request, you agree that your work will be, too.

#### Pull Request Guidelines

- Ensure any install or build dependencies are removed before the end of the layer when doing a build.
- Update the README.md with details of changes to the interface, including new plist variables, exposed ports, useful file locations and container parameters.
- Ensure that your code conforms to our existing code conventions and test coverage.
- Include the relevant issue number, if applicable.
- You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you.

### Attribution

These contribution guidelines have been adapted from [this template][pr].

## Documentation

See [Backend Documentation][be] for details on the backend of our project.

See [Front End Documentation][fe] for details on the front end of our project.

[live]: datadriventransit.org
[notion]: https://www.notion.so/SFMTA-Data-Analysis-d5d25791fbca4b1bbd0049f95275e5a0
[jarie]: https://www.linkedin.com/in/jariebolander/
[api]: http://ds.datadriventransit.org/
[apireadme]: sfmta-data-analysis-ds/sfmta-api/README.md
[python]: https://www.python.org
[postgres]: https://www.postgresql.org/
[rds]: https://aws.amazon.com/rds/
[lambda]: https://aws.amazon.com/lambda/
[eb]: https://aws.amazon.com/elasticbeanstalk/
[amplify]: https://aws.amazon.com/amplify/
[pandas]: https://pandas.pydata.org/
[mapbox]: https://www.mapbox.com/
[flask]: https://flask.palletsprojects.com/en/1.1.x/
[colab]: https://colab.research.google.com/notebooks/intro.ipynb#recent=true
[jupyter]: https://jupyter.org
[labs24]: sfmta-data-analysis-ds/labs24_notebooks
[labs22]: sfmta-data-analysis-ds/deprecated_assets/labs22_notebooks
[nextbus]: www.nextbus.com
[restbus]: http://restbus.info/
[data]: sfmta-data-analysis-ds/DATAREADME.md
[conduct]: sfmta-data-analysis-ds/code_of_conduct.md
[pr]: https://gist.github.com/PurpleBooth/b24679402957c63ec426
[be]: https://github.com/Lambda-School-Labs/sfmta-data-analysis-be
[fe]: https://github.com/Lambda-School-Labs/sfmta-data-analysis-fe
