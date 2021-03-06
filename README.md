# API documentation
## Basic API Usage
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

### "Geo-fences"
We have recently added the ability to add "geo-fences". These allow you to filter against specific areas.
```
http://api.hackfargo.co/calls/type/cat/?start=10-26-2010&end=10-26-2011&maxLat=46.886&minLat=46.884&maxLong=-96.77&minLong=-96.88
```

You can you leave off any of these parameters and it just won't filter out anything based on what is let off. For example if you wanted to get calls for areas west of I-29 you would do something like:
```
http://api.hackfargo.co/calls?start=10-26-2010&end=10-26-2011&maxLong=-96.841045
```

## Sample Data from API
```
[
  {
    "DataSetID": "DispatchLogs",
    "Lat": 46.81618741541262,
    "Long": -96.88359341719978,
    "Date": 1394258006,   // Unix timestamp
    "Description": "LOUD PEOPLE/MARIJUANA ODOR", // This is the field that a type will filter against.
    "Meta": {
      "id": 215986,
      "DateString": "3/7/2014 11:53:26 PM",
      "DateVal": 1394258006,
      "Address": "900 BLK 44 ST S", // Note Address is are only accurate to a block level. Example: 314 Broadway becomes 300 Broadway.
      "NatureOfCall": "LOUD PEOPLE/MARIJUANA ODOR",
      "CallType": "Loud Party/People",
      "IncidentNumber": "",
      "Duration": "",
      "AdditionalInfo": "",
      "CFSID": -5202747,
      "VenueName": "FGO",
      "VenueDescription": "Fargo",
      "Block": "900", // Again this is only accurate to a block level.
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

The current bounds of the of the Lat and Long data values returned are as follows:
```
	latMax = 46.919749
	latMin = 46.803665
	longMax = -96.785670
	longMin = -96.900340
```


## Retrieving counts from the API. 
If instead of looking at specific incidents you just want a count of the incidents  you can add `/count` to the end of the path and instead of getting back specific incidents you will get a responce that has a count of number of calls that meet the criteria of your request.

Example count request:
```
http://api.hackfargo.co/calls/type/loud/count?start=6-20-2012&end=6-21-2013
```

Example count responce:
```
{
  "count": 1649
}
```
