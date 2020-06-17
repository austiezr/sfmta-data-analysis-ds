# DataReadme TODO: 

- Update Route Attributes to reflect what we're currently collecting and using
- Fill out Stop Attributes
- Fill out Vehicle Report Attributes
- Flesh out notes on service types?
- Link to DB Schema (when complete)

## Notes On Data Collection And Use

Data points are collected by [NextBus][nextbus] in collaboration with SFMTA.\
We are accessing this data through the [RestBus API][restbus].

SFMTA's mission statement is provided [here][mission].

A diagram of our DB architecture is available [here][db], as well as in the [main README][readme].

## Outline of Available Data

### Route Attributes

- tag
    - Unique alphanumeric identifier for route, such as “N”.
- title
    - The name of the route.“N-Judah”
- shortTitle
    - Shorter titles are provided that can be useful for UIs where there is not much screen real estate, i.e. mobile. 
      - Only provided where a short title is actually available.
- color
    - The color in hexadecimal format associated with the route.
- oppositeColor
    - The color in hexadecimal that most contrasts with the route color.
- latMin, latMax, lonMin, lonMax
    - Specifies the extent of the route.

### Stop Attributes:

- tag: Unique alphanumeric identifier; depending on the agency, the suffixes may change in the stop tag.

### Vehicle Report Attributes

- 
        
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
