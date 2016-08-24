# bcferries
Find an available reservation

## Installation
```bash
$ pip install -r requirements.txt
```

### Make sure everything is working 
```bash
$ python reservations.py  # this will look for sailings 7 days from now
Available Salings on August 30, 2016
From HORSESHOE BAY To DEPARTURE BAY
+-----------+----------+---------------------+
| Departure | Arrival  | Vessel              |
+-----------+----------+---------------------+
| 6:20 AM   | 8:00 AM  | Queen of Oak Bay    |
| 8:30 AM   | 10:10 AM | Coastal Renaissance |
| 10:40 AM  | 12:20 PM | Queen of Oak Bay    |
| 12:50 PM  | 2:30 PM  | Coastal Renaissance |
| 2:30 PM   | 4:10 PM  | Queen of Cowichan   |
| 5:20 PM   | 7:00 PM  | Coastal Renaissance |
| 7:30 PM   | 9:10 PM  | Queen of Oak Bay    |
| 9:30 PM   | 11:10 PM | Coastal Renaissance |
+-----------+----------+---------------------+
```

## Usage
```python
from datetime import datetime
from reservations import Reservation

res = Reservation(departure_terminal='Tswawwassen', arrival_terminal='Duke Point',
                  departure_date='2016-09-01')
res.start()
sailngs = res.get_available_sailings()  # returns list of Sailing objects

### With context manager ###
with Reservation('Departure Bay', 'Vancouver', departure_date='Oct 1, 2016') as res:
    sailings = res.get_available_sailings()
    # do stuff with sailings
```

### Fuzzy Matching/Date Parsing
There is support for fuzzy matching on terminal names and automatic date parsing for the common date formats.



