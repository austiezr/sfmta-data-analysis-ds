# This document provides information on the SFMTA dataset features

- Data points are collected by the nextbus company in collaboration with the MUNI and BART, within the San Francisco Municipal Transit Authority (SFMTA).  The following link will direct you to the nextbus services [link]<http://www.nextbus.com/>

-  The SFMTA's mission statement is provided in the link below:
    [link]<https://www.sfmta.com/about-us/sfmta-strategic-plan/mission-vision>

- Following will be descriptions of the features provided by nextbus's public XML Feed document
    - The document contains information on how to utilize the API to obtain realtime information on municipal vehicles, with a brief introduction to XML.

## Features and Attributes

##### Note: A large part of this document is a paraphrasing (not verbatim) of the publicXMLFeed document provided by nextbus.  Anywhere text is copied verbatim will be clearly stated.

##### Note on returned data
- The returned data is a list of lists; stops, directions, and paths.  Stops provided to show details; titles, lat/lon, and numID.
- Direction data (lat/lon) will be useful for user interface; "useForUI" set to True.


- Route list for an agency
    - Route lists are obtained through the link below:
    [link]<http://webservices.nextbus.com/service/publicXMLFeed?command=routeList&>
    - After the ampersand, at the end of the link, include the agency variable 'a=<agency>'

### The following is an outline of the attributes for specific features of the dataset

- 'routeConfig' attributes (copied verbatim): Returns a list of routes for an agency. The agency is specified by the "a" parameter in the query string. The route is optionally specified by the "r" parameter. The tag for the route is obtained using the routeList command. If the "r" parameter is not specified, XML data for all routes for the agency is returned. Due to the large size of the resulting XML the routeConfig command is limited to providing data for only up to 100 routes per request. If an agency has more than 100 routes then multiple requests would need to be used to read data for all routes.

    - tag
        - unique alphanumeric identifier for route, such as “N”.
    - title
        - the name of the route to be displayed in a User Interface, such as “N-Judah”
    - shortTitle
        - for some transit agencies shorter titles are provided that can be useful for
        User Interfaces where there is not much screen real estate, such as on smartphones. This element is only provided where a short title is actually available. If a short title is not available then the regular title element should be used.
    - color
        - the color in hexadecimal format associated with the route. Useful for User Interfaces such as maps.
    - oppositeColor
        - the color that most contrasts with the route color. Specified in hexadecimal format. Useful for User Interfaces such as maps. Will be either black or white.
    - latMin, latMax, lonMin, lonMax
        - Specifies the extent of the route.  For instance minimum/maximum lon/lat refer to the minimum and maximums positional geographic points covered by a given route.

