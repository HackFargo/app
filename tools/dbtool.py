import sqlite3
import os
import glob
import simplejson
from datetime import datetime
from geofudge import geofudge

# should probably remove these values, which are always returned by mapquest
# ... but sometimes mapquest still returns others. Looks like a default.
# 1700 BLK DAKOTA DR N Fargo, ND
# 36789/216138 (17.02107%)  46.876960000, -96.784636000 - mapquest
# 10/9245 (0.10817%)  46.263918000, -96.605505000 - mapquest


import geocoder
geo = {'google': geocoder.google,
       'mapquest': geocoder.mapquest,
       'tomtom': geocoder.tomtom,
       'arcgis': geocoder.arcgis}


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
conn = sqlite3.connect('hackfargo.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()


def update_record(CFSID, lat, lon, lookup_type=1):
    query = 'update DispatchLogs set Lat=?, Long=?, GeoLookupType=? where CFSID=?'
    c.execute(query, (lat, lon, lookup_type, CFSID))


def update_geo_real():
    '''
        Use a true upstream geocoder to identify the locations
    '''
    query = '''select * from DispatchLogs where Long=-96.784636'''
    c.execute(query)
    rows = c.fetchall()
    success = 0
    total = len(rows)
    i = 0
    for r in rows:
        # if r['GeoLookupType'] == 2:
            # print 'skipping...'
            #i += 1
            # continue
        address = "%s %s, ND" % (r['Address'], r['VenueDescription'])
        result = geocoder.google(address).latlng
        coder = 'google'
        #result = [None, None]
        #coder = 'none'
        if (result[0] == None):
            #result = geocoder.tomtom(address).latlng
            coder = 'tomtom'
        if (result[0]) == None:
            try:
                result = geocoder.mapquest(address).latlng
            except simplejson.decoder.JSONDecodeError:
                # invalid address parsing error
                pass

            if result[1] == -96.784636:
                result = [None, None]
            coder = 'mapquest'
        if (result[0]) == None:
            result = geocoder.google(address).latlng
            coder = 'google'
        lat, lon = result
        print address
        print '%d/%d (%.5f%%)  %.9f, %.9f - %s' % (i, total, (float(i) / total) * 100, lat, lon, coder)
        if lat != None:
            update_record(r['CFSID'], lat, lon, 2)
            success += 1
        conn.commit()
        i += 1
    print success, 'successful lookups of ', total, ' total rows'


def update_geo():
    query = '''select * from DispatchLogs where GeoLookupType<>2'''
    c.execute(query)
    rows = c.fetchall()
    success = 0
    total = len(rows)
    for r in rows:
        try:
            b = r['Block']
            rn = r['StreetName']
            rt = r['StreetType']
            su = r['StreetSuffix']

            if len(su) >= 2:
                su = su[0]
            if (not su in ['S', 'N']):
                # Skip it
                raise ValueError

            if (rt == ''):
                # '13 AVE'
                print b, rn, rt, su
                if rn.upper() == 'BROADWAY':
                    rt = 'ST'
                    print '   Broadway Fixed'
                else:
                    tokens = r['StreetName'].split(" ")
                    if (len(tokens) == 1):
                        # I94
                        print '   ====> invalid token', tokens
                        raise
                    else:
                        rn = tokens[0]
                        rt = tokens[1]
                        print ' ', rn, rt, ' fixed with tokens'
            # 16 1/2 street
            if ('1/2' in rn):
                tokens = rn.split(" ")
                rn = float(tokens[0]) + .5
            block = int(b)
            roadNum = float(rn)
            roadType = str(rt.upper())
            suffix = str(su.upper())
            if (not rt.upper() in ['ST', 'AVE']):
                # don't parse lanes, cir, etc.
                raise ValueError
        except ValueError:
            print r['Block'], r['StreetName'].upper(), '... trying to fix'
            if r['StreetName'].upper() == 'UNIVERSITY':
                roadNum = 13
                roadType = "ST"
                suffix = "N"
                print '   University fixed'
            elif r['StreetName'].upper() == 'BROADWAY':
                roadNum = 6
                roadType = "ST"
                suffix = "N"
                print '   Broadway Fixed (mapped)'
            elif r['StreetName'].upper() == 'MAIN':
                roadNum = 0
                roadType = "AVE"
                suffix = "N"
                print '   MAIN Fixed'
            elif r['StreetName'].upper() == 'NORTHERN PACIFIC':
                roadNum = .5
                roadType = "AVE"
                suffix = "N"
                print '   NP Ave Fixed'
            else:
                print '   invalid name:', b, rn, rt, su
                continue

        lat, lon = geofudge(int(block), float(roadNum), str(roadType), str(suffix))
        success += 1

        update_record(r['CFSID'], lat, lon)
    conn.commit()
    print success, 'successful lookups of ', total, ' total rows'


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
        CFSID INTEGER UNIQUE,
        VenueName TEXT,
        VenueDescription TEXT,
        Block TEXT,
        StreetPrefix TEXT,
        StreetPretype TEXT,
        StreetName TEXT,
        StreetType TEXT,
        StreetSuffix TEXT,
        Lat REAL,
        Long REAL,
        GeoLookupType INTEGER
        )'''
    #c.execute('DROP TABLE DispatchLogs')
    #c.execute('DROP TABLE BuildingPermits')
    try:
        c.execute(schema)

        # Create Indices
        c.execute('CREATE INDEX i1 ON DispatchLogs (IncidentNumber)')
        c.execute('CREATE INDEX i2 ON DispatchLogs (CallType)')
        c.execute('CREATE INDEX i3 ON DispatchLogs (VenueName)')
    except sqlite3.OperationalError:
        pass

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
                VenueDescription, DateVal, Lat, Long, GeoLookupType) VALUES (?, ?, ?, ?, ?, 
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                '''
            try:
                conn.execute(query, (d['CallType'], d['AdditionalInfo'],
                                     d['NatureOfCall'], d['StreetType'], d['VenueName'], d['Address'],
                                     d['StreetPreType'], d['DateString'], d['Duration'], d['StreetSuffix'],
                                     d['Block'], d['IncidentNumber'], d['CFSID'], d['StreetPrefix'],
                                     d['StreetName'], d['VenueDescription'], dateval, lat, lon, 0))
            except sqlite3.IntegrityError:
                # non-unique data
                pass
    conn.commit()

# CREATE INDEX index_name ON DispatchLogs (column_name)
# CREATE UNIQUE INDEX index_name ON DispatchLogs (column_name)

if __name__ == "__main__":
    # dbinit()
    populate()

    # update_geo_real()
    # conn.close()
