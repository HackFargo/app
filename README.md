app
===

The main repository for project hack fargo

## Sample API Usage
All calls will return a max of 10,000 records.

Get the calls from the last 15 days:
```
http://api.hackfargo.co/calls
```

Get the calls from the from a date range:
```
http://api.hackfargo.co/calls?start=6-20-2013&end=6-21-2013
```

Get the calls related to specific incident type:
```
http://api.hackfargo.co/calls/type/Party
```

Get the calls related to specific incident type with a date range:
```
http://api.hackfargo.co/calls/type/Party?start=3-3-2014&end=3-4-2014
```

## Sample Data from API
```
[
  {
    "DataSetID": "DispatchLogs",
    "Lat": 46.81618741541262,
    "Long": -96.88359341719978,
    "Date": 1394258006,
    "Description": "LOUD PEOPLE/MARIJUANA ODOR",
    "Meta": {
      "id": 215986,
      "DateString": "3/7/2014 11:53:26 PM",
      "DateVal": 1394258006,
      "Address": "900 BLK 44 ST S",
      "NatureOfCall": "LOUD PEOPLE/MARIJUANA ODOR",
      "CallType": "Loud Party/People",
      "IncidentNumber": "",
      "Duration": "",
      "AdditionalInfo": "",
      "CFSID": -5202747,
      "VenueName": "FGO",
      "VenueDescription": "Fargo",
      "Block": "900",
      "StreetPrefix": "",
      "StreetPretype": "",
      "StreetName": "44",
      "StreetType": "ST",
      "StreetSuffix": "S",
      "Lat": 0,
      "Long": 0
    }
  },
  {
    "DataSetID": "DispatchLogs",
    "Lat": 46.830937295065304,
    "Long": -96.79115266298359,
    "Date": 1394164277,
    "Description": "LOUD TV",
    "Meta": {
      "id": 215829,
      "DateString": "3/6/2014 9:51:17 PM",
      "DateVal": 1394164277,
      "Address": "4200 BLK 9 AVENUE CIR S",
      "NatureOfCall": "LOUD TV",
      "CallType": "Loud Noise",
      "IncidentNumber": "2014-00013015",
      "Duration": "2326",
      "AdditionalInfo": "",
      "CFSID": -5202112,
      "VenueName": "FGO",
      "VenueDescription": "Fargo",
      "Block": "4200",
      "StreetPrefix": "",
      "StreetPretype": "",
      "StreetName": "9 AVENUE",
      "StreetType": "CIR",
      "StreetSuffix": "S",
      "Lat": 0,
      "Long": 0
    }
  }
]
```
