from dbtool import normalize_dispatch_address, random_dispatch, update_record, db_commit
import hackfargo


addresses = ['500 BLK 13 ave', '500 BLK 13 ave s', '13 ave s', '3600 BLK ELM ST N', '600 BLK NP AVE', '800 35 ave s', '3900 BLK 42 1/2 ST S']

# for a in addresses:
#    print a.ljust(30), '|', str(normalize_dispatch_address(a, 'Fargo, ND')).ljust(30)

status = {'good': 0, 'bad': 0, 'failed': 0}
for a in random_dispatch(200000):
    address = a['Address']
    normal = str(normalize_dispatch_address(address, 'Fargo, ND'))
    query = hackfargo.geocode(normal)
    if len(query) > 0:
        rating = query[0]['rating']
    else:
        rating = 'n/a'
    print address.ljust(40), '|', normal.ljust(40), '|', rating

    if (rating == 'n/a'):
        status['failed'] += 1
    elif (rating <= 6):
        status['good'] += 1
        # update it...
        update_record(a['CFSID'], query[0]['lat'], query[0]['lon'], 3)
        db_commit()
    else:
        status['bad'] += 1

total = sum(status.values())
processed = status['good'] + status['failed']
print '#' * 80
print 'good:  ', status['good'], '%.0f%%' % ((status['good'] / float(total) * 100)), '(%.0f%%)' % ((status['good'] / float(processed) * 100))
print 'bad:   ', status['bad'], '%.0f%%' % ((status['bad'] / float(total) * 100)), '(%.0f%%)' % ((status['bad'] / float(processed) * 100))
print 'failed:', status['failed'], '%.0f%%' % ((status['failed'] / float(total) * 100))