- SFMTA 'stop' attributes:

    - tag: Unique alphanumeric identifier; depending on the agency, the suffixes may change in the stop tag.

        - E: E-Embarcadero (I: FW, O: MB)
        - F: F-Market & Wharves (I: FW, O: Castro)
        - J: J-Church (I: ES or FE, O: BP)
        - JBUS: JBUS-J Church Bus (I: E, O:BP)
        - KT: KT-Ingleside-Third Street (I: BP, O: S&B)
        - KTBU: KTBU-Kt Ingleside/Third Bus (I:, O:)
        - KLM: KLM-Bus Muni Metro Shuttle
        - L: L-Taraval
        - LBUS: LBUS-L Taraval Bus
        - M: M-Ocean View
        - MBUS: MBUS-M Ocean View Bus
        - N: N-Judah
        - NBUS: NBUS-N Judah Bus Substitution
        - NX: NX-Express
        - S: S-Shuttle
        - 1: 1-California
        - 1AX: 1AX-California A Express
        - 1BX: 1BX-California B Express
        - 2: 2-Sutter/Clement
        - 3: 3-Jackson
        - 5: 5-Fulton
        - 5R: 5R-Fulton Rapid
        - 6: 6-Haight-Parnassus
        - 7: 7-Haight-Noriega
        - 7X: 7X-Noriega Express
        - 8: 8-Bayshore
        - 8AX: 8AX-Bayshore A Express
        - 8BX: 8BX-Bayshore B Express
        - 9: 9-San Bruno
        - 9R: 9R-San Bruno Rapid
        - 10: 10-Townsend
        - 12: 12-Folsom-Pacific
        - 14: 14-Mission
        - 14: 14R-Mission Rapid
        - 14X: 14X-Mission Express
        - 18: 18-46th Avenue
        - 19: 19-Polk
        - 21: 21
        - 22: 22-Fillmore
        - 23: 23-Monterey
        - 24: 24-Divisadero
        - 25: 25-Treasure Island
        - 27: 27-Bryant
        - 28: 28-19th Avenue
        - 28R: 28R-19th Avenue Rapid
        - 29: 29-Sunset
        - 30: 30-Stockton
        - 30X: 30X-Marina Express
        - 31: 31-Balboa
        - 31AX: 31AX-Balboa A Express
        - 31BX: 31BX-Balboa B Express
        - 33: 33-Ashbury-18th St
        - 35: 35-Eureka
        - 36: 36-Teresita
        - 37: 37-Corbett
        - 38: 38-Geary
        - 38R: 38R-Geary Rapid
        - 38AX: 38AX-Geary A Express
        - 38BX: 38BX-Geary B Express
        - 39: 39-Coit
        - 41: 41-Union
        - 43: 43-Masonic
        - 44: 44-O'Shaughnessy
        - 45: 45-Union-Stockton
        - 47: 47-Van Ness
        - 48: 48-Quintara-24th Street
        - 49: 49-Van Ness-Mission
        - 52: 52-Excelsior
        - 54: 54-Felton
        - 55: 55-16th Street
        - 56: 56-Rutland
        - 57: 57-Parkmerced
        - 66: 66-Quintara
        - 67: 67-Bernal Heights
        - 76X: 76X-Marin Headlands Express
        - 78X: 78X-16th Street Arena Express
        - 79X: 79X-Van Ness Arena Express
        - 81X: 81X-Caltrain Express
        - 82X: 82X-Levi Plaza Express
        - 83X: 83X-Mid-Market Express
        - 88: 88-Bart Shuttle
        - 714: 714-Bart Early Bird
        - 90: 90-San Bruno Owl
        - 91: 91-Owl
        - K_OWL: K-Owl
        - L_OWL: L-Owl
        - N_OWL: N-Owl
        - PM: PM-Powell-Mason
        - PH: PH-Powell-Hyde
        - C: C-California Street Cable Car

- The Owl service
    - Owl service runs every half hour between 1 and 5 a.m. nightly, for off peak commuters.  Muni Owl connects other regions in the Bay Area.  The Muni Owls are divided into different levels of service:
        - Subway lines Running Owl Bus Service
            - K_OWL: K-Ingleside Owl (Bus)
            - N_OWL: N-Judah Owl (Bus)
            - L_OWL: L-Taraval Owl (Bus)
            - M: Ocean View Owl (Bus)'
            - T: T-Third Street Owl (Bus)'
            - 5: 5-Fulton
            - 14: 14-Mission'
            - 22: 22-Fillmore
            - 24: 24-Divisadero
            - 25: 25-Treasure Island
            - 38: 38-Geary
            - 44: 44-O'Shaughnessy
            - 48: 48-Quintara-24th Street
            - 90: 90-San Bruno Owl (Fort Mason-Visitacion Valley)
            - 91: 91-Owl  (SF State-West Portal)

- Cable Cars
    - Three main lines; they run above ground and schedules remain relatively static.  Note on out-bound and in-bound directionality; Outbound is to Fisherman's Wharf and Inbound is to Powell and Market.
        - C: C-California Street Cable Car (weekday/weekend schedules vary)
        - PH: PH-Powell-Hyde (schedule is static)
        - PM: PM-Powell-Mason (Weekday/Weekend schedules vary)

- Muni Metro Light Rail
    - 
