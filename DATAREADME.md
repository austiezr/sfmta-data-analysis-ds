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
    - live API source: http://webservices.nextbus.com/service/publicJSONFeed?command=routeConfig&a=sf-muni&r=1

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
  - live API source: http://webservices.nextbus.com/service/publicJSONFeed?command=schedule&a=sf-muni&r=1

### Locations Attributes:

Live API source: http://restbus.info/api/agencies/sf-muni/vehicles

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

### Local Bus Lines

Muni operates 44 local bus routes. Most routes operate on weekdays and weekends;\
the 41 and 88 operate only during weekday peak hours.

All numeric, 1-2 digit Route IDs indicate standard bus lines.\
Any Route IDs not meeting this standard indicate specialty service or different transit types.

### Rapid Bus Lines

On five high-ridership corridors, local buses are supplemented with rapid buses with limited stops. The Rapid routes largely follow the route of the local buses, with some variations.
- 5R: 5R-Fulton Rapid
  - weekdays until 7:00 PM
- 9R: 9R-San Bruno Rapid
  - weekdays until 7:00 PM
- 14R: 14R-Mission Rapid
  - every day until 7:00 PM
- 28R: 28R-19th Avenue Rapid
  - weekdays until 7:00 PM
- 38R: 38R-Geary Rapid
  - every day until 7:00 PM
  
### Express Bus Lines

Muni operates several types of express routes. Twelve routes operate between outer neighborhoods and downtown.\
Buses in the opposite direction run deadhead except for the 8AX and 8BX, which are paired with the local route 8 in the non-peak direction.\
Eight of the express routes are paired into 'A' and 'B' types, which have different local segments on the same corridor.
- 1AX: 1AX-California 'A' Express
- 1BX: 1BX-California 'B' Express
- 7X: 7x-Noriega Express
- 8AX: 8AX-Bayshore 'A' Express
- 8BX: 8BX-Bayshore 'B' Express
- 14X: 14X-Mission Express
- 30X: 30X-Marina Express
- 31AX: 31AX-Balboa 'A' Express
- 31BX: 31BX-Balboa 'B' Express
- 38AX: 38AX-Geary 'A' Express
- 38BX: 38BX-Geary 'B' Express
- Nx: Nx-N Express

Three additional routes provide shorter-distance express service between the Caltrain commuter rail terminal at 4th and King station and business areas near Market Street.\
Like the outer express routes, they operate only at peak hours.
- 81X: 81X-Caltrain Express
  - Operates only in peak direction
  - Operates only during morning
- 82X: 82X-Levi Plaza Express
  - Operates only in peak direction
- 83X: 83X-Mid-Market Express
  - Bidirectional service

Four express routes provide specialized service.
- 76X: 76X-Marin Headlands Express
  - Operates only on weekends and holidays
- 78X: 78X-16th Street Arena Express
  - Operates before and after games at the Chase Center
- 79X: 79X-Van Ness Arena Express
  - Operates before and after games at the Chase Center
- 714: 714-BART Early Bird
  - Limited number of trips between 4:00 and 5:00 AM

### Owl Service & Early Morning Service

Owl service runs every half hour between 1 and 5 a.m. nightly, for off peak commuters.\
Several Owl routes maintain designations from daytime services but run truncated routes.\
In addition to the Owl service, buses provide weekend service along all Muni Metro lines\
from 5am until rail service begins (6am on Saturdays, 8am on Sundays).\
Included below are only lines with unique OWL designations.
- 90: 90-San Bruno Owl
- 91: 91-Third Street/19th Avenue Owl
- K_OWL: K-Owl
  - Only operates in early morning and just after subway closes
- L_OWL: L-Owl
  - Operates all night
- N_OWL: N-Owl
  - Operates all night

### Historic Cable Cars

Three main lines; they run above ground and schedules remain relatively static. Outbound is to Fisherman's Wharf and Inbound is to Powell and Market.
- C: C-California Street Cable Car (weekday/weekend schedules vary)
- PH: PH-Powell-Hyde (schedule is static)
- PM: PM-Powell-Mason (Weekday/Weekend schedules vary)

### Historic Streetcars

Two streetcar lines (E and F) use historic streetcars but serve as full transit routes rather than tourist attractions.
- E: E-Embarcadero
- F: F-Market & Wharves

### Muni Metro Light Rail

The Muni Metro system consists seven light rail lines (six regular lines and one peak-hour shuttle), three tunnels, nine subway stations,\
twenty-four surface stations and eighty-seven surface stops.
- J: J-Church
- K: K-Ingleside
- T: T-Third Street
  - The K and T are interlined; trains switch designations at West Portal (inbound)\
   and Embarcadero (outbound)
- L: L-Taraval
- M: M-Ocean View
- N: N-Judah
- S: S-Shuttle
  - Only operates during peak hours and game days


[nextbus]: https://www.nextbus.com/
[mission]: https://www.sfmta.com/about-us/sfmta-strategic-plan/mission-vision
[restbus]: http://restbus.info/
[db]: https://raw.githubusercontent.com/Lambda-School-Labs/sfmta-data-analysis-ds/master/images/architecture_diagram.png
[readme]: README.md
[reports]: https://github.com/Lambda-School-Labs/sfmta-data-analysis-ds/blob/master/AWS_Lambda/Report_Generation/report_data_structure.md
