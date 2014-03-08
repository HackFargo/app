'''
    This is a simple helper script that reads the json data from the fargo
    dispatch log site, and saves it to file. The date is then decremented
    by one using the python date library, then new data is downloaded
    and the whole thing starts over.

    This is done to not overload the server, and generally be friendly. 1
    second timeout between each call.
    '''

import urllib2
import os
from datetime import date, timedelta
#import simplejson
import time

# url = 'http://services.rrrdc.com/dispatchlogs/Service.asmx/SearchDispatchLogJSON?callback=jQuery172007480677240528166_1394264498029&Venue=FGO&StartDate=03%2F01%2F2014&EndDate=03%2F01%2F2014&Address=&Description=&CallType=&_=1394264550353'

# The URL where the data lives
url = 'http://services.rrrdc.com/dispatchlogs/Service.asmx/SearchDispatchLogJSON?callback=x&Venue=FGO&StartDate=%02d%%2F%02d%%2F%02d&EndDate=%02d%%2F%02d%%2F%02d&Address=&Description=&CallType=&_=1394264550353'

# Gotta start at yesterday
t1 = date.today() - timedelta(days=1)

while (True):
    print 'grabbing json for timestamp ' + t1.isoformat() + '...',
    resource = url % (t1.month, t1.day, t1.year, t1.month, t1.day, t1.year)
    req = urllib2.Request(resource)
    opener = urllib2.build_opener()
    f = opener.open(req)

    # get the actual data, minus the jQuery callback
    s = f.read()[2:-2]
    # simplejson.loads(s)

    # save to file
    if (not os.path.exists('json/')):
        os.mkdir('json/')
    fname = 'json/%02d-%02d-%04d.json' % (t1.month, t1.day, t1.year)
    open(fname, 'w').write(s)
    print 'wrote %s with %d bytes' % (fname, len(s))

    # update the time (subtract 1 day)
    t1 = t1 - timedelta(days=1)
    time.sleep(.2)
