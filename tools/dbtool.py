import sqlite3
import os
import glob
import simplejson
from datetime import datetime

conn = sqlite3.connect('hackfargo.db')
c = conn.cursor()


def dbinit():
    schema = '''
        create table DispatchLogs(
        id INTEGER PRIMARY KEY,
        DateString TEXT,
        DateVal INTEGER ,
        Address TEXT,
        NatureOfCall TEXT,
        CallType TEXT,
        IncidentNumber TEXT,
        Duration TEXT,
        AdditionalInfo TEXT,
        CFSID INTEGER,
        VenueName TEXT,
        VenueDescription TEXT,
        Block TEXT,
        StreetPrefix TEXT,
        StreetPretype TEXT,
        StreetName TEXT,
        StreetType TEXT,
        StreetSuffix TEXT,
        Lat REAL,
        Long REAL
        )'''
    c.execute('DROP TABLE DispatchLogs')
    c.execute(schema)

    # Create Indices
    c.execute('CREATE INDEX i1 ON DispatchLogs (IncidentNumber)')
    c.execute('CREATE INDEX i2 ON DispatchLogs (CallType)')
    c.execute('CREATE INDEX i3 ON DispatchLogs (VenueName)')

    conn.commit()
'''(Pdb) data['DispatchLog'][0].items()
[
('CallType', 'SU'), 
('AdditionalInfo', ''), 
('NatureOfCall', 'SUSPICOUS SUBJECT'), 
('StreetType', 'AVE'), 
('VenueName', 'FGO'), 
('Address', '600 BLK NORTHERN PACIFIC AVE N'), 
('StreetPreType', ''), 
('DateString', '10/4/2012 11:56:54 PM'), 
('Duration', '785'), 
('StreetSuffix', 'N'), 
('Block', 600), 
('IncidentNumber', '2012-00008589'), 
('CFSID', -4909477), 
('StreetPrefix', ''), 
('StreetName', 'NORTHERN PACIFIC'), 
('VenueDescription', 'Fargo')
]
'''


def populate(folder='json/'):
    #files = glob.glob(os.path.join(folder, '*.json'))
    # for f in files:
    f = 'combined.json'
    with open(os.path.join(folder, f), 'r') as h:
        data = simplejson.load(h)['DispatchLog']
        print 'loaded %d items for %s' % (len(data), f)
        n = len(data)
        for i, d in enumerate(data):
            if (i % 5000 == 0):
                print '   (%.0f%%) %d/%d items processed' % ((float(i) / n) * 100, i, n)
            dt = datetime.strptime(d['DateString'], '%m/%d/%Y %I:%M:%S %p')
            # unix timestamp value of the parsed date object
            dateval = dt.strftime('%s')
            lat = 0
            lon = 0
            for (key, val) in d.items():
                if (isinstance(val, basestring)):
                    d[key] = val.strip()
            query = '''INSERT INTO DispatchLogs (CallType, AdditionalInfo, NatureOfCall,
                StreetType, VenueName, Address, StreetPreType, DateString, Duration,
                StreetSuffix, Block, IncidentNumber, CFSID, StreetPrefix, StreetName,
                VenueDescription, DateVal, Lat, Long) VALUES (?, ?, ?, ?, ?, 
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
            conn.execute(query, (d['CallType'], d['AdditionalInfo'],
                                 d['NatureOfCall'], d['StreetType'], d['VenueName'], d['Address'],
                                 d['StreetPreType'], d['DateString'], d['Duration'], d['StreetSuffix'],
                                 d['Block'], d['IncidentNumber'], d['CFSID'], d['StreetPrefix'],
                                 d['StreetName'], d['VenueDescription'], dateval, lat, lon))
    conn.commit()

# CREATE INDEX index_name ON DispatchLogs (column_name)
# CREATE UNIQUE INDEX index_name ON DispatchLogs (column_name)

if __name__ == "__main__":
    dbinit()
    populate()
    conn.close()
