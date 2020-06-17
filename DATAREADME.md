# DataReadme TODO: 

- Flesh out notes on service types?
- Link to DB Schema (when complete)

## Notes On Data Collection And Use

Data points are collected by [NextBus][nextbus] in collaboration with SFMTA.\
We are accessing this data through the [RestBus API][restbus].

SFMTA's mission statement is provided [here][mission].

A diagram of our DB architecture is available [here][db], as well as in the [main README][readme].

## Outline of Available Data

### Routes Attributes:

Note: Route definitions are stored for every route; as route definitions change, we assign end_dates to old versions\
and create new entries for new route definitions. For every unique route, the version with no end date is the active route definition.\
Previous route definitions are maintained for accurate use of historic data.

- rid
    - Unique alphanumeric identifier for route, such as 'LBUS'
- route_name
    - The name of the route, e.g. 'LBUS-L Taraval Bus'
- route_type
    - type of transport route services
      - bus, rapid, shuttle, etc.
- begin_date
    - timestamp for the earliest known date that route definition was in effect
- end_date
    - timestamp for the last known date that route definition was in effect
    - NULL as long as a route definition is active, otherwise populated
- content
  - JSON containing sfmta's definition of that route at that time
    - includes location data for all stops on that route as well as lat/lon definitions of the segments that make up the actual route

### Schedules Attributes:

Note: Schedule definitions are stored for every route; as route schedules change, we assign end_dates to old versions\
and create new entries for new schedules. For every unique route, the version with no end date is the active schedule.\
Previous schedules are maintained for accurate use of historic data.

- rid
  - Unique alphanumeric identifier for route, such as 'LBUS'
- begin_date
    - timestamp for the earliest known date that route schedule was in effect
- end_date
    - timestamp for the last known date that route schedule was in effect
    - NULL as long as a route schedule is active, otherwise populated
- content
  - JSON containing sfmta's schedule for that route at that time
  - includes list of scheduled stops for that route, with timestamps for scheduled service
  - includes schedules for several different classes of service based on day of week, time of day

### Locations Attributes:

- timestamp
  - time of vehicle report collection in UTC
- rid
  - route id that vehicle is assigned to
- vid
  - unique vehicle id number
- age
  - time in seconds from vehicle report to report collection
- kph
  - speed of vehicle in kilometers per hour at time of report
- heading
  - direction of vehicle motion in degrees
    - from 0 to 360, N = 0, E = 90, S = 180, W = 270
- latitude
  - latitude coordinate of vehicle at time of report
- longitude
  - longitude coordinate of vehicle at time of report
- direction
  - specifies route, inbound/outbound direction
  - format of: 
    - 5 digits containing route id and right-filled with underscores
    - followed by I or O for inbound vs outbound
    - followed by one underscore and three digits whose purpose we haven't identified
  - ex: LBUS_O_F00, 9____I_SOO

### Reports Attributes:

- date
  - date for which report is generated
- report
  - list of json objects containing reports for every active route in service as well as aggregate reports
  - reports are more fully explained [here][reports]
        
## Notes On Specific Service Types

### Owl Service

Owl service runs every half hour between 1 and 5 a.m. nightly, for off peak commuters. Muni Owl connects other regions in the Bay Area.

### Cable Cars

Three main lines; they run above ground and schedules remain relatively static. Outbound is to Fisherman's Wharf and Inbound is to Powell and Market.
- C: C-California Street Cable Car (weekday/weekend schedules vary)
- PH: PH-Powell-Hyde (schedule is static)
- PM: PM-Powell-Mason (Weekday/Weekend schedules vary)

### Muni Metro Light Rail


[nextbus]: https://www.nextbus.com/
[mission]: https://www.sfmta.com/about-us/sfmta-strategic-plan/mission-vision
[restbus]: http://restbus.info/
[db]: https://raw.githubusercontent.com/Lambda-School-Labs/sfmta-data-analysis-ds/master/images/architecture_diagram.png
[readme]: README.md
[reports]: https://github.com/Lambda-School-Labs/sfmta-data-analysis-ds/blob/master/AWS_Lambda/Report_Generation/report_data_structure.md
