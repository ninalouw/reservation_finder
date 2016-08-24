# bcferries
Find an available reservation

## Installation
```bash
$ pip install -r requirements.txt
```

### Make sure everything is working 
```bash
$ python reservations.py
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
Note: this will look for sailings 5 days from now from Horseshoe Bay to Departure Bay

## Usage
```python
from datetime import datetime
from reservations import Reservation

res = Reservation(departure_terminal='Tswawwassen', arrival_terminal='Duke Point',
                  departure_date=datetime(2016, 9, 1))
res.get_available_sailings()  # returns list of Sailing objects
```



